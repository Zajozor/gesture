# gesture

A simple accelerometer-based gesture recognition software.
Under heavy development.

Project is using pipenv for dependency management.
For PyQt5, system wide libraries may be required.

- [arduino](arduino) contains code used on the microprocessor
- [graphics](graphics) contains graphics related stuff
    - [shaders](graphics/shaders) GLSL shaders
    - [signal_canvas.py](graphics/signal_canvas.py) simply displays signals in a grid
- [input](input) processes input
    - [data_reader.py](input/data_reader.py) reads form an input parser and shows
      the results in a signal canvas
    - [input_parser.py](input/input_parser.py) reads data from serial port and parses them,
      while handling encoding errors, restarts, reconnecting, etc. has only a single buffer
- [testing](testing) contains various resources and testing scripts
    - [examples](testing/examples) contains example usages of some used libraries
    - [simulate_serial.py](testing/simulate_serial.py) simulates a connected serial port
      with random data
- [constants.py](constants.py) and [utils.py](utils.py) contain common code
    