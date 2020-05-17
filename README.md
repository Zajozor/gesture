# Gesture

A batteries-included IMU-based gesture recognition framework.
Created for my diploma thesis.

The framework connects through a serial port to a custom
ESP8266 based device, which gathers data from five IMUs (accelerometer and gyroscope).
The GUI allows to record and inspect data from the sensors,
saving it to the disk. The export module than groups the
recorded samples into a HDF5 file, to be used in gesture classification.
The classification of the recorded samples is done in a separate project.

Project is using Conda environment for package management.
Use
```bash
conda env create -f environment.yml
```
to create an environment based on the used packages.

The [socat](https://linux.die.net/man/1/socat)
binary is required for simulation of the device.

- [export](export) contains tools for exporting the recorded data to HDF5 format
- [firmware](firmware) contains code used on the microprocessor (Platform.IO project)
- [graphics](graphics) contains sources for the GUI
    - [shaders](graphics/shaders) GLSL shaders
    - [extensions](graphics/widgets) Various Qt widgets used in the GUI
    - [event_filter.py](graphics/event_filter.py) Allows registering app-wide event callbacks
    - [styles.py](graphics/styles.py) Gathers CSS styles used in the widgets
- [input](input) processes input from the sensor and the user
    - [data_router.py](input/data_router.py) reads from a SerialPortParser and passes data to Consumers
    - [serial_port_parser.py](input/serial_port_parser.py) reads and parses data from serial port,
      while handling encoding errors, restarts, reconnecting, etc.
- [processing](processing) contains components for processing the data
    - [consumers](processing/consumers) consume data through DataRouter, either to display it in a GUI or
      for further processing
- [resources](resources) Assets for the GUI (images, models, animations) and session definitions
- [testing](testing) example resources used during development
    - [examples](testing/examples) contains example usages of some used libraries
    - [simulate_serial.py](testing/simulate_serial.py) simulates a connected serial port
      with random data
- [constants.py](constants.py) and [utils.py](utils.py) contain common code
