
import os

from collections import OrderedDict



from experiment import Experiment
from generative_processes import intuitive_theory
from human import Human
from utils import Variable
# Simulation of a number of experiments on the self-serving bias

####################################################################################################################
'''
General Setup 
'''
####################################################################################################################



variables = {}

default = OrderedDict()
default['mean'] = 0
default['std'] = 1
positive_bias = OrderedDict()
positive_bias['mean'] = 0.5
positive_bias['std'] = 1
negative_bias = OrderedDict()
negative_bias['mean'] = -0.5
negative_bias['std'] = 1

# Experimental parameters

# Task importance
variables['TI'] = Variable(1,'TI','fixed',{'fixed':1})

# Controlled parameters
variables['SA'] = Variable(0,'SA','Normal',positive_bias)
variables['PI'] = Variable(0,'PI','Normal',negative_bias)
variables['success'] = 0

# IT Process parameters
variables['skill'] = Variable(1,'skill','Normal',default)
variables['effort'] = Variable(1,'effort','Normal',default)
variables['external'] = Variable(0,'external','Normal',default)
variables['luck'] = Variable(0,'luck','Normal',default)

# Inferencee parameters
variables['L']=100
variables['f']={'mean':lambda x:x,'2ndMoment':lambda x:x**2}


intuitive_theory_params = ['skill','effort','external','luck']
self_concept = ['skill','effort']
relevance = ['TI']
inference_params = ['L']

human = Human(self_concept,relevance,intuitive_theory_params,intuitive_theory,inference_params)

# Create a directory to save the plots in
directory = os.path.join(os.getcwd(),'plots')
# Check whether directory exists, if not create it
if not os.path.exists(directory):
    os.makedirs(directory)

####################################################################################################################
'''
DUAL PROCESS THEORY - https://psycnet.apa.org/record/2001-05824-004
'''
####################################################################################################################




ExperimentDP = Experiment('Duval & Silvia - Simulation',human,variables)

condition1 = {'N':10,'name':'PI0SA0',
              'SA':Variable(0,'SA','fixed',{'fixed':0}),
              'PI':Variable(0,'PI','fixed',{'fixed':0}),
              'success':0}
condition2 = {'N':10,'name':'PI0SA1',
              'SA':Variable(0,'SA','fixed',{'fixed':1}),
              'PI':Variable(0,'PI','fixed',{'fixed':0}),
              'success':0}
condition3 = {'N':10,'name':'PI1SA0',
              'SA':Variable(0,'SA','fixed',{'fixed':0}),
              'PI':Variable(0,'PI','fixed',{'fixed':1}),
              'success':0}
condition4 = {'N':10,'name':'PI1SA1',
              'SA':Variable(0,'SA','fixed',{'fixed':1}),
              'PI':Variable(0,'PI','fixed',{'fixed':1}),
              'success':0}

ExperimentDP.register_condition(condition1)
ExperimentDP.register_condition(condition2)
ExperimentDP.register_condition(condition3)
ExperimentDP.register_condition(condition4)

ExperimentDP.run()
directory = os.path.join(os.getcwd(),'plots')
# Check whether directory exists, if not create it
if not os.path.exists(directory):
    os.makedirs(directory)
ExperimentDP.plot_result(False,directory)

####################################################################################################################
'''
Testing for a main effect of task importance as was shown in - https://journals.sagepub.com/doi/abs/10.1037/1089-2680.3.1.23

Task importance should increase the self-serving-bias. 
'''
####################################################################################################################
condition1 = {'N':100,'name':'HighTI',
              'TI':Variable(0,'SA','fixed',{'fixed':4}),
              'success':0}
condition2 = {'N':100,'name':'LowTI',
              'TI':Variable(0,'SA','fixed',{'fixed':-1}),
              'success':0}

ExperimentTI = Experiment('Effect of Task Importance',human,variables)

ExperimentTI.register_condition(condition1)
ExperimentTI.register_condition(condition2)

ExperimentTI.run()
ExperimentTI.plot_result(False,directory)


####################################################################################################################
'''
Testing the effect of cognitive load: 
'''
####################################################################################################################

condition1 = {'N':100,'name':'Load','SA':Variable(0,'SA','fixed',{'fixed':0}),'success':0}
condition2 = {'N':100,'name':'No-Load','SA':Variable(0,'SA','fixed',{'fixed':1}),'success':0}

ExperimentCL = Experiment('Effect of Cognitive Load',human,variables)

ExperimentCL.register_condition(condition1)
ExperimentCL.register_condition(condition2)

ExperimentCL.run()
ExperimentCL.plot_result(False,directory)

####################################################################################################################
'''
Main effect of self-worth: 
'''
####################################################################################################################

new_experiment = Experiment('role of self-worth',human,variables)

low_param = {'mean':-1,'std':1}
high_param = {'mean':1,'std':1}

condition1 = {'name': 'high self-worth','N':100,'skill':Variable(1,'skill','Normal',high_param),'effort':Variable(1,'effort','Normal',high_param)}
condition2 = {'name': 'low self-worth','N':100,'skill':Variable(1,'skill','Normal',low_param),'effort':Variable(1,'effort','Normal',low_param)}

new_experiment.register_condition(condition1)
new_experiment.register_condition(condition2)

new_experiment.run()
new_experiment.plot_result(False,directory)