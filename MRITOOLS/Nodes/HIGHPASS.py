#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Weds June 07 13:37:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Phase x of pre-processing
# Provide highpass temporal filter using FSL
# Inputs: Nifti file, High pass filter cutoff (s) - iterable, TR
# Outputs:

# 1) / HIGHPASSED: highpassed nifti file.

# Requires: nipype, and fsl

#--- Details

# Employs FSLs bptf.
# The input is seconds and is converted to HWHM
#--- 


tolist = lambda x: [x]
highpass_operand = lambda x:'-bptf %.10f -1'%x

def HPFILTER():

	#--- 1)  Import modules
	import nipype.pipeline.engine as pe
	import os
	from glob import glob
	import nipype.interfaces.fsl as fsl  
	from nipype.interfaces import afni as afni
	import nipype.interfaces.utility as util 
	from nipype.interfaces.utility import Function
	import numpy

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for nifti file

	NIFTIFILE=raw_input('Please drag in the functional volume\n(ensure there is no blank space at the end)\n')
	CUTOFF=input('Please enter the High pass filter cutoff (s)\n')
	TR=input('Please enter the TR(s)\n')

	NIFTIFILE=NIFTIFILE.strip('\'"')
	NIFTIDIR=os.path.split(NIFTIFILE)[0]

	#--- 3) Move to directory

	os.chdir(NIFTIDIR)


	#--- 4) Set up input node
	inputnode = pe.Node(interface=util.IdentityInterface(fields=['cutoff','TR']),name='inputspec')
	inputnode.inputs.TR=float(TR)



	if type(CUTOFF) == float:
		inputnode.inputs.cutoff=float((CUTOFF/(inputnode.inputs.TR*2.5)))
	elif type(CUTOFF) == int:
	inputnode.inputs.cutoff=float((CUTOFF/(inputnode.inputs.TR*2.5)))
	elif type(CUTOFF) == list:
		inputnode.inputs.cutoff=list(numpy.asarray(CUTOFF)/(inputnode.inputs.TR*2.5))
		inputnode.iterables=([('cutoff',CUTOFF)])
		


	#--- 5) Set up filtering node
	highpass = pe.Node(interface=fsl.ImageMaths(suffix='_tempfilt'),name='FILTERED')
	highpass.inputs.in_file = NIFTIFILE

	#--- 6) Get Mean functional volume
	# FSL de-means the data, so the mean functional data needs to be added back on
	meanfunc = pe.Node(interface=fsl.ImageMaths(op_string='-Tmean',suffix='_mean'),name='MEANVOL')
	meanfunc.inputs.in_file=NIFTIFILE


	#--- 7) Get Mean functional volume
	# Use FSL maths to add the mean back onto the highpassed data
	addmean = pe.Node(interface=fsl.BinaryMaths(operation='add'),name='HIGHPASSED')


	#--- 8) Set up workflow
	workflow = pe.Workflow(name='HPFILTER')
	workflow.base_dir = NIFTIDIR

	#--- 9) Connect nodes.
	workflow.connect(inputnode, ('cutoff', highpass_operand), highpass, 'op_string')
	workflow.connect(highpass, 'out_file', addmean, 'in_file')
	workflow.connect(meanfunc, 'out_file', addmean, 'operand_file')

	workflow.write_graph(graph2use='exec')

	#--- 10) Run workflow

	result=workflow.run()

	print "Returning to intital directory"

	os.chdir(INITDIR)