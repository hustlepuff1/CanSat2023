from picamera2 import Picamera2
from time import sleep
import cv2
import object_detection as od


camera=Picamera2()
camera.resolution=(640,480)
camera.framerate=100
#camera.shutter_speed=1000

camera.start(show_preview=True)

try:
    while True:    # 무한루프
        sleep(0.1)   # 1초 마다 실행을 중지하고 다시 실행. 이 시간은 조절 가능
except KeyboardInterrupt:
    # 사용자가 Ctrl + C를 누르면 이곳에 도달
    print("프리뷰를 종료합니다.")
finally:
    # 예외가 발생하든 안하든 마지막에는 카메라를 꼭 종료해야 한다.
    camera.stop()
