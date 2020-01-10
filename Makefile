all: clean build 

build:
	python setup.py build

install: build
	python setup.py install

clean:
	rm -rf *.pyc dist build MANIFEST duckdaq.egg-info

