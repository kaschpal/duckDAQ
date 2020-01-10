############
Installation
############

Linux / OSX
===========

At first, you should have the following requirements installed:

    * python 2.7
    * pandas
    * numpy
    * PySide
    * matplotlib
    * scipy
    * git
    * QtiPlot

On Ubuntu you can install by the following command:

.. code-block:: bash

    $ sudo apt-get install qtiplot git python-scipy python-matplotlib python-pyside python-numpy python-pandas

Then, of course, the LabJack Exodriver and LabJackPython. For
Debian-based distributions, there is an
`easy instruction <http://labjack.com/blog/running-labjackpython-and-exodriver-ubuntu-1004>`_
at LabJack Inc. Don't forget to reboot after installing the driver.

Next, clone the duckDAQ repository at the place, you want duckDAQ installed.
I use my *bin* folder and will assume the rest of the instruction, you also do so.

.. code-block:: bash

    $ cd /home/myusername/bin
    $ git clone git://github.com/kaschpal/duckdaq.git

DuckDAQ uses pyqtgraph
for live plotting. You need version 0.9.7, which you can get at its
`homepage <http://www.pyqtgraph.org>`_.
If you don't want to install it globally, you don't have to. One of pyqtgraphs fantastic
advantages is, that it is totally portabel. Simply place the
pyqtgraph-0.9.7/pyqtgraph  folder
(the one with __init__.py, colormap.py, configfile.py, ... in it) into the *local-modules* folder.
DuckDAQ adds this directory the the *PYTHONPATH* and pyqtgraph is importable.
If you want to put it somewhere else, make also sure, that the
containing directory is in the *PYTHONPATH*.

.. code-block:: bash

    $ cd /tmp/
    $ wget http://www.pyqtgraph.org/downloads/pyqtgraph-0.9.7.tar.gz
    $ tar xvzf pyqtgraph-0.9.7.tar.gz
    $ cd pyqtgraph-0.9.7
    $ mv pyqtgraph /home/myusername/bin/duckDAQ/local-modules/


Now, you can go to the duckDAQ directory and test fuctionality. If the following
goes well, everything should work just fine.

.. code-block:: python

    >>> import duckDAQ


Windows
=======

At first, install the LabJack drivers.

Then choose one python distribution of your choice.
`WinPython <http://code.google.com/p/winpython/>`_
is nice, portabel and already has all packages installed.
`Canopy <https://www.enthought.com/products/canopy/>`_
has a builtin package manager, with which you can install all necessary packages you can
find in the Linux Section.

Then download
`LabJackPython <http://labjack.com/support/labjackpython>`_
from the offical homepage and install it.

