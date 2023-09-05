import os
import re
import glob
import sys
import shutil
import datetime
import mysql.connector
import numpy as np
from math import sin,pi,cos
import time
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QGridLayout, QSplitter, QPushButton, QHBoxLayout, QSizePolicy, QLineEdit, QSpacerItem
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QImage, QColor
from PyQt5.QtCore import QTimer, Qt, QSize, QThread, pyqtSignal
import pyqtgraph as pg
import collections
import get_dataframe
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk



def Ground():

    class MyHandler(FileSystemEventHandler):
        def __init__(self, window):
            self.window = window

        def on_modified(self, event):
            # 파일 들어왔을때 이미지 업데이트
            self.window.current_image_index += 1
            self.window.update_image()

    def set_dark_theme(app):
        # 기본 색 설정
        palette = QPalette()

        palette.setColor(QPalette.Window, QColor(20, 20, 20))  # Darker background color
        palette.setColor(QPalette.WindowText, Qt.white)  # Keep white text
        palette.setColor(QPalette.Base, QColor(15, 15, 15))  # Darker base color
        palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))  # Slightly lighter than base
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(25, 25, 25))  # Darker buttons
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 120, 215))  # Slightly darker link color
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))  # Slightly darker highlight
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)

    class RealTimeGraphWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            # MySQL 연결
            self.cnx = mysql.connector.connect(
                host='bifrost0602.duckdns.org',
                user='TEST',
                port=2024,
                password='1234',
                database='CANSATDB'
            )
            print('Connection Successful')

            # 커서 설정
            self.cursor = self.cnx.cursor(buffered=False)

            # 그래프 데이터 담을 리스트
            self.data_values = {}
            self.max_data_points = 100
            self.graph_items = {}

            # 그래프 표시용 데이터 담을 리스트
            self.graph_boxes = []

            # 전체 프로그램 창 생성
            main_widget = QWidget()

            # 창 크기 설정
            self.setFixedSize(1664, 936)

            # 레이아웃 만들기
            layout = QVBoxLayout()

            # 전체 창 안에 레이아웃 설정
            main_widget.setLayout(layout)

            # 수평의 분리창 만들기
            splitter = QSplitter(Qt.Horizontal)

            ##################### 타이틀 부분 ##########################

            title_widget=QWidget()
            title_layout=QHBoxLayout()
            
            # 라벨 생성 및 텍스트 설정
            title_label = RainbowTitle("가디언즈 오브 갤럭시 지상국")
            title_layout.addWidget(title_label)
            title_widget.setLayout(title_layout)
            title_label.setAlignment(Qt.AlignCenter)
            title_widget.setStyleSheet("""
                                        color: black; 
                                        background-color: rgb(115,108,122);
                                        border-radius: 10px;
                                        font-size: 50px;
                                        """)
            
            layout.addWidget(title_widget)

            ######################  왼쪽 부분 큰틀 생성   ######################
            left_widget = QWidget()
            left_layout = QGridLayout()
            
            # 이미지 이름 레이아웃
            imagename_layout=QVBoxLayout()
            left_layout.addLayout(imagename_layout,1,0)

            # 텍스트 레이아웃
            text_layout=QVBoxLayout()
            left_layout.addLayout(text_layout,2,0)

            #이미지 레이아웃
            image_layout=QVBoxLayout()
            left_layout.addLayout(image_layout,3,0)
            image_layout.setContentsMargins(10,10,10,10)

            left_widget.setLayout(left_layout)

            left_layout.setSpacing(0)

            left_widget.setStyleSheet("""
                                      background-color: rgb(40,40,40);
                                      border-radius: 20px;
                                      """)
            
            #stl 파일 띄우기
            self.frame = QtWidgets.QFrame()
            self.vl = QtWidgets.QVBoxLayout()
            self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
            self.vl.addWidget(self.vtkWidget)

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

            self.ren.AddActor(self.actor)

            self.ren.ResetCamera()

            self.frame.setLayout(self.vl)
            self.setCentralWidget(self.frame)
            
            self.show()
            self.iren.Initialize()

            left_layout.addWidget(self.frame,5,0)

            self.update_rotation(300,30,0)

            # 그래프 타이머
            self.cansattimer = QTimer()
            self.cansattimer.timeout.connect(self.update_graph)
            self.cansattimer.start(100)  # update every 0.05 seconds

            # Image Display 객체 인식된 이미지
            self.image_label = QLabel(self)
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setStyleSheet(""" 
                                           background-color: black;
                                           border-radius: 20px;
                                           """)
            self.image_directory = 'C:/Users/82108/Desktop/CANSAT DATA/image'

            # 텍스트 라벨 추가
            self.text_data_label = QLabel(self)
            text_layout.addWidget(self.text_data_label)

            # 객체 인식된 이미지 이름 라벨 추가
            self.image_name_label = QLabel(self)
            self.image_name_label.setAlignment(Qt.AlignCenter)
            self.image_name_label.setStyleSheet("""
                                                color: black; 
                                                background-color: rgb(115,108,122);
                                                border-radius: 10px;
                                                font-size: 35px;
                                                """)
            imagename_layout.addWidget(self.image_name_label)

            # data의 이름 추가
            self.text_data_label = QLabel(self)
            self.text_data_label.setAlignment(Qt.AlignCenter)
            self.text_data_label.setWordWrap(True)  # Enable word wrap

            # data 이름 높이 설정
            self.text_data_label.setFixedHeight(50)
            imagename_layout.addWidget(self.text_data_label)

            # 이미지들 리스트 sort
            def extract_number(f):
                s = re.search(r'\d+', os.path.basename(f))
                return int(s.group()) if s else None
            
            # glob을 이용하여 이미지 파일 리스트 생성
            self.image_files = glob.glob(os.path.join(self.image_directory, "*.*"))  # "*.*"는 모든 파일을 의미합니다.

            # 숫자를 추출하여 파일 목록을 정렬
            self.image_files = sorted(self.image_files, key=extract_number)
            self.current_image_index = 0  # Set an index to keep track of the current image

            # 이미지 라벨 크기, 이미지 띄우기
            self.image_label.setFixedSize(500, 400)
            image_layout.addWidget(self.image_label)

            # 와치독 옵저버
            self.event_handler = MyHandler(self)
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler, self.image_directory, recursive=False)
            self.observer.start()

            ######################  오른쪽 부분 큰틀 생성   ######################
            right_widget = QWidget()
            right_layout = QVBoxLayout()
            right_widget.setLayout(right_layout)

            ######################    버튼 스타일 설정      ######################
            self.accel_toggle = QPushButton('Accel')
            self.accel_toggle.setStyleSheet("""
                                            QPushButton {
                                                background-color: rgb(220,220,220);
                                                color: black;
                                                border-radius: 10px; 
                                                font-size: 15px;
                                            }
                                            QPushButton:hover {
                                                background-color: red;
                                                }
                                            QPushButton:pressed {
                                                background-color: green;
                                                }
                                            """)

            self.gyro_toggle = QPushButton('Gyro')
            self.gyro_toggle.setStyleSheet("""
                                            QPushButton {
                                                background-color: rgb(220,220,220);
                                                color: black;
                                                border-radius: 10px; 
                                                font-size: 15px;
                                            }
                                            QPushButton:hover {
                                                background-color: red;
                                                }
                                            QPushButton:pressed {
                                                background-color: green;
                                                }
                                            """)

            self.angle_toggle = QPushButton('Angle')
            self.angle_toggle.setStyleSheet("""
                                            QPushButton {
                                                background-color: rgb(220,220,220);
                                                color: black;
                                                border-radius: 10px; 
                                                font-size: 15px;
                                            }
                                            QPushButton:hover {
                                                background-color: red;
                                                }
                                            QPushButton:pressed {
                                                background-color: green;
                                                }
                                            """)

            self.gps_toggle = QPushButton('GPS')
            self.gps_toggle.setStyleSheet("""
                                            QPushButton {
                                                background-color: rgb(220,220,220);
                                                color: black;
                                                border-radius: 10px; 
                                                font-size: 15px;
                                            }
                                            QPushButton:hover {
                                                background-color: red;
                                                }
                                            QPushButton:pressed {
                                                background-color: green;
                                                }
                                            """)

            self.atmo_toggle = QPushButton('Atmo')
            self.atmo_toggle.setStyleSheet("""
                                            QPushButton {
                                                background-color: rgb(220,220,220);
                                                color: black;
                                                border-radius: 10px; 
                                                font-size: 15px;
                                            }
                                            QPushButton:hover {
                                                background-color: red;
                                                }
                                            QPushButton:pressed {
                                                background-color: green;
                                                }
                                            """)

            self.else_toggle = QPushButton('Light')
            self.else_toggle.setStyleSheet("""
                                            QPushButton {
                                                background-color: rgb(220,220,220);
                                                color: black;
                                                border-radius: 10px; 
                                                font-size: 15px;
                                            }
                                            QPushButton:hover {
                                                background-color: red;
                                                }
                                            QPushButton:pressed {
                                                background-color: green;
                                                }
                                            """)

            # 이미지 찾는 버튼 설정
            self.previous_image_button = QPushButton("<")
            self.previous_image_button.setStyleSheet("""
                                            QPushButton {
                                                background-color: rgb(128,128,128);
                                                color: white;
                                                border-radius: 10px; 
                                                font-size: 50px;
                                            }
                                            QPushButton:hover {
                                                background-color: red;
                                                }
                                            QPushButton:pressed {
                                                background-color: green;
                                                }
                                            """)

            self.next_image_button = QPushButton(">")
            self.next_image_button.setStyleSheet("""
                                            QPushButton {
                                                background-color: rgb(128,128,128);
                                                color: white;
                                                border-radius: 10px; 
                                                font-size: 50px;
                                            }
                                            QPushButton:hover {
                                                background-color: red;
                                                }
                                            QPushButton:pressed {
                                                background-color: green;
                                                }
                                            """)

            # 버튼 크기 설정
            for button, graph_box in zip([self.accel_toggle, self.gyro_toggle, self.angle_toggle, self.gps_toggle, self.atmo_toggle, self.else_toggle], self.graph_boxes):
                button.setFixedSize(50, 30)  # adjust the size as needed
                graph_box.hide()

            # 꾸민 버튼을 추가시키기
            # QH H -> Horizontal 수평으로 놓아라! / < > 는 button_layout 에 넣으면 안됨!
            button_layout = QHBoxLayout()
            button_layout.addWidget(self.accel_toggle)
            button_layout.addWidget(self.gyro_toggle)
            button_layout.addWidget(self.angle_toggle)
            button_layout.addWidget(self.gps_toggle)
            button_layout.addWidget(self.atmo_toggle) 
            button_layout.addWidget(self.else_toggle)

            # 오른쪽 레이아웃에 button_layout 추가시키기
            right_layout.addStretch(1)
            right_layout.addLayout(button_layout)

            # < > 버튼 왼쪽에 할당시켜주기
            button_layout = QHBoxLayout()
            left_layout.addLayout(button_layout,4,0)
            button_layout.addWidget(self.previous_image_button)
            button_layout.addWidget(self.next_image_button)

            # 버튼 이벤트 할당
            self.accel_toggle.clicked.connect(self.show_accel_graph)
            self.gyro_toggle.clicked.connect(self.show_gyro_graph)
            self.angle_toggle.clicked.connect(self.show_angle_graph)
            self.gps_toggle.clicked.connect(self.show_gps_graph)
            self.atmo_toggle.clicked.connect(self.show_atmo_graph)
            self.else_toggle.clicked.connect(self.show_else_graph)

            self.previous_image_button.clicked.connect(self.previous_image)
            self.next_image_button.clicked.connect(self.next_image)

            command_layout=QGridLayout()
            right_layout.addLayout(command_layout)
            # 커맨드 입력칸 추가
            self.command_input = QLineEdit()
            self.command_input.setStyleSheet("""
                                                color: black; 
                                                background-color: white;
                                                border-radius: 10px;
                                                font-size: 35px;
                                            """)
            command_layout.addWidget(self.command_input,0,0)

            # 커맨드 입력하기 버튼 추가
            self.add_command_button = QPushButton('명령 송신')
            self.add_command_button.setStyleSheet("""
                                                    QPushButton {
                                                        background-color: rgb(128,128,128);
                                                        color: white;
                                                        border-radius: 10px;
                                                        font-size: 35px;
                                                        
                                                    }
                                                    QPushButton:hover {
                                                        background-color: red;
                                                        }
                                                    QPushButton:pressed {
                                                        background-color: green;
                                                        }
                                                    """)

            self.add_command_button.clicked.connect(self.add_command)
            command_layout.addWidget(self.add_command_button,1,0)

            # 데이터 저장 버튼 추가
            self.save_data_button = QPushButton('데이터 저장')
            self.save_data_button.setStyleSheet("""
                                                    QPushButton {
                                                        background-color: rgb(128,128,128);
                                                        color: white;
                                                        border-radius: 10px;
                                                        font-size: 20px;
                                                        padding: 10px 15px;
                                                    }
                                                    QPushButton:hover {
                                                        background-color: red;
                                                        }
                                                    QPushButton:pressed {
                                                        background-color: green;
                                                        }
                                                    """)
            self.save_data_button.clicked.connect(self.data_save)
            command_layout.addWidget(self.save_data_button,0,1)

            # 명령창 입력 이벤트 추가
            self.command_input.returnPressed.connect(self.add_command)

            # 그래프 추가할 격자 레이아웃 추가
            self.graph_layout = QVBoxLayout()  # QV V -> Vertical로 추가 시키기
            # 우측 상단부터 그래프 레이아웃 추가시키기
            right_layout.insertLayout(0, self.graph_layout)

            # 그래프가 나눠주기
            self.graph_splitter = QSplitter(Qt.Vertical)
            right_layout.insertWidget(
                0, self.graph_splitter)

            ## 그래프 데이터 가져오기 ##
            query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'SENSOR' AND TABLE_SCHEMA = 'CANSATDB'"
            self.cursor.execute(query)
            column_names = self.cursor.fetchall()[1:]
            self.sorted_column_names = column_names

            # 여지껏의 시간 column 없애주기
            self.sorted_column_names.remove(('elapsed_time',))

            for i, column_name in enumerate(self.sorted_column_names):
                graph_widget = pg.PlotWidget()
                graph_widget.hide()  # 처음에 그래프 숨겨주기 / 지우면 그래프 이상하게 표출
                self.graph_boxes.append(graph_widget)

                # 그래프 데이터 series 만들어주기 series: 판다스에서 열이 하나인 데이터프레임을 뜻함
                self.graph_items[column_name[0]] = pg.PlotDataItem(
                    pen=pg.intColor(i, hues=len(self.sorted_column_names)-1))
                self.graph_boxes[i].addItem(self.graph_items[column_name[0]])

                # Deque 만들어주기 deque: list와 similar, 데이터를 양옆에서 편집가능
                self.data_values[column_name[0]] = collections.deque(
                    maxlen=self.max_data_points)

                # 각 그래프 이름 만들어주기
                self.graph_boxes[i].setTitle(column_name[0])

            # 레이아웃에 그래프 추가시켜주기
            for i, graph_widget in enumerate(self.graph_boxes):
                self.graph_layout.addWidget(graph_widget)

            # Add left and right widgets to the splitter
            splitter.addWidget(left_widget)
            splitter.addWidget(right_widget)

            # Set the splitter as the main layout
            layout.addWidget(splitter)

            # Set the main widget as the central widget
            self.setCentralWidget(main_widget)

            # 그래프 타이머
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_graph)
            self.timer.start(50)  # update every 0.05 seconds

            # Set the window title
            self.setWindowTitle('Guardians of the Galaxy Ground Station')

            for i, column_name in enumerate(self.sorted_column_names):
                graph_widget = pg.PlotWidget()
                graph_widget.setBackground('k')  # 'k' stands for black
                graph_widget.hide()  # Hide the graph initially
                # 맨 처음에 self.graph_boxes list에 추가
                self.graph_boxes.append(graph_widget)

        def add_command(self):          # 커맨트 sql에 할당 method
            command = self.command_input.text()
            if command:
                query = f"INSERT INTO COMMANDS (command) VALUES ('{command}')"
                self.cursor.execute(query)
                self.cnx.commit()
                self.command_input.clear()
                print(f"Command '{command}' added")

        def update_image(self):          # 이미지 업데이트 method
            try:
                def extract_number(f):
                    s = re.search(r'\d+', os.path.basename(f))
                    return int(s.group()) if s else None
                # 이미지가 새로 생기면 이미지 업데이트
                if len(self.image_files) >= len(self.image_files):
                    self.image_files = os.listdir(
                        self.image_directory)  # self.image_files를 새로운 이미지들로 업데이트
                    self.image_files = sorted(self.image_files, key=extract_number)
                if len(self.image_files)>= 1:
                        image_file = self.image_files[self.current_image_index]
                        pixmap = QPixmap(os.path.join(self.image_directory, image_file))
                if pixmap.isNull():
                    print('Failed to load image file:', image_file)
                self.image_pixmap = pixmap.scaled(
                    self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(self.image_pixmap)
                
                self.image_name_label.setText(image_file)

                if not self.image_files:
                    print("No images in directory")
                    return

                # 텍스트 데이터
                text_data_file = image_file.replace('.jpg', '.txt')
                text_data_directory = 'C:/Users/82108/Desktop/CANSAT DATA/txt'
                try:
                    with open(os.path.join(text_data_directory, text_data_file), 'r') as file:
                        lines = file.readlines()
                        formatted_data = []
                        for line in lines:
                            items = line.split()
                            if len(items) >= 6:  # Make sure there are at least 6 items in the line
                                # Format the line as "name x = x_coord y = y_coord"
                                formatted_line = f"{items[0]} x = {items[-2]} m y = {items[-1]} m"
                                formatted_data.append(formatted_line)
                        # Set the label text to the formatted data
                        self.text_data_label.setText("\n".join(formatted_data))

                except IOError:
                    print('Failed to load text data file:', text_data_file)
            except:
                pass

        def show_accel_graph(self):
            self._show_graphs(['ax', 'ay', 'az'])

        def show_gyro_graph(self):
            self._show_graphs(['gx', 'gy', 'gz'])

        def show_angle_graph(self):
            self._show_graphs(['angx','angy','HEADING'])

        def show_gps_graph(self):
            self._show_graphs(['lat', 'longi', 'gpsalt'])

        def show_atmo_graph(self):
            self._show_graphs(['temp', 'pressure', 'alt'])

        def show_else_graph(self):
            self._show_graphs(['light'])

        def previous_image(self):
            if len(self.image_files) > 0:
                # 이미지 인덱스를 감소시키고, 리스트의 시작으로 순환
                self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
                self.update_image()

        def next_image(self):
            if len(self.image_files) > 0:
                # 이미지 인덱스를 증가시키고, 리스트의 끝으로 순환
                self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
                self.update_image()

        def _show_graphs(self, column_names):
            # Hide all the graph boxes
            for graph_box in self.graph_boxes:
                graph_box.hide()

            # Find the index of the graph_box corresponding to the column name and show it
            for column_name in column_names:
                for i, sorted_column_name in enumerate(self.sorted_column_names):
                    if sorted_column_name[0] == column_name:
                        self.graph_boxes[i].show()

        def update_graph(self):
            query = 'SELECT elapsed_time, ax, ay, az, gx, gy, gz, angx, angy, HEADING, temp, pressure, alt, lat, longi, gpsalt, light FROM SENSOR ORDER BY elapsed_time DESC LIMIT 1'
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            self.cnx.commit()
            if row is not None:
                elapsed_time = row[0]
                # Change here to skip elapsed_time
                for i, value in enumerate(row[1:]):
                    self.data_values[self.sorted_column_names[i][0]].append(
                        (elapsed_time, value))  # Append tuple (elapsed_time, value)

                for i, graph_item in enumerate(self.graph_items.values()):
                    # Convert list of tuples to numpy array
                    data = np.array(
                        self.data_values[self.sorted_column_names[i][0]])
                    # Set x = data[:, 0] (elapsed_time), y = data[:, 1] (value)
                    graph_item.setData(data[:, 0], data[:, 1])

                angx = row[8] 
                angy = row[9]
                HEADING = row[10]

                self.update_rotation(angx, angy, HEADING)

        def data_save(self):
            hostname = "bifrost0602.duckdns.org"
            port = 2024
            username = "TEST"
            password = "1234"
            database = "CANSATDB"
            table = "SENSOR"

            # 현재 시간을 폴더 이름으로 사용하여 폴더 생성
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            folder_name = os.path.join(r"C:/Users/82108/Desktop/지상국 데이터", current_time)
            
            # 이미지 파일 폴더 경로
            image_directory = r"C:/Users/82108/Desktop/CANSAT DATA/image"
            # 텍스트 파일 폴더 경로
            text_directory = r"C:/Users/82108/Desktop/CANSAT DATA/txt"

            # 이미지 파일들을 폴더로 이동
            destination_image_directory = os.path.join(folder_name, "image")
            os.makedirs(destination_image_directory)
            for image_file in os.listdir(image_directory):
                source_path = os.path.join(image_directory, image_file)
                destination_path = os.path.join(destination_image_directory, image_file)
                shutil.move(source_path, destination_path)

            # 텍스트 파일들을 폴더로 이동
            destination_text_directory = os.path.join(folder_name, "txt")
            os.makedirs(destination_text_directory)
            for text_file in os.listdir(text_directory):
                source_path = os.path.join(text_directory, text_file)
                destination_path = os.path.join(destination_text_directory, text_file)
                shutil.move(source_path, destination_path)


            csv_file = os.path.join(folder_name, "output.csv")
            get_dataframe.export_table_to_csv(hostname, username, password, port, database, table, csv_file)
            print("데이터 저장 완료")

        def closeEvent(self, event):
            # 지상국 종료시 sql 연결 해제
            self.cursor.close()
            self.cnx.close()
            # 지상국 종료시 observer 연결 해제
            self.observer.stop()
            self.observer.join()

        def update_rotation(self, ang_x, ang_y, heading):
            centerOfMassFilter = vtk.vtkCenterOfMass()
            centerOfMassFilter.SetInputData(self.actor.GetMapper().GetInput())
            centerOfMassFilter.SetUseScalarsAsWeights(False)
            centerOfMassFilter.Update()

            center = centerOfMassFilter.GetCenter()  # this is the center of mass

            # Create a transform that rotates the actor
            transform = vtk.vtkTransform()
            transform.Translate(center[0], center[1], center[2])
            transform.RotateX(ang_x)
            transform.RotateY(ang_y)
            transform.RotateZ(heading)
            transform.Translate(-center[0], -center[1], -center[2])

            # Apply the transform to the actor
            self.actor.SetUserTransform(transform)

            # Render the scene
            self.iren.Render()

    class RainbowTitle(QLabel):
        def __init__(self, text):
            super().__init__(text)
            self.setAlignment(Qt.AlignCenter)
            
            # 색상이 변경될 때마다 호출될 함수 설정
            self.colortimer = QTimer()
            self.colortimer.timeout.connect(self.update_color)
            self.colortimer.start(10)  # 0.1초마다 색상 업데이트

        def update_color(self):
            # 시간에 따라 색상이 변하도록 RGB 값을 설정
            t = time.time() * 0.5  # slower transition
            r = sin(2 * pi * (t * 0.7 + cos(t * 0.3) * 0.2)) / 2 + 0.5  # red color
            g = sin(2 * pi * (t * 0.7 + cos(t * 0.3 + 2 * pi / 3) * 0.2)) / 2 + 0.5  # green color
            b = sin(2 * pi * (t * 0.7 + cos(t * 0.3 + 4 * pi / 3) * 0.2)) / 2 + 0.5  # blue color

            r = int(r * 55 + 200)
            g = int(g * 55 + 200)
            b = int(b * 55 + 200)

            color_string = f"rgb({int(r)}, {int(g)}, {int(b)})"
            self.setStyleSheet(f"""
                                        color: black; 
                                        background-color: {color_string};
                                        border-radius: 10px;
                                        font-size: 50px;
                                        font-weight: 900;
                                        """)

    app = QApplication(sys.argv)
    set_dark_theme(app)  # 테마 색상 적용; line 25에
    graphWindow = RealTimeGraphWindow()
    graphWindow.show()
    sys.exit(app.exec_())
