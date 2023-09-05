import bluetooth
import time

def control_on():
	try:
		# ESP32 Bluetooth 주소
		esp32_address = "B0:A7:32:D8:C4:66"  # 실제 ESP32의 Bluetooth 주소로 대체해야 함

		# ESP32와 페어링
		sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		sock.connect((esp32_address, 1))

		# 데이터 송수신
		data = "1"  # '1'을 보냅니다.
		sock.send(data)

		# 연결 종료
		sock.close()
	except Exception as e:
		print(e)

def control_off():
	try:
		# ESP32 Bluetooth 주소
		esp32_address = "B0:A7:32:D8:C4:66"  # 실제 ESP32의 Bluetooth 주소로 대체해야 함

		# ESP32와 페어링
		sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		sock.connect((esp32_address, 1))

		# 데이터 송수신
		data = "0"  # '1'을 보냅니다.
		sock.send(data)

		# 연결 종료
		sock.close()
	except Exception as e:
		print(e)
