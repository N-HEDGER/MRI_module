#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 14:20:58 2017

@author: naah1g08
"""

import nipype.interfaces.fsl as fsl 
import nipype.interfaces.nipy as nipy
import nipype.pipeline.engine as pe
import nipype.interfaces.dcm2nii as dcm2nii
import os
os.chdir('/Users/naah1g08/Desktop/MRI/')
converter=pe.Node(interface=dcm2nii.Dcm2nii(),name='convert')
converter.iterables=('source_dir',['/Users/naah1g08/Desktop/MRI/PA1/SE1/','/Users/naah1g08/Desktop/MRI/PA2/SE1/'])

extracter=pe.Node(interface=fsl.BET(),name='extract')

extracter.inputs.frac=float(0.7)
extracter.iterables=('vertical_gradient',[float(-0.5), float(-0.4)])

register=pe.Node(interface=fsl.FLIRT(),name='regist')

register.inputs.reference='/usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'

workflow = pe.Workflow(name='preproc')
workflow.base_dir = '.'


workflow.connect(converter,'reoriented_and_cropped_files',extracter,'in_file')
workflow.connect(extracter,'out_file',register,'in_file')
workflow.write_graph(graph2use='exec')


workflow.run()
