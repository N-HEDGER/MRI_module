#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Weds June 07 14:01:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Phase x of pre-processing
# Provide wrapper for fsl MCFLIRT and plot motion parameters
# Inputs: Nifti file
# Outputs:
# 1) / MCORRECTED: motion corrected nifti file.
# 2) / PLOTTED: Plots of motion params


# Requires: nipype, and fsl


#--- Details

# Defaults to middle volume.
# Spline interpolation


#--- 

def MCORRECTOR():
	#--- 1)  Import modules
	import nipype.pipeline.engine as pe
	import os
	from glob import glob
	import nipype.interfaces.fsl as fsl

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for directory containing DICOM FILES

	NIFTIFILE=raw_input('Please drag in the nifti\n file you wish to motion correct\n(ensure there is no blank space at the end)')
	NIFTIDIR=os.path.split(NIFTIFILE)[0]
	#--- 3) Move to directory

	os.chdir(NIFTIDIR)


	#--- 4) Set up motion correction node

	motion_correct = pe.Node(interface=fsl.MCFLIRT(save_mats=True,save_plots=True,interpolation='spline'),name='realign')
	motion_correct.inputs.in_file=NIFTIFILE

	#--- 5) Set up plotting node
	plot_motion = pe.Node(interface=fsl.PlotMotionParams(in_source='fsl'),name='plot_motion')
	plot_motion.iterables = ('plot_type', ['rotations', 'translations', 'displacement'])

	
	#--- 6) Set up workflow

	workflow = pe.Workflow(name='SLICETIMER')
	workflow.base_dir = NIFTIDIR


	#--- 7) Connect nodes.

	workflow.connect(motion_correct, 'par_file', plot_motion, 'in_file')


	workflow.write_graph(graph2use='exec')

	#--- 8) Run workflow

	result=workflow.run()


	print "Returning to intital directory"

	os.chdir(INITDIR)