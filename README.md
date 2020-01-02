# gesture

A simple accelerometer-based gesture recognition software.
Under heavy development.

Project is using Conda environment for package management.
Use
```bash
conda env create -f environment.yml
```
to create an environment based on the used packages.

The [socat](https://linux.die.net/man/1/socat)
binary is required for simulation of the device.

- [arduino](arduino) contains code used on the microprocessor
- [graphics](graphics) contains graphics related stuff
    - [shaders](graphics/shaders) GLSL shaders
    - [signal_canvas.py](graphics/widgets/signal_grid_canvas.py) simply displays signals in a grid
- [input](input) processes input from the sensor and the user
    - [controller.py](input/controller.py) controls and runs other components
    - [data_reader.py](input/buffered_data_router.py) reads form an input parser and shows
      the results in a signal canvas
    - [input_parser.py](input/serial_port_parser.py) reads data from serial port and parses them,
      while handling encoding errors, restarts, reconnecting, etc. has only a single buffer
- [processing](processing) contains components for processing the data
    - [recorder.py](processing/consumers/recording_consumer.py) records fed gestures
- [testing](testing) contains various resources and testing scripts
    - [examples](testing/examples) contains example usages of some used libraries
    - [simulate_serial.py](testing/simulate_serial.py) simulates a connected serial port
      with random data
- [constants.py](constants.py) and [utils.py](utils.py) contain common code
   
   
   
## TODO

    
- rozmysliet si gesta
- pocet giest medzi 5 a 20, rozmysliet si tolko aby bol aj dataset
- ako to vobec robit, ci im dat zadanie a blbosti.. 
  mozno nejaky guide programcek

- jednoduche heuristiky, threshold, ked tak nieco zlozitejsie, import only
- poslat mail s clankami -> top DTW a par dalsich top

- serioznejsi model lstm, poslane repo spanie lezanie..


