#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 16:33:40 2017

@author: naah1g08
"""
#--- Goal of the function:
# Perform level 1 analysis, given subject folder input.
# Structural: Converter - extracter - registration
# Functional: Converter - extracter - realigner - plotter
# Endpoint needs to be filtered func data to feed into model pipeline
#---

#--- To do:
# Func extracter
# Plotting elements
# Proper I/O
# 
#---


#--1) Import dependencies
import nipype.interfaces.fsl as fsl 
import nipype.interfaces.nipy.preprocess as nipy
import nipype.pipeline.engine as pe
import nipype.interfaces.dcm2nii as dcm2nii
import os
from glob import glob
from nilearn import plotting
from nilearn import image
from nipype.interfaces.utility import Function
import matplotlib


#--1) IO elements
os.chdir('/Users/naah1g08/Desktop/MRI/ST0')
h=glob('/Users/naah1g08/Desktop/MRI/ST0/*/')

#Converter for structural data. Structural data is located in SE1
STRUCTconverter=pe.Node(interface=dcm2nii.Dcm2nii(),name='convertS')
STRUCTconverter.iterables=('source_dir',[h[1]])

#Converter for functional data. Iterate through the func data, located in SE3, SE5 and SE7
FUNCconverter=pe.Node(interface=dcm2nii.Dcm2nii(),name='convertF')
FUNCconverter.iterables=('source_dir',[h[5]])

#Extracter for structural
extracter=pe.Node(interface=fsl.BET(),name='extract')
extracter.inputs.frac=float(0.65)
extracter.inputs.vertical_gradient=float(-0.5)

#Registration for structural
register=pe.Node(interface=fsl.FLIRT(),name='regist')
register.inputs.reference='/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'

#Spacetimerealigner for functional
Realigner=pe.Node(interface=nipy.SpaceTimeRealigner(),name='realign')
#Realigner.inputs.tr = float(2)
#Realigner.inputs.slice_times= 'asc_alt_2'

#Plot motion params
Plotter=pe.Node(interface=fsl.PlotMotionParams(),name='plot')
Plotter.inputs.in_source = 'fsl'
Plotter.inputs.plot_type = 'displacement'


Smoother=pe.Node(interface=fsl.maths.IsotropicSmooth(),name='smooth')
Smoother.inputs.fwhm= float(5)


# Custom function for plotting extraction.
def bplot(in_file, in_file2):
	from nilearn import image
	from nilearn import plotting
	niftifiledim=len(image.load_img(in_file).shape)
	print "Structural image detected. Displaying full image"
	display=plotting.plot_anat(in_file2)	
	display.add_contours(in_file,filled=True, alpha=0.5,levels=[0.5], colors='b')
	return niftifiledim



SHOWEXTRACT= pe.Node(Function(input_names=['in_file','in_file2'],output_names=['niftifiledim'],function=bplot),name='SHOWEXTRACT')




workflow = pe.Workflow(name='preproc')
workflow.add_nodes([STRUCTconverter])
#workflow.add_nodes([FUNCconverter])

workflow.connect(STRUCTconverter,'reoriented_and_cropped_files',extracter,'in_file')
workflow.connect(extracter,'out_file',register,'in_file')
workflow.connect(extracter,'out_file',SHOWEXTRACT,'in_file')
workflow.connect(STRUCTconverter,'reoriented_and_cropped_files',SHOWEXTRACT,'in_file2')

#workflow.connect(FUNCconverter,'converted_files',Realigner,'in_file')
#workflow.connect(Realigner,'par_file',Plotter,'in_file')
#workflow.connect(Realigner,'out_file',Smoother,'in_file')


workflow.base_dir = '/Users/naah1g08/Desktop/MRI/ST0PIPE'
workflow.write_graph(graph2use='exec')

result=workflow.run()

matplotlib.pyplot.show()
	
 

 












