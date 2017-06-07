# Analysis tools: Setting up your system.

In order to use the analysis tools, you will first need to prepare your system. This is a relatively involved process, consisting of several stages.

# Index
| Phase | Description |
| --- | --- |
| 1 | [Initial Preparations](#initprep) |
| 2 | [Setting up your ANACONDA Environment](#anaconda)|
| 3 | [Setting up FSL](#fsl) |
| 4 | [Setting up mricron/dcm2nii](#dcm2nii) |
| 5 | [Setting up AFNI](#afni) |
| 6 | [Downloading the Nodes and Workflows](#nodes) |
| 7 | [Downloading the Example Data](#data) |
| 8 | [Final checks](#checks) |
***

<a id='initprep'></a>
## Initial Preparations

### Checking your privileges

Fist of all, it is assumed that you have administator privelages for your system. You can verify that you have admin privileges by opening up your terminal application.

1. Enter the command:

```
sudo ls
```
2. You will be prompted to enter your password.
3. As a security measure, you won't recieve any indication that you are typing anything, but proceed as normal and press enter.
4. If a list of files is returned with no error, then you have admin privileges for your system. If an error is returned, then you will need to request admin rights via the relevant pathways.

### Modifying your bash profile

On occasion throughout this process, you will need to modify your *bash profile*. To make this easier, you need to follow these steps.

1. To view your bash profile, in the terminal, enter the command:

```
touch ~/.bash_profile; open ~/.bash_profile
```
2. This should open up the bash profile in your default text editor

3. Next, in the text editor, add the following lines to your bash profile:

```
showmybash() {
touch ~/.bash_profile; open ~/.bash_profile
}
```
4. This has created a function that we can call in the terminal to open the bash profile more easily.
5. Save the .bash_profile and exit.
6. Now, restart the terminal application.
7. If you now type in
```
showmybash
```
then your bash profile should appear as before. In the future, we can call the showmybash function to interact with the bash profile.

***
<a id='anaconda'></a>
## Setting up Your Anaconda Environment

The analysis tools are primarily implemented in python. Moreover, they rely on a series of python 'modules' that will need to be installed and maintained. Anaconda is a popular module and environment manager that can achieve this.

1. Firstly, head to the [Anaconda website](https://www.continuum.io/downloads)
2. Download the Python 2.7 installer for your operating system.
3. Open the installer file and follow the onscreen instructions until successful installation.
4. Next, open up the terminal. We are now going to use Anaconda to create a virtual environment that we will use for our analyses.
5. To do this, type the following commands in the terminal.

```
conda config --add channels intel
conda config --add channels conda-forge
conda create -n fMRI intelpython2_full python=2
```
These commands will create a new environment, named fMRI.

6. To activate this environment, simply enter

```
source activate fMRI
```
7. To view the packages contained in this environment, type:

```
conda list
```

8. We are now going to install the relevant packages into this environment, via pip:

```
pip install nipype
pip install pydotplus
pip install nilearn
pip install graphviz

```
9. Verify that these are installed via another call to conda list. You should see these new items under the list of installed packages.

10. Now, exit, your virtual environment by entering:

```
source deactivate i2
```

***
<a id='fsl'></a>
## Setting up FSL
FSL is a comprehensive library of tools for fMRI analysis. Most of the analysis tools in this repository recruit FSL commands. 

1. To install FSL, follow the official instructions for your OS, located [here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)

2. Before you can use FSL, your system will first need to know where the main FSL shell script is located. On a mac OS, the default install location is in /usr/local. Therefore, add the following to your bash profile (checking that the path is correct).

```
# FSL Setup
FSLDIR=/usr/local/fsl
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH
. ${FSLDIR}/etc/fslconf/fsl.sh
```
3. Next, save your bash profile and restart your terminal application. If your install has been successful, typing the command:

```
fsl
```
should start the main FSL GUI.

***
<a id='dcm2nii'></a>
## Setting up MRIcron/dcm2nii
MRIcron is a lightweight, easy to use application for viewing and basic analysis of fMRI data. MRIcron comes with the incredibly useful dcm2nii application, which elegantly converts DICOM image files to nifti format.

1. 1. To download MRIcron/dcm2nii, follow the official instructions for your OS, located [here](http://people.cas.sc.edu/rorden/mricron/install.html).
2. When the relevant file has been downloaded, unzip/extract it and place the MRIcron folder in a sensible location (e.g. /Applications).
3. Next, add the following lines to your bash profile (changing the path depending on your chosen install location).

```
# dcm2nii Setup
MRICRONDIR=/Applications/mricron
PATH=${MRICRONDIR}:$PATH
export MRICRONDIR PATH

# mricron Setup
MRICRONDIR2=/Applications/MRIcron/mricron.app/Contents/MacOS
PATH=${MRICRONDIR2}:$PATH
export MRICRONDIR2 PATH
```
4. Next, save your bash profile and restart your terminal application. If your install has been successful, entering the command:

```
mricron
```
will start the MRIcron application, and typing the command:

```
dcm2nii
```
will output a bunch of dcm2nii help text to the terminal.

***
<a id='afni'></a>
## Setting up AFNI

***
<a id='nodes'></a>
## Downloading the Nodes and Workflows

***
<a id='data'></a>
## Downloading the Example Data

***
<a id='checks'></a>
## Final checks



