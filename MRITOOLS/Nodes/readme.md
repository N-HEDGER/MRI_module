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
| [Converter](#converter) | 1 | Converts a directory of DICOM files to nifti format | Structural or Functional Data |
| [Extracter](#extracter) | 2 | Remove non-brain tissue | Structural or Functional Data |
| [Register](#register) | >2 | Register image to MNI 152 space | Structural or Functional Data |
| [SpaceRealigner](#spacerealigner)| 3 | Motion correct data | Functional Data |
| [TimeRealigner](#timerealigner) | 4 | Slice-time correct data | Functional Data |
| [Smoother](#smoother) | 5 | Smooth data | Functional Data |
***

<a id='converter'></a>
## Converter

| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| Directory containing DICOM files | /CONVERTED /REORIENTED /CROPPED | dcm2nii, fsl, nipype, nilearn, matplotlib |

![alt text](https://i.imgbox.com/tQKKtAOV.png "Title")

### Description
* This function converts raw DICOM files to nifti (.nii) format.
* DICOM files are converted to nifti, reoriented to MNI 152 space and cropped to remove neck tissue. 

### Instructions
* To call this function, in the ipython terminal type:

```python
run CONVERTER
```

* You will be prompted to input a directory containing the DICOM folders you wish to convert. To do this, navigate to the directory in the finder/ file explorer, drag it into the terminal and press enter.

* A new directory will be created in the input directory called *'CONVERTER'* containing the outputs.

1. / CONVERTED - Converted file

2. / REORIENTED - Converted and reoriented file

3. / CROPPED - Converted, reoriented and cropped file (note that cropped files should only be used for structural images).

* The converted, reoriented nifti file is plotted to force check the result. If the data are 4D (functional) only the first volume is displayed.

![alt text](https://i.imgbox.com/uvxHs9ju.png "Title")
![alt text](https://i.imgbox.com/hKlPBY1s.png "Title")

***
<a id='extracter'></a>
## Extracter
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
| nifti file, fractional ansiotropy threshold (iterable), threshold gradient (iterable) | /REORIENTED /EXTRACTED | fsl, nipype, nilearn, matplotlib |

![alt text](https://i.imgbox.com/Ut5Z5GIu.png "Title")

### Description
* This function performs brain extraction on a nifti input.
* Firstly, reorientation of the volume is applied, then extraction using fsl BET.

### Instructions
* To call this function, in the ipython terminal type:

```python
run EXTRACTER
```

* You will be prompted to input the nifti file you wish to extract. To do this, navigate to the file in the finder/ file explorer, drag it into the terminal and press enter.

* Next, you will be prompted for the *fractional ansiotropy threshold* [0-1]. Broadly, this determines the size of the extracted tissue. Smaller values give larger brain outline estimates.

* Lastly, you will be asked for the *threshold gradient* [-1 - +1]. This determines the vertical gradient of the thresholding. Positive values give larger outline at the bottom and negative values give larger outline at the top. As a general rule of thumb, this value is almost always negative. This is because the reorientation to MNI space is already applied and regardless of cropping, there tends to be more non brain tissue towards the bottom of the volume (because of neck tissue).

* A new directory will be created in the input directory called *'CONVERTER'* containing the outputs.

1. / REORIENTED - Reoriented file

2. / EXTRACTED - Reoriented and extracted file

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
<a id='register'></a>
## Register
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
|reoriented & extracted nifti file, Degrees of freedom (iterable) , Non-linear? (boolean)| /REGISTERED /REGISTERED_WARPED (optional) | fsl, nipype, nilearn, matplotlib |

![alt text](https://i.imgbox.com/FCVdGfpb.png "Title")

### Description
* his function registers structural images to the MNI 152 template
* Inputs should be reoriented and extracted.
* Initially, linear registration is applied with FLIRT, then optionally, non-linear warping is applied with FNIRT, taking in the affine file from the initial FLIRT transformation.

### Instructions
* To call this function, in the ipython terminal type:

```python
run REGISTER
```

* You will be prompted to input the nifti file you wish to register. To do this, navigate to the file in the finder/ file explorer, drag it into the terminal and press enter.

* Next, you will be asked to input the degrees of freedom for the linear registration.

* Finally, you will be asked whether you wish to additionally apply non-linear warping. The default FSL values are assumed.

* A new directory will be created in the input directory called *'REGISTER'* containing the outputs.

1. / REGISTERED - Linearly registered .nii file

2. / REGISTERED_WARPED - Linearly registered and non-linearly warped .nii file

* Outlines of the registered and warped files, superimposed on the MNI 152 template are displayed.

![alt text](https://preview.ibb.co/gzk20k/figure_1.png  "Title")
![alt text](https://preview.ibb.co/hZHzfk/figure_2.png  "Title")


### Iterables

The degrees of freedom are iterable and can be entered as a comma seperated vector, but you should think carefully about whether you want to do this, since a misguided registration can take a lot of time. The FSL default is 12 DOF and this works pretty well most of the time.

### Notes
* As ever, it is beneficial to check the result more thoroughly in fslview or a related application, since the python implementation will only show a 2d figure.

* I assume the default location for the MNI 152 template, so this may need to be changed depending on the install location.

* Note that brain extraction needs to be very good for the non-linear warping to work properly. This is designed as a standalone function (i.e. there is no input from BET) so better results will be obtained if you supply the extracted and non-extracted volumes via the FSL GUI.


***
<a id='spacerealigner'></a>
## SpaceRealigner
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
***

<a id='timerealigner'></a>
## TimeRealigner
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
***

<a id='smoother'></a>
## Smoother
| Inputs | Outputs | Dependencies |
| --- | --- | --- |
***


