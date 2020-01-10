# -*- coding: utf-8 -*-

from .Filter import Filter, Filter_Thread


class SchmittTrigger(Filter):
    """
    Like a hardware Schmitt-trigger, this filter converts the voltage
    value to True/False with hysteresis. Conversion is applied to all ports.
    
    *Arguments*

        in_measurement : Measurement / VirtualMeasurement
            Measurement to read from
        levelRising : float         
            Level in volts, from which on the signal is considered als True
        levelFalling : float
            Level in volts, from which on the signal is considered als False
    
    *Variables*
        outm : VirtualMeasurement
            The created digital Measurement

    """
    def __init__(self, in_measurement, levelRising=4, levelFalling=1):
        Filter.__init__(self, in_measurement)
        self.thread_class = SchmittTrigger_Thread

        self.levelRising = levelRising
        self.levelFalling = levelFalling


class SchmittTrigger_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
        self.lastData = None         # init
    
    def process(self, data):
        # the converted data is temporarely stored in newData
        newData = [None, ] * len(data)   # must be a list, tuples dont support assignment
        newData[0] = data[0]            # clone time

        if self.lastData == None:        # first call 
            # The hight/low decision is made by the mean value
            for val, i in zip( data[1:], list(range(1, len(data))) ):     # let i start at "1", "0" is time
                if val >= (self.parent.levelRising + self.parent.levelFalling) / 2:
                    newData[i] = True
                else:
                    newData[i] = False
        
        else:   # not first call
            for val, lastval, i in zip( data[1:], self.lastData[1:], list(range(1, len(data))) ):    # see loop above
                if val >= self.parent.levelRising and lastval == False:    # high level has been reached from under
                    newData[i] = True
                elif val <= self.parent.levelFalling and lastval == True:    # low level has been reached from above
                    newData[i] = False
                else:                               # leave everything
                    newData[i] = lastval
       

        self.lastData = tuple( newData )    # save
        self.parent.outm.queue.put( self.lastData )

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
