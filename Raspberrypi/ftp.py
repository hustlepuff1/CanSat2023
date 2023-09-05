from ftplib import FTP
import time

# FTP server details
server = 'bifrost0602.duckdns.org'
port = 2025
username = 'bifrost'  # Replace with your FTP username
password = '1234'  # Replace with your FTP password

# Local directory to save the downloaded files
local_directory = 'C:/Users/henry/Desktop'


def download_file(filename):
    ftp = FTP()
    ftp.connect(server, port)
    ftp.login(username, password)
    print('connected!')
    # Change to the FTP directory containing the files
    ftp.cwd('/home/bifrost/')

    # Download the file
    with open(local_directory + filename, 'wb') as file:
        ftp.retrbinary('RETR ' + filename, file.write)

    ftp.quit()


while True:
    # Get the list of files in the FTP directory
    ftp = FTP()
    ftp.connect(server, port)
    ftp.login(username, password)
    ftp.cwd('/home/bifrost/')
    file_list = ftp.nlst()
    ftp.quit()

    # Filter the list to include only .csv files
    csv_files = [
        filename for filename in file_list if filename.lower().endswith('.csv')]

    if csv_files:
        print("Downloading new .csv files...")
        for file in csv_files:
            download_file(file)
            print(f"Downloaded file: {file}")

    time.sleep(60)  # Wait for 60 seconds before checking for new files again
