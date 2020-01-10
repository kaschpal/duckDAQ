# -*- coding: utf-8 -*-

from .Filter import Filter, Filter_Thread

class EdgeFinder(Filter):
    """
    Takes a digital signal and puts out a *"LH"* string for rising edge and a *"HL"* string for falling edge.
    (Since python2 supports no enums yet)

    When the edge appears only at one port (which is - ehm - always the case) the other ports data is "None"
    Conversion is applied to all ports.
    
    *Arguments*

        in_measurement : Measurement / VirtualMeasurement
            Measurement to read from
        putNones : Bool         
            set True, if "None" values should be added to the
            Measurement, when no edge appears. For example,
            this is used by the spikewheel, to put the same distance again, when
            no change of the state appears.
    
    *Variables*
        outm : VirtualMeasurement
            The created new Measurement.
            
    """
    def __init__(self, in_measurement, putNones=False):
        Filter.__init__(self, in_measurement)
        
        self.thread_class = EdgeFinder_Thread
        self.putNones = putNones

class EdgeFinder_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
        self.lastData = None         # init
    
    def process(self, data):
        # the converted data is temporarely stored in newData
        newData = [None, ] * len(data)   # must be a list, tuples dont support assignment
        newData[0] = data[0]            # clone time

        touched = False     # if any edge is found touched is set True. If False, nothing will be appended to the outm

        if self.lastData == None:        # first call, save and return
            pass
        else:   # not first call
            for val, lastval, i in zip( data[1:], self.lastData[1:], list(range(1, len(data))) ):    # see loop above
                if lastval == False and val == True:        # rising edge: l ---> h
                    newData[i] = "LH"
                    touched = True
                elif lastval == True and val == False:      # falling edge: h ---> l
                    newData[i] = "HL"
                    touched = True
                else:
                    newData[i] = None       # fill entries, where no edges appeared with "None"
        
        self.lastData = data    # save

        if touched == True:     # edge appeared 
            self.parent.outm.queue.put( tuple(newData) )
        
        else:                   # if desired, put None-Tuple 
            if self.parent.putNones == True:
                self.parent.outm.queue.put( tuple(newData) )
            
            return          


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
