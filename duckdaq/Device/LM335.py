# -*- coding: utf-8 -*-

from .Device import Device
from duckdaq.Filter import Filter_Thread

class LM335(Device):
    """
    Takes an analog measurement of the voltage, provided by a LM335
    IC. A voltage divider is useful to connect the LM335 at the LV ports,
    which have 12bit resoluton for only 2.5V.
    Conversion in done for all ports.

    *Arguments*

        in_measurement : Measurement / VirtualMeasurement
            The Input measurement.
        voltageDivider : float
            If you divide 1:1, specify "2" as factor, with which the voltage should
            be multiplied. If none is used, give "1".
        celsius : Bool
            +-----+-----------------------------------+
            | True| return temperature in Celsius     |
            +-----+-----------------------------------+
            |False|  temperature should be in Kelvin  |
            +-----+-----------------------------------+
    """
    def __init__(self, in_measurement,
                        voltageDivider=2,
                        celsius=True):
        Device.__init__(self, in_measurement)
        self.thread_class = LM335_Thread
        self.celsius = celsius
        self.voltageDivider = voltageDivider
        
class LM335_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
    
    def process(self, data):
        newData = []
        newData.append( data[0] )   # put time

        for voltage in data[1:]:
            T = voltage * 100 * self.parent.voltageDivider

            if self.parent.celsius == True:
                theta = T - 273.15
                newData.append( theta )
            else:
                newData.append( T )

        self.parent.outm.queue.put( tuple( newData ) )

"""
This file is part of duckDAQ.

DuckDAQ is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

DuckDAQ is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with duckDAQ.  If not, see <http://www.gnu.org/licenses/>.
"""
