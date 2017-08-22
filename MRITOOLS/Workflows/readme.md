# fMRI tools: Workflows

![alt text](https://www.python.org/static/favicon.ico "Title")
# General instructions

To interact with these tools on the fMRI virtual machine:
1. Open the terminal
2. Type *mriconsole* to load the ipython terminal

***

# Index
| Node | Description | Apply to |
| --- | --- | --- |
| [FUNCPIPE](#funcpipe) | Functional pre-processing workflow using FSL and AFNI | Functional Data |
| [NORMPIPE](#normpipe) | Registration and normalisation workflow with ANTs and FSL | Structural and Functional Data |
| [L1PIPE](#l1pipe) | First level analysis of functional data using FSL | Functional Data |
| [FIRPIPE](#firpipe) | Finite impulse response analysis of functional data using AFNI | Functional Data |
| [RENDERPIPE](#renderpipe)| Render first level stats onto anatomy/ MNI | Structural and Functional Data |


***
<a id='funcpipe'></a>
## FUNCPIPE
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| 1) Directory of DICOM files 2) Fractional anisotropy threshold 3) Vertical gradient 4) FWHM (mm) 5) High-pass filter cutoff 6) TR | preprocessed functional data, mean functional volume | fsl, afni, nipype, nilearn, matplotlib |   

![alt text](https://i.imgbox.com/6a0B0J8y.png "Title")

### Description
* Pre - processing workflow for functional data.
* Takes in a folder of DICOM files as input, performs conversion, reorientation, slice-timing correction, motion correction, despiking, brain extraction, smoothing & high-pass filtering.
* Outputs a mean functional volume prior to smoothing for registration/ visualisation of data. 

### Instructions
* To call this function, in the ipython terminal, type:

```python
from MRITOOLS.Workflows import FUNCPIPE
FUNCPIPE()
```

* You will first be prompted to drag in the directory of DICOM files for your functional run.

* Next, you will be required to enter the fractional anisotropy threshold for the extraction [0 - 1].

* Next, you will be required to enter the threshold gradient for the extraction [-1 - 1].

* Next, you will be required to enter the FWHM for the smoothing kernel (mm).

• Next, you will be required to enter the cutoff for the high-pass filter (s).

* Finally, you will be required to enter the TR (s).

* A new directory will be created called *'FUNCPIPE'* containing the outputs. The fully pre-processed data is contained in the *'PREPROCESSED'* directory, the mean functional volume is contained within the *'MEANFUNCTIONAL'* directory.

* Plots of the extraction and smoothing are returned.

***
<a id='normpipe'></a>
## NORMPIPE
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| 1) Also normalise (boolean) 2) Brain extracted structural 3) non brain-extracted structural 4) mean functional volume | 1) Registered structural 2) Registered functional 3) Warped structural 4) Warped functional | FSL, ANTs, nilearn, matplotlib, nipype |

![alt text](https://i.imgbox.com/VqzPwUow.png "Title")

### Description
* Registration and normalisation workflow.
* If also normalise = 1 it will perform registration and normalisation, otherwise just registration is applied. 
* Mean functional volume is registered to the subjects structural volume (FSL BBR).
* Structural volume is registered to the MNI brain (FSL FLIRT).
* Above transformation matrices are combined and applied to the mean functional (FSL applyxfm).
* T1 is then warped to MNI (ANTs Regsistration).
* ANTs transform is then applied to the mean functional (ANTs apply warp). 

### Instructions

* To call this function, in the ipython terminal type:

```python
from MRITOOLS.Workflows import NORMPIPE
NORMPIPE()
```

* Firstly, you be asked whether you wish to perform just registration (0) or registration and normalisation (1).

* Next, you will be required to drag in the brain extracted structural volume.

* Next, you will be required to drag in the non-brain extracted structural volume.

* Next, you will be prompted to drag in the mean functional volume.

* A directory *NORMPIPE* will be created with the following outputs:

1) /REGISTEREDT12MNI - structural .nii file registered to MNI 152 space.
2) /REGISTEREDF2MNI - functional .nii file registered to MNI 152 space.
3) /NORMFUNC - functional .nii file normalised to MNI 152 space.
4) /NORMSTRUCT - structural .nii file normalised to MNI 152 space, ANTS composite normalisation transform. 
5) /CONCATMATRICES - combined transformation matrix for functional image (functional to structural to MNI).

* A plot will display the subjects structural scan (red) on the MNI 152 template.
![alt text](https://i.imgbox.com/eVoDIGih.png "Title")

### Notes
* The ANTs registration algorithm can take a very long time.....

***
<a id='l1pipe'></a>
## L1PIPE
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| 1) pre-processed .nii file 2) TR (s) 3) High pass filter cutoff (s) 4) Directory containing 3-column event files | fsl, nipype, nilearn, matplotlib | 

