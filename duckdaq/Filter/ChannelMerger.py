# -*- coding: utf-8 -*-

from .Filter import Filter, Filter_Thread
import queue

class ChannelMerger(Filter):
    """
    Merges the one-channel measurements (most likely) of a ChannelSplitter into one single
    measurement. All channels **must** have the same timestamps.

    The ChannelMerger takes a list of measurements, which is not supported by the Filter base class.
    Therefor some methods have to be rewritten. If you want to create something simlar, the sourcecode
    if this class is the right point to start.
        
    *Arguments*
        
        in_measList : **list** of Measurement / VirtualMeasurement
            The Measurements, which should be glued together.
        
    *Variables*
        self.outm : VirtualMeasurement
            The resulting single Measurement.

    """
    def __init__(self, in_measList):
        self.thread_class = ChannelMerger_Thread
        
        from duckdaq import VirtualMeasurement
        self.inm = in_measList         # input measurement
        self.outm = VirtualMeasurement(parentFilter=self)          # output measuremnt

        # merge all portslists into one
        self.outm.ports = []
        for portslist in [meas.ports for meas in self.inm]:
            self.outm.ports = self.outm.ports + portslist

class ChannelMerger_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)

    def __get_data(self):
        """ reads a data tuple from the inqueue. Return None, if queue is empty """
        # data is now a list
        data = []

        # foreach queue
        for inqueue in [meas.queue for meas in self.parent.inm]:
            try:
                data.append( inqueue.get(block=True, timeout=0.01) )
            except queue.Empty:
                return None
        
        return data

    def run(self):
        """ this runs, until the inqueue is empty AND the inmeasuremnt is finished
            A Filter subclass has to implement the process() method
        """
        self.parent.outm.RUNNING = True
        
        while self.STOP == False:
            data = self.__get_data()
           
            # is at least one incoming meas RUNNING
            atLeastOneMeasRUNNING = False
            for RUNNING in [meas.RUNNING for meas in self.parent.inm]:
                if RUNNING == True:
                    atLeastOneMeasRUNNING = True
                    break

            if data == None and atLeastOneMeasRUNNING == False:    # no more data chunks and measure is dead
                self.STOP == True
                break  
            elif data == None: # dont process None data
                pass
            else:
                self.process(data)
        
        # make things clear
        self.parent.RUNNING = False
        self.parent.outm.RUNNING = False

    def process(self, data):
        time = data[0][0]   # has to be the same in every mesurement

        newData = []
        newData.append( time )

        for tuple_ in data:
            for val in tuple_[1:]:          # without time
                newData.append(val)

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
