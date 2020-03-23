# Bachelor Thesis in Psychology 

One of the grand goals of AI is to create machines that perform human level reasoning. Recent successes in creating intelligent machines are
still far away from human-level capabilities in terms of generalizability and data-efficiency.

One approach to achieving human level reasoning abilities, put forward by [Joshua Tenenbaum](http://web.mit.edu/cocosci/josh.html)
and [Noah Goodman](https://cocolab.stanford.edu/ndg.html) is based on the idea that human structure their knowledge into intuitive theories.
Simply speaking intutive theories are abstract models that humans have about a given domain that contain information
on the entities of the domain, their relation and their interaction. The intutive theory that has been studied the most is intutive physics, it describes how humans explain themselves physical events. 

The thesis looked closer at intuitive psychology, which is a model, humans use to explain other peoples actions. The framework is used to simulate experiments that investigate the self-serving bias. Experimental evidence is compared to the results produced by the simulation. 

More explanation on the background can be found in the thesis. Graphs and code might not be up to date with the newest version of the framework.

## Install framework

It is the easiest to create a new virtual environment (for example with (conda)[https://docs.conda.io/en/latest/]). Activate the environment and simply clone the git repo into the desired directory. From inside the cog_process_sim directory run

```bash
pip install -e .
```

## Framework 

There are three main classes to support the simulation of experiments 

 * Variable (```utils.py```): A class to simulate a psychological variable, e.g. self-worth. It is assumed to have a certain distribution or can be fixed to a specified value. Basically a wrapper around pyro.distribution objects that simplifies inference with intuitive theories. 

* Human (```human.py```): A class that simulates a participant in an experiment.

* Experiment (```experiment.py```): A class to support setting up and running experiments. Different conditions can be registered.

The file ```generative_processes.py``` contains functions that simulate different intuitive theories.  

The file ```experiments.py``` contains the setup of different experiments trying to reproduce experimental results that have been
empirically established in the literature of the self-serving bias. 

## Simulate your own experiments 

The file run_experiments.py allows you to setup your own experiments interactively and run them. 

To do so just run ```python3 run_experiments.py```.


## Get in touch 

In case you find mistakes, have questions or simply find the idea/topic interesting. Get in touch with nhopner[at]gmail.com

## To-do

* Add logging during experiment run
* Add differnt intuitive theories
* Make setting up experiments more flexible 
