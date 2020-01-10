sudo apt install python3-pyside python3-pyqtgraph cmake libusb-1.0-0-dev python3-pandas python3-pandas

cd /tmp
git clone https://github.com/labjack/exodriver.git
cd exodriver
sudo ./install.sh

pip3 install LabjackPython
pip install LabjackPython
