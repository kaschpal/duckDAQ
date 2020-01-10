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
