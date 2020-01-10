# -*- coding: utf-8 -*-

from .Filter import Filter, Filter_Thread

class Multiplexer(Filter):
    """
    The Multiplexer provides a list of outgoing measurements, which are copies of the input measurement.

    The Filter class provides support for multiple **out**-going measurements, so very little code has to
    be added.
        
    *Arguments*
        
        in_measurement : Measurement / VirtualMeasurement
            The Measurement, which should be cloned.
        n : uint
            How many cloned measurements should be created
        
    *Variables*
        self.outm : **list** of Measurement() Instances
            The cloned measurements

    """
    def __init__(self, in_measurement, n):
        Filter.__init__(self, in_measurement)
        self.thread_class = Multiplexer_Thread
       
        # here are the clones stored, previous outm is deleted 
        del self.outm
        self.outm = []

        from duckdaq import VirtualMeasurement
        for i in range(0, n):                 
            self.outm.append( VirtualMeasurement(parentFilter=self) ) # create empty
            self.outm[i].ports = self.inm.ports  # copy portlist
            
class Multiplexer_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
    
    def process(self, data):
        for meas in self.parent.outm:  # copy to all outs
            meas.queue.put( data )        

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
