from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtGui import QFont
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import mysql.connector
import vtk

center=[0,0,0]

class MainWindow(QtWidgets.QMainWindow):
    global center
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.stable_start_time = None
        
        self.frame = QtWidgets.QFrame()
        self.vl = QtWidgets.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.status_label = QtWidgets.QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)  # Align the label horizontally center

        font = QFont()
        font.setPointSize(20)  # Set font size to 20 points
        self.status_label.setFont(font)

        self.vl.addWidget(self.status_label)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        # Read the STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName("C:/Users/82108/Desktop/캡스톤디자인/인벤터도면/조립품/캔샛.stl")

        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

         # Create an actor
        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)

        # Calculate center of the data
        reader.Update()
        bounds = reader.GetOutput().GetBounds()
        center = [(bounds[0] + bounds[1]) / 2, (bounds[2] + bounds[3]) / 2, (bounds[4] + bounds[5]) / 2]
        print(center)

        # Move the actor to align with the origin
        transform = vtk.vtkTransform()
        transform.Translate(-center[0], -center[1], -center[2])
        self.actor.SetUserTransform(transform)

        self.ren.AddActor(self.actor)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_rotation)
        self.update_timer.start(10)  # Update every second

        self.ren.ResetCamera()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)
        
        self.show()
        self.iren.Initialize()

    def update_rotation(self,center):
        angles = self.get_angles()
        #print(angles)
        if angles is not None:
            ang_x, ang_y, heading = angles
            # Create a transform that rotates the actor
            transform = vtk.vtkTransform()
            transform.Translate(center[0], center[1], center[2])
            transform.RotateX(ang_x)
            transform.RotateY(ang_y)
            transform.RotateZ(heading)
            transform.Translate(-center[0], -center[1], -center[2])

            # Apply the transform to the actor
            self.actor.SetUserMatrix(transform.GetMatrix())

            # Render the scene
            self.iren.Render()

            # Check the stability of the angles
            if abs(ang_x) <= 5 and abs(ang_y) <= 5:
                if self.stable_start_time is None:
                    self.stable_start_time = QTime.currentTime()
                elif self.stable_start_time.secsTo(QTime.currentTime()) >= 5:
                    self.status_label.setText("Stable")
                    self.status_label.setStyleSheet("background-color: green")  # Set background color to green when Stable
            else:
                self.stable_start_time = None
                self.status_label.setText("Unstable")
                self.status_label.setStyleSheet("background-color: red")  # Set background color to red when Unstable

    @staticmethod
    def get_angles():
        cnx = mysql.connector.connect(
            host='bifrost0602.duckdns.org',
            user='TEST',
            port=2024,
            password='1234',
            database='CANSATDB'
        )

        cursor = cnx.cursor()
        query = "SELECT angy, angx, HEADING FROM SENSOR ORDER BY elapsed_time DESC LIMIT 1"
        cursor.execute(query)

        row = cursor.fetchone()
        if row is not None:
            return row
        else:
            return None

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())