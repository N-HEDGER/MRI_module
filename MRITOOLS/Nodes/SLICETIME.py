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
	os.system('clear')
	from glob import glob
	import nipype.interfaces.fsl.preprocess as fslp

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for directory containing DICOM FILES

	NIFTIFILE=raw_input('Please drag in the nifti\n file you wish to slicetime\n(ensure there is no blank space at the end)\n')
	os.system('clear')
	print '---\n'
	TR=float(input('Please enter the TR in seconds\n'))
	os.system('clear')
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



#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Weds June 07 13:37:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# A much better slicetimer function.
# Inputs: 1) Nifti file (iterable) 2) Slice number to correct to (iterable) 3) Acqusition order - a string (iterable) 4) TR (s)
# 1) SLICETIMED (slice time corrected .nii file)
# Plots the shifted timeseries by taking the middle voxel in each slice and plotting the first 20 data points for the corrected and uncorrected volumes


# Requires: nipype, nilearn, nibabel matplotlib, and afni


#--- Details

# Uses fourier interpolation.

#--- 1)  Import modules
def SLICETIMER2():
	import nipype.pipeline.engine as pe
	import matplotlib
	import os
	os.system('clear')
	from glob import glob
	from nilearn import plotting
	from nilearn import image
	from nipype.interfaces.utility import Function
	import nipype.interfaces.utility as util 
	import nipype.interfaces.fsl.utils as fsl
	from nipype.interfaces import afni

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for directory containing DICOM FILES

	NIFTIFILE=input('Please drag in the nifti\n file you wish to slicetime\n(ensure there is no blank space at the end)\n')

	SLICENUM=input('Please enter the slice number you want to correct to')

	print('alt+z = alternating in the plus direction\n')
	print('alt+z2  = alternating, starting at slice #1 instead of #0\n')
	print('alt-z = alternating in the minus direction\n')
	print('alt-z2   = alternating, starting at slice #nz-2 instead of #nz-1\n')
	print('seq+z = seqplus   = sequential in the plus direction\n')
	print('seq-z = seqminus  = sequential in the minus direction\n')

	AQORDER=input('Please enter the string for slice acquisition order (see above)')

	TR=input('Please enter the TR(s)')


	inputnode = pe.Node(interface=util.IdentityInterface(fields=['file','slicenum','aqorder','tr']),name='inputspec')

	if type(NIFTIFILE) == str:
		inputnode.inputs.file=NIFTIFILE
		NIFTIDIR=os.path.split(NIFTIFILE)[0]
		os.chdir(NIFTIDIR)
	elif type(NIFTIFILE) == list:
		inputnode.iterables=([('file',NIFTIFILE)])
		NIFTIDIR=os.path.split(NIFTIFILE[0])[0]
		os.chdir(NIFTIDIR)


	if type(SLICENUM) == int:
		inputnode.inputs.slicenum=SLICENUM
	elif type(SLICENUM) == list:
		inputnode.iterables=([('slicenum',SLICENUM)])

	if type(AQORDER) == str:
		inputnode.inputs.aqorder=AQORDER
	elif type(AQORDER) == list:
		inputnode.iterables=([('aqorder',AQORDER)])

	inputnode.inputs.tr=str(TR)+'s'


	slicetimer=pe.Node(interface=afni.TShift(),name='SLICETIMED')
	slicetimer.inputs.outputtype=('NIFTI_GZ')


	#--- 7) Set up workflow

	workflow = pe.Workflow(name='SLICETIMER2')
	workflow.base_dir = os.getcwd()



	def tshiftplot(pre_file, post_file):
		import matplotlib.patches as mpatches
		import matplotlib.pyplot as plt
		import matplotlib
		import numpy as np
		import nibabel as nib
		img1=nib.load(pre_file)
		data=img1.get_data()
		img2=nib.load(post_file)
		data2=img2.get_data()
		fig, ax = plt.subplots(figsize=(5, 10))
		mid=round(data.shape[0]/2)
		for i in range(data.shape[2]):
			for j in range(1):
			    ax = plt.subplot2grid((data.shape[2],1), (i,j))
			    ax.plot(data[mid,mid,i,1:20],'ro')
			    ax.plot(data[mid,mid,i,1:20],'r-')
			    ax.plot(data2[mid,mid,i,1:20],'g^')
			    ax.plot(data2[mid,mid,i,1:20],'g-')
			    print ('ploting slice' + ' ' + str(i+1))
			    ax.yaxis.set_visible(False)
		green_patch = mpatches.Patch(color='green', label='The shifted data')
		legend2=plt.legend(handles=[green_patch],loc=4)
		plt.gca().add_artist(legend2)
		red_patch = mpatches.Patch(color='red', label='The original data')
		plt.legend(handles=[red_patch],loc=3)
		plt.show()



	TSHIFTPLOT = pe.Node(Function(input_names=['pre_file','post_file'],output_names=['fig'],function=tshiftplot),name='TSHIFTPLOT')


	#--- 8) Connect nodes.

	workflow.connect(inputnode,'file',slicetimer,'in_file')
	workflow.connect(inputnode,'slicenum',slicetimer,'tslice')
	workflow.connect(inputnode,'aqorder',slicetimer,'tpattern')
	workflow.connect(inputnode,'tr',slicetimer,'tr')
	workflow.connect(inputnode,'file',TSHIFTPLOT,'pre_file')
	workflow.connect(slicetimer,'out_file',TSHIFTPLOT,'post_file')



	workflow.write_graph(graph2use='exec')

	#--- 9) Run workflow

	result=workflow.run()


	print "Node completed. Returning to intital directory\n"

	os.chdir(INITDIR)