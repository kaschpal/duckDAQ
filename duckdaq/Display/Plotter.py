# -*- coding: utf-8 -*-

import ipywidgets as widgets
import duckdaq as dd
import duckdaq.Filter as Filter
import time
import bqplot as bq
from IPython.display import display
import pandas as pd
import numpy as np
import threading


class Plotter(widgets.HBox):
    """
    Displays the value of the given port in the in_measurement.

    *Arguments*
        in_measurement : Measurement / VirtualMeasurement
            Input measuremnt
        update_time : int / float
            Delay in seconds between the updates of the display
        ports : list of strings
            The name of the ports to display, has to be in the portlist of
            in_measurement

    *Variables*
        update_time : int / float
            Delay in seconds between the updates of the display
        df : pandas Datafrme
            All values for in_measurement are stored here
        dflock : thereading.Lock
            lock for the dataframe; always use
                width dflock:
                    do something
            when working with df, if the Plotter is running.

    """
    def __init__(self, inm, ports=None, update_time = 0.1):
        super().__init__(layout=widgets.Layout(border="solid", display="flex"))

        self.inm = inm
        self.update_time = update_time     # delay for updating the plot

        if ports == None:
            self.ports = self.inm.ports
        else:
            self.ports = ports

        # create empty dataframe with "t" and the portlist
        self.df = pd.DataFrame(columns=["t"]+self.ports)
        self.dflock = threading.Lock()    # the filter must not write, when we are reading

        self.__Filter = Plotter_Filter(inm, self)
        self.__Filter.start()

        display(self)

        # first call: create figure
        self.upd_plot = self.__init_plt

        while inm.RUNNING == True:
            self.upd_plot()
            time.sleep(self.update_time)

    """ First call: create figure """
    def __init_plt(self):

        # if there is no data yet, abort
        if len(self.df.index) == 0:
            return

        # read data from the filter-thread
        with self.dflock:
            tt = self.df["t"]     # time-scale
            yy = self.df[self.ports]
        yy = yy.transpose()   # is in wrong order

        t_scale = bq.LinearScale()
        y_scale = bq.LinearScale()
        ax_y = bq.Axis(scale=y_scale, orientation='vertical', tick_format='0.2f',
                grid_lines='solid')
        ax_t = bq.Axis(scale=t_scale, grid_lines='solid', label='t in s')

        self.lines = bq.Lines(x=tt, y=yy, scales={'x': t_scale, 'y': y_scale},
                 stroke_width=3, display_legend=True, labels=self.ports)

        # plot figure
        fig = bq.Figure(marks=[self.lines], axes=[ax_t, ax_y],
               legend_location='bottom-right')
        # add toolbar
        tb = bq.Toolbar(figure=fig)

        self.children = [tb, fig]   # fill vbox

        # figure is created; now only update
        self.upd_plot = self.__update

    """ from now on: only update plot x/y-data """
    def __update(self):
        with self.dflock:
            tt = self.df["t"]     # time-scale
            yy = self.df[self.ports]

        yy = yy.transpose()

        self.lines.x = tt
        self.lines.y = yy


class Plotter_Filter(Filter.Filter):
    def __init__(self, inm, parent):
        super().__init__(inm)
        self.thread_class = Plotter_Filter_Thread
        self.parent = parent

class Plotter_Filter_Thread(Filter.Filter_Thread):
    def __init__(self, parent):
        super().__init__(parent)
        #self.fig_empty = parent.parent.fig_empty
        self.parent = parent
        self.first = True

    def __append_to_df(self, data):
        tmplist = [data]
        tmparray = np.asarray( tmplist, dtype=np.float64 )
        mdata = pd.DataFrame( tmparray, columns=["t"] + self.parent.parent.inm.ports)

        with self.parent.parent.dflock:
            self.parent.parent.df = self.parent.parent.df.append(mdata)

    def process(self, data):
        self.__append_to_df(data)
