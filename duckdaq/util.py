# -*- coding: utf-8 -*-

import math
import os
import duckdaq
#import PySide.QtGui as QtGui

def write_csv(filename, measurement):
    """
    Writes the queue of a measurement as csv data to disk.
    The queue will be emptied.
    
    *Arguments*
        
        filename: string
            Desired filename (best absolute)
        measurement: Measurement / VirtualMeasurement
            Measurement from where to empty the queue
    
    *Returns*

        None
    
    """
    queue = measurement.queue
    ports = measurement.ports
    
    if queue.empty() == True:    # not, if nothing in queue
        return
   
   # when no filename is given, open dialog to ask for
    if filename == None:
        homeDir = os.path.expanduser("~")
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        filename = dialog.getSaveFileName(None, "Chose File", homeDir, "CSV (*.csv)")
        filename = filename[0]
        
    file = open(filename, "w") 
    
    # create header
    file.write("t;")
    lenports = len(ports)
    for port, i in zip( ports, list(range(lenports)) ):
        file.write(port)
        if i + 1 < lenports:
            file.write(";")
    file.write("\n")

    # write data to file
    while queue.empty() != True:
        data = queue.get()

        lend = len(data)
        for entry, i in zip( data, list(range(lend))):
            # True/False, can not be interpreted by qtiplot, convert to 1/0
            if entry == True:
                entry = 1
            elif entry == False:
                entry = 0
            file.write(str(entry))
            if i + 1 < lend:
                file.write(";")

        file.write("\n")
    
    file.close()


def read_csv(filename, measurement):
    """
    Reads a file (has to be written by daqjack or in adequate format) and
    puts the content into a measurement. m.ports and m.queue will be replaced
    by the contente of the file

    *Arguments*

        filename : String
            Filename to read from, best absolute
        measurement: Measurement / VirtualMeasurement
            Measurement from where to empty the queue
    
    *Returns*

        None
    
    """
   # when no filename is given, open dialog to ask for
    if filename == None:
        homeDir = os.path.expanduser("~")
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        filename = dialog.getOpenFileName(None, "Chose File", homeDir, "CSV (*.csv)")
        filename = filename[0]
   
    file = open(filename, "r") 
    
    lines = file.readlines()    # read entire file 

    header = lines.pop(0)       # write header into meas.ports
    header = header.strip()     # strip newline /whitespace
    measurement.ports = header.split(";")[1:]       # without "t" field

    with measurement.queue.mutex:
        measurement.queue.queue.clear()   # empty queue

    # add datalines to queue
    for line in lines:
        line = line.strip()        # strip newline / whitespace
       
        data = line.split(";")  # all data as list
        
        for d, i in zip(data, list(range(len(data)))):    # convert to floats (is: string)
            data[i] = float( d )

        measurement.queue.put( tuple(data) )
  
    file.close()


def plot(measurement):
    """
    Creates a quick plot via matplotlib of the data in the queue
    and displays it in an extra window. Will block until the
    windows is closed.

    *Arguments*

        measurement : Measurement / VirtualMeasurement

    *Returns*

        None

    """
    from pylab import plot, ginput, show, legend, grid

    # convert to list and transpose
    qList = queueToList(measurement.queue)

    qList = list(zip( *qList ))

    for num, column in zip( list(range(0, len(qList[1:]))), qList[1:] ):    # without time
        plot( qList[0], column,         # plot( time, voltage )
              label=measurement.ports[num] )     
    
    legend(loc='best')
    grid()
    show()


def call_qtiplot(measurement):
    """
    Opens the data in the queue in QtiPlot. Therefor the queue is saved as csv
    and a startup script is created, which commands QtiPlot to read in the file.
    QtiPlot is called via call(), means: blocking.

    *Arguments*

        measurement : Measurement / VirtualMeasurement

    *Returns*

        None

    """
    queue = measurement.queue
    ports = measurement.ports
    
    if queue.empty() == True:    # only, of data aviable
        return

    from tempfile import NamedTemporaryFile
    script = NamedTemporaryFile()   # our script will be a tempfile
    csv = NamedTemporaryFile()      # to store the data
    
    write_csv(csv.name, measurement)            # fill
    from os import fsync            # flush data to disk, otherwise no content in file
    csv.flush()
    fsync(csv.fileno())

    def writeln(line):      # adds a newline
        script.write(line + "\n") 

    # tablename, columns, rows 
    writeln("t = newTable(\"daqjack\")") # create table

    #reference:
    #void PreviewTable::importASCII(
    # const QString& fname,
    # const QString & sep,
    # int  	ignoredLines,
    # bool  renameCols,
    # bool  stripSpaces,
    # bool  simplifySpaces,
    # bool  importComments,
    # const QString & commentString,
    # int   importMode,
    # const QLocale &  	importLocale,
    # int  	endLine,
    # int  	maxRows 
    #)
    writeln("t.importASCII(\"{}\", \";\", 0, True, True, False, False)".format(csv.name) )

    script.flush()                  #flush
    fsync(script.fileno())

    from subprocess import call     # call scidavis, will block
    call(["qtiplot", "--execute ", script.name])
    
    csv.close()
    script.close()


