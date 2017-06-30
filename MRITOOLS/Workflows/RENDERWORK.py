#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 9 12:00:00 2017
@author: naah1g08
"""
#--- Goal of the function:
# Use FSL and ANTS transforms to render stats image in MNI space.

# Inputs:
# Stats image. Z/t score image in subject space (output of L1PIPE)
# Combined linear transform (used to register functional data to MNI).
# ANTS normalisation composite transform (used to normalise the functional volume to the MNI - output of ).
# Thresh. Threshold for plotting the data. e.g. 2.3 will show voxels with a z score greater than 2.3.

# Outputs:
# 1) / RENDERREG - Regsitered stats image.
# 2) / RENDERNORM - Normalised stats image.


# Requires: nipype, nilearn, matplotlib, fsl


#--- Details

# Nilearn should plot the data to the MNI by default. 

#--- 

def RENDERPIPE():
	#--- 1)  Import modules
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


	#--- 2)  Determine template location and get inputs
	template = Info.standard_image('MNI152_T1_2mm_brain.nii.gz \n')
	in_file=raw_input('Please drag in the stats image')
	in_matrix_file=raw_input('Please drag in the combined registration matrix \n')
	thresh=float(raw_input('Please enter the threshold \n'))
	transforms=raw_input('Please drag in the ANTs normalisation composite transform \n')

	#--- 3)  Make input node
	inputnode = pe.Node(interface=util.IdentityInterface(fields=['thresh']),name='inputnode')
	inputnode.inputs.thresh=thresh

	#--- 4)  Node for registering to MNI
	registerF2S=pe.Node(interface=fsl.ApplyXfm(),name='RENDEREDREG')
	registerF2S.inputs.reference=template
	registerF2S.inputs.in_file=in_file.strip('\'"')
	registerF2S.inputs.in_matrix_file=in_matrix_file.strip('\'"')

	NIFTIDIR=os.path.split(registerF2S.inputs.in_file)[0]


	#--- 5)  Node for ANTs warping to MNI
	apply2mean = pe.Node(ApplyTransforms(args='--float',input_image_type=3,interpolation='Linear',invert_transform_flags=[False],num_threads=1,reference_image=template,terminal_output='file'),name='RENDEREDNORM')
	apply2mean.inputs.transforms=transforms.strip('\'"')

	#--- 6)  Outputnode for warped volume
	outputnode = pe.Node(interface=util.IdentityInterface(fields=['warped']),name='outputnode')


	#--- 7)  Function for plotting over MNI
	def plot(in_file, threshold):
		from nilearn import image
		from nilearn import plotting
		import matplotlib
		display=plotting.plot_stat_map(stat_map_img=in_file,black_bg=bool(1),display_mode='z',cut_coords=10,threshold=float(threshold))
		matplotlib.pyplot.show()
		return display

	plotter=pe.MapNode(Function(input_names=['in_file','threshold'],output_names='display',function=plot),iterfield=['in_file'],name='PLOTTER')


	#--- 8)  Define workflow
	workflow = pe.Workflow(name='RENDERPIPE')
	workflow.base_dir = NIFTIDIR
	

	#--- 9)  Connect nodes
	workflow.connect(registerF2S,'out_file',apply2mean,'input_image')
	workflow.connect(apply2mean,'output_image',outputnode,'warped')
	workflow.connect(outputnode,'warped',plotter,'in_file')
	workflow.connect(inputnode,'thresh',plotter,'threshold')
	
	#--- 10)  Run workflow
	workflow.write_graph(graph2use='exec')
	workflow.run()