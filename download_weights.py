from google_drive_downloader import GoogleDriveDownloader as gdd
import os

if not os.path.exists('./resources'):
	os.makedirs('./resources')

gdd.download_file_from_google_drive(file_id='1yblYSrw6lq-fqNPpqNdVJNXTEs0iiqov', dest_path='./resources/similarity_model_demo1.h5')
gdd.download_file_from_google_drive(file_id='18Ru477eI23kmK5O1tvYJUuxE5cbLXY4N', dest_path='./resources//model_0002999.pth')

