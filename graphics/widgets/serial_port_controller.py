import os

from PyQt5.QtWidgets import QWidget, QLineEdit, QLabel, QPushButton, QGridLayout, QVBoxLayout, QApplication, \
    QComboBox, QFrame
from vispy import app

import constants as cn
from graphics.widgets.serial_port_sim_controller import SerialPortSimulatorController
from graphics.widgets.visual_console_logger import VisualConsoleLogger
from input.serial_port_parser import SerialPortParser


class SerialPortController(QWidget):
    def __init__(self, serial_port_parser_instance: SerialPortParser, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.serial_port_parser_instance = serial_port_parser_instance

        self.serial_port_name_edit = QLineEdit(self.serial_port_parser_instance.serial_port_name)

        self.start_button = QPushButton('🚀 Start serial input')
        self.stop_button = QPushButton('🌑 Stop serial input️')
        self.active_indicator_label = QLabel('')

        def start_serial_port_parser():
            self.serial_port_parser_instance.set_serial_port_name(
                self.serial_port_name_edit.text()
            )
            self.serial_port_parser_instance.start(threaded=True)

        self.start_button.clicked.connect(start_serial_port_parser)

        def stop_serial_port_parser():
            self.serial_port_parser_instance.stop_serial()

        self.stop_button.clicked.connect(stop_serial_port_parser)

        self.serial_port_name_edit.textChanged.connect(
            lambda text: self.serial_port_parser_instance.set_serial_port_name(text)
        )

        self.serial_port_name_combo_box = QComboBox()

        def update_serial_port_name_choices(_):
            self.serial_port_name_combo_box.clear()
            self.serial_port_name_combo_box.addItems(
                map(
                    lambda x: f'/dev/{x}',
                    filter(
                        lambda x: x.startswith('ttys') or x.startswith('cu'),
                        os.listdir('/dev')
                    )
                )
            )

        # TODO properly bind to opening combo box ? -> subclass combobox with custom event filter
        update_serial_port_name_choices(None)

        self.refresh_choices_button = QPushButton('Refresh choices')
        self.refresh_choices_button.clicked.connect(update_serial_port_name_choices)

        def set_serial_port_name_from_choices(text):
            if self.serial_port_name_edit.isEnabled():
                self.serial_port_name_edit.setText(text)

        self.serial_port_name_combo_box.currentTextChanged.connect(set_serial_port_name_from_choices)

        self.start_button.setFont(cn.EMOJI_FONT)
        self.stop_button.setFont(cn.EMOJI_FONT)
        self.active_indicator_label.setFont(cn.EMOJI_FONT)

        visual_console_logger = VisualConsoleLogger(spp_instance=serial_port_parser_instance)

        widget_layout = QGridLayout()
        self.setLayout(widget_layout)
        widget_layout.setColumnStretch(1, 5)
        widget_layout.addWidget(visual_console_logger.native, 0, 1, 12, 1)
        widget_layout.addWidget(self.active_indicator_label, 0, 0)
        widget_layout.addWidget(self.start_button, 1, 0)
        widget_layout.addWidget(self.stop_button, 2, 0)
        widget_layout.addWidget(QLabel('Serial port name:'), 3, 0)
        widget_layout.addWidget(self.serial_port_name_combo_box, 4, 0)
        widget_layout.addWidget(self.refresh_choices_button, 5, 0)
        widget_layout.addWidget(self.serial_port_name_edit, 6, 0)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        widget_layout.addWidget(separator, 7, 0)

        widget_layout.addWidget(SerialPortSimulatorController(
            self.serial_port_name_edit
        ), 8, 0, 3, 1)

        # This needs to be bound to self otherwise is garbage collected
        # TODO do this reactively instead of polling
        self.state_label_timer = app.Timer(interval=0.25, connect=self.update_state_label, start=True)

    def update_state_label(self, _):
        spp_active = self.serial_port_parser_instance.target_active_state
        self.start_button.setEnabled(not spp_active)
        self.stop_button.setEnabled(spp_active)
        self.serial_port_name_edit.setEnabled(not spp_active)
        self.serial_port_name_combo_box.setEnabled(not spp_active)

        if self.serial_port_parser_instance.target_active_state and \
                self.serial_port_parser_instance.current_active_state:
            self.active_indicator_label.setText('Serial port: <br />❇️ connected')
        elif self.serial_port_parser_instance.target_active_state:
            self.active_indicator_label.setText('Serial port: <br />⚠️ connecting..')
        else:
            self.active_indicator_label.setText('Serial port: <br />⛔ disconnected')


if __name__ == '__main__':
    q_app = QApplication([])
    main_widget = QWidget()
    layout = QVBoxLayout()
    main_widget.setLayout(layout)

    spc = SerialPortController(SerialPortParser('test'))
    layout.addWidget(spc)

    main_widget.show()
    q_app.exec_()
