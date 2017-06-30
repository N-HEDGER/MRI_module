#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 9 12:00:00 2017
@author: naah1g08
"""
#--- Goal of the function:
# Use FSL and ANTS to perform registration and normalisation

# Inputs:
# alsonorm (Boolean). Controls whether just registration is performed, or whether normalisation is also performed.
# Brain extracted structural image
# Non-brain extracted structural image
# Brain extracted mean functional volume (produced by FUNCPIPE)

# Outputs:
# 1) / REGISTEREDT12MNI - Structural image registered to the MNI brain (FSL).
# 2) / REGISTEREDF2MNI - Functional image registered to the MNI brain (FSL).
# 3) / CONCATMATRICES - Combined transformation matrix for registering the functional to the MNI (FSL).
# 4) / EPIREG - The initial transform for registering the functional to the Structural (FSL)
# 5) / NORMSTRUCT - Normalised/ warped structural image (ANTs)
# 6) / NORMFUNC - Normalised/ warped structural image (ANTs)


# Requires: dcm2nii, nipype, nilearn, nibabel, dcm2nii, fsl, afni


#--- Details

# This will take a while to run.....
# The point of concat matrices is to perform registration of the functional to the MNI in one transformation, to avoid 
# multiple interpolation.
# This should be pretty robust to partial FOV EPI images because BBR is used.  

#--- 

def NORMPIPE():
  #--- 1)  Import modules
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

 

  INITDIR=os.getcwd();

  
  #--- 2)  Define input node
  template = Info.standard_image('MNI152_T1_2mm_brain.nii.gz')
  inputnode = pe.Node(interface=util.IdentityInterface(fields=['standard']),name='inputspec')
  inputnode.inputs.standard=template



  #--- 3)  Get inputs and define node for registering EPI to structural.
  alsonorm=bool(input('Also normalise?\n'))
  epireg=pe.Node(interface=fslbase.EpiReg(),name='EPIREG')

  t1_brain=raw_input('Please drag in the brain-extracted structural volume\n')
  t1_head=raw_input('Please drag in the non-brain extracted structural volume\n')
  epi=raw_input('Please drag in the mean functional volume.\n')

  

  epireg.inputs.t1_brain=t1_brain.strip('\'"')
  epireg.inputs.t1_head=t1_head.strip('\'"')
  epireg.inputs.epi=epi.strip('\'"')
  NIFTIDIR=os.path.split(epireg.inputs.t1_brain)[0]

  #--- 4)  Register the T1 to the MNI
  registerT12S=pe.Node(interface=fsl.FLIRT(),name='REGISTEREDT12MNI')
  registerT12S.inputs.dof=int(12)
  registerT12S.inputs.reference=template
  registerT12S.inputs.in_file=epireg.inputs.t1_brain


  #--- 5)  Concatenate the two transformation matrices from 3 and 4.
  concatxfm=pe.Node(interface=fslbase.ConvertXFM(),name='CONCATMATRICES')
  concatxfm.inputs.concat_xfm=bool(1)


  #--- 6)  Register the EPI to the standard, using the combined transformation matrix
  registerF2S=pe.Node(interface=fsl.ApplyXFM(),name='REGISTEREDF2MNI')
  registerF2S.inputs.reference=template
  registerF2S.inputs.in_file=epireg.inputs.epi


  #--- 7)  Use ANTS to normalise the structural to the MNI
  antsregfast = pe.Node(Registration(args='--float',collapse_output_transforms=True,
                                  fixed_image=template,
                                  initial_moving_transform_com=True,
                                  output_inverse_warped_image=True,
                                  output_warped_image=True,
                                  sigma_units=['vox']*3,
                                  transforms=['Rigid', 'Affine', 'SyN'],
                                  terminal_output='file',
                                  winsorize_lower_quantile=0.005,
                                  winsorize_upper_quantile=0.995,
                                  convergence_threshold=[1e-08, 1e-08, -0.01],
                                  convergence_window_size=[20, 20, 5],
                                  metric=['Mattes', 'Mattes', ['Mattes', 'CC']],
                                  metric_weight=[1.0, 1.0, [0.5, 0.5]],
                                  number_of_iterations=[[10000, 11110, 11110],
                                                        [10000, 11110, 11110],
                                                        [100, 30, 20]],
                                  radius_or_number_of_bins=[32, 32, [32, 4]],
                                  sampling_percentage=[0.3, 0.3, [None, None]],
                                  sampling_strategy=['Regular',
                                                     'Regular',
                                                     [None, None]],
                                  shrink_factors=[[3, 2, 1],
                                                  [3, 2, 1],
                                                  [4, 2, 1]],
                                  smoothing_sigmas=[[4.0, 2.0, 1.0],
                                                    [4.0, 2.0, 1.0],
                                                    [1.0, 0.5, 0.0]],
                                  transform_parameters=[(0.1,),
                                                        (0.1,),
                                                        (0.2, 3.0, 0.0)],
                                  use_estimate_learning_rate_once=[True]*3,
                                  use_histogram_matching=[False, False, True],
                                  write_composite_transform=True),
                     name='NORMSTRUCT')


  #--- 8)  Apply the same warping to the EPI
  apply2mean = pe.Node(ApplyTransforms(args='--float',input_image_type=3,interpolation='Linear',invert_transform_flags=[False],num_threads=1,reference_image=template,terminal_output='file'),name='NORMFUNC')

  #--- 9)  Also need an outputnode, since otherwise some outputs may be binned.
  outputnode = pe.Node(interface=util.IdentityInterface(fields=['warped','structmat','funcmat','epimat','funcreg','structreg']),name='outputnode')


  #--- 10)  Custom plotting functions.
  def bplot(in_file, in_file2, MNI):
    from nilearn import image
    from nilearn import plotting
    import matplotlib
    niftifiledim=len(image.load_img(in_file).shape)
    display=plotting.plot_anat(template)    
    display.add_edges(in_file)
    display.add_contours(in_file2,filled=True, alpha=0.4,levels=[0.2], colors='b')
    matplotlib.pyplot.show()
    return niftifiledim


  def bplotN(in_file, in_file2, MNI):
      from nilearn import image
      from nilearn import plotting
      import matplotlib
      niftifiledim=len(image.load_img(in_file).shape)
      display=plotting.plot_anat(MNI)    
      display.add_edges(in_file)
      display.add_contours(in_file2,filled=True, alpha=0.4,levels=[0.2], colors='b')
      matplotlib.pyplot.show()
      return niftifiledim

  showregL= pe.Node(Function(input_names=['in_file','in_file2','MNI'],output_names=['niftifiledim'],function=bplot),name='SHOWREG')
  showregNL= pe.Node(Function(input_names=['in_file','in_file2','MNI'],output_names=['niftifiledim'],function=bplotN),name='SHOWREG')


  #--- 11)  Setup workflow
  workflow = pe.Workflow(name='NORMPIPE')
  workflow.base_dir = NIFTIDIR


  #--- 12)  Connect nodes, depending on whether we want to do normalisation too.
  if alsonorm == bool(0):
    workflow.connect(epireg,'epi2str_mat',outputnode,'epimat')
    workflow.connect(epireg,'epi2str_mat',concatxfm,'in_file')
    workflow.connect(registerT12S,'out_matrix_file',concatxfm,'in_file2')
    workflow.connect(concatxfm,'out_file',registerF2S,'in_matrix_file')
    workflow.connect(registerT12S,'out_matrix_file',outputnode,'structmat')
    workflow.connect(registerF2S,'out_matrix_file',outputnode,'funcmat')
    workflow.connect(registerF2S,'out_file',outputnode,'funcreg')
    workflow.connect(registerT12S,'out_file',outputnode,'structreg')
    workflow.connect(registerF2S,'out_file',showregL,'in_file2')
    workflow.connect(registerT12S,'out_file',showregL,'in_file')
    workflow.connect(inputnode,'standard',showregL,'MNI')
    workflow.write_graph(graph2use='exec')
    workflow.run()
  elif alsonorm == bool(1):
    workflow.connect(epireg,'epi2str_mat',outputnode,'epimat')
    workflow.connect(epireg,'epi2str_mat',concatxfm,'in_file')
    workflow.connect(registerT12S,'out_matrix_file',concatxfm,'in_file2')
    workflow.connect(concatxfm,'out_file',registerF2S,'in_matrix_file')
    workflow.connect(registerT12S,'out_matrix_file',outputnode,'structmat')
    workflow.connect(registerF2S,'out_matrix_file',outputnode,'funcmat')
    workflow.connect(registerF2S,'out_file',outputnode,'funcreg')
    workflow.connect(registerT12S,'out_file',outputnode,'structreg')
    workflow.connect(registerF2S,'out_file',apply2mean,'input_image')
    workflow.connect(registerT12S,'out_file',antsregfast,'moving_image')
    workflow.connect(antsregfast,'warped_image',outputnode,'warped')
    workflow.connect([(antsregfast, apply2mean, [('composite_transform','transforms')])])
    workflow.connect(antsregfast,'warped_image',showregNL,'in_file')
    workflow.connect(apply2mean,'output_image',showregNL,'in_file2')
    workflow.connect(inputnode,'standard',showregNL,'MNI')
    workflow.write_graph(graph2use='exec')
    workflow.run()


  print "Node completed. Returning to intital directory\n"
  os.chdir(INITDIR)











































