
# Convert
# Realign
# Slicetime
# Despike
# Motion correct
# Plot motion
# Get mask
# SUSAN
# HIGHPASS
# Need getbtthresh, get meanscale, getusans



import os
import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.interfaces.freesurfer as fs    # freesurfer
import nipype.interfaces.spm as spm
import nipype.interfaces.dcm2nii as dcm2nii
import nipype.interfaces.fsl.utils as fslu
import nipype.interfaces.fsl.preprocess as fslp
from nipype.interfaces import afni as afni

from nipype import LooseVersion


def getthreshop(thresh):
    return ['-thr %.10f -Tmin -bin'%(0.1*val[1]) for val in thresh]

def pickfirst(files):
    if isinstance(files, list):
        return files[0]
    else:
        return files

def pickmiddle(files):
    from nibabel import load
    import numpy as np
    middlevol = []
    for f in files:
        middlevol.append(int(np.ceil(load(f).get_shape()[3]/2)))
    return middlevol

def pickvol(filenames, fileidx, which):
    from nibabel import load
    import numpy as np
    if which.lower() == 'first':
        idx = 0
    elif which.lower() == 'middle':
        idx = int(np.ceil(load(filenames[fileidx]).get_shape()[3]/2))
    elif which.lower() == 'last':
        idx = load(filenames[fileidx]).get_shape()[3]-1
    else:
        raise Exception('unknown value for volume selection : %s' % which)
    return idx

def getbtthresh(medianvals):
    return [0.75*val for val in medianvals]

def chooseindex(fwhm):
    if fwhm<1:
        return [0]
    else:
        return [1]

def getmeanscale(medianvals):
    return ['-mul %.10f'%(10000./val) for val in medianvals]

def getusans(x):
    return [[tuple([val[0],0.75*val[1]])] for val in x]

tolist = lambda x: [x]
highpass_operand = lambda x:'-bptf %.10f -1'%x


