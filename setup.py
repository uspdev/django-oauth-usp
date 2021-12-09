import os
import setuptools
import os
from setuptools import setup

README = os.path.join(os.path.dirname(__file__), 'README.rst')

setup(
    name="django_oauth_usp",
    version="1.1.0",
    url='https://github.com/uspdev/django-oauth-usp.git',
    description="Django oauth usp package",
    long_description=open(README).read(),
    author="Marcelo Schneider",
    author_email="schneider.fei@gmail.com",
    license="MIT",
    zip_safe=False,
    platforms='any',
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
    install_requires=[
        'Django>=3.2'
        'Authlib>=0.15.2',
        'requests>=2.24.0'
    ],
)
