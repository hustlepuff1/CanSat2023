# CanSat2023 Ground Station & Satellite System

This repository contains the full software stack for the CanSat2023 project, including ground station software, data processing utilities, and embedded scripts for Arduino and Raspberry Pi. The system is designed for real-time telemetry, control, and data analysis of a CanSat satellite mission.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Major Components](#major-components)
- [Requirements](#requirements)
- [Setup & Usage](#setup--usage)
- [Data Flow](#data-flow)
- [License](#license)

---

## Features

- **Ground Station GUI**: Real-time sensor data visualization, image display, and command interface using PyQt5.
- **MySQL Integration**: Live telemetry and feedback via remote MySQL database.
- **Image & Text Data Handling**: Automatic update and display of images and detection results.
- **Data Export**: Save all mission data (images, text, sensor logs) to local storage.
- **Embedded Integration**: Scripts for Arduino and Raspberry Pi for sensor reading, control, and communication.
- **FTP Utilities**: Automated file transfer between satellite and ground station.
- **Mapping & Visualization**: Live and static map drawing utilities.
- **Calibration & Testing**: Tools for sensor calibration and system testing.

---

## Project Structure

```
CanSat2023-master/
│
├── GroundStation.py           # Main ground station GUI application
├── get_dataframe.py           # Utility for exporting MySQL tables to CSV
├── calibration.py             # Sensor calibration scripts
├── camera_ftp.py              # FTP utilities for camera/image transfer
├── map.py, map_live.py, ...   # Map drawing and visualization scripts
├── Arduino/                   # Arduino source code for satellite control
├── Raspberrypi/               # Raspberry Pi scripts for onboard operations
├── data/, augmented_images/   # Data and image storage folders
├── gps_app/                   # GPS server and web interface
├── pyqt_test/                 # PyQt5 UI test scripts
├── templates/                 # (Likely) HTML or UI templates
├── README.md                  # This file
└── ... (other utilities and scripts)
```

---

## Major Components

### 1. Ground Station (PC)

- **`GroundStation.py`**  
  Main GUI for real-time monitoring and control. Features:
  - Live sensor data plotting (pyqtgraph)
  - Image and detection result display
  - Command input and feedback
  - Data export (images, text, CSV)
  - Dark theme and custom UI

- **`get_dataframe.py`**  
  Exports MySQL tables to CSV for offline analysis.

- **Mapping Utilities**  
  - `map.py`, `map_live.py`, `map_drawer.py`, `GOGMAP.py`: Scripts for drawing and updating maps with telemetry data.

- **FTP & Data Handling**  
  - `camera_ftp.py`, `ftpdownload.py`, `ftpupload.py`, `object_detection_ftp.py`: Automated file transfer and object detection result handling.

- **Calibration & Testing**  
  - `calibration.py`, `test.py`, `Make_dataframe.py`: Sensor calibration and data preparation.

### 2. Embedded Systems

- **`Arduino/`**  
  Contains Arduino sketches for:
  - Satellite control logic
  - Sensor reading and data transmission

- **`Raspberrypi/`**  
  Python scripts for:
  - Camera control and image capture (`camera.py`, `keepcamera.py`)
  - FTP upload/download
  - Main satellite logic (`cansat.py`, `cansat_advanced.py`)
  - Logging and communication

### 3. Data & Images

- **`data/`, `augmented_images/`**  
  Store captured images and processed/augmented images.

- **`output.csv`**  
  Example of exported sensor data.

### 4. Web & GPS

- **`gps_app/`**  
  Node.js server and web interface for GPS data visualization.

---

## Requirements

- Python 3.x
- PyQt5
- pyqtgraph
- numpy
- mysql-connector-python
- watchdog
- (For web/GPS) Node.js

Install Python dependencies:

```powershell
pip install pyqt5 pyqtgraph numpy mysql-connector-python watchdog
```

---

## Setup & Usage

1. **Configure MySQL**  
   Ensure your MySQL server is running and accessible. Update credentials in `GroundStation.py` if needed.

2. **Run the Ground Station GUI**

   ```powershell
   python GroundStation.py
   ```

3. **Embedded Systems**  
   - Upload Arduino code from `Arduino/` to your microcontroller.
   - Run Raspberry Pi scripts from `Raspberrypi/` as needed.

4. **Data Export**  
   Use the GUI's "데이터 저장" button to save all mission data.

5. **Map & Web Visualization**  
   - Run scripts in `gps_app/` for live GPS tracking.
   - Use mapping scripts for visualization.

---

## Data Flow

1. **Satellite (Arduino/Raspberry Pi)**  
   - Collects sensor data and images.
   - Sends data to MySQL and/or via FTP to ground station.

2. **Ground Station (PC)**  
   - Receives and visualizes data in real time.
   - Allows operator to send commands and save data.

3. **Web & Mapping**  
   - Optional: Visualize GPS and mission data on maps or web dashboards.

---

## License

Feel free to do whatever the hell you want.
If you are planning to make money with this? Well then, good luck.

---
