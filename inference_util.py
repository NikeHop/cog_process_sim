### All classes that are necessary to perform inference

from collections import defaultdict
import numpy as np
import pyro.distributions
import pyro.poutine as poutine
import torch



class LW(object):
    '''
    A class to perform Likelihood-Weighting inference for an arbitrary generative process

    The model is a probability distribution p(X,Y), where X are the unobservable variables
    and Y are the observable variables. Given observations Y the goal is to estimate
    E[f(X)], where the expectation is taken over p(X|Y).
    '''

    def __init__(self, model, f={}):
        '''
        :param model: (callable) a stochastic generative process that contains named sample statements
        :param f: (dict) a dictionary containing functions for which the expectation should be determined
        '''

        self.model = model
        self.f = f

    def inferLW(self, L, observation, *args, **kwargs):
        '''
        Perform inference for a given set of observations. The formula to determine the estimates is

        E[f(X)] = 1/K sum(p(Y|X)/sum(p(Y|X)) * f(X)),

        where the sum is taken over the samples.

        :param L: (int) Number of samples
        :param observation: (dict) dictionary that contains the obs. The keys are the sample-names
        :param args: arguments to evaluate the model
        :param kwargs: key-word arguments to evaluate the model

        :return: estimates (dictionary), logW_sum (float)

        '''

        # Condition the model on the given observations
        cond_model = pyro.condition(self.model, data=observation)
        # collect the sum of the log-probabilities of the observables by executing the conditioned model
        logWs = []
        # E[f(X)] is saved in estimates for each unobserved variable
        estimates = defaultdict(dict)
        # collect sampled values of the unobserved variables
        samples = defaultdict(list)

        for _ in range(L):
            # Run the conditioned model and construct the directed graphical model
            trace_DS = poutine.trace(cond_model).get_trace(*args, **kwargs)
            # Determine the log-probability of each sampled value
            trace_DS.log_prob_sum()
            # Get the observational nodes from the data structure
            obs_nodes = trace_DS.observation_nodes
            # For each observational node extract the log-probabilities of the sampled values
            # Sum those values up to obtain the log-probability of the observed values
            logWs.append(sum([trace_DS.nodes[elem]['log_prob_sum'] for elem in obs_nodes]))
            # Add the sampled values for each unobserved variable to a list
            __ = [samples[elem].append(trace_DS.nodes[elem]['value']) for elem in trace_DS.stochastic_nodes]

        # need likelihoods not log-likelihoods
        logWs = [np.exp(elem) for elem in logWs]
        logW_sum = sum(logWs)
        # Compute likelihood weights
        weights = np.array(logWs) / logW_sum.item()
        # Determine the estimates of the expectations for each function f regsitered with the class
        for key in samples.keys():
            for name, elem in self.f.items():
                estimates[key][name] = \
                    sum(elem(np.array(samples[key])) * weights)
        return estimates, logW_sum


if __name__ == '__main__':
    '''
    Tests whether the inference classes work. Perform inference in a simple Beta-Binomial model.
    
    theta ~ Beta(a,b) (prior)
    X | theta ~ Ber(theta) (likelihood)
    theta | X ~ Beta(a+x,b+n-x) (posterior)
    
    '''

    # Set up the Beta-Binomial model

    def beta_binomial_model(n,a,b):
        theta = pyro.sample('theta', pyro.distributions.Beta(a,b))
        k = pyro.sample('successes', pyro.distributions.Binomial(torch.tensor(n, dtype=torch.float32), theta))
        return k


    n = torch.tensor(10,dtype=torch.float32) # number of trials
    a = torch.tensor(5,dtype=torch.float32)  # prior parameter of Beta-distribution
    b = torch.tensor(10,dtype=torch.float32)  # prior parameter of Beta-distribution
    k = torch.tensor(4,dtype=torch.float32)  # number of success
    p = a + k # posterior parameter of Beta-distribution
    q = b + n - k # posterior parameter of Beta-distribution
    theoretical_post_expectation = p.item() / (p + q).item()

    # expectation of the posterior using Likelihood-Weighting
    lw = LW(beta_binomial_model,f = {'identity':lambda x:x})
    # parameters for inference
    L = 1000
    obs = {'successes': k }
    estimates, _  = lw.inferLW(L,obs,n,a,b)


    print(f'The theoretical expectation is: {theoretical_post_expectation}')
    print(f'The estimated expectation is: {estimates["theta"]["identity"]}')
    print(f'The difference is: {abs(theoretical_post_expectation-estimates["theta"]["identity"])}')



