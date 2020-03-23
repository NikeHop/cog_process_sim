# Classes that help set up a participant

import pyro

from utils import Variable
from inference_util import LW


class Human(object):
    '''
    Describes a participant of an experiment

    The situation the participant is currently in, can be described via a set of variables that is registered
    with the participant.
    '''

    def __init__(self, self_concept, relevance, intuitive_theory_params, intuitive_theory, inference_params):
        '''

        :param self_concept: (list) names of variables that describe the self.
        :param relevance: (list) names of variables that influence the relevance of a task
        :param intuitive_theory_params: (list)
        :param intuitive_theory: (callable) generative process
        :param inference_params: (list) names of variables that describe the inference procedure
        '''
        self.concept = self_concept
        self.relevance = relevance
        self.intuitive_theory = intuitive_theory
        self.intuitive_theory_params = intuitive_theory_params
        self.inference_params = inference_params

    def set_variables(self, variables, sample):
        '''
        Sets the variables for the current condition the human is in

        :param variables: (dict) contains all the variables that describe an experimental condition
        :param sample: (bool) whether the variables should be sampled
        '''

        self.variables = variables
        if sample:
            for elem in self.variables:
                if isinstance(elem, Variable):
                    elem.sample()


    def get_inference_params(self):
        '''
        Returns a list of the variables that specify the inference procedure of the condition

        :return:
        '''

        return [self.variables[elem] for elem in self.inference_params]

    def get_intuitive_theory_params(self):
        '''
        A list of variables that are part of the intuitive theory

        :return: (list) containing Variable objects
        '''
        return [self.variables[elem] for elem in self.intuitive_theory_params]

    def get_self_worth(self, current_situation):
        '''
        Return current self-worth

        :param current_situation: (dict) contains the variables of the intutive theory and their current estimates.

        :return: (float)
        '''
        self_worth = 0
        for elem in self.concept:
            self_worth += current_situation[elem]['mean']
        return self_worth

    def get_relevance(self):
        '''
        Returns a value indicating the relevance of the task

        :return: (float)
        '''

        relevance = 0
        for elem in self.relevance:
            relevance += self.variables[elem].get_current_value()
        return relevance

    def decorate_self_worth(self):
        '''
        Returns the

        :return: (callable)
        '''

        def new_it(*args):
            # Run the initial intuitive theory
            sampled_var = self.intuitive_theory(*args)
            mean = 0
            # determine the sampled self-worth
            for elem in self.concept:
                mean += sampled_var[elem]
            self.worth = pyro.sample('self-worth', pyro.distributions.Normal(mean, 1))
            return self.worth

        # return the extended intuitive theory
        return new_it

    def discrepancy(self, prior, post):
        '''

        :param prior: (dict) contains the mean of the variables of the intuitive theory before inference
        :param post: (dict) contains estimates of the mean of the variables of the intuitive theory after inference

        :return: (float) Score that describes the difference in the self-worth before the observation
                         was made and after inference.
        '''

        diff = 0
        for elem in self.concept:
            diff += post[elem]['mean'] - prior[elem]['mean']
        return diff


    def do_attribution(self, prior, post, alpha, beta):
        '''
        Given prior and posterior means of the unobserved variables, determine the difference and weight it
        to get a measure of how much the participant attributed an event internally vs. externally.

        :param prior: (dict) for each unobserved variable of the intuitive theory contains estimates
        :param post: (dict) for each unobserved variable of the intuitive theory contains estimates
        :param alpha: (float) weight of the internal attribution
        :param beta: (float) weight of the external attribution

        :return: (float) Rating by how much the outcome is attributed internally
        '''

        internal = sum([abs(post[elem.name]['mean'] - prior[elem.name]['mean']) for elem in self.get_intuitive_theory_params() if elem.internal == 1])
        external = sum([abs(post[elem.name]['mean'] - prior[elem.name]['mean']) for elem in self.get_intuitive_theory_params() if elem.internal == 0])
        attr = alpha * internal - beta * external
        return attr.item()

    def do_attribution_internal(self, prior, post, alpha):
        '''
        Does the same as do_attribution but ignores the external variables
        '''

        internal = sum([abs(post[elem.name]['mean'] - prior[elem.name]['mean']) for elem in self.get_intuitive_theory_params() if elem.internal == 1])
        attr = alpha * internal
        return attr.item()


    def inference(self):
        '''
        Implements the process model of the self-serving bias.

        Inference process:
        Step 1. Observe the outcome --> Outcome registered as a variable in self.variables
        Step 2. Perform automatic inference --> In automatic inference we only let the internal variables vary
        Step 3. Check whether self.awareness is high
        If low:
            Step 4. Use the results from Step 2 to do attribution
        If high:
            Step 5. Determine whether there exists a discrepancy between inferred values and the self-concept
            If discrepancy is positive:
                Step 6. Attribution with higher focus on internal attributes
            If discrepancy is negative:
                Step 7. Determine whether there is a probability of improvement
                If prob. of improv. is high:
                    Step 8. Do attribution based on automatic inference in Step 2
                If prob. of improv. is low:
                    Step 9. Do attribution based on inference with fixed self-worth

        :return: A value that quantifies how strong the internal attribution is
        '''

        ## Step 1:  Observe the outcome

        obs = {'success': self.variables['success']}

        ## Step 2:  Perform inference only letting the internal variables vary ##

        prior = {elem.name: elem.param for elem in self.get_intuitive_theory_params()}

        # Add the external variables to the observations
        for elem in self.get_intuitive_theory_params():
            if elem.internal == 0:
                obs[elem.name] = prior[elem.name]['mean']

        # Create the LW-inference class
        inference_class = LW(self.intuitive_theory, self.variables['f'])
        estimates, logW_sum = inference_class.inferLW(*self.get_inference_params(), obs, *self.get_intuitive_theory_params())

        # Extract results
        post = {elem.name: estimates[elem.name] for elem in self.get_intuitive_theory_params()}

        ## Step 3: Check whether self-awareness is high

        self.variables['SA'].sample()
        if not (self.variables['SA'] > 0):
            ## Step 4: Low self-awareness uses the results from automatic inference to do attribution
            return self.do_attribution_internal(prior, post, 1)
        else:
            ## Step 5: Determine discrepancy between inferred values and self-concept

            diff = self.discrepancy(prior, post)
            # Task-relevance
            relevance = self.get_relevance()
            # Discrepancy is worse/better for relevant tasks
            diff = relevance * diff

            if diff >= 0:
                ## Step 6: Attirbution based on automatic inference with focus on internal variables
                return self.do_attribution_internal(prior, post, 1 + diff)
            else:
                ## Step 7 Determine the probability of improvement
                self.variables['PI'].sample()
                if self.variables['PI'] > 0:
                    ## Step 8: Do attribution on automatic inference
                    return self.do_attribution_internal(prior, post, 1)
                else:
                    ## Step 9: Do attribution based on inference with fixed self-worth

                    # Determine self-worth before the event happened
                    self_worth = self.get_self_worth(prior)
                    # Extend the intutive theory to contain self-worth
                    self_worth_model = self.decorate_self_worth()
                    # Condition the model on self_worth and do inference
                    obs = {'self-worth': self_worth, 'success': self.variables['success']}
                    inference_class = LW(self_worth_model, self.variables['f'])
                    estimates, logW_sum = inference_class.inferLW (*self.get_inference_params(), obs, *self.get_intuitive_theory_params())
                    # Get values after conditioning
                    post = {elem.name: estimates[elem.name] for elem in self.get_intuitive_theory_params()}
                    # Do attribution
                    return self.do_attribution(prior, post, 1, 1 + abs(diff))