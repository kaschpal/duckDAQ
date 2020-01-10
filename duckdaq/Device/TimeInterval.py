# -*- coding: utf-8 -*-

from .Device import Device
from duckdaq.Filter import Filter_Thread

class TimeInterval(Device):
    """
    Takes an analog measurement and gives the time intervals, in which
    the channel turns HIGH.
    Conversion is applied to every channel.

    With the argument invert, active-low *and* active-high devices can
    be used in one measurement. For example, PHYWE light barriers are active-low, Leybod
    light barriers are active-high.
       
    *Arguments*

        in_measurement : Measurement / VirtualMeasurement
            The input measurement; has to be **analog**, digitalisation
            is done by the class itself.
        intervalType : Bool
            Set "True", if the default is active-high.
            Set "False", if the deault is active-low.

            When set "False", all examples for invert behave exactly vice versa.
        invert : List of Bools
            List of all channels, where True indicates, this one
            should be inverted.
            
            **Example, when intervalType=True:** In a three-port measurment, [False, True, False] means,
            that the second one should Be inverted.

            **Clarification, when intervalType=True:** If the hardware device is active-low, specify "True",
            if it is active-high, "False".
    
    *Variables*
        outm : VirtualMeasurement
                the created Measurement. Every time one
                one interval is through, the duration is
                given. if one port has an interval, the
                others get a "None".

    """
    def __init__(self, in_measurement, intervalType = True, invert=None):
        Device.__init__(self, in_measurement)
        self.thread_class = TimeInterval_Thread
        
        self.ainm = self.inm  # give to schmitttriger
        
        # set the edgetype, which indicates start / stop of the interval
        # if the interval should be High, fist comes L-->H, then H-->L
        if intervalType == True:
            self.startEdge = "LH"
            self.stopEdge = "HL"
        elif intervalType == False:
            self.startEdge = "HL"
            self.stopEdge = "LH"
        else:
            raise TypeError("intervalType must be boolean")


        from duckdaq.Filter import SchmittTrigger, EdgeFinder, Outlier_Buster
        # create SchmittTrigger for digitalisation
        self.schmitt = SchmittTrigger(self.ainm)
        self.schmitt.start()

        # for outliers
        #self.ob = Outlier_Buster(self.schmitt.outm)
        #self.ob.start()
        self.ob = self.schmitt

        # eventually invert
        if invert != None:
            # check, if argument is valid
            if len(invert) != len(self.inm.ports):
                raise TypeError("invert invalid")
            
            from duckdaq.Filter import ChannelSplitter, ChannelMerger, Inverter

            self.cs = ChannelSplitter(self.ob.outm)
            self.cs.start()
            
            # create inverter, if channel should be inverted
            self.splittedChannels = []
            for i, channel in zip( list(range(len(self.cs.outm))), self.cs.outm ):
                if invert[i] == True:
                    inv = Inverter(channel)
                    inv.start()
                    self.splittedChannels.append( inv.outm )
                else:
                    self.splittedChannels.append( channel )
            
            # merge channels together
            self.cm = ChannelMerger( self.splittedChannels )
            self.cm.start()
            
            # create EdgeFinder for delays
            self.edge = EdgeFinder(self.cm.outm)
        else:
            # create EdgeFinder for delays
            self.edge = EdgeFinder(self.ob.outm)
        
        self.edge.start()

        # will be called by the thread instead
        self.inm = self.edge.outm

class TimeInterval_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
        self.lastData = [None, ] * len(self.parent.inm.ports)   # init
    
    def process(self, data):
        newData = [None, ] * (len(data) - 1)    # t will no more appear
        touched = False                 # True, if an interval appeared
        
        if self.lastData[0] == None:    # first call
            pass
        else:    # lastData exists
            lastTime = self.lastData[0]
            time = data[0]
            deltat = time - lastTime

            for i, lastval, val in zip(list(range(len(data[1:]))), self.lastData[1:], data[1:]):
                if (lastval == self.parent.startEdge) and (val == self.parent.stopEdge):
                    newData[i] = deltat
                    touched = True

        self.lastData = data

        # write only, if the newData is not empty
        if touched == True:
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
