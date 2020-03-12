Q_PUSH_BUTTON_TOGGLE_STYLE = """
QPushButton {
    background-color: rgba(50,200,50,50%); border-radius: 5px;
}
QPushButton:disabled {
    background-color: rgba(200,200,200,30%); border-radius: 5px;
}
"""

Q_PROGRESS_BAR_STYLE = """
QProgressBar {
    border: 3px solid gray;
    border-radius: 5px;
    height: 25px;
}

QProgressBar::chunk {
    background: qlineargradient(
    x1: 0, y1: 0.5,
    x2: 1, y2: 0.5,
    stop: 0 "#AA5C65",
    stop: 0.5 "#EDD982",
    stop: 1 "#7AB567"
    );
}
"""
