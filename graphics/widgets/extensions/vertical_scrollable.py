from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel, QStackedLayout, QBoxLayout, QScrollArea


class VerticalScrollableExtension(QStackedLayout):
    """
    Takes QVBoxLayout, bundles it and returns a layout.
    The input layout is shown as vertically scrolled in the resulting layout.
    By default the direction is BottomToTop.
    """

    def __init__(self, scrolled_layout: QVBoxLayout, direction=QBoxLayout.BottomToTop, *args, **kwargs):
        super().__init__(*args, **kwargs)

        scrolled_layout.setDirection(direction)

        # First we put the layout into a widget
        container_widget = QWidget()
        container_widget.setLayout(scrolled_layout)

        # Then we create a scrollarea containing that widget
        # (if the scrollarea contained only the layout, it would not work)
        display_column_scroll_area = QScrollArea()
        display_column_scroll_area.setWidget(container_widget)

        display_column_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        display_column_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        display_column_scroll_area.setWidgetResizable(True)

        # At the end, we bundle the scrollarea into the layout
        self.addWidget(display_column_scroll_area)


if __name__ == '__main__':
    app = QApplication([])
    scrollable = QVBoxLayout()
    for i in range(50):
        scrollable.addWidget(QLabel(f'{i}'))

    main_widget = QWidget()
    main_widget.setLayout(VerticalScrollableExtension(scrollable))
    main_widget.show()
    app.exec_()
