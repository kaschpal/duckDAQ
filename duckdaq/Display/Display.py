# -*- coding: utf-8 -*-

class Display():
    """
    This is class, from which any display has to be inherited.
    Right now, it is nothing more than a QWidget with another name.

    The Display can initialize as a gui window and then update of the
    data is performed by the Filter mechanism.
    (See creation of Filters.)

    A very simple Display is the Voltmeter, look into its sources, if you
    want to write your own Display.

    *Arguments*
        
        inmeas : Measurement / VirtualMeasurement
            The Measurement, which should be displayed
        updateTime : float
            How often, the display should be updated.

    """

    def __init__(self, inmeas, updateTime=1):
        QtGui.QWidget.__init__(self)

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
