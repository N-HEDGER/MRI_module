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
		outfilename=outfile.name
		print(os.path.abspath(outfilename))
		return os.path.abspath(outfilename)

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
	workflow.base_dir = EVENTFILES
	# Connect nodes
	workflow.connect(inputnode,'dir',plotter,'in_file')
	workflow.connect(inputnode,'dir',concat,'in_file')
	workflow.connect(inputnode,'max',plotter,'maxT')
	workflow.connect(concat,'outfile',outputnode,'out_file')
	workflow.connect(concat,'outfile',plotter2,'in_file')
	workflow.connect(inputnode,'max',plotter2,'maxT')
	workflow.write_graph(graph2use='exec')
	

	workflow.run()

	print "Node completed. Returning to intital directory\n"

	os.chdir(INITDIR)


#--- Goal of the function:
# Use AFNI 3Dinfo to get mean HRF within an ROI. Plot the HRF for each regressor

# Inputs:

# 1) BRIK of beta weights (output of FIRPIPE)
# 2) Binary masks (iterable - can be entered as a comma, seperated vector[mask1,mask2]) 

# Outputs:
# /ROISTATS .csv file of mean beta weight within the ROI defined by the mask.
# A plot is returned displaying the mean beta weights for the HRF within the ROI.

# Requires nipype, afni, numpy, matplotlib

#--- Details
# The values on the x axis correspond to the default values of the TENT command for FIR pipe (0,12,7)
# These are 7 linearly spaced values between 0 and 12 seconds from STIM onset


def ROIPARAMS():
	import nipype.pipeline.engine as pe
	import glob
	from nipype import Function
	import nipype.interfaces.utility as util
	import os
	import numpy as np
	from nipype.interfaces.utility import Merge
	from nipype.interfaces import afni as afni

	INITDIR=os.getcwd();

	BETAS=input('Please drag in the BRIK of beta weights\n')
	BETAS2=BETAS.strip('\'"')
	mask2=input('Please drag in the ROI mask\n')


	inputnode = pe.Node(interface=util.IdentityInterface(fields=['BETAS','MASKS']),name='inputspec')


	if type(mask2) == str:
		inputnode.inputs.MASKS=mask2
		NIFTIDIR=os.path.split(mask2)[0]
		os.chdir(mask2)
	elif type(mask2) == list:
		inputnode.iterables=([('MASKS',mask2)])
		NIFTIDIR=os.path.split(mask2[0])[0]
		os.chdir(NIFTIDIR)

	inputnode.inputs.BETAS=BETAS2


	ROIINFO=pe.Node(interface=afni.ROIStats(),name='ROISTATS')


	def PLOTTENTSINROI(in_file,maskname):
		import matplotlib.pyplot as plt
		import numpy as np
		import os
		my_data2 = np.loadtxt(fname=in_file,delimiter='\t',comments='!',usecols=(2,),skiprows=3)
		my_datalabels = np.genfromtxt(fname=in_file,delimiter='\t',comments='!',usecols=(1,),skip_header=3,dtype=None)
		mystr = []
		for instr in range(0,len(my_datalabels)):
			start=my_datalabels[instr].index('[')+1
			end=my_datalabels[instr].index('#')
			mystr.append(my_datalabels[instr][start:end])
		used = set()
		unique = [x for x in mystr if x not in used and (used.add(x) or True)]
		fig, ax = plt.subplots(figsize=(10, 10))
		st=np.linspace(0,len(my_data2)-(len(my_data2)/len(unique)),len(unique))
		from matplotlib.pyplot import cm 
		import numpy as np
		plt.style.use('ggplot')
		plt.tight_layout()
		title=os.path.split(maskname)[1]
		fig.suptitle(title)
		ax1=plt.subplot2grid((2,len(unique)),(0,0),colspan=len(unique))
		color=cm.rainbow(np.linspace(0,1,len(unique)))
		for lines in range(0,len(unique)):
			xax=np.linspace(1,(len(my_data2)/len(unique)),(len(my_data2)/len(unique)))
			print(lines)
			ax=plt.subplot2grid((2,len(unique)),(1,lines))
			ax1.plot(xax,my_data2[st[lines]:st[lines]+(len(my_data2)/len(unique))],c=color[lines])
			ax1.plot(xax,my_data2[st[lines]:st[lines]+(len(my_data2)/len(unique))],'*',c=color[lines])
			x=my_data2[st[lines]:st[lines]+(len(my_data2)/len(unique))]
			ax.set_ylim([min(my_data2),max(my_data2)])
			ax.set_xlim([min(xax),max(xax)])
			ax.set_title(unique[lines])
			ax.set_ylabel('Beta weight')
			ax.set_xlabel('Time from onset')
			ax.plot(xax, x, '--', linewidth=3,c=color[lines])
			ax.plot(xax, x, '*', linewidth=4,c=color[lines])
		plt.show()



	plotter = pe.Node(Function(input_names=['in_file','maskname'],output_names=['fig'],function=PLOTTENTSINROI),name='PLOTROI')


	workflow = pe.Workflow(name='ROISTATS')
	workflow.base_dir = os.getcwd()


	workflow.connect(inputnode,'BETAS',ROIINFO,'in_file')
	workflow.connect(inputnode,'MASKS',ROIINFO,'mask')
	workflow.connect(inputnode,'MASKS',plotter,'maskname')
	workflow.connect(ROIINFO,'stats',plotter,'in_file')


	workflow.write_graph(graph2use='exec')

	result=workflow.run()


	print "Node completed. Returning to intital directory\n"

	os.chdir(INITDIR)












