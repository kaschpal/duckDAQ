# -*- coding: utf-8 -*-

from .Filter import Filter, Filter_Thread

class Channel_Selector(Filter):
    """
    Creates a measurement with only the specified port in it. This is specially
    useful in cooperation with a Multiplexer, i.e. if you want to display two
    ports with each one Voltmeter display.

        
    *Arguments*

        in_measurement : Measurement / VirtualMeasurement
            Measurement to read from
        portname : string            
            The desired port, i.e. "AIN3")
    
    *Variables*
        outm : VirtualMeasurement
            The created one-port-measurement

    """
    def __init__(self, in_measurement, portname):
        Filter.__init__(self, in_measurement)
        self.thread_class = Channel_Selector_Thread

        # only one port left
        self.outm.ports = [portname]
        # get index of portname in data tuple               # !!!!!!!!!!!!!!!!!!!!! TRY
        self.portIndex = self.inm.ports.index(portname) + 1 # increment, cause time is inserted at the beginning

class Channel_Selector_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
    
    def process(self, data):
        t = data[0]         # time
        vol = data[self.parent.portIndex] # desired port

        self.parent.outm.queue.put( (t, vol) )        

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
