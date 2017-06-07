#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 16:33:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Undefined stage of pre-processing.
# Provide wrapper for FSL FLIRT and FNIRT and register brain to MNI 152 space.
# Inputs: brain extracted nifti file, degrees of freedom.
# Outputs:
# 1) / REGISTERED (nifti file that has been linearly registered to MNI 152 space using FLIRT)
# 2) / REGISTERED_WARPED (optional) (nifti file that has been initially registered by FLIRT, before non-linear warpng is applied)
# Requires: fsl, nipype, nilearn

#--- Details

# Note that brain extraction needs to be very good for the non-linear warping to work. This is designed as a standalone function
# (i.e. there is no input from BET, so better results will be obtained if you supply the extracted and non-extracted volumes via the GUI.
# FLIRTED AND FNIRTED files are plotted over the MNI 152 template.
# Obsviously, the location of the MNI 152 brain template may vary, so I have only assumed default location here.

#--- 

def REGISTER():
	#--- 1)  Import modules
	import nipype.pipeline.engine as pe
	import matplotlib
	import os
	from glob import glob
	from nilearn import plotting
	from nilearn import image
	from nipype.interfaces.utility import Function
	import nipype.interfaces.fsl.preprocess as fsl
	import nipype.interfaces.fsl.utils as fslu


	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for nifti file

	NIFTIFILE=raw_input('Please drag in the \nnifti file you wish to convert\n(ensure there is no blank space at the end)')
	NIFTIDIR=os.path.split(NIFTIFILE)[0]
	os.chdir(NIFTIDIR)

	niftifiledim=len(image.load_img(NIFTIFILE).shape)

	if niftifiledim == 4:
		raise ValueError('Functional data detected, only use this function for structural volumes')
		print "Returning to intital directory"
		os.chdir(INITDIR)
	else:
		print "Structural image detected"

	#--- 4) Prompt user for dof and warping options

	dof=input('Please input the degrees of freedom \n (6,7,9 or 12)')
	nonlinear=input('Also apply non-linear warping? [0=no,1=yes]')




	#--- 5) Set up registration node

	register=pe.Node(interface=fsl.FLIRT(),name='REGISTERED')
	register.inputs.in_file=NIFTIFILE
	register.inputs.reference='/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'

	if type(dof) == int:
		register.inputs.dof=int(dof)
	elif type(dof) == list:
		register.iterables=([('dof',dof)])



	#--- 6) Custom plotting function for linear registration.

	def bplot(in_file):
		from nilearn import image
		from nilearn import plotting
		niftifiledim=len(image.load_img(in_file).shape)
		print "Structural image detected. Displaying full image"
		display=plotting.plot_anat('/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz', title = "Registered (Linear) volume overlayed on MNI")		
		display.add_edges(in_file)
		return niftifiledim


	#--- 7) Custom plotting function for non-linear warping

	def bplotN(in_file):
		from nilearn import image
		from nilearn import plotting
		niftifiledim=len(image.load_img(in_file).shape)
		print "Structural image detected. Displaying full image"
		display=plotting.plot_anat('/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz', title = "Registered (Non-linear) volume overlayed on MNI")		
		display.add_edges(in_file)
		return niftifiledim

	showextract= pe.Node(Function(input_names=['in_file'],output_names=['niftifiledim'],function=bplot),name='SHOWEXTRACT')
	showextractNL= pe.Node(Function(input_names=['in_file'],output_names=['niftifiledim'],function=bplotN),name='SHOWEXTRACTNL')



	#--- 8) Set up warping node

	register2=pe.Node(interface=fsl.FNIRT(),name='REGISTERED_WARPED')
	register2.inputs.ref_file=register.inputs.reference
	register2.inputs.in_file=NIFTIFILE


	#--- 9) Set up workflow

	workflow = pe.Workflow(name='REGISTER')
	workflow.base_dir = NIFTIDIR

	#--- 10) Connect nodes.

	if nonlinear:
		workflow.connect(register,'out_file',showextract,'in_file')
		workflow.connect(register,'out_matrix_file',register2,'affine_file')
		workflow.connect(register2,'warped_file',showextractNL,'in_file')
	else:
		workflow.connect(register,'out_file',showextract,'in_file')

	#--- 11) Run workflow
	workflow.write_graph(graph2use='exec')
	result=workflow.run()

	#--- 12) Show plot
	matplotlib.pyplot.show()

	os.chdir(INITDIR)

