#--- Goal of the function:
# Print the header of a nifti file and output some text files with the important info

# Inputs:

# 1) Nifti file ((iterable))

# Outputs:
# AFFINE
# SHAPE 
# VOXELSIZE
# TR

# Requires nipype, nilearn, matplotlib



def INSPECTOR():
	import nipype.pipeline.engine as pe
	import matplotlib
	import os
	os.system('clear')
	from glob import glob
	from nilearn import plotting
	from nilearn import image
	from nipype.interfaces.utility import Function
	import nipype.interfaces.utility as util 
	import nipype.interfaces.fsl.utils as fsl


	INITDIR=os.getcwd();

	#--- 3) Prompt user for directory containing DICOM FILES

	NIFTIFILE=input('Please drag in the functional file you want to inspect')

	inputnode = pe.Node(interface=util.IdentityInterface(fields=['file']),name='inputspec')


	if type(NIFTIFILE) == str:
		inputnode.inputs.file=NIFTIFILE
		NIFTIDIR=os.path.split(NIFTIFILE)[0]
		os.chdir(NIFTIDIR)
	elif type(NIFTIFILE) == list:
		inputnode.iterables=([('file',NIFTIFILE)])
		NIFTIDIR=os.path.split(NIFTIFILE[0])[0]
		os.chdir(NIFTIDIR)


	def getinfo(in_file):
		import numpy as np
		import nibabel as nib
		from nilearn import image
		import os
		import pandas as pd
		nifti = nib.load(in_file)
		SHAPE= image.load_img(in_file).shape
		AFFINE = nifti.affine
		VOXSIZE = nifti.header['pixdim'][1:4]
		TR = (nifti.header['pixdim'][4:5])




		filename1=os.getcwd()+'/'+'AFFINE_info.txt'
		filename2=os.getcwd()+'/'+'SHAPE_info.txt'
		filename3=os.getcwd()+'/'+'VOXSIZE_info.txt'
		filename4=os.getcwd()+'/'+'TR_info.txt'
		np.savetxt(filename1,AFFINE,newline=" ")
		np.savetxt(filename2,SHAPE,newline=" ")
		np.savetxt(filename3,VOXSIZE,newline=" ")
		np.savetxt(filename4,TR,newline=" ")
		print(nifti.header)
		return filename1,filename2,filename3,filename4



	GETINFO = pe.Node(Function(input_names=['in_file'],output_names=['filename1','filename2','filename3','filename4'],function=getinfo),name='GETINFO')

	workflow = pe.Workflow(name='INSPECT')
	workflow.base_dir = os.getcwd()
	workflow.connect(inputnode,'file',GETINFO,'in_file')
	result=workflow.run()
	print "Node completed. Returning to intital directory\n"

	os.chdir(INITDIR)






def fprintf(stream, format_spec, *args):
	stream.write(format_spec % args)


def findniftis(FOLDER,ext):
    def fprintf(stream, format_spec, *args):
        stream.write(format_spec % args)
    import os
    import sys
    niftilist=list()
    for file in os.listdir(FOLDER):
        if file.endswith(ext):
            niftilist.append(FOLDER+"/"+file)
    fprintf(sys.stdout, "Found %d nifti files", len(niftilist))
    return(sorted(niftilist))


def getinfolist(niftilist):
    import numpy as np
    import nibabel as nib
    from nilearn import image
    import os
    import pandas as pd
    
    
    b=list()
    for file in niftilist :
        nifti = nib.load(file)
        SHAPE= image.load_img(file).shape
        VOXSIZE = nifti.header['pixdim'][1:4]
        TR = (nifti.header['pixdim'][4:5])
        VOXFRAME=pd.DataFrame(VOXSIZE)
        VOXFRAME=VOXFRAME.T
        SHAPEFRAME=pd.DataFrame(SHAPE)
        SHAPEFRAME=SHAPEFRAME.T
        TR = (nifti.header['pixdim'][4:5])[0]
        VOXFRAME.columns=['VoxsizeX','VoxsizeY','VoxsizeZ']

        if len(SHAPE)==4:
        	SHAPEFRAME.columns=['ShapeX','ShapeY','ShapeZ','Volumes']
        elif len(SHAPE)==3:
       		SHAPEFRAME.columns=['ShapeX','ShapeY','ShapeZ']
        CFRAMEi=pd.concat([VOXFRAME,SHAPEFRAME],axis=1)
        CFRAMEi['TR'] = TR 
        CFRAMEi['FILE'] = os.path.split(file)[1]
     
        b.append(CFRAMEi)
    CFRAME=pd.concat(b)
    return CFRAME





