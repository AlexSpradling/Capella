from setuptools import setup, find_packages

setup(
    name='Capella',
    version='2.0',
    packages=find_packages(),
    description='A Python package for celestial navigation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Alex Spradling',
    author_email='alexspradling@gmail.com',
    url='https://github.com/AlexSpradling/Capella',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)