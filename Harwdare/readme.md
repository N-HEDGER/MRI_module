# Hardware

## Linux Machines

## fMRI Virtual Machine

### Specifications and requirements
The fMRI virtual machine is configured with *2GB* of RAM, a virtual hard disk that will grow to **50GB** in size and shared networking.
It will require a **64 bit** operating system to run. You will need a system with at least **4GB** to run the machine and *8GB* is recommended.

### Details
| | | 
| --- | --- |
| **Operating system** | Linux/Ubuntu 16.04 "Xenial Xerus" |
| **Installed software** | Neurodebian, fsl, afni, mricron/dcm2nii, anaconda, python 2.7 | 
***

### Installation instructions

The software [VirtualBox](https://www.virtualbox.org/wiki/Downloads) emulates the hardware of a PC allowing you to run a second operating system 'in a window'.  

1. First of all, follow the installation instructions to install VirtualBox on your computer.
2. Next, download the fMRI virtual machine from this address (this is a large file and so may take quite a while).
3. Next, open VirtualBox and go to *file - import appliance* and select the .ova file you downloaded in 2.
4. The fMRI virtual machine should now appear in the left panel of the VirtualBox window.
5. Double clicking on the virtual machine will boot it.
6. When prompted for a login, type 'fmri2016'




