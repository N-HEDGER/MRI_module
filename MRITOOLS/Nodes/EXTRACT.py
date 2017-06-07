#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 16:33:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Phase 2 of pre-processing
# Provide wrapper for FSL BET and remove non brain tissue.
# Inputs: nifti file, frac, gradient. Frac and gradient can be entered as a comma seperated vector e.g. [0.2,0.3]
# Outputs: extracted nifti file, plot of extracted brain overlayed over original image.
# Requires: fsl nipype, nilearn
#---

def EXTRACTER():
	#--- 1)  Import modules
	import nipype.interfaces.dcm2nii as dcm2nii
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

	#--- 3) Prompt user for directory containing NIFTI FILES

	NIFTIFILE=raw_input('Please drag in the \nnifti file you wish to extract\n(ensure there is no blank space at the end)')
	NIFTIDIR=os.path.split(NIFTIFILE)[0]
	frac=input('Please input the fractional ansiotropy threshold \n in the range [0-1]')
	grad=input('Please input the gradient \n in the range [-1 1]')

	#--- 3) Move to directory

	os.chdir(NIFTIDIR)


	#--- 4) Realign for good practice. Seems like BET should assume a default orientation.

	realigner=pe.Node(interface=fslu.Reorient2Std(),name='REORIENTED')
	realigner.inputs.in_file=NIFTIFILE


	#--- 5) Set up extracter node


	#The input parameters depend on the dimensions of the file, so check these using nilearn.
	niftifiledim=len(image.load_img(NIFTIFILE).shape)

	extracter=pe.Node(interface=fsl.BET(),name='EXTRACTED')
	extracter.inputs.mask=bool(1)

	# Input can either be a list or float. Lists are iterables, floats are inputs.
	if type(grad) == float and type(frac) == float:
		extracter.inputs.frac=float(frac)
		extracter.inputs.vertical_gradient=float(grad)
	elif type(grad) == list and type(frac) == list:
		extracter.iterables=([('frac',frac),('vertical_gradient',grad)])
	elif type(grad) == float and type(frac) == list:
		extracter.iterables=([('frac',frac)])
		extracter.inputs.vertical_gradient=float(grad)
	elif type(grad) == list and type(frac) == float:
		extracter.iterables=([('vertical_gradient',grad)])
		extracter.inputs.frac=float(frac)


	if niftifiledim == 3:
		extracter.inputs.functional=bool(0)
	else:
		extracter.inputs.functional=bool(1)


	#--- 6) Set up a plotting node


	# Overlay extraction on original file.
	def bplot(in_file,in_file2,in_file3):
		from nilearn import image
		from nilearn import plotting
		niftifiledim=len(image.load_img(in_file).shape)
		if niftifiledim == 3:
			print "Structural image detected. Displaying full image"
			display=plotting.plot_anat(in_file2, title = "Extraction overlayed on original")		
			display.add_contours(in_file,filled=True, alpha=0.5,levels=[0.2], colors='b')
			display.add_edges(in_file3)
		else:
			print "Functional image detected. Displaying first volume"
			firstim=image.index_img(in_file, 0)
			firstim2=image.index_img(in_file2, 0)
			display=plotting.plot_anat(firstim2, title = "Extraction overlayed on original")	
			display.add_contours(firstim,filled=True, alpha=0.5,levels=[0.2], colors='b')
			display.add_edges(in_file3)
		return niftifiledim



	showextract= pe.Node(Function(input_names=['in_file','in_file2','in_file3'],output_names=['niftifiledim'],function=bplot),name='SHOWEXTRACT')

	#--- 7) Set up workflow
	workflow = pe.Workflow(name='EXTRACTER')
	workflow.base_dir = NIFTIDIR

	#--- 8) Connect nodes.
	workflow.connect(realigner,'out_file',extracter,'in_file')
	workflow.connect(realigner,'out_file',showextract,'in_file2')
	workflow.connect(extracter,'out_file',showextract,'in_file')
	workflow.connect(extracter,'mask_file',showextract,'in_file3')

	workflow.write_graph(graph2use='exec')

	#--- 9) Run workflow
	result=workflow.run()

	#--- 10) Show plot
	matplotlib.pyplot.show()

	print "Returning to intital directory"
	os.chdir(INITDIR)


