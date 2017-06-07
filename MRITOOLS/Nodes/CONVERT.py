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
# 3) / CROPPED reoriented and cropped nifti file.

# Requires: dcm2nii, nipype, nilearn, nibabel. dcm2nii and fsl


#--- Details

# dcm2nii is recruited for conversion, but fsl is recruited for cropping and reorienting
# This is because dcm2nii doesnt seem to handle reorienting and cropping for partial brain 
# functional data.
# Reoriented files are plotted.
# The cropping stage may not be useful for functional data, since I dont know how it affects slice timing.

#--- 

def CONVERTER():
	#--- 1)  Import modules
	import nipype.interfaces.dcm2nii as dcm2nii
	import nipype.pipeline.engine as pe
	import matplotlib
	import os
	from glob import glob
	from nilearn import plotting
	from nilearn import image
	from nipype.interfaces.utility import Function
	import nipype.interfaces.fsl.utils as fsl

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for directory containing DICOM FILES

	DICOMDIR=raw_input('Please drag in the directory of\nDICOM files you wish to convert\n(ensure there is no blank space at the end)')

	#--- 3) Move to directory

	os.chdir(DICOMDIR)


	#--- 4) Set up converter node for conversion to nifti

	converter=pe.Node(interface=dcm2nii.Dcm2nii(),name='CONVERTED')
	converter.inputs.source_dir=DICOMDIR
	converter.inputs.gzip_output=bool(1)


	#--- 5) Set up realigner node to match orientation of MNI 152

	realigner=pe.Node(interface=fsl.Reorient2Std(),name='REORIENTED')
	realigner.inputs.output_type='NIFTI_GZ'


	#--- 5) Set up a cropping node 

	cropper=pe.Node(interface=fsl.RobustFOV(),name='CROPPED')


	#--- 6) Set up a plotting node

	def bplot(in_file):
		from nilearn import image
		from nilearn import plotting
		niftifiledim=len(image.load_img(in_file).shape)
		if niftifiledim == 3:
			print "Structural image detected. Displaying full image. For structural data, use the data contained within '/CROPPED'"
			display=plotting.plot_anat(in_file, title="Converted structural file")
		else:
			print "Functional image detected. Displaying first volume For functional data, use the data contained within /'REORIENTED'"
			firstim=image.index_img(in_file, 0)
			display=plotting.plot_anat(firstim,title="Volume 1 of funcional data")
		return niftifiledim


	showconvert= pe.Node(Function(input_names=['in_file'],output_names=['niftifiledim'],function=bplot),name='SHOWCONVERT')


	#--- 7) Set up workflow

	workflow = pe.Workflow(name='CONVERTER')
	workflow.base_dir = DICOMDIR



	#--- 8) Connect nodes.

	workflow.connect(converter,'converted_files',realigner,'in_file')
	workflow.connect(realigner,'out_file',cropper,'in_file')
	workflow.connect(realigner,'out_file',showconvert,'in_file')

	workflow.write_graph(graph2use='exec')

	#--- 9) Run workflow

	result=workflow.run()

	#--- 10) Show plot
	matplotlib.pyplot.show()

	print "Returning to intital directory"

	os.chdir(INITDIR)












