# -*- coding: utf-8 -*-

from .Device import Device
from duckdaq.Filter import Filter_Thread

class SpikeWheel(Device):
    """
    Takes an analog measurement (only one port) from a spikewheel
    attached to a light barrier and delivers as output
    distance, velocity and acceleration.
    Velocity is usable (when fitted), acceleration is mostly crap, depends on the
    resolution of the wheel.

    The newly created ports are:

    ======== ======== ============
    "s"      "v"      "a"
    ======== ======== ============
    distance velocity acceleration
    ======== ======== ============
   
    *Arguments*

        in_measurement : Measurement / VirtualMeasurement
            Input measuremnt, give only **one port**; The Measurement has to be
            **analog**, conversion is done by the class itself.
        numberOfSpikes
            How many spikes the wheel has
        diameter
            Diameter of the wheel
    
    *Variables*
        outm : VirtualMeasurement
            the created Measurement of t,s,v,a

    """
    def __init__(self, in_measurement,
                        numberOfSpikes=20,
                        diameter=25):
        Device.__init__(self, in_measurement)
        self.thread_class = SpikeWheel_Thread
        
        if len(in_measurement.ports) > 1:
            raise TypeError("SpikeWheel can only be called with a one-port measurement.")

        from math import pi
        perimeter = (diameter * pi) / 1000     # in meters
        
        # distance, which is traveled after each change of h/l or l/h
        self.deltaS = (perimeter / numberOfSpikes) * 2

        self.ainm = self.inm  # give to schmitttriger

        from duckdaq.Filter import SchmittTrigger, EdgeFinder
        # create SchmittTrigger for digitalisation
        self.schmitt = SchmittTrigger(self.ainm)
        self.schmitt.start()
        # create EdgeFinder for delays
        self.edge = EdgeFinder(self.schmitt.outm, putNones=True)  # without Nones, process is not called every sample
        self.edge.start()

        # will be called by the thread instead
        self.inm = self.edge.outm

        # replace by distance, velocity, acceleration
        self.outm.ports = ["s", "v", "a"]


class SpikeWheel_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
        self.lastData = [None, ] * 4         # init
    
    def process(self, data):
        t = data[0]

        lastt = self.lastData[0] 
        lasts = self.lastData[1] 
        lastv = self.lastData[2]
        lasta = self.lastData[3]
       
        # if no edge appeared, set deltas=0
        if data[1] == None:
            ds = 0
        else:  # edge appeared: wheel moved forward
            ds = self.parent.deltaS

        if lastt != None:
            deltat = t - lastt    # time between actual and last data
        
        newData = [None, ] * 4  # time, s, v, a

        if   lasts == None:      # first call, no lastdistance given
            newData[0] = t       # copy time, s
            newData[1] = 0
        elif lastv == None:      # second call, no velocity given
            #newData[0] = t
            #newData[1] = lasts + self.parent.deltaS             # s = s_0 + ds
            #newData[2] = self.parent.deltaS / deltat            # v = ds / dt
            newData[0] = t
            newData[1] = lasts + ds             # s = s_0 + ds
            newData[2] = ds / deltat            # v = ds / dt
        else:
            #newData[0] = t
            #newData[1] = lasts + self.parent.deltaS             # s = s_0 + ds
            #newData[2] = self.parent.deltaS / deltat            # v = ds / dt
            #newData[3] = (newData[2] - lastv) / deltat           # a = dv / dt
            newData[0] = t
            newData[1] = lasts + ds             # s = s_0 + ds
            newData[2] = ds / deltat            # v = ds / dt
            newData[3] = (newData[2] - lastv) / deltat           # a = dv / dt


        self.parent.outm.queue.put( tuple( newData ) )
        self.lastData = newData

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
