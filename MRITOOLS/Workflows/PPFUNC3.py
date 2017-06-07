#--- 1)  Import modules
from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range

import os                                    # system functions
import nipype.interfaces.dcm2nii as dcm2nii
import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.modelgen as model   # model generation
import nipype.algorithms.rapidart as ra      # artifact detection
import nipype.interfaces.fsl.utils as fslu
import nipype.interfaces.fsl.preprocess as fslp
from nipype.interfaces import afni as afni
from nipype.interfaces.utility import Function
import matplotlib
from nilearn import plotting
from nilearn import image

import os
import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.interfaces.freesurfer as fs    # freesurfer
import nipype.interfaces.spm as spm


INITDIR=os.getcwd();

workflow = pe.Workflow(name='PREPROC')

#--- 3) Prompt user for directory containing DICOM FILES

DICOMDIR=raw_input('Please drag in the directory of\nDICOM files you wish to convert\n(ensure there is no blank space at the end)')

#--- 3) Move to directory

os.chdir(DICOMDIR)


#--- 4) Set up converter node for conversion to nifti

converter=pe.Node(interface=dcm2nii.Dcm2nii(),name='CONVERTED')
converter.inputs.source_dir=DICOMDIR
converter.inputs.gzip_output=bool(1)


#--- 5) Set up realigner node to match orientation of MNI 152

realigner=pe.Node(interface=fslu.Reorient2Std(),name='REORIENTED')
realigner.inputs.output_type='NIFTI_GZ'

workflow.connect(converter,'converted_files',realigner,'in_file')


#--- 6) Set up a slice timing node

slicetimer=pe.Node(interface=fslp.SliceTimer(),name='SLICETIMED')
slicetimer.inputs.interleaved = True
slicetimer.inputs.time_repetition = float(2)

workflow.connect(realigner, 'out_file', slicetimer, 'in_file')


#--- 7) Convert to float.
img2float = pe.Node(interface=fsl.ImageMaths(out_data_type='float',op_string='',suffix='_dtype'),name='img2float')
workflow.connect(slicetimer,'slice_time_corrected_file',img2float,'in_file')

#--- 8) Motion correct.
motion_correct = pe.Node(interface=fsl.MCFLIRT(save_mats=True,save_plots=True,interpolation='spline'),name='realign')

workflow.connect(img2float, 'out_file', motion_correct, 'in_file')


#--- 9) Despike
despiker=pe.Node(interface=afni.Despike(),name='DESPIKED')
despiker.inputs.outputtype = 'NIFTI_GZ'

workflow.connect(motion_correct,'out_file',despiker,'in_file')

#--- 10) Plot motion.
plot_motion = pe.Node(interface=fsl.PlotMotionParams(in_source='fsl'),name='plot_motion')
plot_motion.iterables = ('plot_type', ['rotations', 'translations'])

workflow.connect(motion_correct, 'par_file', plot_motion, 'in_file')

#--- 11) Extract
extracter=pe.Node(interface=fsl.BET(),name='EXTRACTED')
extracter.inputs.frac=float(0.4)
extracter.inputs.mask=bool(1)
extracter.inputs.functional=bool(1)

workflow.connect(despiker, 'out_file', extracter, 'in_file')


def bplot(in_file,in_file2,in_file3):
	from nilearn import image
	from nilearn import plotting
	niftifiledim=len(image.load_img(in_file).shape)
	firstim=image.index_img(in_file, 0)
	firstim2=image.index_img(in_file2, 0)
	display=plotting.plot_anat(firstim2, title = "Extraction overlayed on original")	
	display.add_contours(firstim,filled=True, alpha=0.5,levels=[0.2], colors='b')
	display.add_edges(in_file3)
	return niftifiledim

#--- 12) Show extract

showextract= pe.Node(Function(input_names=['in_file','in_file2','in_file3'],output_names=['niftifiledim'],function=bplot),name='SHOWEXTRACT')

workflow.connect(despiker,'out_file', showextract,'in_file2')
workflow.connect(extracter,'out_file', showextract,'in_file')
workflow.connect(extracter,'mask_file', showextract,'in_file3')

workflow.base_dir = DICOMDIR
workflow.write_graph(graph2use='exec')

#--- 13) Run workflow
result=workflow.run()

#--- 14) Show plot
matplotlib.pyplot.show()


os.chdir(INITDIR)







