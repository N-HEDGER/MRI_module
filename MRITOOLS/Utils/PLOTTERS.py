#--- Goal of the function:
# Use nilearn to convolve cannonica HRF with stimulus event onset files

# Inputs:

# 1) Directory of 3 column event files
# 2) Length of the run in seconds.

# Outputs:
# Plot of each regressor
# Plot of all regressors

# Requires nipype, nilearn, matplotlib

#--- Details
# Uses the Glover hrf (response to 1s auditory stimulus)




def PLOTHRFS():
	# ---1) Import modules
	import nipype.pipeline.engine as pe
	import nipype.algorithms.modelgen as model
	import glob
	from nipype import Function
	import matplotlib
	import nipype.interfaces.utility as util
	import os
	import numpy as np
	import matplotlib.pyplot as plt
	from nipy.modalities.fmri import hrf
	from nipy.modalities.fmri.utils import T, lambdify_t
	from nipype.interfaces.utility import Merge

	INITDIR=os.getcwd();

	EVENTFILES=input('Please drag in the directory of 3 column event files')
	maxT=raw_input('Please give the length of the run in seconds')
	EVENTFILES2=EVENTFILES.strip('\'"')
	EVENTFILESLIST=glob.glob(EVENTFILES2 + '/*')

	inputnode = pe.Node(interface=util.IdentityInterface(fields=['dir','max']),name='inputspec')

	inputnode.inputs.dir=EVENTFILESLIST
	inputnode.inputs.max=int(maxT)



	# Define some functions

	# Plot the regressors for each text file
	def hrfplot(in_file,maxT):
		import numpy as np
		import matplotlib.pyplot as plt
		from pylab import figure, axes, pie, title, show
		from nipy.modalities.fmri import hrf
		from nipy.modalities.fmri.utils import T, lambdify_t
		import csv
		with open(in_file) as f:
			reader = csv.reader(f, delimiter=str("\t"))
			d = list(reader)
		mat=np.array(d)
		onsets=mat[:,0]
		int_lst_onsets = [int(float(x)) for x in onsets]
		glover = hrf.glover(T)
		tb=int_lst_onsets
		bb = 1
		nb = bb * sum([glover.subs(T, T - t) for t in tb])
		nbv = lambdify_t(nb)
		t = np.linspace(0,float(maxT),10000)
		plt.plot(t, nbv(t), c='b', label=in_file)
		for t in tb:
			plt.plot([t,t],[0,bb*0.1],c='r')
		plt.legend()
		plt.show()



	# Make a big text file combining all event onsets
	def getoveralll(in_file):
		import os
		with open(os.getcwd()+'/overall.txt', 'w') as outfile:
			for fname in in_file:
				with open(fname) as infile:
					outfile.write(infile.read())
		outfile=outfile.name
		return os.path.abspath(outfile)

	# Plot the overall regressor
	def hrfplot2(in_file,maxT):
		import numpy as np
		import matplotlib.pyplot as plt
		from pylab import figure, axes, pie, title, show
		from nipy.modalities.fmri import hrf
		from nipy.modalities.fmri.utils import T, lambdify_t
		import csv
		with open(in_file) as f:
			reader = csv.reader(f, delimiter=str("\t"))
			d = list(reader)
		mat=np.array(d)
		onsets=mat[:,0]
		int_lst_onsets = [int(float(x)) for x in onsets]
		int_lst_onsets.sort()
		glover = hrf.glover(T)
		tb=int_lst_onsets
		bb = 1
		nb = bb * sum([glover.subs(T, T - t) for t in tb])
		nbv = lambdify_t(nb)
		t = np.linspace(0,float(maxT),10000)
		plt.plot(t, nbv(t), c='b', label=in_file)
		for t in tb:
			plt.plot([t,t],[0,bb*0.1],c='r')
		plt.legend()
		plt.show()


	# Create utility nodes
	plotter=pe.MapNode(Function(input_names=['in_file','maxT'],output_names='bb',function=hrfplot),iterfield=['in_file'],name='PLOTTER')

	concat=pe.Node(Function(input_names=['in_file'],output_names='outfile',function=getoveralll),name='CONCAT')

	plotter2=pe.Node(Function(input_names=['in_file','maxT'],output_names='bb',function=hrfplot2),name='PLOTTER2')

	outputnode = pe.Node(interface=util.IdentityInterface(fields=['out_file']),name='outputnode')

	workflow = pe.Workflow(name='PLOTHRF')

	# Connect nodes
	workflow.connect(inputnode,'dir',plotter,'in_file')
	workflow.connect(inputnode,'dir',concat,'in_file')
	workflow.connect(inputnode,'max',plotter,'maxT')
	workflow.connect(concat,'outfile',outputnode,'out_file')
	workflow.connect(concat,'outfile',plotter2,'in_file')
	workflow.connect(inputnode,'max',plotter2,'maxT')
	workflow.write_graph(graph2use='exec')
	workflow.base_dir = EVENTFILES

	workflow.run()

	print "Node completed. Returning to intital directory\n"

	os.chdir(INITDIR)


















