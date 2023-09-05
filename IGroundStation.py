import threading
import time
import os
import mysql.connector
from ftplib import FTP
from GroundStation import Ground
from ftpdownload import download_files_ftp
import shutil
import get_dataframe
import datetime

# Create an Event object
stop_event = threading.Event()

#시작 전 처리
def delete_all_files_in_directory(directory):
    files_remaining = True

    while files_remaining:
        files_remaining = False  # 초기에는 남은 파일이 없다고 가정
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                files_remaining = True  # 파일이 삭제되었으므로 남은 파일이 있다고 표시

def delete_all_files_in_ftp_directory(host, port, username, password, directory):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login(user=username, passwd=password)
    
    ftp.cwd(directory)
    
    def delete_file(line):
        # Split the string to isolate the filename
        split_line = line.split()
        filename = split_line[-1]

        # Check if the line represents a file (not a directory)
        if line[0] != 'd':
            try:
                ftp.delete(filename)
            except:
                print(f"Failed to delete {filename}")
    
    # Use the callback function for each file in the directory
    ftp.dir(delete_file)

    ftp.quit()


# MySQL connection
cnx = mysql.connector.connect(
    host='bifrost0602.duckdns.org',
    user='TEST',
    port=2024,
    password='1234',
    database='CANSATDB'
    )

cursor = cnx.cursor(buffered=False)

#테스트 테이블 초기화
query='DELETE FROM COMMANDS'
cursor.execute(query)
cnx.commit()
cursor.close()
cnx.close()

#json 파일 초기화
try:
    os.remove("C:/Users/82108/Desktop/캡스톤디자인/CODE/지상국/downloaded_files.json")
except:
    pass

print('지상국 시작 준비 중...')
delete_all_files_in_directory('C:/Users/82108/Desktop/CANSAT DATA/image')
delete_all_files_in_directory('C:/Users/82108/Desktop/CANSAT DATA/text')
delete_all_files_in_ftp_directory('bifrost0602.duckdns.org', 2025, 'bifrost', '1234', '/home/bifrost/Documents')
print('지상국 시작')

def ftp_task():
    file_number = 1
    while not stop_event.is_set():
        try:
            download_files_ftp('bifrost0602.duckdns.org', 'bifrost', '1234', 2025, 'C:/Users/82108/Desktop/CANSAT DATA', file_number)
            file_number += 1
            time.sleep(0.1)
        except Exception as e:
            continue

def ground_task():
    try:
        Ground()
    finally:
        # If the ground task finishes, signal the other thread to stop
        stop_event.set()

thread1 = threading.Thread(target=ftp_task)
thread2 = threading.Thread(target=ground_task)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

# MySQL connection
cnx = mysql.connector.connect(
    host='bifrost0602.duckdns.org',
    user='TEST',
    port=2024,
    password='1234',
    database='CANSATDB'
    )

hostn = "bifrost0602.duckdns.org"
portn = 2024
usern = "TEST"
passwordn = "1234"
databasen = "CANSATDB"
tablen = "SENSOR"

cursor = cnx.cursor(buffered=False)
query="INSERT INTO COMMANDS (command) VALUES ('stop')"
print('캔위성 종료 중...')
cursor.execute(query)
cnx.commit()
time.sleep(5) #캔위성이 종료될때까지 기다려
print('데이터 저장 중...')
# 현재 시간을 폴더 이름으로 사용하여 폴더 생성
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
folder_name = os.path.join(r"C:/Users/82108/Desktop/지상국 데이터", current_time)
            
# 이미지 파일 폴더 경로
image_directory = r"C:/Users/82108/Desktop/CANSAT DATA/image"
# 텍스트 파일 폴더 경로
text_directory = r"C:/Users/82108/Desktop/CANSAT DATA/text"

# 이미지 파일들을 폴더로 이동
destination_image_directory = os.path.join(folder_name, "image")
os.makedirs(destination_image_directory)
for image_file in os.listdir(image_directory):
    source_path = os.path.join(image_directory, image_file)
    destination_path = os.path.join(destination_image_directory, image_file)
    shutil.move(source_path, destination_path)

# 텍스트 파일들을 폴더로 이동
destination_text_directory = os.path.join(folder_name, "text")
os.makedirs(destination_text_directory)
for text_file in os.listdir(text_directory):
    source_path = os.path.join(text_directory, text_file)
    destination_path = os.path.join(destination_text_directory, text_file)
    shutil.move(source_path, destination_path)

csv_file = os.path.join(folder_name, "output.csv")
get_dataframe.export_table_to_csv(hostn, usern, passwordn, portn, databasen, tablen, csv_file)
#테스트 테이블 초기화
query='DELETE FROM COMMANDS'
cursor.execute(query)
cnx.commit()
query='DELETE FROM FEEDBACK'
cursor.execute(query)
cnx.commit()
cursor.close()
cnx.close()
print("종료 완료")