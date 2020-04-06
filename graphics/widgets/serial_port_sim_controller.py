from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, QSlider

import constants as cn
from testing.simulate_serial import SerialSimulator


class SerialPortSimulatorController(QWidget):
    def __init__(self, serial_port_name_edit, *args, **kwargs):
        """
        Serial port name edit text is changed when you start the simulator
        to the appropriate serial port.
        """
        super().__init__(*args, **kwargs)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        toggle_simulation_button = QPushButton('Start serial simulator')
        simulation_info_label = QLabel('Not running')
        simulator_randomize_button = QPushButton('Randomize simulator data')
        self.serial_simulator = SerialSimulator()

        def toggle_serial():
            self.serial_simulator.exit_requested = not self.serial_simulator.exit_requested
            if not self.serial_simulator.exit_requested:
                self.serial_simulator.start()
                serial_port_name_edit.setText(self.serial_simulator.output_socket_for_app)
                simulation_info_label.setText('Running')
                toggle_simulation_button.setText('Stop serial simulator')
            else:
                simulation_info_label.setText('Not running')
                toggle_simulation_button.setText('Start serial simulator')

        toggle_simulation_button.clicked.connect(toggle_serial)

        simulator_randomize_button.clicked.connect(self.serial_simulator.randomize_data)

        main_layout.addWidget(toggle_simulation_button)
        main_layout.addWidget(simulation_info_label)
        main_layout.addWidget(simulator_randomize_button)

        # Frequency change control

        current_frequency_slider = QSlider(Qt.Horizontal)
        current_frequency_slider.setRange(2, 50)
        current_frequency_slider.setSliderPosition(cn.SIMULATOR_FREQUENCY)
        current_frequency_label = QLabel(f'{current_frequency_slider.sliderPosition()}')

        def change_simulator_frequency(frequency):
            current_frequency_label.setText(f'{frequency}')
            self.serial_simulator.set_frequency(frequency)

        current_frequency_slider.sliderMoved.connect(change_simulator_frequency)

        main_layout.addWidget(current_frequency_label)
        main_layout.addWidget(current_frequency_slider)

        QApplication.instance().aboutToQuit.connect(self.close_simulator)

    def close_simulator(self):
        self.serial_simulator.kill_socket()


if __name__ == '__main__':
    app = QApplication([])
    main_widget = QWidget()
    layout = QHBoxLayout()

    main_widget.setLayout(layout)

    edit = QLineEdit('Hai')
    layout.addWidget(edit)
    layout.addWidget(SerialPortSimulatorController(edit))
    main_widget.setFixedSize(600, 200)
    main_widget.show()
    app.exec_()
