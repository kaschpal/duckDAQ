from threading import Thread
import queue
from duckdaq import VirtualMeasurement

class Filter():
    """
    A general Filter Class. A Filter takes an input measurement and creates an output measurement,
    in which the processed data will be put.
    in Filter(), no actual data manipulation is implemented.
    To create a Filter, make an inheritance class of Filter() and Filter_Thread(). In the __init__() method
    of your Filter()-Class, self.thread_class must be set.

    If you want to write your own filter, you read the source of some of the easy ones, like Channel_Selector
    or Multiplexer.
       
    *Arguments*

        in_measurement : Measurement / VirtualMeasurement
            The ingoing data. Usually one measurement.

    *Variables*
    
        self.thread_class : Filter.Filter_Thread inheritance
            The Filter_Thread, see above
        self.inm : Measurement / VirtualMeasurement
            The measurement, which goes into the filter
        self.outm : Measurement / VirtualMeasurement
            One **or** a list of outgoing measurements.

    """
    def __init__(self, in_measurement):  # the measurement object to filter 
        self.RUNNING = False	  # can be checked, if an analysis is already RUNNING
        self.thread_class = None    #Filter_Thread

        self.inm = in_measurement          # input measurement
        self.outm = VirtualMeasurement(parentFilter=self)       # output measuremnt
        
        # copy ports entry, if the filter does not want to change anything here
        self.outm.ports = self.inm.ports

    def start(self):
        """
        Sets the status "RUNNING", then
        creates and starts the thread.

        *Arguments*

            None

        *Returns*

            None

        """
        self.RUNNING = True
        self.thread = self.thread_class(self)    # create the thread
        self.thread.start()

    def start_block(self):
        """
        Starts the thread with start() and joins the thread. This can be used, 
        when scripts want to wait for the filter to be finished before proceeding.
        It's actually a very useful method.

        *Arguments*

            None

        *Returns*

            None

        """
        self.start()
        self.thread.join()

    def stop(self):
        """
        Stops the thread and sets the status "not RUNNING".

        *Arguments*

            None

        *Returns*

            None

        """
        self.thread.terminate()     # kill thread
        self.thread.join()          # wait to finish 
        self.RUNNING = False        # useless? happens in the thread already?

    def restart(self):
        """
        Stops the thread and starts it again.
        
        **I never used this and can't think of a scenario to use it. May disappear the future.**

        *Arguments*

            None

        *Returns*

            None

        """
        self.stop()
        self.start()


class Filter_Thread(Thread):
    """
    The real data manipulation takes place in the process() method of the custom Filter_Thread().
    process() is called by run() and gets one tuple from the input queue. In process() now
    data manipulation can be implemented. The process() method writes
    into the outgoing measurment(s) itself. (access via self.parent.outm)
    The Filter_Thread() class takes care, that all measurements have their .RUNNING variable set the right way.

    *Arguments*

        parent : Filter inheritance
            The filter which created this thread

    *Variables*
        
        STOP : Bool
            Set True, if you want to abort the thread. There are methods for this too, see
            members.
    
    """
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.STOP = False               # set True, if abortion is requested

    def terminate(self):
        """
        Aborts the thread.
        
        *Arguments*

            None

        *Returns*

            None
        
        """
        self.STOP = True


    def __get_data(self):
        """
        This is used by the mainloop of the run method.
        Reads a data tuple from the inqueue. Return None, if queue is empty
        """
        try:
            data = self.parent.inm.queue.get(block=True, timeout=0.01)
        except queue.Empty:
            return None

        return data


    def process(self, data):
        """
        This is the method which has to be overloaded by any Filter_Thread inheritance.
        
        As implemented in the base class, it does literally (read: "pass") nothing.
        process() is called by run() everytime, new measurement data is aviable from
        the input measurement.

        *Arguments*

            data : tuple of the form (time, data0, data1, data2, ...)
                data to process

        *Variables*
            self.parent.outm.queue : output queue
                Actually no variable of the method, but this is where the outgoing
                data tuples have to be put. If you create a list, convert with tuple(list).

        *Returns*

            None

        """
        pass

    def run(self):
        """ 
        This runs, until the input-queue is empty **and** the input-measurement is finished. Or the thread is canceled
        by setting self.TOP (or calling self.terminate()).
        
        At first, run() sets the output measurement RUNNING, preventing filters behind this filter to stop.

        Then the central loop runs, which feeds process() with data.

        When - for any reason - we are finished, the parent filter and the output measurments are set back as
        not RUNNING.

        """
        # Make sure, the outgoing measurement(s) appear(s) as RUNNING
        if isinstance(self.parent.outm, list): # list of measurements, from Multiplexer, i.e.
            for meas in self.parent.outm:
                meas.RUNNING = True
        else:
            self.parent.outm.RUNNING = True
        
        while self.STOP == False:
            data = self.__get_data()
            
            if data == None and self.parent.inm.RUNNING == False:    # no more data chunks and measure is dead
                self.STOP == True
                break  
            elif data == None and self.parent.inm.RUNNING == True: # dont process None data
                continue
            else:
                self.process(data)

        # make things clear
        self.parent.RUNNING = False
        
        if isinstance(self.parent.outm, list): # list of measurements, from Multiplexer, i.e.
            for meas in self.parent.outm:
                meas.RUNNING = False
        else:
            self.parent.outm.RUNNING = False



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