def create_featreg_preproc(name='featpreproc', highpass=True, whichvol='middle'):
    """Create a FEAT preprocessing workflow with registration to one volume of the first run

    Parameters
    ----------

    ::

        name : name of workflow (default: featpreproc)
        highpass : boolean (default: True)
        whichvol : which volume of the first run to register to ('first', 'middle', 'last', 'mean')

    Inputs::

        inputspec.func : functional runs (filename or list of filenames)
        inputspec.fwhm : fwhm for smoothing with SUSAN
        inputspec.highpass : HWHM in TRs (if created with highpass=True)

    Outputs::

        outputspec.reference : volume to which runs are realigned
        outputspec.motion_parameters : motion correction parameters
        outputspec.realigned_files : motion corrected files
        outputspec.motion_plots : plots of motion correction parameters
        outputspec.mask : mask file used to mask the brain
        outputspec.smoothed_files : smoothed functional data
        outputspec.highpassed_files : highpassed functional data (if highpass=True)
        outputspec.mean : mean file

    Example
    -------

    >>> preproc = create_featreg_preproc()
    >>> preproc.inputs.inputspec.func = ['f3.nii', 'f5.nii']
    >>> preproc.inputs.inputspec.fwhm = 5
    >>> preproc.inputs.inputspec.highpass = 128./(2*2.5)
    >>> preproc.base_dir = '/tmp'
    >>> preproc.run() # doctest: +SKIP

    >>> preproc = create_featreg_preproc(highpass=False, whichvol='mean')
    >>> preproc.inputs.inputspec.func = 'f3.nii'
    >>> preproc.inputs.inputspec.fwhm = 5
    >>> preproc.base_dir = '/tmp'
    >>> preproc.run() # doctest: +SKIP
    """

    version = 0
    if fsl.Info.version() and \
            LooseVersion(fsl.Info.version()) > LooseVersion('5.0.6'):
        version = 507

    featpreproc = pe.Workflow(name=name)

    """
    Set up a node to define all inputs required for the preprocessing workflow

    """

    if highpass:
        inputnode = pe.Node(interface=util.IdentityInterface(fields=['func',
                                                                     'fwhm',
                                                                     'highpass']),
                            name='inputspec')
        outputnode = pe.Node(interface=util.IdentityInterface(fields=['reference',
                                                                      'motion_parameters',
                                                                      'realigned_files',
                                                                      'motion_plots',
                                                                      'mask',
                                                                      'smoothed_files',
                                                                      'highpassed_files',
                                                                      'mean']),
                             name='outputspec')
    else:
        inputnode = pe.Node(interface=util.IdentityInterface(fields=['func',
                                                                     'fwhm']),
                            name='inputspec')
        outputnode = pe.Node(interface=util.IdentityInterface(fields=['reference',
                                                                      'motion_parameters',
                                                                      'realigned_files',
                                                                      'motion_plots',
                                                                      'mask',
                                                                      'smoothed_files',
                                                                      'mean']),
                             name='outputspec')

    """
    Set up a node to define outputs for the preprocessing workflow

    """

    """
    Convert functional images to float representation. Since there can
    be more than one functional run we use a MapNode to convert each
    run.
    """

    # 1)  Convert from DICOM to nifti Y
    converter=pe.Node(interface=dcm2nii.Dcm2nii(),name='CONVERTED')
    converter.inputs.gzip_output=bool(1)
    featpreproc.connect(inputnode, 'func', converter, 'source_dir')

    # 2)  Realign to MNI orientation Y
    realigner=pe.Node(interface=fslu.Reorient2Std(),name='REORIENTED')
    realigner.inputs.output_type='NIFTI_GZ'
    featpreproc.connect(converter,'converted_files',realigner,'in_file')

    # 3) Slice time Y
    slicetimer=pe.Node(interface=fslp.SliceTimer(),name='SLICETIMED')
    slicetimer.inputs.interleaved = True
    featpreproc.connect(realigner,'out_file',slicetimer,'in_file')

    # 4) Despike Y
    despiker=pe.Node(interface=afni.Despike(),name='DESPIKED')
    despiker.inputs.outputtype = 'NIFTI_GZ'
    featpreproc.connect(slicetimer,'slice_time_corrected_file',despiker,'in_file')


    # 5) Conversion to float Y
    img2float = pe.MapNode(interface=fsl.ImageMaths(out_data_type='float',
                                                    op_string='',
                                                    suffix='_dtype'),
                           iterfield=['in_file'],
                           name='img2float')

    featpreproc.connect(despiker,'out_file', img2float, 'in_file')
    
    # 6) Extract the middle (or what whichvol points to) volume of the first run as the reference (simplify)
    

    if whichvol != 'mean':
        extract_ref = pe.Node(interface=fsl.ExtractROI(t_size=1),
                              iterfield=['in_file'],
                              name='extractref')
        featpreproc.connect(img2float, ('out_file', pickfirst), extract_ref, 'in_file')
        featpreproc.connect(img2float, ('out_file', pickvol, 0, whichvol), extract_ref, 't_min')
        featpreproc.connect(extract_ref, 'roi_file', outputnode, 'reference')

    
    # 7) Realign the functional runs to the reference (`whichvol` volume of first run)
    
    motion_correct = pe.MapNode(interface=fsl.MCFLIRT(save_mats=True,
                                                      save_plots=True,
                                                      interpolation='spline'),
                                name='realign',
                                iterfield=['in_file'])
    featpreproc.connect(img2float, 'out_file', motion_correct, 'in_file')

    if whichvol != 'mean':
        featpreproc.connect(extract_ref, 'roi_file', motion_correct, 'ref_file')
    else:
        motion_correct.inputs.mean_vol = True
        featpreproc.connect(motion_correct, ('mean_img', pickfirst), outputnode, 'reference')

    featpreproc.connect(motion_correct, 'par_file', outputnode, 'motion_parameters')
    featpreproc.connect(motion_correct, 'out_file', outputnode, 'realigned_files')

    
    # 8) Plot the estimated motion parameters Y
    
    plot_motion = pe.MapNode(interface=fsl.PlotMotionParams(in_source='fsl'),
                             name='plot_motion',
                             iterfield=['in_file'])
    plot_motion.iterables = ('plot_type', ['rotations', 'translations'])
    featpreproc.connect(motion_correct, 'par_file', plot_motion, 'in_file')
    featpreproc.connect(plot_motion, 'out_file', outputnode, 'motion_plots')

    
    # 9) Extract the mean volume of the first functional run
    
    meanfunc = pe.Node(interface=fsl.ImageMaths(op_string='-Tmean',
                                                suffix='_mean'),
                       name='meanfunc')
    featpreproc.connect(motion_correct, ('out_file', pickfirst), meanfunc, 'in_file')

    
    # 10) Strip the skull from the mean functional to generate a mask (needed? or just BET the whole run?)
    

    meanfuncmask = pe.Node(interface=fsl.BET(mask=True,
                                             no_output=True,
                                             frac=0.3),
                           name='meanfuncmask')
    
    featpreproc.connect(meanfunc, 'out_file', meanfuncmask, 'in_file')

    
    # 11) Mask the functional runs with the extracted mask (just bet the whole run)


    maskfunc = pe.MapNode(interface=fsl.ImageMaths(suffix='_bet',
                                                   op_string='-mas'),
                          iterfield=['in_file'],
                          name='maskfunc')
    featpreproc.connect(motion_correct, 'out_file', maskfunc, 'in_file')
    featpreproc.connect(meanfuncmask, 'mask_file', maskfunc, 'in_file2')

    
    # 12) Determine the 2nd and 98th percentile intensities of each functional run
    

    getthresh = pe.MapNode(interface=fsl.ImageStats(op_string='-p 2 -p 98'),
                           iterfield=['in_file'],
                           name='getthreshold')
    featpreproc.connect(maskfunc, 'out_file', getthresh, 'in_file')

    
    # 13) Threshold the first run of the functional data at 10% of the 98th percentile
    

    threshold = pe.MapNode(interface=fsl.ImageMaths(out_data_type='char',
                                                    suffix='_thresh'),
                           iterfield=['in_file', 'op_string'],
                           name='threshold')
    featpreproc.connect(maskfunc, 'out_file', threshold, 'in_file')

    
    # 14) Define a function to get 10% of the intensity
    

    featpreproc.connect(getthresh, ('out_stat', getthreshop), threshold, 'op_string')

    
    # 15) Determine the median value of the functional runs using the mask
    

    medianval = pe.MapNode(interface=fsl.ImageStats(op_string='-k %s -p 50'),
                           iterfield=['in_file', 'mask_file'],
                           name='medianval')
    featpreproc.connect(motion_correct, 'out_file', medianval, 'in_file')
    featpreproc.connect(threshold, 'out_file', medianval, 'mask_file')

    
    # 16) Dilate the mask (eh?)
    

    dilatemask = pe.MapNode(interface=fsl.ImageMaths(suffix='_dil',
                                                     op_string='-dilF'),
                            iterfield=['in_file'],
                            name='dilatemask')
    featpreproc.connect(threshold, 'out_file', dilatemask, 'in_file')
    featpreproc.connect(dilatemask, 'out_file', outputnode, 'mask')

    
    # 17) Mask the motion corrected functional runs with the dilated mask (what is special about this????)


    maskfunc2 = pe.MapNode(interface=fsl.ImageMaths(suffix='_mask',
                                                    op_string='-mas'),
                           iterfield=['in_file', 'in_file2'],
                           name='maskfunc2')
    featpreproc.connect(motion_correct, 'out_file', maskfunc2, 'in_file')
    featpreproc.connect(dilatemask, 'out_file', maskfunc2, 'in_file2')

    """
    Smooth each run using SUSAN with the brightness threshold set to 75%
    of the median value for each run and a mask constituting the mean
    functional
    """

    smooth = create_susan_smooth()

    featpreproc.connect(inputnode, 'fwhm', smooth, 'inputnode.fwhm')
    featpreproc.connect(maskfunc2, 'out_file', smooth, 'inputnode.in_files')
    featpreproc.connect(dilatemask, 'out_file', smooth, 'inputnode.mask_file')

    """
    Mask the smoothed data with the dilated mask
    """

    maskfunc3 = pe.MapNode(interface=fsl.ImageMaths(suffix='_mask',
                                                    op_string='-mas'),
                           iterfield=['in_file', 'in_file2'],
                           name='maskfunc3')

    featpreproc.connect(smooth, 'outputnode.smoothed_files', maskfunc3, 'in_file')

    featpreproc.connect(dilatemask, 'out_file', maskfunc3, 'in_file2')

    concatnode = pe.Node(interface=util.Merge(2),
                         name='concat')
    featpreproc.connect(maskfunc2, ('out_file', tolist), concatnode, 'in1')
    featpreproc.connect(maskfunc3, ('out_file', tolist), concatnode, 'in2')

    """
    The following nodes select smooth or unsmoothed data depending on the
    fwhm. This is because SUSAN defaults to smoothing the data with about the
    voxel size of the input data if the fwhm parameter is less than 1/3 of the
    voxel size.
    """
    selectnode = pe.Node(interface=util.Select(), name='select')

    featpreproc.connect(concatnode, 'out', selectnode, 'inlist')

    featpreproc.connect(inputnode, ('fwhm', chooseindex), selectnode, 'index')
    featpreproc.connect(selectnode, 'out', outputnode, 'smoothed_files')

    """
    Scale the median value of the run is set to 10000
    """

    meanscale = pe.MapNode(interface=fsl.ImageMaths(suffix='_gms'),
                           iterfield=['in_file', 'op_string'],
                           name='meanscale')

    featpreproc.connect(selectnode, 'out', meanscale, 'in_file')

    """
    Define a function to get the scaling factor for intensity normalization
    """

    featpreproc.connect(medianval, ('out_stat', getmeanscale), meanscale, 'op_string')

    """
    Generate a mean functional image from the first run
    """

    meanfunc3 = pe.Node(interface=fsl.ImageMaths(op_string='-Tmean',
                                                 suffix='_mean'),
                        iterfield=['in_file'],
                        name='meanfunc3')

    featpreproc.connect(meanscale, ('out_file', pickfirst), meanfunc3, 'in_file')
    featpreproc.connect(meanfunc3, 'out_file', outputnode, 'mean')

    """
    Perform temporal highpass filtering on the data
    """

    if highpass:
        highpass = pe.MapNode(interface=fsl.ImageMaths(suffix='_tempfilt'),
                              iterfield=['in_file'],
                              name='highpass')
        featpreproc.connect(inputnode, ('highpass', highpass_operand), highpass, 'op_string')
        featpreproc.connect(meanscale, 'out_file', highpass, 'in_file')

        if version < 507:
            featpreproc.connect(highpass, 'out_file', outputnode, 'highpassed_files')
        else:
            """
            Add back the mean removed by the highpass filter operation as of FSL 5.0.7
            """
            meanfunc4 = pe.MapNode(interface=fsl.ImageMaths(op_string='-Tmean',
                                                            suffix='_mean'),
                                   iterfield=['in_file'],
                                   name='meanfunc4')

            featpreproc.connect(meanscale, 'out_file', meanfunc4, 'in_file')
            addmean = pe.MapNode(interface=fsl.BinaryMaths(operation='add'),
                                 iterfield=['in_file', 'operand_file'],
                                 name='addmean')
            featpreproc.connect(highpass, 'out_file', addmean, 'in_file')
            featpreproc.connect(meanfunc4, 'out_file', addmean, 'operand_file')
            featpreproc.connect(addmean, 'out_file', outputnode, 'highpassed_files')

    return featpreproc

