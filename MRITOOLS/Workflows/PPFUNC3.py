#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 16:33:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Pre-processing pipeline.
# Use dcm2nii, FSL and AFNI to form a funcitonal pre-processing pipeline
# Inputs: directory of DICOM files, fwhm of Gaussian (smoothing), highpass filter (secs), TR

# Outputs:
# 1) / CONVERTED: nifti file.
# 2) / REORIENTED reoriented nifti file.
# 3) / CROPPED reoriented and cropped nifti file.

# Requires: dcm2nii, nipype, nilearn, nibabel. dcm2nii and fsl


#--- Details

# dcm2nii is recruited for conversion, but fsl is recruited for cropping and reorienting
# This is because dcm2nii doesnt seem to handle reorienting and cropping for partial brain 
# functional data.
# Reoriented files are plotted.
# The cropping stage may not be useful for functional data, since I dont know how it affects slice timing.

#--- 



#--- 1)  Import modules
from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range

import os                                    # system functions
import nipype.interfaces.dcm2nii as dcm2nii
import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.rapidart as ra      # artifact detection
import nipype.interfaces.fsl.utils as fslu
import nipype.interfaces.fsl.preprocess as fslp
from nipype.interfaces import afni as afni
from nipype.interfaces.utility import Function
import matplotlib
from nilearn import plotting
from nilearn import image

import os
import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.interfaces.freesurfer as fs    # freesurfer
import nipype.interfaces.spm as spm

tolist = lambda x: [x]
highpass_operand = lambda x:'-bptf %.10f -1'%x


INITDIR=os.getcwd();

workflow = pe.Workflow(name='FUNCPIPE')

# Define inputs
inputnode = pe.Node(interface=util.IdentityInterface(fields=['fwhm','highpass']),name='inputspec')


#--- 3) Prompt user for directory containing DICOM FILES

DICOMDIR=raw_input('Please drag in the directory of\nDICOM files you wish to convert\n(ensure there is no blank space at the end)')



# Define inputs
FWHM=input('Please enter the FWHM of the smoother')

inputnode.inputs.fwhm=FWHM
inputnode.inputs.highpass=float(18)


#--- 4) Move to directory

os.chdir(DICOMDIR)


#--- 5) Set up converter node for conversion to nifti
converter=pe.Node(interface=dcm2nii.Dcm2nii(),name='CONVERTED')
converter.inputs.source_dir=DICOMDIR
converter.inputs.gzip_output=bool(1)


#--- 6) Set up realigner node to match orientation of MNI 152
realigner=pe.Node(interface=fslu.Reorient2Std(),name='REORIENTED')
realigner.inputs.output_type='NIFTI_GZ'

workflow.connect(converter,'converted_files',realigner,'in_file')


#--- 7) Set up a slice timing node
slicetimer=pe.Node(interface=fslp.SliceTimer(),name='SLICETIMED')
slicetimer.inputs.interleaved = True
slicetimer.inputs.time_repetition = float(2)

workflow.connect(realigner, 'out_file', slicetimer, 'in_file')


#--- 8) Convert to float.
img2float = pe.Node(interface=fsl.ImageMaths(out_data_type='float',op_string='',suffix='_dtype'),name='IMG2FLOATED')

workflow.connect(slicetimer,'slice_time_corrected_file',img2float,'in_file')

#--- 9) Motion correct.
motion_correct = pe.Node(interface=fsl.MCFLIRT(save_mats=True,save_plots=True,interpolation='spline'),name='MCORRECTED')

workflow.connect(img2float, 'out_file', motion_correct, 'in_file')


#--- 10) Despike
despiker=pe.Node(interface=afni.Despike(),name='DESPIKED')
despiker.inputs.outputtype = 'NIFTI_GZ'

workflow.connect(motion_correct,'out_file',despiker,'in_file')

#--- 11) Plot motion.
plot_motion = pe.Node(interface=fsl.PlotMotionParams(in_source='fsl'),name='MOTIONPLOTTED')
plot_motion.iterables = ('plot_type', ['rotations', 'translations'])

workflow.connect(motion_correct, 'par_file', plot_motion, 'in_file')

#--- 12) Extract
extracter=pe.Node(interface=fsl.BET(),name='EXTRACTED')
extracter.inputs.frac=float(0.6)
extracter.inputs.vertical_gradient=float(-0.1)
extracter.inputs.mask=bool(1)
extracter.inputs.functional=bool(1)

workflow.connect(despiker, 'out_file', extracter, 'in_file')


#--- 11) Smooth
smoother=pe.MapNode(interface=afni.BlurInMask(),name='SMOOTHED',iterfield=['fwhm'])
smoother.inputs.outputtype='NIFTI_GZ'

workflow.connect(inputnode, 'fwhm', smoother, 'fwhm')
workflow.connect(extracter, 'out_file', smoother, 'in_file')
workflow.connect(extracter, 'mask_file', smoother, 'mask')


#--- 11) Highpass filter

# Filtering node
highpass = pe.MapNode(interface=fsl.ImageMaths(suffix='_tempfilt'),name='HIGHPASSED',iterfield=['in_file'])


workflow.connect(inputnode, ('highpass', highpass_operand), highpass, 'op_string')
workflow.connect(smoother, 'out_file', highpass, 'in_file')

# Need to add back the mean removed by FSL
meanfunc = pe.MapNode(interface=fsl.ImageMaths(op_string='-Tmean',suffix='_mean'),name='meanfunc',iterfield=['in_file'])
workflow.connect(smoother, 'out_file', meanfunc, 'in_file')

addmean = pe.MapNode(interface=fsl.BinaryMaths(operation='add'),name='ADDMEAN',iterfield=['in_file','operand_file'])

workflow.connect(highpass, 'out_file', addmean, 'in_file')
workflow.connect(meanfunc, 'out_file', addmean, 'operand_file')

outputnode = pe.Node(interface=util.IdentityInterface(fields=['highpassed_files']),name='outputnode')

workflow.connect(addmean, 'out_file', outputnode, 'highpassed_files')


def bplot(in_file,in_file2,in_file3):
	from nilearn import image
	from nilearn import plotting
	niftifiledim=len(image.load_img(in_file).shape)
	firstim=image.index_img(in_file, 0)
	firstim2=image.index_img(in_file2, 0)
	display=plotting.plot_anat(firstim2, title = "Extraction overlayed on original")	
	display.add_contours(firstim,filled=True, alpha=0.5,levels=[0.2], colors='b')
	display.add_edges(in_file3)
	return niftifiledim

#--- 12) Show extract

showextract= pe.Node(Function(input_names=['in_file','in_file2','in_file3'],output_names=['niftifiledim'],function=bplot),name='SHOWEXTRACT')

workflow.connect(despiker,'out_file', showextract,'in_file2')
workflow.connect(extracter,'out_file', showextract,'in_file')
workflow.connect(extracter,'mask_file', showextract,'in_file3')


meanfunc2 = pe.Node(interface=fsl.ImageMaths(op_string='-Tmean',suffix='_mean'),name='meanfunc2')
workflow.connect(extracter, 'out_file', meanfunc2, 'in_file')
workflow.connect(meanfunc2, 'out_file', outputnode, 'mean_functional_volume')


workflow.base_dir = DICOMDIR
workflow.write_graph(graph2use='exec')

#--- 13) Run workflow
result=workflow.run()

#--- 14) Show plot
matplotlib.pyplot.show()


os.chdir(INITDIR)







