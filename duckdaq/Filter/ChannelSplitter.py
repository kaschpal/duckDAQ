# -*- coding: utf-8 -*-

from .Filter import Filter, Filter_Thread

class ChannelSplitter(Filter):
    """
    Slits one Measurement consisting of n channels into n Measurements with one channel.
    This can be used in combination with a ChannelMerger to modify only one channel.

    The StopWatch Device for example has the ability to invert one or more channels; the ingoing
    Measurement there is divided by a ChannelSplitter, only the desired one is inverted and
    then all ports are glued together again with an ChannelMerger. See code for example.
        
    *Arguments*
        
        in_measurement : Measurement / VirtualMeasurement
            The Measurement, which should be splitted.
        
    *Variables*
        self.outm : **list** of Measurement() Instances
            The splitted single-channel measurements

    """
    def __init__(self, in_measurement):
        Filter.__init__(self, in_measurement)
        self.thread_class = ChannelSplitter_Thread
       
        # here are the single ones stored, previous outm is deleted 
        del self.outm
        self.outm = []

        from duckdaq import VirtualMeasurement
        for i in range(0, len(self.inm.ports) ): 
            self.outm.append( VirtualMeasurement(parentFilter=self) ) # create empty
            self.outm[i].ports = [ self.inm.ports[i] ]  # copy port from portlist
            
class ChannelSplitter_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
    
    def process(self, data):
        time = data[0]
        for meas, i in zip(self.parent.outm, list(range(1, len(self.parent.outm)+1)) ):  # copy to all outs
            meas.queue.put( (time, data[i]) )        

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