def create_susan_smooth(name="susan_smooth", separate_masks=True):
    """Create a SUSAN smoothing workflow

    Parameters
    ----------

    ::

        name : name of workflow (default: susan_smooth)
        separate_masks : separate masks for each run

    Inputs::

        inputnode.in_files : functional runs (filename or list of filenames)
        inputnode.fwhm : fwhm for smoothing with SUSAN
        inputnode.mask_file : mask used for estimating SUSAN thresholds (but not for smoothing)

    Outputs::

        outputnode.smoothed_files : functional runs (filename or list of filenames)

    Example
    -------

    >>> smooth = create_susan_smooth()
    >>> smooth.inputs.inputnode.in_files = 'f3.nii'
    >>> smooth.inputs.inputnode.fwhm = 5
    >>> smooth.inputs.inputnode.mask_file = 'mask.nii'
    >>> smooth.run() # doctest: +SKIP

    """

    susan_smooth = pe.Workflow(name=name)

    """
    Set up a node to define all inputs required for the preprocessing workflow

    """

    inputnode = pe.Node(interface=util.IdentityInterface(fields=['in_files',
                                                                 'fwhm',
                                                                 'mask_file']),
                        name='inputnode')

    """
    Smooth each run using SUSAN with the brightness threshold set to 75%
    of the median value for each run and a mask consituting the mean
    functional
    """

    smooth = pe.MapNode(interface=fsl.SUSAN(),
                        iterfield=['in_file', 'brightness_threshold', 'usans'],
                        name='smooth')

    """
    Determine the median value of the functional runs using the mask
    """

    if separate_masks:
        median = pe.MapNode(interface=fsl.ImageStats(op_string='-k %s -p 50'),
                            iterfield=['in_file', 'mask_file'],
                            name='median')
    else:
        median = pe.MapNode(interface=fsl.ImageStats(op_string='-k %s -p 50'),
                            iterfield=['in_file'],
                            name='median')
    susan_smooth.connect(inputnode, 'in_files', median, 'in_file')
    susan_smooth.connect(inputnode, 'mask_file', median, 'mask_file')

    """
    Mask the motion corrected functional runs with the dilated mask
    """

    if separate_masks:
        mask = pe.MapNode(interface=fsl.ImageMaths(suffix='_mask',
                                                   op_string='-mas'),
                          iterfield=['in_file', 'in_file2'],
                          name='mask')
    else:
        mask = pe.MapNode(interface=fsl.ImageMaths(suffix='_mask',
                                                   op_string='-mas'),
                          iterfield=['in_file'],
                          name='mask')
    susan_smooth.connect(inputnode, 'in_files', mask, 'in_file')
    susan_smooth.connect(inputnode, 'mask_file', mask, 'in_file2')

    """
    Determine the mean image from each functional run
    """

    meanfunc = pe.MapNode(interface=fsl.ImageMaths(op_string='-Tmean',
                                                   suffix='_mean'),
                          iterfield=['in_file'],
                          name='meanfunc2')
    susan_smooth.connect(mask, 'out_file', meanfunc, 'in_file')

    """
    Merge the median values with the mean functional images into a coupled list
    """

    merge = pe.Node(interface=util.Merge(2, axis='hstack'),
                    name='merge')
    susan_smooth.connect(meanfunc, 'out_file', merge, 'in1')
    susan_smooth.connect(median, 'out_stat', merge, 'in2')

    """
    Define a function to get the brightness threshold for SUSAN
    """
    susan_smooth.connect(inputnode, 'fwhm', smooth, 'fwhm')
    susan_smooth.connect(inputnode, 'in_files', smooth, 'in_file')
    susan_smooth.connect(median, ('out_stat', getbtthresh), smooth, 'brightness_threshold')
    susan_smooth.connect(merge, ('out', getusans), smooth, 'usans')

    outputnode = pe.Node(interface=util.IdentityInterface(fields=['smoothed_files']),
                         name='outputnode')

    susan_smooth.connect(smooth, 'smoothed_file', outputnode, 'smoothed_files')

    return susan_smooth


preproc = create_featreg_preproc()
preproc.inputs.inputspec.func = raw_input('Please drag in the directory of\nDICOM files you wish to convert\n(ensure there is no blank space at the end)')
preproc.inputs.inputspec.fwhm = 5
preproc.inputs.inputspec.highpass = 90

os.chdir(preproc.inputs.inputspec.func)
preproc.base_dir = preproc.inputs.inputspec.func
preproc.write_graph(graph2use='exec')
#preproc.run() 




