# fMRI tools: Nodes

![alt text](https://www.python.org/static/favicon.ico "Title")
# General instructions
To access these tools:
1. Open the terminal
2. Type *ipython* to load the ipython terminal
***
# Index
| Node | Phase | Description | Apply to |
| --- | --- | --- | --- |
| [CONVERTER](#converter) | 1 | Converts a directory of DICOM files to nifti format | Structural or Functional Data |
| [SLICETIMER](#slicetimer) | 2 | Correct for slice timing differences | Functional Data |
| [MCORRECTOR](#mcorrector) | 3 | Correct for head movement | Functional Data |
| [EXTRACTER](#extracter) | 4 | Extract non-brain tissue | Structural or Functional Data |
| [SMOOTHER](#smoother)| 5 | Spatially smooth data | Functional Data |
| [HPFILTER](#hpfilter) | 6 | Apply high-pass temporal filtering to data | Functional Data |
***

<a id='converter'></a>
## CONVERTER

| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| i) Directory containing DICOM files | i) converted .nii file ii) reoriented .nii file | dcm2nii, fsl, nipype, nilearn, matplotlib |

![alt text](https://i.imgbox.com/tQKKtAOV.png "Title")

### Description
* This function converts raw DICOM files to nifti (.nii) format.
* DICOM files are converted to nifti, reoriented to MNI 152 space and cropped to remove neck tissue. 

### Instructions
* To call this function, in the ipython terminal type:

```python
from MRITOOLS.Nodes import CONVERTER
CONVERTER()
```

* You will be prompted to input a directory containing the DICOM folders you wish to convert. To do this, navigate to the directory in the finder/ file explorer, drag it into the terminal and press enter.

* A new directory will be created in the input directory called *'CONVERTER'* containing the outputs.

1. / CONVERTED - Converted file

2. / REORIENTED - Converted and reoriented file

* The converted, reoriented nifti file is plotted to force check the result. If the data are 4D (functional) only the first volume is displayed.

![alt text](https://i.imgbox.com/uvxHs9ju.png "Title")
![alt text](https://i.imgbox.com/hKlPBY1s.png "Title")

***
<a id='slicetimer'></a>
## SLICETIMER
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| i) .nii file ii) TR (s) | i) slice-timing corrected .nii file | fsl, nipype |

![alt text](https://i.imgbox.com/j0CDjG3V.png "Title")

### Description
* Performs slice timing correction, using the FSL slicetimer algorithm.
* It is nothing more than a simple wrapper.

### Instructions
* To call this function, in the ipython terminal type:

```python
from MRITOOLS.Nodes import SLICETIMER
SLICETIMER()
```

* You will then be prompted to drag in the nifti file you wish to slicetime.
* Next, you will be required to input the TR (s).

* A new directory will be created in the input directory called *'SLICETIMER'* containing the outputs:

1. / SLICETIMED - Slice-timing corrected nifti file (with suffix 'st').

### Notes
* An interleaved aquisition is assumed, since it is the most common.
* The middle slice is the reference slice, to which all other slices are interpolated to.

***

<a id='mcorrector'></a>
## MCORRECTOR
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| i) .nii file | i) motion corrected .nii file ii) plots of motion parameters | fsl, nipype |

![alt text](https://i.imgbox.com/HtOAWsDc.png "Title")


### Description
* Performs motion correction, using the FSL MCFLIRT algorithm.
* Outputs the motion-corrected .nii file and plots of the estimated motion parameters.

### Instructions
* To call this function, in the ipython terminal type:

```python
from MRITOOLS.Nodes import MCORRECTOR
MCORRECTOR()
```

* You will then be prompted to drag in the nifti file you wish to motion correct

* A new directory will be created in the input directory called *'MCORRECTOR'* containing the outputs:

1. / MCORRECTED - Motion corrected .nii file. Plots of the motion parameters (translations (below) and rotations).

![alt text](https://i.imgbox.com/hjaQb9Gc.png "Title")


### Notes
* The reference volume is the middle volume.

***

<a id='extracter'></a>
## EXTRACTER
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| i) nifti file ii) fractional anisotropy threshold (iterable) iii) threshold gradient (iterable) | i) extracted brain .nii file ii) binary brain mask .nii file | fsl, nipype, nilearn, matplotlib |

