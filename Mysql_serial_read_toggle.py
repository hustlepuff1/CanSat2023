import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QGridLayout, QSplitter, QPushButton, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QImage
from PyQt5.QtCore import QTimer, Qt, QSize
import pyqtgraph as pg
import collections

class RealTimeGraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # MySQL connection
        self.cnx = mysql.connector.connect(
            host='bifrost0602.duckdns.org',
            user='TEST',
            port=2024,
            password='1234',
            database='CANSATDB'
        )
        print('Connection Successful')

        # Create a cursor
        self.cursor = self.cnx.cursor(buffered=False)

        # Create a deque to store data values
        self.data_values = {}
        self.max_data_points = 100
        self.graph_items = {}

        # Create a list of boxes to display the graph
        self.graph_boxes = []

        # Create a main widget
        main_widget = QWidget()

        # Create a layout
        layout = QVBoxLayout()

        # Create a horizontal layout for title and image
        title_layout = QHBoxLayout()
        layout.addLayout(title_layout)

        # Create an image label for title and load an image into it
        self.title_image_label = QLabel()
        title_pixmap = QPixmap('C:/Users/82108/Desktop/title.png')  # replace with the path to your image
        self.title_image_label.setPixmap(title_pixmap.scaledToHeight(self.height() // 4))  # adjust the image size to 1/4 of the window height
        title_layout.addWidget(self.title_image_label)

        # Create an image label and load an image into it
        self.image_label = QLabel()
        image_pixmap = QPixmap('C:/Users/82108/Desktop/raro.png')  # replace with the path to your image
        self.image_label.setPixmap(image_pixmap.scaledToHeight(self.height() // 4))  # adjust the image size to 1/4 of the window height
        title_layout.addWidget(self.image_label)

        # Create toggle buttons
        self.a_toggle = QPushButton('A')
        self.g_toggle = QPushButton('G')
        self.m_toggle = QPushButton('M')
        self.alt_toggle = QPushButton('ALT')
        self.gps_toggle = QPushButton('GPS')
        self.else_toggle = QPushButton('Else')

        # Adjust button size
        for button in [self.a_toggle, self.g_toggle, self.m_toggle, self.alt_toggle, self.gps_toggle, self.else_toggle]:
            button.setFixedSize(50, 30)  # adjust the size as needed

        # Create a layout for the buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Add buttons to the layout
        button_layout.addWidget(self.a_toggle)
        button_layout.addWidget(self.g_toggle)
        button_layout.addWidget(self.m_toggle)
        button_layout.addWidget(self.alt_toggle)
        button_layout.addWidget(self.gps_toggle)
        button_layout.addWidget(self.else_toggle)

        # Connect clicked event of each button
        self.a_toggle.clicked.connect(self.show_a_graph)
        self.g_toggle.clicked.connect(self.show_g_graph)
        self.m_toggle.clicked.connect(self.show_m_graph)
        self.alt_toggle.clicked.connect(self.show_alt_graph)
        self.gps_toggle.clicked.connect(self.show_gps_graph)
        self.else_toggle.clicked.connect(self.show_else_graph)

        # Create a grid layout for the graphs
        self.graph_layout = QGridLayout()
        layout.addLayout(self.graph_layout)

        # Create data names and boxes to display the graph and add them to the grid
        query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'SENSOR' AND TABLE_SCHEMA = 'CANSATDB'"
        self.cursor.execute(query)
        column_names = self.cursor.fetchall()[1:]
        self.sorted_column_names = column_names
        self.sorted_column_names.remove(('elapsed_time',))  # remove the 'elapsed_time' column
        for i, column_name in enumerate(self.sorted_column_names):
            graph_widget = pg.PlotWidget()
            self.graph_boxes.append(graph_widget)

            # Create a graph data series
            self.graph_items[column_name[0]] = pg.PlotDataItem(pen=pg.intColor(i, hues=len(self.sorted_column_names)-1))
            self.graph_boxes[i].addItem(self.graph_items[column_name[0]])

            # Create a deque to store data values
            self.data_values[column_name[0]] = collections.deque(maxlen=self.max_data_points)

            # Add title to each graph
            self.graph_boxes[i].setTitle(column_name[0])

        # Set the grid layout on the main widget
        main_widget.setLayout(layout)

        # Set background image
        oImage = QImage("C:/Users/82108/Desktop/background.png") # replace with the path to your background image
        sImage = oImage.scaled(QSize(self.width(), self.height()))  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(1, QBrush(sImage))  # 10 = Windowrole
        main_widget.setPalette(palette)
        main_widget.setAutoFillBackground(True)

        # Set the main widget as the central widget
        self.setCentralWidget(main_widget)

        # Create a timer and connect it
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(100)  # update every 0.1 seconds

    def show_a_graph(self):
        self._show_graphs(['ax', 'ay', 'az'])

    def show_g_graph(self):
        self._show_graphs(['gx', 'gy', 'gz'])

    def show_m_graph(self):
        self._show_graphs(['mx', 'my', 'mz'])

    def show_alt_graph(self):
        self._show_graphs(['temp', 'pressure', 'alt'])

    def show_gps_graph(self):
        self._show_graphs(['lat', 'longi', 'gpsalt'])

    def show_else_graph(self):
        self._show_graphs(['light', 'Heading'])

    def _show_graphs(self, column_names):
        # Clear the layout
        for i in reversed(range(self.graph_layout.count())): 
            self.graph_layout.itemAt(i).widget().setParent(None)

        # Add graphs to the layout
        for i, column_name in enumerate(column_names):
            idx = self.sorted_column_names.index((column_name,))  # find the index of the column_name
            row = i // 3  # row number
            col = i % 3  # column number
            self.graph_layout.addWidget(self.graph_boxes[idx], row, col)

    def update_graph(self):
        # Execute SQL query
        query = 'SELECT ax, ay, az, gx, gy, gz, mx, my, mz, temp, pressure, alt, lat, longi, gpsalt, light, Heading FROM SENSOR ORDER BY elapsed_time DESC LIMIT 1'
        self.cursor.execute(query)

        # Fetch results
        result = self.cursor.fetchone()

        # Print results
        if result is not None:
            for i, column_name in enumerate(self.sorted_column_names):
                self.data_values[column_name[0]].append(result[i])
                self.graph_items[column_name[0]].setData(range(len(self.data_values[column_name[0]])), self.data_values[column_name[0]])

        self.cnx.commit()

    def resizeEvent(self, event):
        # Update pixmap scaling when window size changes
        self.title_image_label.setPixmap(self.title_pixmap.scaledToHeight(self.height() // 4))
        self.image_label.setPixmap(self.image_pixmap.scaledToWidth(self.width() // 4))

        # Update background image scaling when window size changes
        oImage = QImage("C:/Users/82108/Desktop/background.png")
        sImage = oImage.scaled(QSize(self.width(), self.height()))
        palette = QPalette()
        palette.setBrush(1, QBrush(sImage))
        self.centralWidget().setPalette(palette)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimeGraphWindow()
    window.setWindowTitle('Guardians of Galaxy Ground Station')
    window.showMaximized()
    sys.exit(app.exec_())
