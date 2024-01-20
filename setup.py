from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='AudioIO',
    description='A Python Toolkit of Interfaces for Audio Input and Outputs',
    version='0.0.2',
    author='Joram Millenaar',
    author_email='joormillenaar@live.nl',
    url='https://github.com/jofoks/AudioIO',
    install_requires=['numpy'],
    packages=['AudioIO'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['audio', 'IO', 'WAV', 'microphone', 'audiostreaming', 'sound device'],
    license='MIT'
)
