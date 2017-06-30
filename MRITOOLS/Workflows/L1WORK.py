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

	runs=raw_input('Please drag in the directory of pre-processsed functional data\n')
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
	Designer.inputs.bases = {'dgamma':{'derivs': True}}
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
	outputnode = pe.Node(interface=util.IdentityInterface(fields=['im']),name='outputnode')


	#--- 8)  Plotting node
	def plot(in_file):
		from nilearn import image
		from nilearn import plotting
		import matplotlib
		niftifiledim=len(image.load_img(in_file).shape)
		display=plotting.plot_stat_map(stat_map_img=in_file,black_bg=bool(1),bg_img=False,display_mode='z',cut_coords=10,threshold=float(0))
		matplotlib.pyplot.show()
		return niftifiledim


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


	workflow.base_dir = NIFTIDIR
	workflow.write_graph(graph2use='exec')
	workflow.run()

	