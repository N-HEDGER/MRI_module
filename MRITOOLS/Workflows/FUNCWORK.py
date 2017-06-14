from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range


#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 9 12:00:00 2017
@author: naah1g08
"""
#--- Goal of the function:
# Use dcm2nii, FSL and AFNI to form a funcitonal pre-processing pipeline

# Inputs:
# directory of DICOM files
# fwhm of Gaussian smoother (mm)
# highpass filter cutoff (secs).
# TR (secs)

# Outputs:
# 1) / CONVERTED - nifti file (dcm2nii)
# 2) / REORIENTED - reoriented nifti file (FSL).
# 3) / SLICETIMED - Sicetimed file (FSL)
# 4) / IMG2FLOAT - conversion to float (FSL)
# 5) / MCORRECTED - motion corrected file (FSL)
# 6) / DESPIKED - despiked file (AFNI)
# 7) / MOTION PLOTTED - (FSL, actually contained within MCORRECTED)
# 8) / EXTRACTED - extracted brain, extracted brain mask (FSL)
# 9) / SMOOTHED - Smoothed data (AFNI)
# 10) / HIGHPASSED - Temporal filtered data (FSL)
# 11) / PREPROCESSED - Filtered data with mean added on (FSL)

# MEANFUNCTIONAL - mean functional volume (FSL)
# SHOWEXTRACT - visualise extraction (nilearn)
# SHOWSMOOTH - visualise smoothing (nilearn)

# Requires: dcm2nii, nipype, nilearn, nibabel, dcm2nii, fsl, afni


#--- Details

# Interleaved aquisition is assumed.
# Slice timing is relative to middle slice
# Motion correction is relative to middle volume, spline interpolation.
# Extraction is plotted
# Smoothing is plotted

#--- 


def FUNCPIPE():
	#--- 1)  Import modules

	import os                                    # system functions
	import nipype.interfaces.dcm2nii as dcm2nii
	import nipype.interfaces.io as nio           # Data i/o
	import nipype.interfaces.fsl as fsl          # fsl
	import nipype.interfaces.utility as util     # utility
	import nipype.pipeline.engine as pe          # pypeline engine
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


	tolist = lambda x: [x]
	highpass_operand = lambda x:'-bptf %.10f -1'%x

	#--- 2) Prompt user for directory containing DICOM FILES

	INITDIR=os.getcwd();

	#--- 3) Prompt user for inputs.

	DICOMDIR=raw_input('Please drag in the directory of\nDICOM files you wish to pre-process\n(ensure there is no blank space at the end)\n')
	print ('---\n')
	DICOMDIR=DICOMDIR.strip('\'"')
	FWHM=float(input('Please enter the FWHM of the smoother (mm) \n'))
	print ('---\n')
	HIGHPASS=float(input('Please enter the High Pass filter cutoff (s)\n'))
	print ('---\n')
	TR=float(input('Please enter the TR (s)\n'))
	print ('---\n')


	#--- 4) Define workflow and input node.

	workflow = pe.Workflow(name='FUNCPIPE')
	inputnode = pe.Node(interface=util.IdentityInterface(fields=['fwhm','highpass','TR']),name='inputspec')

	inputnode.inputs.fwhm=FWHM
	inputnode.inputs.TR=TR
	inputnode.inputs.highpass=float(HIGHPASS/(inputnode.inputs.TR*2.5))


	#--- 5) Move to directory
	os.chdir(DICOMDIR)


	#--- 6) Set up converter node for conversion to nifti
	converter=pe.Node(interface=dcm2nii.Dcm2nii(),name='CONVERTED')
	converter.inputs.source_dir=DICOMDIR
	converter.inputs.gzip_output=bool(1)


	#--- 7) Set up realigner node to match orientation of MNI 152
	realigner=pe.Node(interface=fslu.Reorient2Std(),name='REORIENTED')
	realigner.inputs.output_type='NIFTI_GZ'

	workflow.connect(converter,'converted_files',realigner,'in_file')


	#--- 8) Set up a slice timing node
	slicetimer=pe.Node(interface=fslp.SliceTimer(),name='SLICETIMED')
	slicetimer.inputs.interleaved = True

	workflow.connect(inputnode, 'TR', slicetimer, 'time_repetition')
	workflow.connect(realigner, 'out_file', slicetimer, 'in_file')


	#--- 9) Convert to float.
	img2float = pe.Node(interface=fsl.ImageMaths(out_data_type='float',op_string='',suffix='_dtype'),name='IMG2FLOATED')

	workflow.connect(slicetimer,'slice_time_corrected_file',img2float,'in_file')

	#--- 10) Motion correct.
	motion_correct = pe.Node(interface=fsl.MCFLIRT(save_mats=True,save_plots=True,interpolation='spline'),name='MCORRECTED')

	workflow.connect(img2float, 'out_file', motion_correct, 'in_file')


	#--- 11) Despike
	despiker=pe.Node(interface=afni.Despike(),name='DESPIKED')
	despiker.inputs.outputtype = 'NIFTI_GZ'

	workflow.connect(motion_correct,'out_file',despiker,'in_file')

	#--- 12) Plot motion.
	plot_motion = pe.Node(interface=fsl.PlotMotionParams(in_source='fsl'),name='MOTIONPLOTTED')
	plot_motion.iterables = ('plot_type', ['rotations', 'translations'])

	workflow.connect(motion_correct, 'par_file', plot_motion, 'in_file')

	#--- 13) Extract
	extracter=pe.Node(interface=fsl.BET(),name='EXTRACTED')
	extracter.inputs.frac=float(0.6)
	extracter.inputs.vertical_gradient=float(-0.1)
	extracter.inputs.mask=bool(1)
	extracter.inputs.functional=bool(1)

	workflow.connect(despiker, 'out_file', extracter, 'in_file')


	#--- 14) Smooth
	smoother=pe.MapNode(interface=afni.BlurInMask(),name='SMOOTHED',iterfield=['fwhm'])
	smoother.inputs.outputtype='NIFTI_GZ'

	workflow.connect(inputnode, 'fwhm', smoother, 'fwhm')
	workflow.connect(extracter, 'out_file', smoother, 'in_file')
	workflow.connect(extracter, 'mask_file', smoother, 'mask')


	#--- 15) Highpass filter

	# Filtering node
	highpass = pe.MapNode(interface=fsl.ImageMaths(suffix='_tempfilt'),name='HIGHPASSED',iterfield=['in_file'])

	workflow.connect(inputnode, ('highpass', highpass_operand), highpass, 'op_string')
	workflow.connect(smoother, 'out_file', highpass, 'in_file')

	#--- 16) Mean functional volume
	# Need to add back the mean removed by FSL
	meanfunc = pe.MapNode(interface=fsl.ImageMaths(op_string='-Tmean',suffix='_mean'),name='meanfunc',iterfield=['in_file'])
	workflow.connect(smoother, 'out_file', meanfunc, 'in_file')

	#--- 17) Add mean back to highpassed data (FINAL OUTPUT)
	addmean = pe.MapNode(interface=fsl.BinaryMaths(operation='add'),name='PREPROCESSED',iterfield=['in_file','operand_file'])

	workflow.connect(highpass, 'out_file', addmean, 'in_file')
	workflow.connect(meanfunc, 'out_file', addmean, 'operand_file')

	outputnode = pe.Node(interface=util.IdentityInterface(fields=['highpassed_files']),name='outputnode')

	workflow.connect(addmean, 'out_file', outputnode, 'highpassed_files')



	# Utility function for plotting extraction
	def bplot(in_file,in_file2,in_file3):
		from nilearn import image
		from nilearn import plotting
		import matplotlib
		niftifiledim=len(image.load_img(in_file).shape)
		firstim=image.index_img(in_file, 0)
		firstim2=image.index_img(in_file2, 0)
		display=plotting.plot_anat(firstim2)	
		display.add_contours(firstim,filled=True, alpha=0.5,levels=[0.2], colors='b')
		display.add_edges(in_file3)
		matplotlib.pyplot.show()
		return niftifiledim

	#--- 18) Show extraction
	showextract= pe.Node(Function(input_names=['in_file','in_file2','in_file3'],output_names=['niftifiledim'],function=bplot),name='SHOWEXTRACT')

	workflow.connect(despiker,'out_file', showextract,'in_file2')
	workflow.connect(extracter,'out_file', showextract,'in_file')
	workflow.connect(extracter,'mask_file', showextract,'in_file3')

	# Utility function for plotting extraction
	def splot(in_file):
		from nilearn import image
		from nilearn import plotting
		import matplotlib
		niftifiledim=len(image.load_img(in_file).shape)
		firstim=image.index_img(in_file, 0)
		display=plotting.plot_anat(firstim,display_mode='z',cut_coords=10)
		matplotlib.pyplot.show()	
		return niftifiledim

	#--- 19) Show smoothing
	showsmooth= pe.MapNode(Function(input_names=['in_file'],output_names=['niftifiledim'],function=splot),iterfield=['in_file'],name='SHOWSMOOTH')

	workflow.connect(smoother,'out_file', showsmooth,'in_file')



	#--- 20) Mean functional volume (for plotting stats)
	meanfunc2 = pe.Node(interface=fsl.ImageMaths(op_string='-Tmean',suffix='_mean'),name='MEANFUNCTIONAL')
	workflow.connect(extracter, 'out_file', meanfunc2, 'in_file')
	workflow.connect(meanfunc2, 'out_file', outputnode, 'mean_functional_volume')

	#--- 21) Plot workflow
	workflow.base_dir = DICOMDIR
	workflow.write_graph(graph2use='exec')

	#--- 22) Plot workflow
	result=workflow.run()

	#--- 23) Show plots
	

	#--- 24) Return to initial working directory
	print ("Workflow completed. Returning to intital directory\n")
	os.chdir(INITDIR)







