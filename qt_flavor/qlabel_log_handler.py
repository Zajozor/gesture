import logging


class QLabelHandler(logging.Handler):
    def __init__(self, label):
        super(QLabelHandler, self).__init__(logging.DEBUG)
        self.current_lines = []
        self.label = label

    def emit(self, record):

        entry = self.format(record)
        self.current_lines.append(entry)
        self.label.setText('\n'.join(self.current_lines))
        self.label.adjustSize()
        self.label.parent().parent().verticalScrollBar()\
            .setSliderPosition(self.label.parent().parent().verticalScrollBar().maximum())
