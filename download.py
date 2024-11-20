import requests
import threading
import urllib.parse
import os
import time

def concatenate_parts(filename):
    part_files = [f"{filename}.part{i}" for i in range(6)]
    with open(filename, 'wb') as f:
        for part_file in part_files:
            with open(part_file, 'rb') as pf:
                f.write(pf.read())

def download_part(url, start, end, filename):
    headers = {'Range': f'bytes={start}-{end}'}
    response = requests.get(url, headers=headers, stream=True)
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

import time
import requests
import urllib.parse
import threading

def download_file(url):
    filename = urllib.parse.urlparse(url).path.split('/')[-1]
    num_threads = 6

    
    head_response = requests.head(url)
    file_size = int(head_response.headers.get('Content-Length', 0))

    start_time = time.time()  

    if 'Accept-Ranges' not in head_response.headers or head_response.headers['Accept-Ranges'] != 'bytes':
        response = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        end_time = time.time()  
        download_time = end_time - start_time  

        
        return f"Server does not support range requests. Downloading the file in one go. " \
               f"Download complete! Download time: {download_time:.2f} seconds, " \
               f"File Size: {file_size / (1024 * 1024):.2f} megabytes"

    
    part_size = file_size // num_threads
    threads = []

    for i in range(num_threads):
        start = i * part_size
        end = start + part_size - 1
        if i == num_threads - 1:
            end = file_size - 1
        thread_args = {
            'url': url,
            'start': start,
            'end': end,
            'filename': f'{filename}.part{i}'
        }

        thread = threading.Thread(target=download_part, kwargs=thread_args)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    concatenate_parts(filename)
    end_time = time.time()
    download_time = end_time - start_time
    return f"Download complete! Download time: {download_time:.2f} seconds, File Size: {file_size / (1024 * 1024):.2f} megabytes"
    part_files = [f"{filename}.part{i}" for i in range(num_threads)]
    for part_file in part_files:
        os.remove(part_file)

if __name__ == "__main__":
    url = input("Enter the URL: ")
    result_message = download_file(url)
    print(result_message)  
