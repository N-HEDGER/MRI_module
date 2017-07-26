# Hardware

## fMRI Virtual Machine

![alt text](https://i.imgbox.com/GgMktKyo.png "Title")

### Specifications and requirements
The fMRI virtual machine is configured with *~4GB* of RAM, a virtual hard disk that will grow to **50GB** in size and shared networking.
It will require a **64 bit** operating system to run. A computer with at least *8GB* RAM is recommended to run the machine.

### Details
| | | 
| --- | --- |
| **Operating system** | Linux/Ubuntu 16.04 "Xenial Xerus" |
| **Installed software** | Neurodebian, fsl (v 5.0.9), afni (v Debian-16.2.07), mricron/dcm2nii (v Debian 04.08.2014), ANTs (v 2.1.0), anaconda, python (v 2.7) |

***

### Installation instructions.

The software [VirtualBox](https://www.virtualbox.org/wiki/Downloads) emulates the hardware of a PC, allowing you to run a second operating system 'in a window' of your personal computer.  

1. First of all, follow the installation instructions on the VirtualBox website to install VirtualBox on your computer.

2. Next, download the fMRI virtual machine from [this address](https://drive.google.com/open?id=0B6MT4TSJ7f53VU1XcnhySUY2aDg) (this is a large file (around 10GB) and so may take quite a while to download).

3. Next, open the VirtualBox application and go to *file - import appliance*. Select the .ova file you downloaded in step 2 (below) and continue with all the default options.


![alt text](https://i.imgbox.com/OBhfqBwO.png "Title")


4. After the import has completed, The fMRI virtual machine (fMRI_VM) should now appear in the left panel of the VirtualBox window (below).


![alt text](https://i.imgbox.com/4EYLQeKN.png "Title")


5. Double clicking on the fMRI_VM will boot it. Wait a short while for the login screen to appear.

6. When prompted for a login (below), type 'fmri2016'.

7. You should now be presented with the Ubuntu Desktop environment!


![alt text](https://i.imgbox.com/tjKj9wg2.png "Title")


8. You can shut down the machine at any time by simply closing the window. 

### Configuring the memory allocated to the VM.

* By default, 4GB of memory will allocated to the machine. You may want to allocate more (or less) depending on the memory specs of your personal computer. 

* To do this, before booting the machine, highlight it and navigate to *settings - system*. You will then be given the option to alter the memory that is allocated to the machine via a slider (below). It is not recommended that you allocate any more memory than is indicated by the green region of the slider.


![alt text](https://i.imgbox.com/VBmAJF9G.png "Title")


* In general, anything below 2GB RAM is likely to cause the VM to run very slowly. I wouldn't recommend anything below 4GB. 

### Maintaining the python environment

* A python environment (mritool) is activated by deafult via [anaconda](https://www.continuum.io/downloads). This has a number of neuroimaging packages installed (nipype, nilearn, nibabel, MRITOOLS itself).

* [Here](https://drive.google.com/open?id=0B6MT4TSJ7f53cG4xRTNWV2hDRXM) is a list of modules that are installed in this environment and their versions. You can create this list yourself via entering the command: 'conda list' into the terminal.

* If you want to install new packages, or update existing ones, you can do this via entering the following into the terminal: 

```
pip install packagename
```

or 

```
pip install --upgrade packagename
```

* The MRITOOLS module itself can be updated via:

```
updateMRITOOLS
```





