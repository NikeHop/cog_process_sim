### Here all classes related to generative processes should be contained


import pyro
import pyro.distributions

from utils import sigmoid


def intuitive_theory(Skill, Effort, External, Luck):
    '''

    :param Skill: (Variable)
    :param Effort: (Variable)
    :param External: (Variable)
    :param Luck: (Variable)

    :return: A dictionary of the sampled values, keys are variable names, values are the sampled values.
    '''
    # Sample skill
    skill = pyro.sample(Skill.name, Skill.return_dist())
    # Sample Effort
    effort = pyro.sample(Effort.name, Effort.return_dist())
    # Sample External
    external = pyro.sample(External.name, External.return_dist())
    # Sample luck
    luck = pyro.sample(Luck.name, Luck.return_dist())
    # Determine success probability
    success_prob = sigmoid(skill + effort + external + luck)
    # Sample success
    success = pyro.sample('success', pyro.distributions.Bernoulli(success_prob))
    # Create a dictionary with a the sampled variables
    dic = {Skill.name: skill, Effort.name: effort, External.name: external, Luck.name: luck, 'success': success}
    return dic