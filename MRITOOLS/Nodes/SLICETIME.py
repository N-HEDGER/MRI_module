#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Weds June 07 13:37:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Phase x of pre-processing
# Provide wrapper for fsl slicetimer
# Inputs: Nifti file TR (secs)
# Outputs:
# 1) / SLICETIMED: slice time corrected nifti file.


# Requires: nipype, and fsl


#--- Details

# Interleaved aquisition is assumed by default
# Shifted to the timing of a middle slice


#--- 

def SLICETIMER():
	#--- 1)  Import modules
	import nipype.pipeline.engine as pe
	import os
	from glob import glob
	import nipype.interfaces.fsl.preprocess as fslp

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for directory containing DICOM FILES

	NIFTIFILE=raw_input('Please drag in the nifti\n file you wish to slicetime\n(ensure there is no blank space at the end)\n')
	print '---\n'
	TR=float(input('Please enter the TR in seconds\n'))
	print '---\n'
	NIFTIFILE=NIFTIFILE.strip('\'"')
	NIFTIDIR=os.path.split(NIFTIFILE)[0]

	#--- 3) Move to directory

	os.chdir(NIFTIDIR)


	#--- 4) Set up slice timing node


	slicetimer=pe.Node(interface=fslp.SliceTimer(),name='SLICETIMED')
	slicetimer.inputs.interleaved = True
	slicetimer.inputs.time_repetition = float(TR)
	slicetimer.inputs.in_file=NIFTIFILE


	#--- 7) Set up workflow

	workflow = pe.Workflow(name='SLICETIMER')
	workflow.base_dir = NIFTIDIR


	#--- 8) Connect nodes.

	workflow.add_nodes([slicetimer])


	workflow.write_graph(graph2use='exec')

	#--- 9) Run workflow

	result=workflow.run()


	print "Node completed. Returning to intital directory\n"

	os.chdir(INITDIR)