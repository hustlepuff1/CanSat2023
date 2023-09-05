from ftplib import FTP
import os

def download_files_ftp(hostname, username, password, port, base_local_directory, file_number):
    # FTP connection setup
    ftp = FTP()
    ftp.connect(hostname, port)
    ftp.login(username, password)

    # Format local directories with the directory_number
    local_directory_jpg = os.path.join(base_local_directory, "image")
    local_directory_txt = os.path.join(base_local_directory, "text")

    # Format the filenames with the file_number
    jpg_file = f"image{file_number}.jpg"
    txt_file = f"image{file_number}.txt"

    # Create the local directories if they don't exist
    os.makedirs(local_directory_jpg, exist_ok=True)
    os.makedirs(local_directory_txt, exist_ok=True)

    # Define the paths (both local and remote) for the files
    files_to_download = [
        {
            'remote_path': '/home/bifrost/Documents/' + jpg_file,
            'local_path': os.path.join(local_directory_jpg, jpg_file)
        },
        {
            'remote_path': '/home/bifrost/Documents/' + txt_file,
            'local_path': os.path.join(local_directory_txt, txt_file)
        },
    ]

    # Loop through the files to download
    for file in files_to_download:
        # Download the file
        with open(file['local_path'], 'wb') as local_file:
            ftp.retrbinary('RETR ' + file['remote_path'], local_file.write)

    # Close FTP connection
    ftp.quit()

    return True