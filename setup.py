from setuptools import setup

setup(
    name='cog_process_sim',
    version='1',
    url='https://github.com/NikeHop/cog_process_sim',
    author='Niklas Höpner',
    author_email='nhopner@gmail.com',
    description='A simple framework for simulating experiments about the self-serving bias',
    install_requires=['pyro','tqdm','numpy','matplotlib']
)
