#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 15:10:23 2017

@author: naah1g08
"""

import nipype.interfaces.fsl as fsl 
import nipype.pipeline.engine as pe
import nipype.algorithms.modelgen as model
import glob

specify_model = pe.Node(interface=model.SpecifyModel(), name="specify_model")
specify_model.inputs.input_units = 'secs'
specify_model.inputs.functional_runs = ['/Users/naah1g08/Desktop/MRI/ST0/SE3/featpreproc/addmean/mapflow/_addmean0/20170411_101533ep2dboldmocop220003mmiso1s005a001_reoriented_st_despike_dtype_mcf_mask_smooth_mask_gms_tempfilt_maths.nii.gz']
specify_model.inputs.time_repetition = 2
specify_model.inputs.high_pass_filter_cutoff = 90.
specify_model.inputs.event_files=glob.glob('/Users/naah1g08/Desktop/MRI/ST0/SE3/Events/*')[1:3]



Designer=pe.Node(interface=fsl.Level1Design(),name='Design')
Designer.inputs.interscan_interval = float(2.0)
Designer.inputs.bases = {'dgamma':{'derivs': False}}
Designer.inputs.model_serial_correlations=bool(0)

cont1=('Upright', 'T', ['B1INVINVNEUT.RUN001', 'B1INVINVFEAR.RUN001'], [1, 1])


Designer.inputs.contrasts=[cont1]


Model=pe.Node(interface=fsl.FEATModel(),name='Model')

fgls=pe.Node(interface=fsl.FILMGLS(),name='GLS')
fgls.inputs.in_file='/Users/naah1g08/Desktop/MRI/ST0/SE3/featpreproc/addmean/mapflow/_addmean0/20170411_101533ep2dboldmocop220003mmiso1s005a001_reoriented_st_despike_dtype_mcf_mask_smooth_mask_gms_tempfilt_maths.nii.gz'
fgls.inputs.smooth_autocorr=False
fgls.inputs.mask_size=5
fgls.inputs.threshold=0


workflow = pe.Workflow(name='WORK2')

workflow.connect(specify_model,'session_info',Designer,'session_info')
workflow.connect(Designer,'fsf_files',Model,'fsf_file')
workflow.connect(Designer,'ev_files',Model,'ev_files')
workflow.connect(Model,'design_file',fgls,'design_file')
workflow.connect(Model,'con_file',fgls,'tcon_file')



workflow.base_dir = '/Users/naah1g08/Desktop/MRI'
workflow.write_graph(graph2use='exec')
workflow.run()