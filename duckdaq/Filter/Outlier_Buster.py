# -*- coding: utf-8 -*-

from .Filter import Filter, Filter_Thread

class Outlier_Buster(Filter):
    """
    Deletes outliners from measurement. Outliers are single values, which are a certain voltage higher / lower, than
    the two surrounding values. The outliners are replaced by "None"
        
    *Arguments*

        in_measurement : Measurement / VirtualMeasurement
            Measurement to read from
        th : float
            Threshold of voltage. Only if the outlier is has a value of
            "th" more than the surrounding two, it is removed
    
    *Variables*
        outm : VirtualMeasurement
            The created new Measurement.
        
    """
    def __init__(self, in_measurement, th=2):
        Filter.__init__(self, in_measurement)
        self.thread_class = Outlier_Buster_Thread
        self.th = float(th)

class Outlier_Buster_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
        self.nextToLastData = [None, ] * ( len(self.parent.inm.ports) + 1)
        self.lastData = [None, ] * ( len(self.parent.inm.ports) + 1)         # init
    
    def process(self, data):
        newData = [None, ] * len(data)   # must be a list, tuples dont support assignment
        
        if self.nextToLastData[0] == None and self.lastData[0] == None:        # first call, fill first entry, then quit
            self.nextToLastData = data
            return
        
        elif self.lastData[0] == None:   # second call, fill second entry, then quit
            self.lastData = data
            return
       
        else:   # not first call
            for val, lval, ntlval, i in zip( data[1:], self.lastData[1:],  self.nextToLastData[1:], list(range(1, len(data))) ): 
                if lval > val + self.parent.th and lval > ntlval + self.parent.th:  # high outliner 
                    newData[i] = None
                elif lval < val-self.parent.th and lval < ntlval-self.parent.th: # low outliner
                    newData[i] = None
                else:
                    newData[i] = lval

        # shift
        self.nextToLastData = self.lastData
        self.lastData = data

        newData[0] = self.lastData[0]            # clone time
#        self.lastData = tuple( newData )    # save
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
