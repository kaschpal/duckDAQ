# -*- coding: utf-8 -*-

import ipywidgets as widgets
import time
import duckdaq.util as util
import duckdaq.Filter as Filter
from IPython.core.display import display
        
class Multimeter(widgets.HBox):
    def __init__(self, inm, port, unit="V"):
        super().__init__(layout=widgets.Layout(border="solid", display="flex"))
        
        self.__port_label = widgets.Label(value=port + ":  ")
        self.value_label = widgets.Label()
        self.inm = inm
        self.unit = unit
        self.port = port
        
        self.update_time = 1
        
        self.children = [self.__port_label, self.value_label]
        
        self.__Filter = Multimeter_Filter(self.inm, self)
        self.__Filter.start()

        display(self)


class Multimeter_Filter(Filter.Filter):
    def __init__(self, inm, parent):
        super().__init__(inm)
        self.thread_class = Multimeter_Filter_Thread
        self.parent = parent

class Multimeter_Filter_Thread(Filter.Filter_Thread):
    def __init__(self, parent):
        super().__init__(parent)

    def process(self, data):
        # look for the desired port to display
        portlist = self.parent.inm.ports
        i = portlist.index(self.parent.parent.port)
        
        t = data[0]   # time is the first entry
        value = data[i+1] # the port is shifted by the time-entry
        
        todisplay = util.round_sig( value, 4 )
        self.parent.parent.value_label.value = str(todisplay) + "   " + str(self.parent.parent.unit)
    
        # update the display one every ?? second
        time.sleep(self.parent.parent.update_time)
        self.parent.parent.inm.queue.queue.clear()



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
