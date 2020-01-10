#########
TODO List
#########

release 0.1
===========

- (done) filter NaN entries from series in plotter before plotting
- (done) fix SpikeWheel
- (done) reimplement processing
- (done) windows port
- (done) add/delete curves/plots in Plotter
- (done) add plot legend
- (done) delted curves should be removed from the legend
- (done) live update should stop, when the measurment is idle
- (done) fix some start/stop issues in measurement
- (done) add qtiplot to plotter
- (done) add csv export to plotter
- (done) include the filter thread *into* the filter class? --> NO!
- (done) fix segmentation fault of plotter
- (done) stopwatch should be a qwidget
- (done) voltmeter should be a qwidget
- (done) add hold button functionalty to voltmeter
- (done) logging
- (done) list of plots as argument in Plotter
- (done) implement data_ndarray right
- (done) rewrite the whole configuration mess
- (done) add framerate / let plotter sleep a while
- (done) plotter should stop, when the laster filter runs out, not the
    original hw-measurement
- (done) add counter mode


- add path only, if not alread added in __init__.py

- documentation: api reference
- documentation: installation
- documentation: tutorial

- polish stopwatch, possibility of specifying mass, diameter, ...
- add voltage divider filter
- read EDITOR enviroment variable


release 0.2 or later
====================

- add output
- add single shot mode
- add "kill hw measurement at exit" option to displays
- select and delete data regions in Plotter
- gui for measurement
- at doubleclick rename plot/tab
- type all filters by use of ndarrays insted of tuples
- fits in plotter
- functions in plotter
- allocate new memory, when the mdata overflows in Plotter
- add error handling for streaming
- specify at voltmeter, which port to display
- move labjack calls out of Measurement.py to prepare support of other devices
