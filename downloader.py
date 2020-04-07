from podnapisi import PodnapisiNet
import requests
import zipfile
import glob
import srt
import os
import shutil

class SubtitleDownloader(object):

    def __init__(self):
        self.temporary_folder_number = 0
        self.subtitle_api = PodnapisiNet()

    def download_file(self, url, path):
        response = requests.get(url)
        with open(path, 'wb') as output_file:
            output_file.write(response.content)

    def unzip_file(self, path, extract_directory):
        with zipfile.ZipFile(path, 'r') as zip_file:
            zip_file.extractall(extract_directory)

    def download_subtitles(self, subtitle):
        self.temporary_folder_number += 1

        zip_file_path = './subtitles/temp{}.zip'.format(self.temporary_folder_number)
        extract_folder_path = './subtitles/temp{}'.format(self.temporary_folder_number)

        self.download_file(subtitle['download_url'], zip_file_path)

        # First create a new folder for the zip and then extract zip archive inside of it
        os.mkdir(extract_folder_path)
        self.unzip_file(zip_file_path, extract_folder_path)

        # Remove the zip file
        os.remove(zip_file_path)

        # Find the extracted srt files in folder
        subtitle_files = glob.glob('{}/*.srt'.format(extract_folder_path))
        return subtitle_files[0], extract_folder_path

    def parse_srt_file(self, path):
        with open(path, 'r', encoding='utf-8') as subtitle_file:
            file_content = subtitle_file.read()
            subtitle_generator = srt.parse(file_content)
            return subtitle_generator
    
    def get_subtitles(self, keywords):
        subtitles = self.subtitle_api.search(keywords)
        path, extracted_path = self.download_subtitles(subtitles[0])
        subtitle = self.parse_srt_file(path)
        shutil.rmtree(extracted_path)
        return subtitles[0], subtitle