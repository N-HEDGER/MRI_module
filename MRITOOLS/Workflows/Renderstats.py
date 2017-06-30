

from nipype.interfaces.ants import Registration, ApplyTransforms
import nipype.pipeline.engine as pe
import matplotlib
import os
from glob import glob
from nilearn import plotting
from nilearn import image
from nipype.interfaces.utility import Function
import nipype.interfaces.fsl.preprocess as fsl
import nipype.interfaces.fsl as fslbase
import nipype.interfaces.fsl.utils as fslu
from nipype.interfaces.fsl import Info
import nipype.interfaces.utility as util





template = Info.standard_image('MNI152_T1_2mm_brain.nii.gz')
registerF2S=pe.Node(interface=fsl.ApplyXfm(),name='REGISTEREDF2MNI')
registerF2S.inputs.reference=template
registerF2S.inputs.in_file=raw_input('EPI')
registerF2S.inputs.in_matrix_file=raw_input('flirt')

apply2mean = pe.Node(ApplyTransforms(args='--float',input_image_type=3,interpolation='Linear',invert_transform_flags=[False],num_threads=1,reference_image=template,terminal_output='file'),name='NORMFUNC')
apply2mean.inputs.transforms=raw_input('ants')

outputnode = pe.Node(interface=util.IdentityInterface(fields=['warped']),name='outputnode')



workflow = pe.Workflow(name='RENDERPIPE')
workflow.base_dir = '/Users/naah1g08/Desktop/MRI'
workflow.connect(registerF2S,'out_file',apply2mean,'input_image')
workflow.connect(apply2mean,'output_image',outputnode,'warped')

workflow.run()