#--- Goal of the function:
# Use FSL and utility functions to perform level 1 analysis on example data

# Inputs:
# Pre-processed functional data (output of FUNCPIPE or equivalent)
# TR (s)
# High pass filter cutoff (s)
# Directory of 3 column event files

# Outputs:
# / FILM_GLS - z score images
# / MODEL - .png file of design matrix

# Requires fsl, nipype, nilearn, matplotlib

#--- Details
# Double gamma convolution
# 3 contrasts are specified. Main effect of task, Upright faces, Scrambled faces, Upright v scrambled faces. 
# z stats are plotted. 


def L1PIPE(): 

	# ---1) Import modules
	import nipype.interfaces.fsl as fsl 
	import nipype.pipeline.engine as pe
	import nipype.algorithms.modelgen as model
	import glob
	from nipype import Function
	import matplotlib
	import nipype.interfaces.utility as util
	import os


	#--- 2) Specify model node
	specify_model = pe.Node(interface=model.SpecifyModel(), name="SPECIFY_MODEL")
	specify_model.inputs.input_units = 'secs'

	runs=raw_input('Please drag in the pre-processsed functional data\n')
	runs2= runs.strip('\'"')

	NIFTIDIR=os.path.split(runs2)[0]

	specify_model.inputs.functional_runs = [runs2]
	specify_model.inputs.time_repetition = float(raw_input('Enter the TR (s)\n'))
	specify_model.inputs.high_pass_filter_cutoff = float(raw_input('Enter the High pass filter cutoff (s)\n'))
	EVENTFILES=raw_input('Please drag in the directory of 3 column event files')
	EVENTFILES2=EVENTFILES.strip('\'"')
	EVENTFILESLIST=glob.glob(EVENTFILES2 + '/*')
	specify_model.inputs.event_files=sorted(EVENTFILESLIST)


	#--- 3) Level 1 design node.
	Designer=pe.Node(interface=fsl.Level1Design(),name='DESIGN')
	Designer.inputs.interscan_interval = float(specify_model.inputs.time_repetition)
	Designer.inputs.bases = {'dgamma':{'derivs': False}}
	Designer.inputs.model_serial_correlations=bool(0)

	#--- 4) Make some contrasts
	cont1=('Task', 'T', ['B1INVFEAR.RUN001', 'B1INVINVFEAR.RUN001', 'B1INVINVNEUT.RUN001', 'B1INVNEUT.RUN001', 'B1SCFEAR.RUN001', 'B1SCNEUT.RUN001', 'B1UPFEAR.RUN001', 'B1UPINVFEAR.RUN001', 'B1UPINVNEUT.RUN001', 'B1UPNEUT.RUN001'], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
	cont2=('Up', 'T', ['B1INVFEAR.RUN001', 'B1INVINVFEAR.RUN001', 'B1INVINVNEUT.RUN001', 'B1INVNEUT.RUN001', 'B1SCFEAR.RUN001', 'B1SCNEUT.RUN001', 'B1UPFEAR.RUN001', 'B1UPINVFEAR.RUN001', 'B1UPINVNEUT.RUN001', 'B1UPNEUT.RUN001'], [0, 0, 0, 0, 0, 0, 1, 0, 0, 1])
	cont3=('SC', 'T', ['B1INVFEAR.RUN001', 'B1INVINVFEAR.RUN001', 'B1INVINVNEUT.RUN001', 'B1INVNEUT.RUN001', 'B1SCFEAR.RUN001', 'B1SCNEUT.RUN001', 'B1UPFEAR.RUN001', 'B1UPINVFEAR.RUN001', 'B1UPINVNEUT.RUN001', 'B1UPNEUT.RUN001'], [0, 0, 0, 0, 1, 1, 0, 0, 0, 0])
	cont4=('UpvSC', 'T', ['B1INVFEAR.RUN001', 'B1INVINVFEAR.RUN001', 'B1INVINVNEUT.RUN001', 'B1INVNEUT.RUN001', 'B1SCFEAR.RUN001', 'B1SCNEUT.RUN001', 'B1UPFEAR.RUN001', 'B1UPINVFEAR.RUN001', 'B1UPINVNEUT.RUN001', 'B1UPNEUT.RUN001'], [0, 0, 0, 0, -1, -1, 1, 0, 0, 1])
	Designer.inputs.contrasts=[cont1, cont2, cont3, cont4]

	#--- 5) FSL model node
	Model=pe.Node(interface=fsl.FEATModel(),name='FEATMODEL')

	#--- 6) FILM GSL node
	fgls=pe.Node(interface=fsl.FILMGLS(),name='FILM_GLS')
	fgls.inputs.in_file=runs2

	#--- 7) outputnode for the design image (gets binned otherwise)
	outputnode = pe.Node(interface=util.IdentityInterface(fields=['im','cope','varcope','dof','resid','params','sigmas']),name='outputnode')


	#--- 8)  Plotting node
	def plot(in_file):
		from nilearn import image
		from nilearn import plotting
		import matplotlib
		display=plotting.plot_stat_map(stat_map_img = in_file, display_mode='z', cut_coords=10, threshold=float(0))
		matplotlib.pyplot.show()



	plotter=pe.MapNode(Function(input_names=['in_file'],output_names='display',function=plot),iterfield=['in_file'],name='PLOTTER')

	workflow = pe.Workflow(name='L1PIPE')
	

	workflow.connect(specify_model,'session_info',Designer,'session_info')
	workflow.connect(Designer,'fsf_files',Model,'fsf_file')
	workflow.connect(Designer,'ev_files',Model,'ev_files')
	workflow.connect(Model,'design_file',fgls,'design_file')
	workflow.connect(Model,'con_file',fgls,'tcon_file')
	workflow.connect(Model,'design_image',outputnode,'im')
	
	# Feed the z stats to the plotter.
	workflow.connect(fgls,'zstats',plotter,'in_file')
	workflow.connect(fgls,'copes',outputnode,'cope')
	workflow.connect(fgls,'varcopes',outputnode,'varcope')
	workflow.connect(fgls,'dof_file',outputnode,'dof')
	workflow.connect(fgls,'residual4d',outputnode,'resid')
	workflow.connect(fgls,'param_estimates',outputnode,'params')
	workflow.connect(fgls,'sigmasquareds',outputnode,'sigmas')
	




	workflow.base_dir = NIFTIDIR
	workflow.write_graph(graph2use='exec')
	workflow.run()



#--- Goal of the function:
# Use AFNI and utility functions to obtain TENT functions for a set of regressors

# Inputs:
# Pre-processed functional data (output of FUNCPIPE or equivalent)
# Directory of 3 column event files

# Outputs:
# / AFNIFYTXT - Text files converted to AFNI format
# / AFNIFYCMD - 1) .jpg file of design matrix 2) 1D file of design matrix 3) .BRIK - beta weights for the TENT functions.
# The contents (3Dinfo) of the BRIK is printed to the ipython terminal.

# Requires afni, nipype, nilearn, matplotlib

#  --- Details
# ANFI adds a constant term and linear term to the model
# The output data is stored in afni format and nii format.


def FIRIPE(): 
	# ---1) Import modules
	import nipype.pipeline.engine as pe
	import glob
	from nipype import Function
	import nipype.interfaces.utility as util
	import os
	import numpy as np
	from nipype.interfaces.utility import Merge

	# ---2) Get event files and functional data
	EVENTFILES=input('Please drag in the directory of 3 column event files\n')
	EVENTFILES2=EVENTFILES.strip('\'"')
	func=input('Please drag in the pre-processed functional data\n')
	func2=func.strip('\'"')
	NIFTIDIR=os.path.split(func2)[0]

	# ---3) Setup input node
	inputnode = pe.Node(interface=util.IdentityInterface(fields=['eventdir','func']),name='inputspec')

	inputnode.inputs.functional=func2
	inputnode.inputs.eventdir=EVENTFILES2


	# ---4) Setup function for converting FSL files to AFNI format.
	def fsl2afni(dir):
		import os
		import numpy as np
		import glob
		infiles=glob.glob(dir + '/*')
		infiles=sorted(infiles)
		filename = []
		for infile in range(0,len(infiles)):
			print (infiles[infile])
			with open(infiles[infile],'r') as f:
		  		LoL=[x.strip().split('\t') for x in f]
		  	arr=np.array(LoL)
		  	onsets=arr[:,0]
		  	int_lst_onsets = np.transpose([int(float(x)) for x in onsets])
		  	print (int_lst_onsets)
		  	filename.append(os.getcwd()+'/'+os.path.splitext(os.path.split(infiles[infile])[1])[0]+'_afni.txt')
		  	np.savetxt(filename[infile],int_lst_onsets,newline=" ")
	  	return filename
		

	afnifytxt=pe.Node(Function(input_names=['dir'],output_names='filename',function=fsl2afni),name='AFNIFYTXT')


	# ---4) Now use all this information to pass the 3Ddeconvolve command to the command line.

	def afnistring(filenames,func):
		import os
		afnistr = []
		for infile in range(0,len(filenames)):
			afnistr.append('-stim_times' + ' ' + str(infile+1) + ' ' + filenames[infile] + ' ' + "'TENT(0,12,7)'" + ' ' + '-stim_label' + ' ' + str(infile+1) + ' ' + os.path.splitext(os.path.split(filenames[infile])[1])[0])
			print (afnistr[infile])
		afnicmd=' '.join(afnistr)
		precmd='3dDeconvolve -input' + ' ' + func + ' ' '-bucket' + ' ' + 'output.nii' + ' ' + '-num_stimts' + ' ' + str(len(filenames))
		acmd= '-xjpeg X.jpg -fout -tout -bout -x1D matrix -cbucket TENTs'
		cmd=' '.join([precmd,afnicmd])
		cmd2=' '.join([cmd,acmd])
		os.system(cmd2)
		os.system('3Dinfo -verb TENTS')
		return cmd2


	afnifycmd=pe.Node(Function(input_names=['filenames','func'],output_names='cmd2',function=afnistring),name='AFNIFYCMD')


	workflow = pe.Workflow(name='FIRPIPE')
	workflow.base_dir = NIFTIDIR
	workflow.write_graph(graph2use='exec')

	workflow.connect(inputnode,'eventdir',afnifytxt,'dir')
	workflow.connect(afnifytxt,'filename',afnifycmd,'filenames')
	workflow.connect(inputnode,'functional',afnifycmd,'func')

	# Change the config, otherwise all the afni outputs are deleted. 
	workflow.config['execution'] = {'remove_unnecessary_outputs': 'False'}

	workflow.run()

	