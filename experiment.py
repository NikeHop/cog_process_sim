
import os

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

class Experiment(object):
    '''
    Class to support simulating an experiment

    A list of experimental conditions is kept. The experimental conditions are described
    by a setting of the variables in the variables dictionary, a number of participants in each
    experimental group and a name for the condition.

    The experiment can be run and the results are plotted
    '''

    def __init__(self, name, human, variables):
        '''
        :param name: (string) Name of the experiment
        :param human: (Human) Human class which
        :param variables: (dict) a dictionary that has as keys variable names and as values Variable objects.
                                 the same variables are shared across conditions just with different values.
                                 The values that are distinct for the experimental group are registered as conditions
        '''

        self.name = name
        self.conditions = []
        self.n_conditions = 0
        self.human = human
        self.variables = variables


    def register_condition(self, condition):
        '''

        :param condition: (dict) contains a description of the experimental condition
                                 'N': Number of participants,
                                 'name': Name of the condition,
                                 variables that are manipulated e.g.
                                 'success': whether the outcome was a success or not
        '''

        self.n_conditions += 1
        self.conditions.append(condition)


    def run(self):
        '''
        Run each condition. Store the attribution results in a dictionary where the keys are the experiments names.
        The attribution results are a list of internal attribution scores.
        '''

        # Dictionary that stores results
        self.results = {}
        # Repeat for each condition
        print(f'Experiment {self.name} starts')
        for elem in self.conditions:
            attributions = []
            # set up a dictionary that contains the values of the variables in that condition
            vs = self.variables
            for var_name, var_value in elem.items():
                if var_name != 'N' and var_name != 'name':
                    vs[var_name] = var_value

            # Repeat the number of participants in a condition
            participants = tqdm(range(elem['N']),desc=f'Condition {elem["name"]}')
            for _ in participants:
                # Create a participant
                self.human.set_variables(vs, True)
                # Do inference and save it
                attributions.append(self.human.inference())
            # save results for that condition
            self.results[elem['name']] = attributions

    def z_transform(self, attr, mean, std):
        '''
        Given an array of values and a mean and std.
        Apply the z-score transformation.
        '''

        return (np.array(attr) - mean) / std

    def plot_result(self,plot,directory):
        '''

        :param plot: (bool) If true: additionally to saving the plot it also outputs it.
        :param directory: (string) The plot is saved to a folder called 'plot-results' in the current directory.

        :return z-values: (dict) Has experiment names as keys and the means of the z-values as values
        '''
        total = []
        for l in self.results.values():
            total += l

        # Calculate the mean and std of all values for z-transformation
        mean = np.mean(total)
        std = np.std(total)

        z_values = {name: np.mean(self.z_transform(value, mean, std)) for name, value in self.results.items()}
        z_std = {name: np.std(self.z_transform(value, mean, std))/np.sqrt(len(value)) for name, value in self.results.items()}

        # Plot or save the different values for each experimental group
        names = z_values.keys()
        means = z_values.values()
        x = np.arange(self.n_conditions)
        plt.clf()
        plt.errorbar(x,means,yerr=z_std.values(),fmt='o')
        plt.xticks(x, names)
        plt.title(self.name)
        plt.xlim(min(x)-1,max(x)+1)
        plt.ylabel('Level of internal attribution')
        plt.savefig(os.path.join(directory,self.name+' Results '))
        if plot:
            plt.plot()
        return z_values

    def summary(self):
        '''
        Print out a summary of the experiment
        '''

        print(f'Experiment name: {self.name}')
        print(f'Number of conditionss: {self.n_conditions}')
        print('The conditions are as follows')
        for i,cond in enumerate(self.conditions):
            print(f'Condition: {i}')
            for name,value in cond.items():
                print(f'{name}: {value}')





