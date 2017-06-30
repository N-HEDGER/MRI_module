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

***

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

***

***
<a id='l1pipe'></a>
## L1PIPE
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
***

<a id='renderpipe'></a>
## RENDERPIPE
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| 1) Stats image 2) Combined linear transform matrix to MNI 3) ANTs composite warping transform to MNI 4) Threshold | Stats image rendered to MNI/ subject anatomical space | ANTs, FSL, nilearn, matplotlib, nipype |

![alt text](https://i.imgbox.com/9NhMmVHs.png "Title")

***

