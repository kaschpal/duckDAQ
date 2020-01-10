# -*- coding: utf-8 -*-

## include modules directory to the path, so pyqtgraph is importable, if it is not globally installed
import os as __os #, sys

if "__DDPATH__" not in locals():     # only at first call
    __DDPATH__ = __os.path.dirname( __os.path.abspath(__file__) ) + __os.sep
    # sys.path.append( __DDPATH__ + "local-modules" + os.sep)


# Qt modules
#import PySide.QtGui as __QtGui
#import PySide.QtCore as QtCore
#import PySide.QtUiTools as QtUiTools


# parts of the module
from . import util
from .Measurement import Measurement
from .VirtualMeasurement import VirtualMeasurement
from . import Filter
#from . import Display
from . import Device


__all__ = ["util", "Measurement", "VirtualMeasurement", "Filter", "Device"]


# if not already existing, create QApplication
#if __QtGui.QApplication.instance() is None:
#    __QApp__ = __QtGui.QApplication([])
#else:
#    __QApp__ = __QtGui.QApplication.instance()


# used to terminate dd scripts
#def gui_block():
#
#    # block till all qt windows are closed
#    returncode = __QApp__.exec_()
#
#    # exit cleanly
#    exit( returncode  )


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
