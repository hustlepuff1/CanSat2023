from ftplib import FTP
import os
import json

def download_files_ftp(hostname, username, password, port, remote_directory, local_directory_jpg, local_directory_txt, downloaded_files_path):
    
    try:
        # Load list of downloaded files
        try:
            with open(downloaded_files_path, 'r') as f:
                downloaded_files = json.load(f)
        except FileNotFoundError:
            downloaded_files = []

        # FTP connection setup
        ftp = FTP()
        ftp.connect(hostname, port)
        ftp.login(username, password)

        # Change directory on FTP server
        ftp.cwd(remote_directory)

        # List all files in the directory
        files = ftp.nlst()

        # Loop through all files
        for file in files:
            # Skip if the file has already been downloaded
            if file in downloaded_files:
                continue

            # Check for .jpg and .txt files
            if file.endswith('.jpg'):
                local_directory = local_directory_jpg
            elif file.endswith('.txt'):
                local_directory = local_directory_txt
            else:
                continue  # if it's neither a .jpg nor a .txt, skip to the next file

            # Define local path where the file will be saved
            local_file_path = os.path.join(local_directory, file)

            # Download the file
            with open(local_file_path, 'wb') as local_file:
                ftp.retrbinary('RETR ' + file, local_file.write)
                #ftp.delete(file) #파일삭제
            # Add file to the list of downloaded files
            downloaded_files.append(file)

        # Save the list of downloaded files
        with open(downloaded_files_path, 'w') as f:
            json.dump(downloaded_files, f)

        # Close FTP connection
        ftp.quit()

    except Exception as e:
        print("An error occurred while downloading the file.")
        print(e)

    return True