#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 16:33:40 2017
@author: naah1g08
"""
#--- Goal of the function:
# Phase 2 of pre-processing
# Provide wrapper for FSL BET and remove non brain tissue.
# Inputs: nifti file.
# Outputs: extracted nifti file, plot of extracted brain overlayed over original image.
# Requires: fsl nipype, nilearn
#---

#--- Details

# This is just a verbose version of EXTRACTER
# Instead of prompting the user for the frac and grad inputs, it just performs 36 extractions by creating linearly spaced vectors
# (min to max) for each of the input variables.
# This is probably extremely memory intensive, but may be required to refine results.

#--- 

def VERBOSE_EXTRACTER():
	#--- 1)  Import modules
	import nipype.interfaces.dcm2nii as dcm2nii
	import nipype.pipeline.engine as pe
	import matplotlib
	import os
	from glob import glob
	from nilearn import plotting
	from nilearn import image
	from nipype.interfaces.utility import Function
	import nipype.interfaces.fsl.preprocess as fsl
	import nipype.interfaces.fsl.utils as fslu
	import numpy

	#--- 2)  Record intial working directory

	INITDIR=os.getcwd();

	#--- 3) Prompt user for directory containing NIFTI FILES

	NIFTIFILE=raw_input('Please drag in the \nnifti file you wish to extract\n(ensure there is no blank space at the end)')
	NIFTIDIR=os.path.split(NIFTIFILE)[0]
	frac=list(numpy.linspace(start=0,stop=1,num=6))
	grad=list(numpy.linspace(start=-1,stop=1,num=6))

	#--- 3) Move to directory

	os.chdir(NIFTIDIR)


	#--- 4) Realign for good practice. Seems like BET should assume a default orientation.

	realigner=pe.Node(interface=fslu.Reorient2Std(),name='REORIENTED')
	realigner.inputs.in_file=NIFTIFILE


	#--- 5) Set up extracter node


	#The input parameters depend on the dimensions of the file, so check these using nilearn.
	niftifiledim=len(image.load_img(NIFTIFILE).shape)

	extracter=pe.Node(interface=fsl.BET(),name='EXTRACTED')

	# Input can either be a list or float. Lists are iterables, floats are inputs.
	if type(grad) == float and type(frac) == float:
		extracter.inputs.frac=float(frac)
		extracter.inputs.vertical_gradient=float(grad)
	elif type(grad) == list and type(frac) == list:
		extracter.iterables=([('frac',frac),('vertical_gradient',grad)])
	elif type(grad) == float and type(frac) == list:
		extracter.iterables=([('frac',frac)])
		extracter.inputs.vertical_gradient=float(grad)
	elif type(grad) == list and type(frac) == float:
		extracter.iterables=([('vertical_gradient',grad)])
		extracter.inputs.frac=float(frac)


	if niftifiledim == 3:
		extracter.inputs.functional=bool(0)
	else:
		extracter.inputs.functional=bool(1)


	#--- 6) Set up a plotting node


	# Overlay extraction on original file.
	def bplot(in_file,in_file2):
		from nilearn import image
		from nilearn import plotting
		niftifiledim=len(image.load_img(in_file).shape)
		if niftifiledim == 3:
			print "Structural image detected. Displaying full image"
			display=plotting.plot_anat(in_file2, title = "Extraction overlayed on original")		
			display.add_contours(in_file,filled=True, alpha=0.5,levels=[0.2], colors='b')
		else:
			print "Functional image detected. Displaying first volume"
			firstim=image.index_img(in_file, 0)
			firstim2=image.index_img(in_file2, 0)
			display=plotting.plot_anat(firstim2, title = "Extraction overlayed on original")	
			display.add_contours(firstim,filled=True, alpha=0.5,levels=[0.2], colors='b')
		return niftifiledim



	showextract= pe.Node(Function(input_names=['in_file','in_file2'],output_names=['niftifiledim'],function=bplot),name='SHOWEXTRACT')

	#--- 7) Set up workflow
	workflow = pe.Workflow(name='EXTRACTER')
	workflow.base_dir = NIFTIDIR

	#--- 8) Connect nodes.
	workflow.connect(realigner,'out_file',extracter,'in_file')
	workflow.connect(realigner,'out_file',showextract,'in_file2')
	workflow.connect(extracter,'out_file',showextract,'in_file')

	workflow.write_graph(graph2use='exec')

	#--- 9) Run workflow
	result=workflow.run()

	#--- 10) Show plot
	matplotlib.pyplot.show()

	print "Returning to intital directory"
	os.chdir(INITDIR)




