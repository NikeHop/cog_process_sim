# Utility functions

import numpy as np
import pyro.distributions


def sigmoid(x):
    '''
    Implements the sigmoid function for a one-dimensional input

    :param x: (float)
    :return: (float) function value at point x
    '''
    return 1/(1+np.exp(-x))


class Variable(object):
    '''
    Class to define a variable that is part of the psychological process.
    Wrapper around pyro.distribution object for easier interface.
    '''

    distributions = {'Normal': pyro.distributions.Normal, \
                     'Binomial': pyro.distributions.Binomial, \
                     'Exponential': pyro.distributions.Exponential, \
                     'fixed': 0}

    def __init__(self, internal, name, dist, param):
        '''
^
        :param internal: (0/1) binary variables: 0 means external
        :param name: (string) name of the variable
        :param dist: (string) name of the distribution that describes how the variable is distributed
        :param param: (dict) contains all the parameters to sample from the distribution
        '''

        assert internal in [0,1], 'Internal must be a binary variable, i.e. can only take the values 0/1'
        self.internal = internal
        self.name = name
        self.dist = dist
        self.param = param
        self.sample()

    def return_dist(self):
        '''

        :return: pyro.distribution object instantiated with the parameters of the Variable
        '''

        return Variable.distributions[self.dist](*self.param.values())

    def sample(self):
        '''
        Sample a new value for the Variable from the given distribution.
        If the Variable is fixed then the current value remains the fixed value.
        '''

        if 'fixed' in self.dist:
            self.current_value = self.param['fixed']
        else:
            self.current_value = Variable.distributions[self.dist](*self.param.values()).sample()

    def get_current_value(self):
        '''
        Returns the current value

        :return: (float)
        '''
        return self.current_value

    def __gt__(self, i):
        '''
        Implements the magic method 'greater than'

        :param i: (float)

        :return: 0/1
        '''

        c = self.get_current_value()
        if c > i:
            return 1
        return 0

    def __eq__(self, i):
        '''
        Implements the magic method 'equal'

        :param i: (float)

        :return: 0/1
        '''
        c = self.get_current_value()
        if c == i:
            return 1
        return 0

    def __repr__(self):
        print(f'Distribution: {self.dist}')
        print(f'Current Value: {self.current_value}')
        return ''

# Error class for setting up experiment interactively:

class RangeError(Exception):
    pass

# Check whether an integer entry is valid

def check_int(int_string,min=-float('Inf'),max=float('Inf')):
    '''
    :param int_string: (string)
    :param min: (int)
    :param max: (int)
    :return: (int)
    '''
    number = 0
    try:
        number = int(int_string)
        if number > max or number < min:
            raise RangeError()
    except ValueError:
        print('The value you entered is not an integer')
    except RangeError:
        print(f'The value you entered is not between {min}-{max}')

    return number


### Data structure that contains all the information on a variable (e.g. what is the default distribution)
low_param = {'mean':-1,'std':1}
high_param = {'mean':1,'std':1}
TI_high = Variable(1,'TI','fixed',{'fixed':0})
TI_low = Variable(1,'TI','fixed',{'fixed':2})
SA_high = Variable(0,'SA','fixed',{'fixed':-1})
SA_low = Variable(0,'SA','fixed',{'fixed':1})
PI_low = Variable(0,'PI','fixed',{'fixed':-1})
PI_high = Variable(0,'PI','fixed',{'fixed':1})
skill_low = Variable(1,'skill','Normal',low_param)
skill_high = Variable(1,'skill','Normal',high_param)
effort_low = Variable(1,'effort','Normal',low_param)
effort_high = Variable(1,'effort','Normal',high_param)
external_low = Variable(0,'external','Normal',low_param)
external_high = Variable(0,'external','Normal',high_param)
luck_low = Variable(0,'luck','Normal',low_param)
luck_high = Variable(0,'luck','Normal',high_param)


####

library_variables = {'TI':{'h':TI_high,'l':TI_low},
                     'SA':{'h':SA_high,'l':SA_low},
                     'PI':{'h':PI_low,'l':PI_high},
                     'skill':{'h':skill_low,'l':skill_high},
                     'effort':{'h':effort_low,'l':effort_high},
                     'luck':{'h':external_low,'l':external_high},
                     'external':{'h':luck_low,'l':luck_high}
                     }

