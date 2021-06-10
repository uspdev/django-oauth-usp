import setuptools
from setuptools import setup

setup(
    name="django_oauth_usp",
    version="0.0.1",
    url = 'https://github.com/uspdev/django-oauth-usp.git',
    description="Django oauth usp package",
    author="Marcelo",
    author_email="schneider.fei@gmail.com",
    packages=setuptools.find_packages(),
    install_requires=[
        'Django>=3.2'
        'Authlib>=0.15.2',
        'requests>=2.24.0',

    ],
)
