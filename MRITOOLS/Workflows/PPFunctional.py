#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 16:33:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Workflow for pre-processing functional data
# Nodes: Converter, Extracter, SpaceRealigner,TimeRealigner, detrender Smoother.
# Inputs: 1) Directory containing functional data 2) Slice aquisition order, 3) fwhm of Gaussian smoother.
# Outputs: Functional data that has been converted, extracted, motion corrected, slice time corrected and smoothed.
# Plots of extraction, plots of motion params, plots of smoothed data are provided.
# Requires: fsl, nipype, nilearn, nipy
#---



#--- 1)  Import modules
import nipype.interfaces.dcm2nii as dcm2nii
import nipype.pipeline.engine as pe
import matplotlib
import os
from glob import glob
from nilearn import plotting
from nilearn import image
from nipype.interfaces.utility import Function
import nipype.interfaces.fsl.utils as fsl
import nipype.interfaces.fsl.preprocess as fslp
import nipype.interfaces.fsl.maths as fslm
from nipype.interfaces import afni as afni
import nipype.algorithms.rapidart as rad

#--- 2)  Record intial working directory

INITDIR=os.getcwd();

#--- 3) Prompt user for directory containing DICOM FILES

DICOMDIR=raw_input('Please drag in the directory of\nDICOM files you wish to convert\n(ensure there is no blank space at the end)')

#--- 3) Move to directory

os.chdir(DICOMDIR)


#--- 4) Set up converter node for conversion to nifti

converter=pe.Node(interface=dcm2nii.Dcm2nii(),name='CONVERTED')
converter.inputs.source_dir=DICOMDIR
converter.inputs.gzip_output=bool(1)


#--- 5) Set up realigner node to match orientation of MNI 152

realigner=pe.Node(interface=fsl.Reorient2Std(),name='REORIENTED')
realigner.inputs.output_type='NIFTI_GZ'



#--- 6) Set up a plotting node

def bplot(in_file):
	from nilearn import image
	from nilearn import plotting
	niftifiledim=len(image.load_img(in_file).shape)
	if niftifiledim == 3:
		print "Structural image detected. Displaying full image. For structural data, use the data contained within '/CROPPED'"
		display=plotting.plot_anat(in_file, title="Converted structural file")
	else:
		print "Functional image detected. Displaying first volume For functional data, use the data contained within /'REORIENTED'"
		firstim=image.index_img(in_file, 0)
		display=plotting.plot_anat(firstim,title="Volume 1 of funcional data")
	return niftifiledim


showconvert= pe.Node(Function(input_names=['in_file'],output_names=['niftifiledim'],function=bplot),name='SHOWCONVERT')


#--- 7) Set up a slice timing node


slicetimer=pe.Node(interface=fslp.SliceTimer(),name='SLICETIMED')
slicetimer.inputs.interleaved = True


#--- 8) Set up extraction node
extracter=pe.Node(interface=fslp.BET(),name='EXTRACTED')
extracter.inputs.frac=float(0.3)
extracter.inputs.vertical_gradient=float(-0.4)
extracter.inputs.functional=bool(1)


#--- 9) Set up a motion correction node
mcorrector=pe.Node(interface=fslp.MCFLIRT(),name='MOTION_CORRECTED')
mcorrector.inputs.save_plots=bool(1)
mcorrector.inputssave_mats=bool(1)


#--- 10) Set up a plot motion params node

plotmps=pe.Node(interface=fsl.PlotMotionParams(),name='PLOTTED_MOTION')
plotmps.inputs.in_source = 'fsl'
plottypes=['rotations','translations','displacement']
plotmps.iterables=([('plot_type',plottypes)])


#--- 11) Set up outlier detection node

AD=pe.Node(interface=rad.ArtifactDetect(),name='ATRTEFACT_DETECTED')
AD.inputs.parameter_source = 'FSL'
AD.inputs.norm_threshold = 1
AD.inputs.zintensity_threshold = 3
AD.inputs.save_plot=bool(1)

#--- 11) Set up a detrending node
detrender=pe.Node(interface=afni.Detrend(),name='DETRENDED')
detrender.inputs.args = '-polort 2'
detrender.inputs.outputtype = 'NIFTI_GZ'


#--- 11) Set up a despiking npde
despiker=pe.Node(interface=afni.Despike(),name='DESPIKED')
despiker.inputs.outputtype = 'NIFTI_GZ'



#--- 12) Set up a smoothing node

smoother=pe.Node(interface=fslm.IsotropicSmooth(),name='SMOOTHED')
smoother.inputs.fwhm=float(5)



#--- 13) Set up workflow

workflow = pe.Workflow(name='PPFUNCTIONAL')
workflow.base_dir = DICOMDIR



#--- 8) Connect nodes.

workflow.connect(converter,'converted_files',realigner,'in_file')
workflow.connect(realigner,'out_file',showconvert,'in_file')
workflow.connect(realigner,'out_file',slicetimer,'in_file')
workflow.connect(slicetimer,'slice_time_corrected_file',extracter,'in_file')
workflow.connect(extracter,'out_file',mcorrector,'in_file')
workflow.connect(mcorrector,'par_file',plotmps,'in_file')
workflow.connect(mcorrector,'out_file',detrender,'in_file')
#workflow.connect(mcorrector,'par_file',AD,'realignment_parameters')
#workflow.connect(mcorrector,'out_file',AD,'realigned_files')
workflow.connect(detrender,'out_file',despiker,'in_file')
workflow.connect(despiker,'out_file',smoother,'in_file')



workflow.write_graph(graph2use='exec')

#--- 9) Run workflow

result=workflow.run()

#--- 10) Show plot
matplotlib.pyplot.show()

print "Returning to intital directory"

os.chdir(INITDIR)
