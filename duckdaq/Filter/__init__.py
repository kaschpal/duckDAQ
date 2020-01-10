# -*- coding: utf-8 -*-

from .Filter import Filter, Filter_Thread

from .Channel_Selector import Channel_Selector
from .Inverter import Inverter
from .Multiplexer import Multiplexer
from .ChannelSplitter import ChannelSplitter
from .ChannelMerger import ChannelMerger
from .SchmittTrigger import SchmittTrigger
from .Outlier_Buster import Outlier_Buster
from .EdgeFinder import EdgeFinder

__all__ = ["Filter", "Filter_Thread", "Channel_Selector",
            "Inverter", "Multiplexer", "ChannelSplitter", "ChannelMerger", "SchmittTrigger", "Outlier_Buster", "EdgeFinder"]

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
