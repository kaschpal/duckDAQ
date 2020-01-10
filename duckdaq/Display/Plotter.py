# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore
from sys import argv
import numpy as np
import pandas as pd
import pyqtgraph as pg

from duckdaq import Measurement, VirtualMeasurement
from duckdaq.Filter import Filter, Filter_Thread
import duckdaq
import PlotterWidgets
import threading
import time
import os

from Display import Display


#def applyPatches():
#    # Monkeypatching label remove method
#    #
#    import types
#    import PlotterMonkeyPatches
#    pg.graphicsItems.LegendItem.LegendItem.removeItem = PlotterMonkeyPatches.removeItem 
        

class Plotter(Display):
    """
    This widget displays measurement data in form of a graph. The length of the time-axis is
    taken automatically from the original hardware measurment, or has to be provided via
    argument.

    By default, the Plotter starts in live-mode, which means, it updates the graph as new
    data is read. Because in a stream measurement, data arrives in chunks, live-mode
    only works smooth for polling mode. And, of course, you need a fast machine, if
    you want live update with 50kSamples.

    The Plotter checks the queue from the measurement, so the
    live-button pops out, when measurment or the last filter is finished.
    Plots and curves can be added as desired.

    If no list of inital plots (see arguments) is specified, the
    inital display is only one tab with all curves in it.

    *Arguments*

        inm : Measurement / VirtualMeasurement
            the input measurement, if none is given, a class own will be created
        timeWindow : float
            number of seconds to show
        yMin, yMax : numeric 
            Minium and maximum values for y-axis
        startLive : Bool
            True, if the Plotter should be startd in Live-mode
        initialPlots : List of Lists of Strings
            The plots, which should be displayed initially. It is a List,
            in which each entry is List, which represents a plot tab.

            **Example**: [ ["AIN1"], ["AIN2", "AIN3"] ] means, that there
            should be two plot tabs, one with only AIN1 and one with both
            AIN2 and AIN3 in it.
        FPS : int
            approximate desired framerate
    """

    class __plotsNcurves(list):
        """
        a central register for all plots with the contained curves is created
        all this information can be obtained by asking the tabwidget and its
        plotwidgets, but is should be faster and easier (for updating curves)
        by keeping a central database
        structure is: [ [plotwidget1, [ (curve11, key), (curve12, key) ...] ],
                        [plotwidget2, [ (curve21, key), (curve22, key) ... ] ] ... 
                      ]
        """
        def __init__(self):
            list.__init__(self)
            
        def addPlot(self, plotWid):
            """ simply adds one plot without curves """
            self.append(  [ plotWid, [] ] )

        def removePlot(self, plotWid):
            """ removes a given plot with all its curves from the list """
            for plot, cklist in self:
                if plot == plotWid:
                    self.remove( [plot, cklist] )
                    return
            # no matching plot
            raise KeyError("Trying to remove nonexistant plotWidget")

        def addCurve(self, plotWid, curve, key):
            """ adds one curve with the df key to a plot """
            for entry in self:      # cycle plots
                if entry[0] == plotWid:     # is the desired plot
                    entry[1].append( (curve, key) )
                    return
            # no matching plot
            raise KeyError("Trying to add curve to a nonexistant plotWidget")
        
        def delCurve(self, plotWid, curve):
            """ deltes one curve from plot"""
            for entry in self:      # cycle plots
                if entry[0] == plotWid:     # is the desired plot
                    cklist = entry[1]   # the (curve, key)
                    for _curve, key in cklist:      # cycle
                        if _curve == curve:
                            cklist.remove( (_curve, key) )  # remove tuple
                            return

            # no matching plot
            raise KeyError("Trying to add curve to a nonexistant plotWidget")

        def getCurvesAll(self):
            """
            Gets simply all curves in the whole tabfild

            returns a list of tuples (curve, key) """
            rlist = [] # to return
            
            for plot, kcTuple in self:
                rlist = rlist + list(kcTuple)

            return rlist
        
        def getCurvesPlot(self, plot):
            """
            Gets the curves in one plot

            returns a list of tuples (curve, key) """
            
            for _plot, curves in self:
                if _plot == plot:
                    return curves 
            
            # no matching plot
            raise KeyError("trying to get curves from a plot, which does not exist")
   

    def __init__( self, inm=None,
                        timeWindow=None,
                        startLive=True,
                        yMin=0,
                        yMax=5,
                        initialPlots=None,
                        FPS=25):
        QtGui.QWidget.__init__(self)

        #applyPatches() #see beginning of file
        self.FPS = FPS
        
        # if no measurement is given, create one
        if inm == None:
             raise NotImplementedError("Show dialog for Measurement creation here. NYI")
        else:
            self.inMeas = inm
        
        # display options
        self.yRange = ( yMin, yMax )

        # here, the length of the x-axis is set
        # if the desired length is set already as paramter, things are trivial
        # otherwise, the lengt has to be read from the hardware measurement
        
        hwMeas = self.inMeas.findHardwareMeasurement()
        self.hwMeas = hwMeas    # shorter above
        # copy, nicer to read
        mxCount = hwMeas.MAX_COUNT
        mxTime = hwMeas.MAX_TIME
        freq = hwMeas.SCAN_FREQUENCY
        delay = hwMeas.DELAY
        mtype = hwMeas.TYPE
        
        if timeWindow is None:  # has to be calculated from the hardware measurment

            # infinite measurement cant be autoplotted
            if mxTime == None and mxCount == None:
                raise KeyError("Can't autoplot a measurement with no maxtime and maxcount given. specify timeWindow to Plotter() ")
            
            # "stream"-mode
            if mtype == "STREAM":
                if mxCount == None: # very easy: just maxtime given
                    self.timeWindow = mxTime
                elif mxTime == None: # quite easy: just count and frequency given
                    self.timeWindow = mxCount / freq
                else:               # take the mininum
                    self.timeWindow = min(mxTime, mxCount / freq )
                    
            # "poll"-mode
            elif mtype == "POLL" or mtype == "COUNT":
                if mxCount == None: # very easy: just maxtime given
                    self.timeWindow = mxTime
                elif mxTime == None: # quite easy: just count and delay given
                    self.timeWindow = mxCount * delay
                else:               # take the mininum
                    self.timeWindow = min(mxTime, mxCount * delay )
        else: # time window given
            self.timeWindow = timeWindow


        # set title and size
        self.resize(1000,600)
        self.setWindowTitle('Plotter')
        
        # create tabs
        self.tabWid = PlotterWidgets.HidingTabWidget(parent=self)
        self.tabWid.setTabsClosable(True)
        
        # central layout
        self.grid = QtGui.QGridLayout()
        
        # load button bar
        self.controlBar = PlotterWidgets.PlotterControlBar(parent=self)
        
        # load toolbar
        self.plotToolBar = PlotterWidgets.PlotToolBar(parent=self)
        
        # populate grid layout
        self.grid.addWidget( self.controlBar, 0, 0 )
        self.grid.addWidget( self.plotToolBar, 1, 0 )
        self.grid.addWidget( self.tabWid, 2, 0 )
        
        # central is the grid 
        self.setLayout(self.grid)
        self.show()
       
        # This is the central data storage. Measurement data is stored as a pandas DataFrame
        # Because dynamic ndarray are veryveryvers slow, the df is preallocated based
        # on maxtime, maxcount delay and samplerate
        # gladly all comparions of maxcount and so on has been done above already
        # indexing can't be done by measurement time, because they may not be aequidistant

        if mtype == "STREAM":   # simple: n = samplerate * timeWindow
            dim = freq * self.timeWindow
        
        elif mtype == "POLL" or mtype == "COUNT":
            srate = 500    # assuming 0.5kSamples in polling. is too much anyway
            dim = srate * self.timeWindow      

            # subtract delay:
            sumDelay = delay * self.timeWindow  # delay in the whole measurement
            dim = dim - sumDelay * srate
       
        dim = dim + 20000       # just to be shure

        # finally create empty dataframe
        idx = np.arange(0, dim) 
        col = ["t"] + self.inMeas.ports # add column for time
        
        self.mdata = pd.DataFrame( index=idx, columns=col, dtype=np.float64 ) # all empty with NaN

        # start datareader thread, exits, if no data left, can be restarted by refreh-button
        self.dataReader = Plotter_dataReader(self.inMeas, self)
        self.dataReader.start()

        # centryl register of plots and curves, see def at the beginning of the class
        self.plotsNcurves = self.__plotsNcurves()

        # if no inital plots are desired, create one plot for all existing ports
        if initialPlots is None:
            self.addPlot(ports=self.inMeas.ports, title="all")
        else:                           # create tab for each list
            for keylist in initialPlots:
                self.addPlot(ports=keylist, title=" ".join(keylist) )   # title is simply the keys seperated by spaced
        
        # connect Buttons
        self.controlBar.buttonUpdate.clicked.connect( self.updateClicked )
        self.controlBar.buttonLive.clicked.connect( self.liveClicked )
        self.controlBar.buttonClear.clicked.connect( self.clearClicked )
        self.controlBar.buttonQtiplot.clicked.connect( self.qtiplotClicked )
        self.controlBar.buttonCsv.clicked.connect( self.csvClicked )
        
        # bind actions for the toolbar
        self.plotToolBar.act_addPlot.triggered.connect(self.diaAddPlot)
        self.plotToolBar.act_addCurve.triggered.connect(self.diaAddCurve)
        self.plotToolBar.act_delCurve.triggered.connect(self.diaDelCurve)
        self.plotToolBar.act_addFunction.triggered.connect(self.diaAddFunction)

        # connect close of tabs, so that the plots can be removed
        self.tabWid.tabCloseRequested.connect( self.__tabCloseHandler )
        
        # create Display Updater
        self.updTimer = QtCore.QTimer(self)
        self.updTimer.timeout.connect( self.__autoUpdateCurrentPlot  )

        # if desired, start in Live-Mode
        if startLive == True:
            self.controlBar.buttonLive.click()

    
    
    def closeEvent(self, event):
        """
        Handles closing the Plotter widget. *This is a reimplementation.*
        All threads (the updater and the filter) are terminated.
        Maybe it will ask, if there is unsaved work sometime.

        *Arguments*

            event: PySide.QtGui.QCloseEvent
                Close event

        *Returns*

            None
        
        """
        self.__updaterStop()
        self.dataReader.stop()
        
        event.accept()



    def diaAddPlot(self):
        """
        Adds an empty plot to the tabfield
        
        *Arguments*

            None

        *Returns*
            
            None

        """
        self.addPlot()
        

    def penFinder(self, plot):
        """
        Tries to find a pen, which is not yet used inside a plot
        
        *Arguments*

            plot: pg.widgets.PlotWidget
                The plot in which to find a pen

        *Returns*
            pen : string
                String describing the pen, which can be passed to 
                which can be passed to setData()
        
        """
        pens = ["r", "g", "b", "c", "m", "y", "k", "w"]
        
        cnk = self.plotsNcurves.getCurvesPlot(plot) # all curves in plot
        used = []   # pens used in plot
        
        for curve, key in cnk:          # fill 
            used.append( curve.opts["pen"] )

        # cut out all pens, which are already used
        notused = [pen for pen in pens if pen not in used]
        
        if notused: # not empty
            return notused[0]   # first aviable
        else:
            return "r"
            # TODO: with more than ten curves, this is stupdid


    def diaAddCurve(self):
        """
        Displays a dialog for adding one curve to the current plot.
        The chosen curve is then added, if the dialog is escaped, nothings will
        happen.

        *Arguments*
            
            None

        *Returns*

            None
        
        """
        plot = self.tabWid.currentWidget()  # current plot
        curves = self.plotsNcurves.getCurvesPlot( plot ) # curves
        curves = [p for c, p in curves]     # extract portsname
        notplotted = [x for x in self.inMeas.ports if x not in curves]  # ports not alread inside
        notplotted.sort()

        if notplotted:  # not empty
            dia = PlotterWidgets.ListChooser( notplotted )
        
            chosen = dia.exec_()

            if chosen != 0: # something chosen
                selPort = notplotted[chosen-1]  # return one incremented
                self.addCurve(plot, selPort, pen=self.penFinder(plot) )

            else:   # dialog canceled
                pass
        else:
            pass


    def diaDelCurve(self):
        """
        Displays a dialog for deleting one curve from the current plot.
        If one is chosen, the curve is deleted, if the dialog is escaped,
        nothing will happen.

        *Arguments*

            None

        *Returns*

            None

        """
        plot = self.tabWid.currentWidget()  # current plot
        curves = self.plotsNcurves.getCurvesPlot( plot ) # curves in plot
        curves = [p for c, p in curves]     # extract portsname
        curves.sort()               # sort

        if curves:  # not empty
            dia = PlotterWidgets.ListChooser( curves )
        
            chosen = dia.exec_()

            if chosen != 0: # something chosen
                selPort = curves[chosen-1]  # return one incremented
                self.delCurve(plot, selPort)

            else:   # dialog canceled
                pass
        else:
            pass
        

    def diaAddFunction(self):
        pass


    def __tabCloseHandler(self, index):
        """ with the tab, remove the plot from the database """
        self.plotsNcurves.removePlot( self.tabWid.widget(index) )
        self.tabWid.removeTab(index)
    

    def __createVirtualMeasurement(self):
        """ creates a virtual measurement from the data in self.mdata """
        
        exportMeas = VirtualMeasurement(self, ports=self.mdata.columns[1:] )

        for i in self.mdata.index:
            exportMeas.queue.put( tuple( self.mdata.ix[i] ) )

        return exportMeas

    
    def qtiplotClicked(self):
        """
        Creates a measurement from the mdata dataframe and opens it in qtiplot
        
        *Arguments*

            None

        *Returns*

            None
        """

        self.__createVirtualMeasurement().data_qtiplot()
   

    def csvClicked(self):
        """
        Creates a measurement from mdata dataframe and opens a file dialog
        for export to cvs
        
        *Arguments*

            None

        *Returns*

            None
        
        """

        meas = self.__createVirtualMeasurement()
        meas.data_csv_write()

    
    def clearClicked(self):
        """
        Clears the mdata dataframe and updates all plots.
        The size of mdata is preserved, all data is overwritten
        with NaN.

        *Arguments*

            None

        *Returns*

            None

        """
        idx = self.mdata.index
        col = ["t"] + self.inMeas.ports # add column for time
       
        self.dataReader.thread.mdLock.acquire()       # assure, only one thread uses it
        self.mdata = pd.DataFrame( index=idx, columns=col, dtype=np.float64 ) # all empty with NaN
        self.dataReader.thread.mdLock.release()

        self.updateAll()

    def updateClicked(self):
        """
        Wrapper fuction for updateAll(), just added for readability
        
        *Arguments*

            None

        *Returns*

            None
        
        """
        self.updateAll()
    
    def liveClicked(self):
        """
        If the display updater timer is started, it will be stopped.
        If the display updater timer is stopped, it will be startd.
        The appearence of Live-Button is changed to display the state.
        
        *Arguments*
        
            None
            
        *Returns*
        
            None
            
        """
        state = self.controlBar.buttonLive.STATE

        if state == True:    # just activated
            self.__updaterStart()
        elif state == False: # just deactivated
            self.__updaterStop()

    def __updaterStart(self):
        """ start display updater """
        self.updTimer.start(0)

    def __updaterStop(self):
        """ stop display updater """
        self.updTimer.stop()

    def __autoUpdateCurrentPlot(self):
        """ wrapper fuction for live update, which checks, if
            the in-measurement is still active. Should only be
            called by the updateThread
        """
        if self.inMeas.RUNNING == True or self.inMeas.queue.empty() == False:
            # wait a bit, for not using all cpu time for updating
            time.sleep(1. / self.FPS)

            self.updateCurrentPlot()
        else:
            self.controlBar.buttonLive.click()
    
    
    def updateCurrentPlot(self):
        """
        Updates the plot currently viewed in the tabfield

        *Arguments*

            None

        *Returns*

            None

        """
        plot = self.tabWid.currentWidget()

        ckList = self.plotsNcurves.getCurvesPlot(plot)
        
        for curve, key in ckList:
            x, y = self.dataByKey(key)
            curve.setData( x=x,  y=y )        # update curve with the ned x'ses

    def updateCurve(self, curve, key):
        """
        Update one single curve in an plot
        
        *Arguments:*
            
            curve: pg.GraphicsItems.PlotCurveItem
                Curve, which should be updated
            key: string
                The name of the curve, e.g. a port "AIN0"

        *Returns*
            
            None
        
        """
        x, y = self.dataByKey(key)
        
        curve.setData( x=x,  y=y )        # update curve with the ned x'ses

    def updateAll(self):
        """
        Updates all curves with the current data
        
        *Arguments*

            None

        *Returns*

            None
        
        """
       
        for curve, key in self.plotsNcurves.getCurvesAll():
            x, y = self.dataByKey(key)
            curve.setData( x=x,  y=y )        # update curve with the ned x'ses
        
    def dataByKey(self, key, dropna=True):
        """
        Returns the stored mdata of "key" as x and y ndarray
        NaN vaulues are dropped by default (can't be plotted by pyqtgraph)

        *Arguments*
            
            key: string
                The name of the curve, e.g. a port "AIN0"
            dropna: bool
                set False, if you want NaN entries, i.e. to know
                when theses happened

        *Returns*

            x: np.ndarray
                x data (time)
            
            y: np.ndarray
                y data (values)

        """
        # retrieve 
        time = self.mdata["t"].values
        data = self.mdata[key].values
        
        if dropna == False:     # no further modification needed
            return time, data       # x, y

        else:
            # glue together to one array
            # [t1, t2, t3, t4, ...]
            # [y1, y1, y3, y4, ...]
            arrT = np.vstack( (time, data) )

            # transpose
            arr = arrT.transpose()

            # cut out the NaNs via a boolean mask:
            # http://stackoverflow.com/questions/2695503/removing-pairs-of-elements-from-numpy-arrays-that-are-nan-or-another-value-in
            arr = arr[ ~(np.isnan(arr).any(1)) ]
            
            arrT = arr.transpose()

            return arrT[0], arrT[1]


    def addSinglePlot(self, key):
        """
        Adds one tab with a single curve in it
        
        *Arguments:*
            
            key: string
                The name of the curve, e.g. a port "AIN0"

        *Returns*
            
            plotWid: pg.GraphicsItems.PlotItem
                The created Plot
        
        """
        
        plotWid = self.addPlot(ports=[key], title=key)
        
        return plotWid
   

    def addPlot(self, ports=[], title="Untitled"):
        """
        Adds one plot with zero or more curves.
       
        *Arguments*

            ports: list of strings
                The desired ports of curves
            title: string
                Title of the plot, will be displayed in the tab
        
        *Returns*
            
            plotWid: pg.GraphicsItems.PlotItem
                The created Plot

        """
        plotWid = pg.PlotWidget(parent=self.tabWid, name=title)  # create plot widget
        plotWid.addLegend()                                     # with legend
        plotWid.showGrid(x=True, y=True)                         # default: with grid
        self.tabWid.addTab(plotWid, title)                       # add as tab
        
        # set width and disable autorange
        plotWid.setRange( xRange=(0, self.timeWindow), yRange=self.yRange )    
        plotWid.disableAutoRange('xy')

        # register plot
        self.plotsNcurves.addPlot(plotWid)
      
        # add all desired ports as curves to the plot
        for port in ports:
            curve = self.addCurve(plotWid, port, pen=self.penFinder(plotWid) )               # add port as curve to tab
        
        return plotWid


    def addCurve(self, plot, key, pen):
        """
        Adds one curve to a plot

        *Arguments*
            
            plot: pg.GraphicsItems.PlotItem
                Plot, to which the curve should be added
            key: string
                The name of the curve, e.g. a port "AIN0"
            pen: string
                Pen, with which the plot should be drawed
        
        *Returns*
            
            curve: pg.GraphicsItems.PlotCurveItem
                Created curve
        
        """

        curve = plot.plot(pen=pen, name=key)                   # create curve
        self.plotsNcurves.addCurve(plot, curve, key)  # register
        x, y = self.dataByKey(key)
        curve.setData( x=x,  y=y )        # update curve with the ned x'ses
        
        return curve
    
    def delCurve(self, plotWid, key):
        """
        Removes one curve from the given plot
        
        *Arguments*
            
            plot: pg.GraphicsItems.PlotItem
                Plot from which the curve should be deleted 
            key: string
                The name of the curve, e.g. a port "AIN0"

        *Returns*

            None
        
        """

        curves = self.plotsNcurves.getCurvesPlot(plotWid) # all curves in plot
        desired = [curve for curve, name in curves if name == key][0] # the curve with the matching key

        self.plotsNcurves.delCurve(plotWid, desired)  # unregister first, else it is redrawn
        plotWid.removeItem(desired)     # remove from plot
        plotWid.plotItem.legend.removeItem(key)  # remove from legend





"""
This reads the input measurement data into the dataframe mdata. It is a simple filter.
"""
class Plotter_dataReader(Filter):
    def __init__(self, in_measurement, parent_ui):
        Filter.__init__(self, in_measurement)
        self.thread_class = Plotter_dataReader_Thread

        self.parent_ui = parent_ui  # The plotter class

class Plotter_dataReader_Thread(Filter_Thread):
    def __init__(self, parent):
        Filter_Thread.__init__(self, parent)
        
        self.i = 0   # current index of the dataframe
        self.mdLock = threading.Lock()

    def process(self, data):
        da = np.array( self.parent.parent_ui.inMeas.queue.get(), dtype=np.float64)  # as array
        
        
        self.mdLock.acquire()       # assure, only one thread uses it. the other one is clearClicked in main
        self.parent.parent_ui.mdata.ix[self.i] = da  # insert
        self.mdLock.release()
        
        self.i = self.i + 1
        
        


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
