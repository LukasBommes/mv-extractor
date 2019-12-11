## Building and Distributing

This document is intended for developers of this project. It explains first, how to a local version of the library inside the provided Docker container. Later, it explains how to build Python wheels for distribution via PyPI.


### Building from Source

The following steps explain how to build and run a local version of the library inside the provided Docker container.

0. Build and start the container image
```
sudo docker-compose build
sudo-docker-compose up
```
1. Enter interactive shell in a new terminal
```
sudo docker exec -it video_cap_dev bash
```
2. Build from source
```
python3 setup.py install
```
3. Run the test to see if everything works
```
python3 video_cap_test.py
```

### Building Python Wheels

This packages the entire application in form of binary python wheels which can be uploaded to PyPI and easily installed via pip.

Build and start the Docker container with `sudo docker-compose build` and `sudo-docker-compose up` and enter an interactive shell prompt `sudo docker exec -it video_cap_dev bash`. All following steps have to be performed inside this shell prompt.

Install all Python versions for which distribution wheels should be build
```
sudo apt-get update && sudo apt-get install python3.6 python3.7
```
Install virtual environment
```
pip3 install virtualenv
```

For each Python version (3.x) repeat the following steps
0. Enter the correct directory
```
cd /home/video_cap
```
1. Create a virtual environment
```
virtualenv --python=/usr/bin/python3.x venv3.x
```
2. Activate the environment
```
source venv3.x/bin/activate
```
3. Install packages into virtual environment
```
pip3 install pkgconfig==1.5.1 numpy==1.17.0
```
4. Create the python wheel
```
python3 setup.py bdist_wheel
```
5. Deactivate the environment
```
deactivate
```

This creates the Python wheel for distribution via PyPI. For further details refer to the [packaging guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires).

Once uploaded to PyPI, installation via `pip install video_cap` is possible on machines which run a compatible python version.
