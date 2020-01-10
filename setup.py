# -*- coding: utf-8 -*-

#from distutils.core import setup
from setuptools import setup

setup(
    name = "duckdaq",
    packages = ["duckdaq", "duckdaq.Filter", "duckdaq.Device", "duckdaq.Display"],
    version = "0.1",
    description = "Didactic lab software for the LabJack U3-HV",
    author = "Ulrich Leutner",
    author_email = "ulli@koid.org",
    url = "https://duckdaq.readthedocs.org/en/latest/index.html",
    download_url = "https://github.com/kaschpal/duckdaq/tarball/master",
    install_requires = ["pyqtgraph>=0.9.8", "PySide>=1.2.0"],
    keywords = ["labjack", "daq", "education", "physics"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Physics"
        ],
    long_description = """\
Duckdaq is an educational software for data acquisition and analyis. The focus
lies on live analyis both in class and in lab.

The program aims to provide similar functionality as common didactic software
like Leybold CassyLab or PHYWE measure. The difference is, that experiments
are not clicked together like in the programs mentioned above, because this
is unflexible, slow, inconvenient and provides no mechanism, to extend the
software.

Just like in LabVIEW, data flow is the foundation of duckdaq. Data comes
from sources (called Measurements) is modified sample by sample with a cascade
of Filters (which are e.g. converting voltage to temperature) and then the
result goes to a Display, for example a plotter.

Unlike in LabVIEW, you don’t program grahically, but in form of a python
script.

Documentation: https://duckdaq.readthedocs.org/en/latest/index.html
"""
)
