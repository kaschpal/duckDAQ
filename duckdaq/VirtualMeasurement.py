# -*- coding: utf-8 -*-

from threading import Thread
import multiprocessing as mp

class VirtualMeasurement():
    """
    These virtual measurements are created by filters. The only have a queue and a portslist.
    The Filter, which created this vm is in self.parentFilter. This way, the original
    hardware measurement can be obtained.
       
    **Arguments**

        parentFilter : Filter
            The filter, which creates this virtual Measurement.
            This is important to find the original hardware bases Measument,
            which stands at the beginning.

        ports : list of strings
            The names of the ports can be modified already here.

        filename : string
            Is the filename, where csvdata is saved.

    **Variables**
        self.parentFilter
            the filter, which created the virtual measurement
        self.queue
            The queue, where the measurement data is put. See arguments
        self.ports
            The list of ports.
        self.RUNNING
            Is set True, if the filter is RUNNING.
    """
    def __init__(self, parentFilter, ports=[], FILE=None):
        
        self.FILE = FILE            # file to write data to
        self.RUNNING = False	    # check, if a daq is runnging
        self.ports=ports            # ports to read, is a list i.e. ["AIN0", "DIN3]

        # the filter which created this vm
        self.parentFilter = parentFilter
        
        # create queue
        from queue import Queue   
        self.queue = Queue()
    
    def findHardwareMeasurement(self, meas=None):
        """
        This method return the original hardware-based measurment,
        from which a chain of filters has its source data.
        Here, the recursion starts or passes through.

        *Arguments*
            
            meas : Measurement, VirtualMeasurement
                This is for recursion, **DO NOT USE THIS ARGUMENT**.

        *Returns*
            
            meas: Measurement, VirutalMasurement
                The found one.

        """
        from .Measurement import Measurement
        
        # first call
        if meas == None:
            return self.findHardwareMeasurement(self)        

        # if no hw measurement, call again with the filters input meas
        if type( meas ) is Measurement:
            return meas
        else:
            return meas.parentFilter.inm.findHardwareMeasurement()

    
    # reimport methods for data export
    #
    #
    def data_print(self):
        """
        Print out the aquired data, drops from queue
        
        *Arguments*

            None

        *Returns*
            
            None
        
        """
        while self.queue.empty() != True:
            print(self.queue.get())


    def data_csv_write(self, filename=None):
        """
        Writes the queue as csv data to disk
        
        *Arguments*
            
            filename: string
                Desired filename (best absolute). If no filename is given,
                filename will be used.
        
        *Returns*

            None
        
        """
        if filename is not None:
            pass
        else:
            filename = self.FILE

        from duckdaq.util import write_csv
        write_csv(filename, self)
    
    
    def data_csv_read(self, filename):
        """
        Reads a csv file into the queue
        
        *Arguments*
            
            filename: string
                Desired filename (best absolute). If no filename is given,
                filename will be used.
        
        *Returns*

            None
        
        """
        from duckdaq.util import read_csv 
        read_csv(filename, self)


    def data_qtiplot(self):
        """
        Opens the data in the queue in QtiPlot. Therefor the queue is saved as csv
        and a startup script is created, which commands QtiPlot to read in the file.

        *Arguments*

            None

        *Returns*

            None

        """
        from duckdaq.util import call_qtiplot
        call_qtiplot(self)
   

    def data_plot(self):
        """
        Creates a quick plot via matplotlib of the data in the queue
        and displays it in an extra window.

        *Arguments*

            None

        *Returns*

            None

        """
        from duckdaq.util import plot
        plot(self)


    def data_ndarray(self):
        """
        Creates an ndarray from the data in the queue.
        
        *Arguments*

            None

        *Returns*

            data: np.ndarray
                The measurement data is two-dimensional ndarray.
                
                Format:
                
                +--------+--------+--------+------+
                | time0  | time1  | time2  | ...  |
                +--------+--------+--------+------+
                | dataA0 | dataA1 | dataA2 | ...  |
                +--------+--------+--------+------+
                | dataB0 | dataB1 | dataB2 | ...  |
                +--------+--------+--------+------+
                | ...    | ...    | ...    |  ... |
                +--------+--------+--------+------+

        """
        from duckdaq.util import meas2ndarray
        return meas2ndarray(self)

    
    def data_dataframe(self):
        """
        Returns the data in the queue as pandas DataFrame

        *Arguments*

            None

        *Returns*

            df: pd.DataFrame
                The data as dataframe. Index is the time, columns are the ports.

                Format:

                ===== ==== ====
                index AIN0 AIN1
                ===== ==== ====
                t0    d0   d0
                t1    d1   d1
                t2    d2   d2
                ...   ...  ...
                ===== ==== ====
        
        """
        from duckdaq.util import meas2dataframe
        return meas2dataframe(self)


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
