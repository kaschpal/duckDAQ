# -*- coding: utf-8 -*-

from threading import Thread
import os
import time

# show log messages about the measurements
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(name)s %(asctime)s > %(message)s',
                    datefmt='%I:%M:%S')

# os detection for the StreamReader / system time
if os.name == "posix":
    import multiprocessing as forkmod
    forker = forkmod.Process
    systemtime = time.time
elif os.name == "nt":
    import threading as forkmod
    forker = forkmod.Thread
    systemtime = time.clock
    time.clock()    # start timer

class Measurement():
    """
    Performs a mesurement.

    *Arguments*
        
        ports : list of strings
            A list of strings, which name the ports on which measarument should
            take place. Format is AINx, and DINx, where x is the number
            of the port.
        type : String
            type of measurement
                1) "POLL": the queue is filled while polling
                2) "STREAM": read stream data
                3) "COUNT": read counter, data in the queue is then a frequency
        max_count : int
            Specifies, how many samples should be taken. In stream mode, there will
            be some recorded some more.
        max_time : int
            Specifies, how long the measurement will take. See above for stream mode.
        delay : float
            In poll mode, between the samples this time in seconds will be delayed.
        scan_frequency : int
            In stream mode, this is the number of samples per second. Maximum is 50000,
            minimum depends on LabJack and driver, reasonable is 10000
        count_interval : float
            Time in seconds, how often the measured frequency in count-mode is put
            into the queue.
        filename : string
            Is the filename, where CSV data is saved to or read from.
            If there is no filename passed to the csv methods, this filename is used.
            If no filename is given at all, a dialog appears.
        queue : Queue.Queue
            If specified, this queue will be used to put the measurement data.
            If none is given, an empty one is created.
        


    *Variables*

        queue : Queue.Queue
            The queue, where the measurement data is put. See arguments
        ports : list of strings
            The list of ports, see arguments.
        RUNNING : bool
            Is set True, if a measurement takes place. This is important for Filters,
            which stop reading the queue, if it is empty AND self.RUNNING is False.
    """
    def __init__(self, ports=[],
                 max_count=None,
                 max_time=None,
                 count_interval=1,
                 type="POLL",
                 queue=None,
                 delay=0,
                 scan_frequency=10000,
                 filename=None):

        self.max_count = max_count  # maximum count of samples to measure
        self.count_interval = count_interval
        self.max_time = max_time    # maximum amount of time in seconds to measure
        self.delay = delay          # delay between the measumentes in seconds
        self.type = type            # type of measurement:  1) POLL: the queue is filled while polling
                                    #                       2) STREAM: read stream data
        self.scan_frequency = scan_frequency # number of samples per second for stream mode
        self.filename = filename            # filename to write data to
        self.RUNNING = False	    # check, if a daq is runnging
        self.queue=queue            # the queue to fill, has to be a Queue object. if none given we will create one
        self.ports=ports            # ports to read, is a list i.e. ["AIN0", "DIN3]

        from queue import Queue   # check, if queue is a deque. if no queue given, create one
        
        if self.queue is None:
            self.queue = Queue()
        elif type(self.queue) is not Queue:
            raise TypeError("queue argument for measurement() is not of type Queue.Queue")


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
            filename = self.filename

        from duckdaq.util import write_csv
        write_csv(filename, self)
    
    
    def data_csv_read(self, filename=None):
        """
        Reads a csv file into the queue
        
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
            filename = self.filename

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


    def findHardwareMeasurement(self, meas=None):
        """
        This method return the original hardware-based measurment,
        from which a chain of filters has its source data. Here, the
        recursion ends.

        *Arguments*
            
            meas : Measurement, VirtualMeasurement
                This is for recursion, **DO NOT USE THIS ARGUMENT**.

        *Returns*
            
            meas: Measurement, VirutalMasurement
                The found one. This instance.

        """
        return self

    def start(self):
        """
        Creates one daq thread and starts the measurement as defined
        in the class arguments. RUNNING is set True. If the daq is
        already RUNNING, nothing happens.

        *Arguments*

            None

        *Returns*

            None

        """
        if not self.RUNNING:
            self.RUNNING = True
            self.daq_thread = LJ_Daq_thread(self)    # create the collector thread
            self.daq_thread.start()
        else:
            pass


    def start_block(self):
        """
        Starts the daq with start() and joins the thread. This can be used, 
        when scripts want to wait for the daq to be finished before proceeding.
        It's actually a very useful method.

        *Arguments*

            None

        *Returns*

            None

        """
        self.start()
        self.daq_thread.join()


    def stop(self):
        """
        Stops the daq thread and RUNNING is set False. If the daq is
        not RUNNING, nothing happens.

        *Arguments*

            None

        *Returns*

            None

        """
        if self.RUNNING:
            self.daq_thread.terminate()     # kill daqthread
            self.daq_thread.join()          # wait to finish 
            #del self.daq_thread
            self.RUNNING = False
        else:
            pass

    def restart(self):
        """
        Stops the measurement, clears the queue and restarts it again.

        *Arguments*

            None

        *Returns*

            None

        """
        self.stop()
        self.queue.queue.clear()      # clear queue
        self.start()


""" Here is the real DAQ performed. """
class LJ_Daq_thread(Thread):
    def __init__(self, parent):
        Thread.__init__(self)
        self.parent = parent
        self.queue = self.parent.queue  # to put data
        self.STOP = False               # set True, if abortion is requested

        self.portlist = self.create_portlist(self.parent.ports)
        
        # create logger
        self.logger = logging.getLogger(__name__)
        
    
    def create_portlist(self, ports):
        from re import search
        portlist = []
        
        # create List of ports to read from in a more machine friendly way
        for port in ports:
            match = search('^AIN([0-3])$', port)
            if match:   # AIN in HV ports specified
                portlist.append( ("A", int(match.group(1))) )
                continue

            match = search('^DIN([4-7])$', port)
            if match:   # DIN in FIO ports
                if self.parent.type == "STREAM":        # not in stream mode
                    self.STOP = True
                    raise NotImplementedError("Stream is not aviable for digital ports. stopping.")
                portlist.append( ("D", int(match.group(1))) )
                continue
            
            match = search('^AIN([4-7])$', port)
            if match:   # AIN in FIO ports
                portlist.append( ("A", int(match.group(1))) )
                continue

        if len(portlist) != len(ports):
            print("there were not supported ports in the list")
        
        return portlist

    
    def terminate(self):
        """ abort measurement """
        self.STOP = True

    def count(self):
        counterPin = self.portlist[0][1]
        
        # lowest timer is fio4, thus lowest counter fio5
        if counterPin < 5:
            self.logger.info("Lowest port for counter is FIO 05")
            self.logger.info("  ... aborting")
            exit()
        
        self.logger.info("  placing timer on FIO" + str(counterPin - 1) )
        self.logger.info("  placing counter on FIO" + str(counterPin) )

        
        numOfCounters = 1
        clockBase = "1MHz"
        clockDivisor = 0

        import u3
        import datetime
        import time

        clkBaseStr = clockBase

        if clockBase is "1MHz":
            clockBase = 3
        elif clockBase is "4MHz":
            clockBase = 4
        elif clockBase is "12MHz":
            clockBase = 5
        elif clockBase is "48MHz":
            clockBase = 6
        else:
            self.logger.info("Invalid clockBase for timer/counter specified")
            self.logger.info("  possible: 1MHz, 4MHz, 12MHz, 48MHz")
            self.logger.info("  ... aborting")
            exit()
        
        self.logger.info("  clock frequency is " + str(clkBaseStr) )
        self.logger.info("  clock divisor is " + str(clockDivisor) )
        
        # Enable the timers, make sure no pin is set to analog
        self.lj.configIO(
                    NumberOfTimersEnabled = numOfCounters,
                    EnableCounter1=True,
                    TimerCounterPinOffset = counterPin-1,       # first comes the timer, then the counter
                    FIOAnalog = 0)

        sysTimerConf = u3.TimerConfig(0,10,0) 
        self.lj.getFeedback(sysTimerConf)

        self.lj.configTimerClock(TimerClockBase = clockBase,
                            TimerClockDivisor = clockDivisor)

        #print "U3 Configuration: ", self.lj.configU3()
        
        # handles for timer / counter
        clkTimer = u3.Timer0(False)
        counter = u3.Counter1(False)
        
        # stop systemtime from computer
        start_time = systemtime()
        number_of_measures = 0

        ##
        ##
        ## Counter Loop
        while True:
            if self.STOP is True:    # exit condition
                break

            # stop actual time
            act_time = systemtime() - start_time
           
            
            # before sleep
            startData = self.lj.getFeedback(clkTimer, counter)
            prevClock = startData[0]
            prevEvents = startData[1]
            
            # pause and wait for events
            time.sleep( self.parent.count_interval )
           
            # after sleep
            results = self.lj.getFeedback(clkTimer, counter)
            clock = results[0]
            events = results[1]
            
            # calculate frequency
            counts = events - prevEvents   # temp store here
            intervalTime = clock - prevClock   # temp store here
            deltaT = intervalTime / 4e6

            freq = float(counts) / deltaT 

            # put measures
            self.queue.put( (act_time,) + tuple([freq]) )
            #print ( (act_time,) + tuple([freq]) )


            # count and delay
            number_of_measures = number_of_measures + 1
            
            # max count/time exceeded
            if (self.parent.max_count is not None) and (number_of_measures >= self.parent.max_count):
                break
            if (self.parent.max_time is not None) and (act_time >= self.parent.max_time):
                break
    
        #self.lj.close()         # close device


    def poll(self):
        from duckdaq.util import setDataDirection
        setDataDirection(self.lj, self.portlist)
        
        from time import sleep

        start_time = systemtime()
        number_of_measures = 0
        
        # configure FIO ports to digital/analog
        
        while True:
            if self.STOP is True:    # exit condition
                break

            # stop actual time
            act_time = systemtime() - start_time
           
            results = []   # temp store here
            # measure
            for typ, n in self.portlist:
                if typ == "A":               # analog
                    results.append( self.lj.getAIN(n) )
                if typ == "D":               # digital
                    results.append( self.lj.getFIOState(n) )
                    pass

            self.queue.put( (act_time,) + tuple(results) )
            
            # count and delay
            number_of_measures = number_of_measures + 1
            sleep(self.parent.delay)

            if (self.parent.max_count is not None) and (number_of_measures >= self.parent.max_count):   # max count/time exceeded
                break
            if (self.parent.max_time is not None) and (act_time >= self.parent.max_time):
                break
        
        #self.lj.close()         # close device


    def stream_converter(self):
        from u3 import U3
        import queue

        start_time = systemtime()
        number_of_measures = 0
        
        # period of time between measures
        deltaT = 1.0 / self.parent.scan_frequency   # each dT one measurement

        start_time = systemtime() # remeasure starttime for accuracy
        # process data / mainloop
       
        while self.STOP == False:
            
            try:
                result = self.rawQueue.get(True, 1)    # wait gently for 1s
            except queue.Empty:
                # break only, of the stream_reader is already dead
                if self.stream_reader.is_alive() == True:
                    continue
                else:
                    break
           
            if result == None:      # happens at slow sample rates (why?)
                continue

            #self.stream_reader.ljLock.acquire() # assure, only one process uses it. the other one is in stream_reader 
            package = self.lj.processStreamData(result["result"])
            #self.stream_reader.ljLock.release()

            # stop actual time
            act_time = systemtime() - start_time
           
            # make a array-matrix: [[results of ain0],[results of ain1], ...]
            matrix = []
            for port in self.parent.ports:
                matrix.append(package[port])
           
            matrix = list(zip(*matrix))     # transpose matrix: [(value ain0, value ain1, ...)(value ain0, value ain1, ...) ...]

            for row in matrix:          # append as tuple
                mTime = number_of_measures * deltaT
                self.parent.queue.put( (mTime,) + tuple(row) )
                number_of_measures = number_of_measures + 1

            if (self.parent.max_count is not None) and (number_of_measures >= self.parent.max_count):   # max count/time exceeded
                break
            if (self.parent.max_time is not None) and (act_time >= self.parent.max_time):
                break


            #i = package["errors"]
            #if i != 0:
            #    print i

        

    def run(self):
        """ mainloop"""
        
        if self.STOP is True:    # exit condition: maybe set on init
            self.parent.RUNNING = False
            return
        
        # open labjack for all measurements
        from duckdaq.util import initLJ
        self.lj = initLJ()
        
        if self.lj == None:
            print("device cannot be opened. stopping. please connect device")
            raise RuntimeError
        
        # data direction registers
        from duckdaq.util import setDataDirection
        setDataDirection(self.lj, self.portlist)
        
        self.logger.info("starting measurement")
        self.logger.info("    mode: " + self.parent.type)
        self.logger.info("    maxtime: " + str(self.parent.max_time) )
        self.logger.info("    maxcount: " + str(self.parent.max_count) )
        
        #
        #   loop for Polling
        #
        if self.parent.type == "POLL":
            self.poll()


        #
        #   loop for Counters 
        #
        elif self.parent.type == "COUNT":
            self.count()


        #
        #   loop for stream mode
        #
        elif self.parent.type == "STREAM":

            # on windows we have to use a thread, on linux we can use a process
            if os.name == "posix":
                self.rawQueue = forkmod.Queue()         # temperary for raw stream data
            elif os.name == "nt":
                import queue
                self.rawQueue = queue.Queue()

            pl = [ p for (d, p) in self.portlist] # create list of ports to stream from
            self.lj.streamConfig(NumChannels=len(pl),
                                    PChannels=pl,                   # PChannels: channels to scan
                                    NChannels=[31 for i in pl],     # NChannels: "31: to GND"
                                    Resolution=3,                   # Resolution: 3 = MAX           
                                    ScanFrequency=self.parent.scan_frequency)   # samples per second
            
            self.stream_reader = LJ_Stream_Reader(rawQueue = self.rawQueue,
                                                  labjack = self.lj)
            self.stream_reader.start()
            self.stream_converter()     # loops until enough packages are read
            self.stream_reader.stop_reading() # kill daq process at exit
            
            # stream has to be closed first, wait for exit
            self.stream_reader.join()

            del self.rawQueue           # no more needed
        
        #
        #   # unknown measurement type
        #
        else: 
            raise NotImplementedError("Measurement type " + self.parent.type + " not aviable")


        self.parent.RUNNING = False
        
        self.lj.close()         # close device

        self.logger.info("measurement finished")

    
# On Linux start Process, on Windows a Thread.
# Windows does not support unpickleable argements for processees
# see beginning of the file for mechanism
class LJ_Stream_Reader(forker):
    def __init__(self, rawQueue, labjack):
        forker.__init__(self)
        
        self.rawQueue = rawQueue
        """
        self.portlist = portlist
        self.scan_frequency = scan_frequency
        self.max_count = max_count
        self.max_time = max_time
        """
        self.lj = labjack

        self.STOP = forkmod.Event()  # for clean exit

        #self.ljLock = mp.Lock() # using the lj methods needs to be restricted to only one process

    def stop_reading(self):
        self.STOP.set()

    def run(self):
        from time import time, sleep
        import copy

        # period of time between measures
        #deltaT = 1.0 / self.scan_frequency   # each dT one measurement

        #start_time = systemtime() # remeasure starttime for accuracy
        
        self.lj.streamStart() # GO!
       
        # process data / mainloop
        while not self.STOP.is_set():
            
            #self.ljLock.acquire()       # assure, only one process uses it. the other one is in stream_converter
            returnDict = next(self.lj.streamData(convert = False))
            #self.ljLock.release()

            self.rawQueue.put( copy.deepcopy(returnDict) )

        self.lj.streamStop()        # has to be called _here_
        
        #self.terminate()

        # if terminate fails
        # create logger
        logger = logging.getLogger(__name__)
        
        import os
        logger.info("termination failed, killing (SIGKILL) daq process")
        os.kill( self.pid, 9 )


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