![alt text](https://i.imgbox.com/vsthco54.png "Title")

### Description
* Workflow for performing a simple level 1 analysis on the example data.
* Data should be pre-processed (i.e. output of FUNCPIPE).
* It is useless for anything else unless the Designer node is modified.
* Plots the stats images using nilearn.

### Instructions
* To call this function, in the ipython terminal type:
```python
from MRITOOLS.Workflows import L1PIPE
L1PIPE()
```

* You will first be prompted to drag in the .nii file of pre-processed functional data (e.g. the output of FUNCPIPE).

* Next, you will be prompted to enter the TR (s).

* Next, you will be prompted to enter the highpass filter cutoff (s).

* Lastly, you will be prompted to enter the directory containing the 3 column event onset files.

* A directory *L1PIPE* will be created with the following outputs:

1) /FEATMODEL - a .png file of the design (below). 

![alt text](https://i.imgbox.com/E8WY7bbk.png "Title")

2) /FILM_GLS - z statistic .nii files. These will be plotted.

![alt text](https://i.imgbox.com/kl6pOFrU.png "Title")

***

<a id='firpipe'></a>
## FIRPIPE
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| 1) Preprocessed .nii file 2) Directory of event onset files| .jpg of model matrix, 1D plot of model matrix, AFNI bucket (fullstats), beta-weight bucket (betas) | afni, nipype|   

### Description
* Uses AFNI 3Ddeconvolve to estimate the shape of the HRF for each stimulus type in each voxel.
* Takes in a folder of 3 column event onset files (FSL format) and a pre-processed .nii file as inputs. Event files are converted to AFNI format, then these are used to form basis functions. As per AFNI default, each stimulus event is modeled as 7 basis functions (HRF of 12 seconds, with 7 beta weights to be estimated, starting at stimulus onset).
* The full statistical dataset (F,t and beta) are output to an AFNI bucket 'fullstats'.
* The beta weights are also extracted and sent to a seperate AFNI bucket 'betas'.
* After the model fitting, AFNIs '3Dinfo' command is called to show the contents of the fullstats bucket.

### Instructions
* To call this function, in the ipython terminal, type:

```python
from MRITOOLS.Workflows import FIRPIPE
FIRPIPE()
```

* You will first be prompted to drag in a directory of 3 column event onset files.

* Next, you will be required to drag in your pre-processed .nii file (output of FUNCPIPE or equivalent).

* A new directory will be created called *'FIRPIPE'* containing the outputs. The event files converted to afni format are in the
*'AFNIFYTXT'* directory. The *'AFNIFYCMD'* directory contains:

1) fullstats - an afni bucket containing all statistical volumes (F, t and beta). There will be a statistical image for each basis function for each stimulus type (i.e. 7 for each stimulus type). Also returned are the statistical volumes for the linear and constant terms (AFNI default).
2) betas - an afni bucket with just the beta weights.
3) matrix.1D - the design matrix in 1D format. This can be displayed via a call to '1Dplot' in the terminal.
4) X.jpg - the design matrix in .jpg format.

* 3Dinfo is called to display the contents of the fullstats bucket in the terminal.

***

<a id='renderpipe'></a>
## RENDERPIPE
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| 1) Stats image 2) Combined linear transform matrix to MNI 3) ANTs composite warping transform to MNI 4) Threshold | Stats image rendered to MNI/ subject anatomical space | ANTs, FSL, nilearn, matplotlib, nipype |

![alt text](https://i.imgbox.com/9NhMmVHs.png "Title")

### Description
* Workflow to render stats images to the MNI template/ structural volume.
* Requires that you run NORMPIPE first to get the transformation matrices and L1PIPE first to get the stats images. 

### Instructions
* To call this function, in the ipython terminal type:
```python
from MRITOOLS.Workflows import RENDERPIPE
RENDERPIPE()
```
* You will first be prompted to drag in the statistics image (e.g. z or t image, output from L1PIPE).

* You will then be prompted to input the matrix that transforms from the subjects functional image to MNI space (e.g. the output of NORMPIPE/CONCATMATRICES.

* Next you will be prompted to input the matrix that normalised the subjects T1 to the MNI (e.g. the output of NORMPIPE/NORMSTRUCT).

* Lastly, you will be prompted to input the threshold to apply to the statistics image (this is for plotting purposes, entering *2.3* will render voxels with a z score of >2.3 onto the MNI brain).

* A plot will be produced, showing the stats image rendered onto the MNI brain (see below).

![alt text](https://i.imgbox.com/QqCVWa0v.png "Title")

* The normalised stats image is contained within RENDERPIPE/RENDEREDNORM.

***

