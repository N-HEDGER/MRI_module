# Hardware

## fMRI Virtual Machine

![alt text](https://i.imgbox.com/GgMktKyo.png "Title")

### Specifications and requirements
The fMRI virtual machine is configured with *~4GB* of RAM, a virtual hard disk that will grow to **50GB** in size and shared networking.
It will require a **64 bit** operating system to run. A computer with at least *8GB* is recommended to run the machine.

### Details
| | | 
| --- | --- |
| **Operating system** | Linux/Ubuntu 16.04 "Xenial Xerus" |
| **Installed software** | Neurodebian, fsl, afni, mricron/dcm2nii, ANTs, anaconda, python 2.7 | 
***

### Installation instructions.

The software [VirtualBox](https://www.virtualbox.org/wiki/Downloads) emulates the hardware of a PC allowing you to run a second operating system 'in a window'of your personal computer.  

1. First of all, follow the installation instructions to install VirtualBox on your computer.
2. Next, download the fMRI virtual machine from [this address](https://drive.google.com/open?id=0B6MT4TSJ7f53VU1XcnhySUY2aDg) (this is a large file (around 10GB) and so may take quite a while to downloads).
3. Next, open VirtualBox and go to *file - import appliance* and select the .ova file you downloaded in step 2 (below).

![alt text](https://i.imgbox.com/OBhfqBwO.png "Title")

4. The fMRI virtual machine (fMRI_VM) should now appear in the left panel of the VirtualBox window (below).

![alt text](https://i.imgbox.com/4EYLQeKN.png "Title")

5. Double clicking on the virtual machine will boot it.
6. When prompted for a login (below), type 'fmri2016'.

![alt text](https://i.imgbox.com/tjKj9wg2.png "Title")


## Linux Machines




