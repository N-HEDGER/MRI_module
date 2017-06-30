# fMRI tools: Workflows

![alt text](https://www.python.org/static/favicon.ico "Title")
# General instructions
To access these tools:
1. Open the terminal
2. Type *ipython* to load the ipython terminal
***

# Index
| Node | Description | Apply to |
| --- | --- | --- |
| [FUNCPIPE](#funcpipe) | Functional pre-processing workflow | Functional Data |
| [NORMPIPE](#normpipe) | Registration and normalisation workflow | Structural and Functional Data |
| [L1PIPE](#l1pipe) | First level analysis of functional data | Functional Data |
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
* Mean functional volume is registered to the subjects structural volume (FSL BBR)
* Structural volume is registered to the MNI brain (FSL FLIRT).
* Above transformation matrices are combined and applied to the mean functional (FSL applyxfm).
* T1 is then warped to MNI (ANTs Regsistration)
* Transform is applied to the mean functional (ANTs apply warp). 

### Instructions
* Firstly, you be asked whether you wish to perform just registration (0) or registration and normalisation (1).

* Next, you will be required to drag in the brain extracted structural volume.

* Next, you will be required to drag in the non-brain extracted structural volume.

* Next, you will be prompted to drag in the mean functional volume.

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

### Description
* Workflow for performing a simple level 1 analysis on the example data.
* Data should be pre-processed (i.e. output of FUNCPIPE).
* It is useless for anything else unless the Designer node is modified.
* Plots the stats images using nilearn.


![alt text](https://i.imgbox.com/vsthco54.png "Title")

![alt text](https://i.imgbox.com/E8WY7bbk.png "Title")

![alt text](https://i.imgbox.com/kl6pOFrU.png "Title")

***

<a id='renderpipe'></a>
## RENDERPIPE
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| 1) Stats image 2) Combined linear transform matrix to MNI 3) ANTs composite warping transform to MNI 4) Threshold | Stats image rendered to MNI/ subject anatomical space | ANTs, FSL, nilearn, matplotlib, nipype |

### Description
* Workflow to render stats images to the MNI template/ structural volume.
* Requires that you run NORMPIPE first to get the transformation matrices and L1PIPE first to get the stats images. 

![alt text](https://i.imgbox.com/9NhMmVHs.png "Title")

![alt text](https://i.imgbox.com/QqCVWa0v.png "Title")


***

