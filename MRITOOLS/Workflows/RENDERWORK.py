#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 9 12:00:00 2017
@author: naah1g08
"""
#--- Goal of the function:
# Use FSL and ANTS transforms to render stats image in MNI space.

# Inputs:
# Stats image. Z/t score image in subject space.
# Combined linear transform (used to register functional data to MNI).
# ANTS normalisation composite transform (used to normalise the functional volume to the MNI).
# Thresh. Threshold for plotting the data. e.g. 2.3 will show voxels with a z score greater than 2.3.

# Outputs:
# 1) / RENDERREG - Regsitered stats image.
# 2) / RENDERNORM - Normalised stats image.


# Requires: nipype, nilearn, matplotlib, fsl


#--- Details

# Nilearn should plot the data to the MNI by default. 

#--- 

def RENDERPIPE():
	from nipype.interfaces.ants import Registration, ApplyTransforms
	import nipype.pipeline.engine as pe
	import matplotlib
	import os
	from glob import glob
	from nilearn import plotting
	from nilearn import image
	from nipype.interfaces.utility import Function
	import nipype.interfaces.fsl.preprocess as fsl
	import nipype.interfaces.fsl as fslbase
	import nipype.interfaces.fsl.utils as fslu
	from nipype.interfaces.fsl import Info
	import nipype.interfaces.utility as util


	thresh=float(raw_input('Please enter the threshold'))

	inputnode = pe.Node(interface=util.IdentityInterface(fields=['thresh']),name='inputnode')
	inputnode.inputs.thresh=thresh

	template = Info.standard_image('MNI152_T1_2mm_brain.nii.gz')
	registerF2S=pe.Node(interface=fsl.ApplyXfm(),name='RENDEREDREG')
	registerF2S.inputs.reference=template


	in_file=raw_input('Please enter the stats image')
	in_matrix_file=raw_input('Please enter the combined registration matrix')
	

	registerF2S.inputs.in_file=in_file.strip('\'"')
	registerF2S.inputs.in_matrix_file=in_matrix_file.strip('\'"')

	apply2mean = pe.Node(ApplyTransforms(args='--float',input_image_type=3,interpolation='Linear',invert_transform_flags=[False],num_threads=1,reference_image=template,terminal_output='file'),name='RENDEREDNORM')
	
	transforms=raw_input('Please enter the ANTs normalisation composite transform')

	apply2mean.inputs.transforms=transforms.strip('\'"')

	outputnode = pe.Node(interface=util.IdentityInterface(fields=['warped']),name='outputnode')

	def plot(in_file,threshold):
	from nilearn import image
	from nilearn import plotting
	import matplotlib
	display=plotting.plot_stat_map(stat_map_img=in_file,black_bg=bool(1),display_mode='z',cut_coords=10,threshold=float(thresh))
	matplotlib.pyplot.show()

	plotter=pe.MapNode(Function(input_names=['in_file','threshold'],output_names='display',function=plot),iterfield=['in_file'],name='PLOTTER')



	workflow = pe.Workflow(name='RENDERPIPE')
	workflow.base_dir = '/Users/naah1g08/Desktop/MRI'
	workflow.connect(registerF2S,'out_file',apply2mean,'input_image')
	workflow.connect(apply2mean,'output_image',outputnode,'warped')
	workflow.connect(outputnode,'warped',plotter,'in_file')
	workflow.connect(inputnode,'thresh',plotter,'threshold')


	workflow.run()