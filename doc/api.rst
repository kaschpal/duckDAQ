#############
Api-Reference
#############


Measurements
############

A Measurement is the source of data.


Hardware-based Measurements
===========================

.. automodule:: duckdaq.Measurement
.. autoclass:: Measurement
    :members:

Virtual Measurements
====================

.. automodule:: duckdaq.VirtualMeasurement
.. autoclass:: VirtualMeasurement
    :members:

Displays
########

These are the displays, which can be used to visualize the data collected by a measurement.

.. automodule:: duckdaq.Display


Creation of Displays
====================

At the moment, a display is nothing more than a direct
inheritance of QWidget, but with an other name.
**This may change in the future.**

A Display takes the data from a measurement and makes it aviable for the
user. This is done with a Filter, which is
created by the display.

A Display could be seven-segment-like window, a oszilloskope-like plotter or
a simple text-data-logger, but also a class, which takes the data, chunk by chunk and writes it into a hdf5 or
csv file is possible.

Displays are always QWidgets, to make it easy to embed them into a new GUI.

.. autoclass:: Display
    :members:

Already written Displays
========================

Voltmeter
---------

.. autoclass:: Voltmeter 
    :members:

Plotter
-------

.. autoclass:: Plotter
    :members:

Stopwatch
---------

.. autoclass:: Stopwatch
    :members:


Filters
#######

Filter are used to modify the measurement data, i.e. convert an analog value
to boolean True/False.
Filter usually have one input and one output measurement and can be combined
in various ways.

.. automodule:: duckdaq.Filter 

Creation of Filters
===================

.. autoclass:: Filter
    :members:

Already written Filters
=======================

1. Data convertion filters
--------------------------

    **Schmitt-Trigger**

    .. autoclass:: SchmittTrigger
        :members:

    **Inverter**

    .. autoclass:: Inverter
        :members:

    **Edge Finder**

    .. autoclass:: EdgeFinder
        :members:

    **Outlier Buster**

    .. autoclass:: Outlier_Buster
        :members:


2. Format convertion filters
----------------------------

    **Multiplexer**

    .. autoclass:: Multiplexer 
        :members:

    **Channel Splitter**

    .. autoclass:: ChannelSplitter
        :members:

    **Channel Merger**

    .. autoclass:: ChannelMerger 
        :members:

    **Channel Selector**

    .. autoclass:: Channel_Selector
        :members:


Devices
#######

Technically, a Device is a direct derivation of a Filter. **This may change in the Future.**

A Device is a Filter which is bound to a special sensoric hardware and typically outputs
its values not in volts, but the units of the physical value it measures.

For example, a thermometer-device like the LM335 takes the voltage of the the sensor
and puts the temperature in Celsius or Kelvin.

.. automodule:: duckdaq.Device 

Creation of Devices
===================

.. autoclass:: Device 
    :members:

Already written Devices
=======================

Time interval
-------------

.. autoclass:: TimeInterval
    :members:

Spikewheel
----------

.. autoclass:: SpikeWheel
    :members:

LM335 (temperature sensor IC)
-----------------------------

.. autoclass:: LM335
    :members:


Utility functions
#################

These are functions I did not want to bind to a certain class, because
I thought they may be used somewhere else. Some LabJack dependent
functions also reside here, since I started to think about the
possibility of other DAQ devices could be supported.


.. automodule:: duckdaq.util 
    :members:
