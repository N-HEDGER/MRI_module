#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 16:33:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Phase 1 of pre-processing
# Provide wrapper for dcm2nii and output plot.
# Inputs: directory of DICOM files.
# Outputs:
# 1) / CONVERTED: nifti file.
# 2) / REORIENTED reoriented nifti file.

# Requires: dcm2nii, nipype, nilearn, nibabel. dcm2nii and fsl


#--- Details

# dcm2nii is recruited for conversion, but fsl is recruited for reorienting
# This is because dcm2nii doesnt seem to handle reorienting for partial brain 
# functional data.
# Reoriented files are plotted.


#--- 

def CONVERTER():
	
	#--- 1)  Import modules
	import nipype.interfaces.dcm2nii as dcm2nii
	import nipype.pipeline.engine as pe
	import matplotlib
	import os
	os.system('clear')
	from glob import glob
	from nilearn import plotting
	from nilearn import image
	from nipype.interfaces.utility import Function
	import nipype.interfaces.fsl.utils as fsl

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for directory containing DICOM FILES

	DICOMDIR=raw_input('Please drag in the directory of\nDICOM files you wish to convert\n(ensure there is no blank space at the end)\n')
	os.system('clear')
	print '---\n'
	# Get rid of extra strings (Linux terminal)
	DICOMDIR=DICOMDIR.strip('\'"')
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
		import matplotlib
		niftifiledim=len(image.load_img(in_file).shape)
		if niftifiledim == 3:
			display=plotting.plot_anat(in_file)
			matplotlib.pyplot.show()
		else:
			firstim=image.index_img(in_file, 0)
			display=plotting.plot_anat(firstim)
			matplotlib.pyplot.show()
		return niftifiledim


	showconvert= pe.Node(Function(input_names=['in_file'],output_names=['niftifiledim'],function=bplot),name='SHOWCONVERT')


	#--- 7) Set up workflow

	workflow = pe.Workflow(name='CONVERTER')
	workflow.base_dir = DICOMDIR



	#--- 8) Connect nodes.

	workflow.connect(converter,'converted_files',realigner,'in_file')
	workflow.connect(realigner,'out_file',showconvert,'in_file')

	workflow.write_graph(graph2use='exec')

	#--- 9) Run workflow

	result=workflow.run()

	#--- 10) Show plot
	

	print "Node completed. Returning to intital directory\n"

	os.chdir(INITDIR)



def CONVERTER2(): #--- 1)  Import modules
	import nipype.interfaces.dcm2nii as dcm2nii
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

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for directory containing DICOM FILES

	DICOMDIR=input('Please drag in the directory of\nDICOM files you wish to convert\n(ensure there is no blank space at the end)\n')


	inputnode = pe.Node(interface=util.IdentityInterface(fields=['file']),name='inputspec')

	if type(DICOMDIR) == str:
		inputnode.inputs.file=DICOMDIR
		os.chdir(DICOMDIR)
	elif type(DICOMDIR) == list:
		inputnode.iterables=([('file',DICOMDIR)])
		os.chdir(DICOMDIR[0])
		os.chdir("..")

	#--- 3) Move to directory



	#--- 4) Set up converter node for conversion to nifti

	converter=pe.Node(interface=dcm2nii.Dcm2nii(),name='CONVERTED')
	converter.inputs.gzip_output=bool(1)


	#--- 5) Set up realigner node to match orientation of MNI 152

	realigner=pe.Node(interface=fsl.Reorient2Std(),name='REORIENTED')
	realigner.inputs.output_type='NIFTI_GZ'


	#--- 6) Set up a plotting node

	def bplot(in_file):
		from nilearn import image
		from nilearn import plotting
		import matplotlib
		niftifiledim=len(image.load_img(in_file).shape)
		if niftifiledim == 3:
			display=plotting.plot_anat(in_file)
			matplotlib.pyplot.show()
		else:
			firstim=image.index_img(in_file, 0)
			display=plotting.plot_anat(firstim)
			matplotlib.pyplot.show()
		return niftifiledim


	showconvert= pe.Node(Function(input_names=['in_file'],output_names=['niftifiledim'],function=bplot),name='SHOWCONVERT')


	#--- 7) Set up workflow

	workflow = pe.Workflow(name='CONVERTER')
	workflow.base_dir = os.getcwd()



	#--- 8) Connect nodes.

	workflow.connect(inputnode,'file',converter,'source_dir')
	workflow.connect(converter,'converted_files',realigner,'in_file')
	workflow.connect(realigner,'out_file',showconvert,'in_file')

	workflow.write_graph(graph2use='exec')

	#--- 9) Run workflow

	result=workflow.run()

	#--- 10) Show plot


	print "Node completed. Returning to intital directory\n"

	os.chdir(INITDIR)









