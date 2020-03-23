# Set up an experiment and execute it from the command line

from collections import OrderedDict
import os

from experiment import Experiment
from generative_processes import intuitive_theory
from human import Human
from utils import check_int
from utils import library_variables
from utils import Variable


# Set up the basics of an experiment
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


print('This is supposed to be an interactive guide to setting up and running an experiment')

name_experiment = input('What is the name of your experiment? (string): ')
num_conditions = input('How many conditions does the experiment have? (0-10): ')
num_conditions = check_int(num_conditions,0,10)

variables_input = input(
    'What variables should be manipulated? Enter their abbreviations (in brackets) with spaces inbetween. A possible list follows\n'
    'success - (success)\n'
    'task importance - (TI)\n'
    'self-awareness - (SA)\n'
    'probability of improvement - (PI)\n'
    'number of samples in experiment - (L)\n'
    'skill - (skill)\n'
    'effort - (effort)\n'
    'external - (external)\n'
    'luck - (luck)\n'
    'E.g. SI TI PI'
    'Any variable that is not set is sampled from a default distribution\n'
    'The possible values for the variables will be displayed at choosing time\n'
    ': ')

# Create a list of variables

variables_input = variables_input.strip().split(" ")

# Set up an experiment
new_experiment = Experiment(name_experiment,human,variables)

# Register the conditions
for i in range(num_conditions):
    condition = {}
    name_condition = input(f'What is the name of the condition {i} (string) :')
    condition['name'] = name_condition
    num_participant = input('What is the number of participants (int) :')
    num_participant = check_int(num_participant,0)
    condition['N'] = num_participant
    for var in variables_input:
        var_value = input(f'Value of {var} in condition: {condition["name"]} - onlroy high/low possible [h/l]: ')
        try:
            condition[var] = library_variables[var][var_value]
        except KeyError:
            print(f'{var_value} is not a valid entry')
            exit()

    print(condition)
    new_experiment.register_condition(condition)


## Create a summary of the experiment

new_experiment.summary()

# Run it

yes = input('Do you want to run the experiment [y/n]: ')

valid_answer = True

while valid_answer:
    if yes=='y':
        new_experiment.run()
        new_experiment.plot_result(False,directory)
        valid_answer=False
    elif yes=='n':
        valid_answer=False
        pass
    else:
        print('This was not a valid answer')
        yes = input('Next try: ')


