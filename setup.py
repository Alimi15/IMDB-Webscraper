from setuptools import setup
from setuptools import find_packages

setup(
    name='IMDbWebscraper',
    version='1.0',
    description='Package that scrapes data about the top 150 rated superhero feature films from IMDb',
    url='https://github.com/Alimi15/IMDB-Webscraper.git',
    author='Ali Iltaf',
    license='MIT',
    packages=find_packages(),
    install_requires=['selenium'],
)