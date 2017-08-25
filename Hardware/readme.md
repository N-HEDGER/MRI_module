# Hardware

## fMRI Virtual Machine

![alt text](https://i.imgbox.com/GgMktKyo.png "Title")

### Specifications and requirements
The fMRI virtual machine is configured with *~4GB* of RAM, a virtual hard disk that will grow to **50GB** in size and shared networking.
It will require a **64 bit** operating system to run. A computer with at least *4GB* RAM is recommended to run the machine.

### Details
| | | 
| --- | --- |
| **Operating system** | Linux/Ubuntu 16.04 "Xenial Xerus" |
| **Installed software** | Neurodebian, fsl (v 5.0.9), afni (v Debian-16.2.07), mricron/dcm2nii (v Debian 04.08.2014), ANTs (v 2.1.0), anaconda, python (v 2.7) |

***

### Installation instructions.

The software [VirtualBox](https://www.virtualbox.org/wiki/Downloads) emulates the hardware of a PC, allowing you to run a second operating system 'in a window' of your personal computer.  

1. First of all, follow the installation instructions on the VirtualBox website to install VirtualBox on your computer.

2. Next, download the fMRI virtual machine from [this address](https://drive.google.com/open?id=0B6MT4TSJ7f53UFN6UndmWFJSdGc) (this is a large file (around 10GB) and so may take quite a while to download).

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

* By default, 1.9 GB of memory will allocated to the machine. You may want to allocate more (or less) depending on the memory specs of your personal computer. 

* To do this, before booting the machine, highlight it and navigate to *settings - system*. You will then be given the option to alter the memory that is allocated to the machine via a slider (below). It is not recommended that you allocate any more memory than is indicated by the green region of the slider.


![alt text](https://i.imgbox.com/VBmAJF9G.png "Title")


* In general, anything below 1GB RAM is likely to cause the VM to run very slowly.

### Adding additional storage to the VM.

* For practical reasons, the VM hard disk will only grow to 50GB in size. This is fine for experimenting with a small amount of data but may prove insufficient for large scale projects.

* It is straightforward to add additional virtual hard disks to the machine. You are only limited by the storage space available on the host machine.

1. When the machine is powered off, right click on the VM in the virtualbox window and navigate to *settings-storage*.
2. In the 'storage tree', click on Controller: SATA and press the floppy disk icon with a green plus symbol.
3. Select *add hard disk*
4. Select *VHD*
5. Select *fixed size*
6. Allocate the storage space you require on the new disk.
7. After the disk has been created it will appear as an instance in the storage tree.
8. Highlight it and check the 'Hot pluggable' option.
9. Click ok to save these new settings.
10. Now boot the VM and log on. 
11. Use the *search your computer* widget in the side bar to search for an application called *Disks*. Open this application.
12. Select your newly created drive. Make very sure that you are selecting the new drive, or you could delete your existing data with the following steps. 
12. Click the gear icon (under Volumes), select *Format Partition*, make your selections (the defaults are fine), name the drive, and click *Format*. When prompted, click Format a second time, and the drive will be formatted and ready to use.
13. When you next open the file explorer, the new drive will appear under the main 'Computer' hard disk.


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





