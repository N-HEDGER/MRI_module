# fMRI software
The amount of data handling and pre-processing involved in fMRI analysis can be quite intimidating.

What options do we have available to help us with all this?

Currently, there is a huge range of software packages for fMRI analysis. Well-known examples include FSL, SPM, Freesurfer and many more.

![alt text](https://i.imgbox.com/FOp1JK5t.png "Title")

On the surface, this wide array of choices seems like a good thing, but it is actually associated with a range of issues

### No unifying operating interface

The first problem is that these different software packages are interfaces with in fundamentally different ways. For instance:
* We interact with FSL, Freesurfer and AFNI commands via shell scripting.
* SPM is implemented in MATLAB
* Other options such as Nipy and Nilearn are implemented in Python.

This means that there is no unfying operating interface - we have to use different applications and programming languages.

To make matters worse, some software packages do not work on some operating systems. For instance FSL and Freesurfer do not work on windows.

### The learning curve

Another issue associated with this, is the substantial learning curve involved.

Each of these software packages have their own quirks, parameters and usages that require extensive time and interaction to learn.

For instance, someone that wanted to use both SPM and FSL would have to learn both MATLAB and UNIX programming, which is a non-trivial task.

Perhaps because of this, researchers tend to remain ‘loyal’ to a particular software package, to avoid investing the time involved in learning how to use more than one.

This is bad practice, because some software packages are proven to be better at some aspects of pre-processing than others.

For instance, unbiased tests have shown that ANTs is found to be far superior to FSL at normalization, but many people would be reluctant to learn ANTS for one task if they already know FSL.

### Lack of transparency

Another problem that is produced is a lack of transparency in fMRI analyses.

The method sections in fMRI papers are often quite opaque and it can be very difficult to effectively share your analyses with other people, particularly if your workflow involved lots of different software packages.

This makes reproducing and replicating results even harder. 

# Nipype 

So you may have noticed that I am painting a fairly bleak picture here.

This is where Nipype comes in.

Nipype is a framework that allows you to interface with a number of different fMRI software packages within a single python script. 

The syntax of a Nipype script is actually very straightforward.  

Firstly, you import interfaces (these are your software packages, such as FSL, SPM and so on).

Next, you define nodes (these are the particular processes performed by the interfaces, like spatial smoothing, slice timing correction and so on).

As a next step, you define inputs for your nodes (for instance, the volume that you want to perform the spatial smoothing on).

Lastly, you can connect nodes together to form a workflow (for instance, I may want to perform slice timing correction with FSL and then spatial smoothing with SPM).

Finally, you run the workflow.

## A simple Nipype script.

Its probably useful to give an example of a Nipype script. 

![alt text](https://i.imgbox.com/baD5T4K1.png "Title")

Here I have given a very simple one, which is just 10 lines of code.

In this first section, I import the interfaces. In this case, I import dicom to nifti , which is a file converter and I also import fsl

Next, I define some nodes. I import the dicom to nifti converter from the dicom to nifti interface and I import a function that reorients volumes from the fsl interface

In this next section, I provide some inputs to the nodes, such as where the DICOM files can be found.

Next, I connect the nodes together, so that once my data are converted by dicom to nifti, they will be reoriented by fsl

Finally I run the workflow.

Nipype then produces several outputs:

![alt text](https://i.imgbox.com/IrZkdgNV.png "Title")

It produces an intuitively appealing graph, that displays the workflow.

Nipype then produces a folder for each node. /CONVERTED contains the converted nifti file and /REORIENTED contains the reoriented and converted nifti file.

## Why Python/ Nipype? 

It’s now probably worth discussing the reasons why Python is an appropriate engine for fMRI analysis.

Firstly, Python is free.

Python is also a default installation on many modern computers – it doesn’t need to be downloaded or installed in many cases.

Next, it is obviously important for our practices to be future-proof. The future looks quite bright for python as it is becoming increasingly popular. Recently, google search queries for ‘learn python’ have overtaken those for 'learn java', 'learn C' and 'learn javascript'. Python is also the most popular introductory programming language at many Universities.

Python is also a very intuitive, easy to learn language. We have already seen a very simple script early on and Python programs are on average 3-5 times shorter than the equivalent java program.

In Nipype, all algorithms from all software packages are treated in exactly the same way – as nodes with a series of inputs and outputs. This greatly simplifies the learning curve because instead of having to learn FSL, SPM, AFNI, Freesurfer and so on we only have to learn one thing - Python.

Lastly, it is very easy to share Python scripts with other researchers.
