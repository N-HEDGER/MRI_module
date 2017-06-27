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
from nipype import Function
import matplotlib
import nipype.interfaces.utility as util

specify_model = pe.Node(interface=model.SpecifyModel(), name="specify_model")
specify_model.inputs.input_units = 'secs'
specify_model.inputs.functional_runs = ['/Users/naah1g08/Desktop/MRI/ST0/SE3/FUNCPIPE/PREPROCESSED/mapflow/_PREPROCESSED0/20170411_101533ep2dboldmocop220003mmiso1s005a001_reoriented_st_dtype_mcf_despike_brain_blur_tempfilt_maths.nii.gz']
specify_model.inputs.time_repetition = 2
specify_model.inputs.high_pass_filter_cutoff = 90.
specify_model.inputs.event_files=glob.glob('/Users/naah1g08/Desktop/MRI/ST0/SE3/Events/*')



Designer=pe.Node(interface=fsl.Level1Design(),name='Design')
Designer.inputs.interscan_interval = float(2.0)
Designer.inputs.bases = {'dgamma':{'derivs': True}}
Designer.inputs.model_serial_correlations=bool(0)

cont1=('Upright', 'T', ['B1INVFEAR.RUN001', 'B1INVINVFEAR.RUN001', 'B1INVINVNEUT.RUN001', 'B1INVNEUT.RUN001', 'B1SCFEAR.RUN001', 'B1SCNEUT.RUN001', 'B1UPFEAR.RUN001', 'B1UPINVFEAR.RUN001', 'B1UPINVNEUT.RUN001', 'B1UPNEUT.RUN001'], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

cont2=('Up', 'T', ['B1INVFEAR.RUN001', 'B1INVINVFEAR.RUN001', 'B1INVINVNEUT.RUN001', 'B1INVNEUT.RUN001', 'B1SCFEAR.RUN001', 'B1SCNEUT.RUN001', 'B1UPFEAR.RUN001', 'B1UPINVFEAR.RUN001', 'B1UPINVNEUT.RUN001', 'B1UPNEUT.RUN001'], [0, 0, 0, 0, 0, 0, 1, 0, 0, 1])
cont3=('SC', 'T', ['B1INVFEAR.RUN001', 'B1INVINVFEAR.RUN001', 'B1INVINVNEUT.RUN001', 'B1INVNEUT.RUN001', 'B1SCFEAR.RUN001', 'B1SCNEUT.RUN001', 'B1UPFEAR.RUN001', 'B1UPINVFEAR.RUN001', 'B1UPINVNEUT.RUN001', 'B1UPNEUT.RUN001'], [0, 0, 0, 0, 1, 1, 0, 0, 0, 0])
cont4=('UpvSC', 'T', ['B1INVFEAR.RUN001', 'B1INVINVFEAR.RUN001', 'B1INVINVNEUT.RUN001', 'B1INVNEUT.RUN001', 'B1SCFEAR.RUN001', 'B1SCNEUT.RUN001', 'B1UPFEAR.RUN001', 'B1UPINVFEAR.RUN001', 'B1UPINVNEUT.RUN001', 'B1UPNEUT.RUN001'], [0, 0, 0, 0, -1, -1, 1, 0, 0, 1])


Designer.inputs.contrasts=[cont1, cont2, cont3, cont4]


Model=pe.Node(interface=fsl.FEATModel(),name='Model')

fgls=pe.Node(interface=fsl.FILMGLS(),name='GLS')
fgls.inputs.in_file='/Users/naah1g08/Desktop/MRI/ST0/SE3/FUNCPIPE/PREPROCESSED/mapflow/_PREPROCESSED0/20170411_101533ep2dboldmocop220003mmiso1s005a001_reoriented_st_dtype_mcf_despike_brain_blur_tempfilt_maths.nii.gz'
#fgls.inputs.mask_size=0
#fgls.inputs.threshold=0


outputnode = pe.Node(interface=util.IdentityInterface(fields=['im']),name='outputnode')


workflow = pe.Workflow(name='WORK4')

workflow.connect(specify_model,'session_info',Designer,'session_info')
workflow.connect(Designer,'fsf_files',Model,'fsf_file')
workflow.connect(Designer,'ev_files',Model,'ev_files')
workflow.connect(Model,'design_file',fgls,'design_file')
workflow.connect(Model,'con_file',fgls,'tcon_file')
workflow.connect(Model,'design_image',outputnode,'im')


def plot(in_file):
	from nilearn import image
	from nilearn import plotting
	display=plotting.plot_stat_map(stat_map_img=in_file,black_bg=bool(1),display_mode='z',cut_coords=20,threshold=float(2.3))





plotter=pe.MapNode(Function(input_names=['in_file'],output_names='display',function=plot),iterfield=['in_file'],name='PLOTTER')

workflow.connect(fgls,'zstats',plotter,'in_file')


workflow.base_dir = '/Users/naah1g08/Desktop/MRI'
workflow.write_graph(graph2use='exec')
workflow.run()

matplotlib.pyplot.show()