def queueToList(queue):
    """
    Takes all items in a queue and returns them in a list in
    the right order.

    *Arguments*

        queue : Queue.Queue
            queue to convert and empty

    *Returns*
        result : list
            list of the items which were in the queue

    """
    
    import time
    result = []

    while queue.empty() != True:
        result.append( queue.get() )
    return result


def initLJ():
    """
    Opens the next aviable Labjack (U3) and returns the instance.
    If no LabJack is connected, an exception is raised.

    *Arguments*
        
        None

    *Returns*
        
        lj : U3.U3
            Instance of the LabJack device

    """
    from u3 import U3
    from re import search
    from LabJackPython import NullHandleException

    try:
        lj = U3()          # init lj
        #self.lj.reset()
        lj.getCalibrationData()
    except NullHandleException:
        return None

    return lj


def setDataDirection(labjack, portlist):
    """
    Sets the HV-Analog-In and FIO ports if a LabJack instance to digital or analog input.
    If you want to set AIN1 as digital input, specify "DIN1" in Measurement.ports. If you want
    it analog, name it "AIN1".

    The same way, i.e. "DIN5" means, that the FIO number 5 should be a digital input.

    *Arguments*

        labjack: U3.U3
            **Initalised** LabJack instance

        portslist: portlist created by Measurement.Daq_thread.create_portlist()
            already formated portlist, **not a regular list of strings**

    """
    from u3 import BitDirWrite
    
    for typ, n in portlist:
#            if n < 4:       # HV ports are hard wired
#                continue
        if typ == "D":
            labjack.configDigital(n)    # "0" is input
        if typ == "A":
            labjack.configAnalog(n)



def uiLoader(widget, file):
    """
    Loads a user interface from a qtdesigner file
    into a widget.

    *Arguments*

        widget : QtGui.QWidget or derived
            The widget, which should be replaced by the loaded one
        file : String
            filename relative to the "ui" directory 

    *Returns*
        
        None

    """
    import PySide.QtCore as QtCore
    import PySide.QtUiTools as QtUiTools

    # load user interface
    loader = QtUiTools.QUiLoader()
    filename = duckdaq.__DDPATH__ + "ui" + os.sep + file
    file = QtCore.QFile(filename)
    print(filename)
    file.open(QtCore.QFile.ReadOnly)
    loader.load(file, widget)
    file.close()


def round_sig(x, n):
    """
    Returns a real number rounded to n significant digits
    
    *Arguments*

        x : float
            number to round
        n : int
            number of significant digits

    *Returns*
        
        result : float
            argument x rounded

    """
    return round(x, int(n - math.ceil(math.log10(abs(x)))))


def meas2ndarray(meas):
    """
    Creates an ndarray from the data in the queue of a measurement.
    The queue is emptied.
    
    *Arguments*

        measurement : Measurement / VirtualMeasurement

    *Returns*

        data: np.ndarray
            The measurement data as two-dimensional ndarray.
            
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
    import numpy as np
   
    # fetch as list
    tmplist = queueToList( meas.queue )

    # create ndarray
    array = np.asarray( tmplist, dtype=np.float64 )

    return array


def meas2dataframe(meas):
    """
    Creates an pandas DataFrame from the data in the queue of a measurement.
    The queue is emptied.
    
    *Arguments*

        measurement : Measurement / VirtualMeasurement

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
    import pandas as pd
    
    # fetch as ndarray
    tmpmdata = meas.data_ndarray()
    
    # transposed array
    #tmpmdataT = tmpmdata.transpose()
    
    #idx=tmpmdataT[0].transpose()   # the index
    #data=tmpmdataT[1:].transpose() # the data

    mdata = pd.DataFrame( tmpmdata, columns=["t"] + meas.ports)  # columns are named after the ports
   
    return mdata

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
