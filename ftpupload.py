from ftplib import FTP
import os

def upload_file_ftp(hostname, username, password, port, local_file_path, remote_directory):
    try:
        # FTP 연결 설정
        ftp = FTP()
        ftp.connect(hostname, port)
        ftp.login(username, password)

        print('접속완료')

        # 원격 디렉토리로 이동
        ftp.cwd(remote_directory)

        print('디렉토리 이동')

        # 로컬 파일 열기
        with open(local_file_path, 'rb') as file:
            print('파일 업로드 중')
            # 파일 업로드
            try:
                ftp.storbinary('STOR ' + os.path.basename(local_file_path), file)
            except Exception as e:
                print(e)
        # FTP 연결 닫기
        ftp.quit()
        print("파일 업로드가 완료되었습니다.")

    except Exception as e:
        print("파일 업로드 중 오류가 발생했습니다.")
        print(e)

# 파일 업로드 함수 호출
upload_file_ftp('bifrost0602.duckdns.org', 'bifrost', '1234', 2025, "C:/Users/82108/Desktop/output_control1.csv", '/home/bifrost/Documents')