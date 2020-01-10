# -*- coding: utf-8 -*-

from .Filter import Filter, Filter_Thread


class Inverter(Filter):
    """
    Inverts a digital measurement:
    
    +------+----+-------+
    | True | -> | False |
    +------+----+-------+
    | False| -> |  True |
    +------+----+-------+

    Analog signals (read: values which are not bool) are not touched.
    
    *Arguments*

        in_measurement : Measurement / VirtualMeasurement
            Measurement to read from
    
    *Variables*
        outm : VirtualMeasurement
            The created inverted measurement

    """
    def __init__(self, in_measurement):
        Filter.__init__(self, in_measurement)
        self.thread_class = Inverter_Thread


class Inverter_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
    
    def process(self, data):
        newData = [None, ] * len(data)   # must be a list, tuples dont support assignment
        newData[0] = data[0]            # clone time

        # invert and leave analogue data untouched
        for entry, i in zip( data[1:], list(range(1, len(data))) ):
            if entry == True:
                newData[i] = False
            elif entry == False:
                newData[i] = True
            else:
                newData[i] = entry
        
        self.parent.outm.queue.put( tuple(newData) )

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
