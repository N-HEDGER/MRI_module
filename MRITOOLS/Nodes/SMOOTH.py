#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Weds June 07 13:37:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Phase x of pre-processing
# Provide wrapper for afni 3D BlurinMask
# Inputs: Nifti file, nifti mask, FWHM of smoother -iterable (mm)
# Outputs:

# 1) / SMOOTHED: smoothed nifti file.


# Requires: nipype, and fsl


#--- Details

# Employs ANFIs 3DBlurinMask.
# Applying the mask speeds up the operation, so this is taken as mandatory input.

#--- 

def SMOOTHER():

	#--- 1)  Import modules
	import nipype.pipeline.engine as pe
	import os
	from glob import glob
	import nipype.interfaces.fsl.preprocess as fslp
	from nipype.interfaces import afni as afni
	import nipype.interfaces.utility as util 
	from nipype.interfaces.utility import Function

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for nifti file

	NIFTIFILE=raw_input('Please drag in the functional volume\n(ensure there is no blank space at the end)\n')
	NIFTIMASK=raw_input('Please drag in the mask\n for the functional volume\n(ensure there is no blank space at the end)\n')
	FWHM=input('Please enter the FWHM (mm) of the smoother')


	NIFTIFILE=NIFTIFILE.strip('\'"')
	NIFTIDIR=os.path.split(NIFTIFILE)[0]

	#--- 3) Move to directory

	os.chdir(NIFTIDIR)


	#--- 4) Set up input node
	inputnode = pe.Node(interface=util.IdentityInterface(fields=['fwhm']),name='inputspec')
	inputnode.inputs.fwhm=FWHM

	#--- 5) Set up smoothing node
	smoother=pe.MapNode(interface=afni.BlurInMask(),name='SMOOTHED',iterfield=['fwhm'])
	smoother.inputs.outputtype='NIFTI_GZ'
	smoother.inputs.in_file=NIFTIFILE
	smoother.inputs.mask=NIFTIMASK

	#--- 6) Function for plotting result
	def splot(in_file):
		from nilearn import image
		from nilearn import plotting
		import matplotlib
		niftifiledim=len(image.load_img(in_file).shape)
		firstim=image.index_img(in_file, 0)
		display=plotting.plot_anat(firstim,display_mode='z',cut_coords=10)	
		matplotlib.pyplot.show()
		return niftifiledim

	#--- 7) Node for plotting smoothing
	showsmooth= pe.MapNode(Function(input_names=['in_file'],output_names=['niftifiledim'],function=splot),iterfield=['in_file'],name='SHOWSMOOTH')


	#--- 8) Set up workflow
	workflow = pe.Workflow(name='SMOOTHER')
	workflow.base_dir = NIFTIDIR

	#--- 9) Connect nodes.
	workflow.connect(inputnode, 'fwhm', smoother, 'fwhm')
	workflow.connect(smoother,'out_file', showsmooth,'in_file')

	workflow.write_graph(graph2use='exec')

	#--- 10) Run workflow

	result=workflow.run()

	print "Returning to intital directory"

	os.chdir(INITDIR)