![alt text](https://i.imgbox.com/Ut5Z5GIu.png "Title")

### Description
* This function performs brain extraction on a nifti input.
* Firstly, reorientation of the volume is applied, then extraction using fsl BET.

### Instructions
* To call this function, in the ipython terminal type:

```python
from MRITOOLS.Nodes import EXTRACTER
EXTRACTER()
```

* You will be prompted to input the nifti file you wish to extract. To do this, navigate to the file in the finder/ file explorer, drag it into the terminal and press enter.

* Next, you will be prompted for the *fractional ansiotropy threshold* [0-1]. Broadly, this determines the size of the extracted tissue. Smaller values give larger brain outline estimates.

* Lastly, you will be asked for the *threshold gradient* [-1 - +1]. This determines the vertical gradient of the thresholding. Positive values give larger outline at the bottom and negative values give larger outline at the top. As a general rule of thumb, this value is almost always negative. This is because the reorientation to MNI space is already applied and regardless of cropping, there tends to be more non brain tissue towards the bottom of the volume (because of neck tissue).

* A new directory will be created in the input directory called *'EXTRACTER'* containing the outputs.

1. / REORIENTED - Reoriented file

2. / EXTRACTED - Reoriented and extracted file, binary brain mask.

* The reoriented, extracted nifti file is plotted and overlayed on the original image to force check the result. 


![alt text](https://i.imgbox.com/WgabSHu8.png "Title")

### Iterables
Both input parameters (*fractional ansiotropy threshold* and *threshold gradient*) can be input as either a single value, or as a comma - seperated vector. If entered as a vector, then the program will iterate throught the inputted values. For instance, the inputs

```python
[0.3,0.7]
```

```python
[-0.1,-0.4]
```
will result in the following folder structure, each folder containing the results of each combination of the parameters:

![alt text](https://i.imgbox.com/WDz8Awuj.png "Title")

### Notes
* It is beneficial to check the result more thoroughly in fslview or a related application, since the python implementation will only show a 2d figure.

* A good quality extraction is essential for good registration, so test a lot of values to see what works.

* Also contained within this folder is the function VERBOSE_EXTRACTER, which will apply 36 combinations of the two input parameters (linearly spaced). This is quite time consuming and memory intensive, but it  will give you a very thorough summary of impact the combinations of values have, so that you can refine future calls to EXTRACTER.
***

<a id='smoother'></a>
## SMOOTHER
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| i) .nii brain, ii) .nii binary brain mask iii) FWHM of smoother (interable, mm) | i) spatially smoothed .nii file | afni, nilearn, matplotlib, nipype |

![alt text](https://i.imgbox.com/2vENpEOU.png "Title")

### Description
* Performs spatial smoothing, using the AFNI 3DBlurinMask implementation.

### Instructions
* To call this function, in the ipython terminal type:

```python
from MRITOOLS.Nodes import SMOOTHER
SMOOTHER()
```
* You will then be prompted to drag in a brain-extracted .nii file.

* Next, you are prompted to drag in the binary brain mask (both of these are outputs of the EXTRACTER node).

* Finally, you are required to input the FWHM of the smoother (mm).

* A new directory will be created in the location of the input brain volume, titled *'SMOOTHER'*, containing the outputs:

1. /SMOOTHED - Spatially smoothed .nii file

* A plot of the first smoothed volume is displayed to force check the result.

### Iterables

* The input parameter *FWHM* is iterable, it can be entered as a comma separated vector of values. If entered in this way, then the program will iterate through the inputted values. For instance, the input:

```python
[3,5,6]
```
will result in a smoothing kernel with a FWHM of 3,5 & 6 mm being applied.

***

<a id='hpfilter'></a>
## HPFILTER
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| .nii file, high pass filter cutoff (iterable, s), TR | temporally filtered .nii file | fsl, nipype |

![alt text](https://i.imgbox.com/eoqdBFXo.png "Title")

### Description
* Performs high-pass temporal filtering, using fslmaths

### Instructions
* To call this function, in the ipython terminal type:

```python
from MRITOOLS.Nodes import HPFILTER
HPFILTER()
```
* You will then be prompted to drag in a .nii file.

* Next, you are prompted to input the high-pass filter cutoff (s)

* Finally, you are required to input the TR (s)

* A new directory will be created in the location of the input brain volume, titled *'HPFILTER'*, containing the outputs:

1. /FILTERED - Temporally filtered file (with mean volume subtracted).
2. /MEANVOL - Mean functional volume.
3. /HIGHPASSED - Temporally filtered file (with mean volume added back on).

### Iterables

* The input parameter *High pass filter cutoff* is iterable, it can be entered as a comma separated vector of values. If entered in this way, then the program will iterate through the inputted values. For instance, the input:

```python
[90,120]
```

will result of a high-pass cutoff of 90 and 120 s being applied. 

### Notes

* A mean functional volume is created using fslmaths and added to the filtered data. This is because as of FSL version 5.0.7, the filtering operation subtracts the mean from the filtered data. 

***


