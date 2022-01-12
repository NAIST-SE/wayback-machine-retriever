import re
import csv
import json
import os
import shutil
import time
import requests
from random import randint
from urllib.parse import urlparse


def get_wayback_availability():
    try:
        return session.get(url=query_url, headers=headers)
    except requests.ConnectionError:
        return None


if __name__ == '__main__':
    # https://archive.org/help/wayback_api.php
    base_url = 'http://archive.org/wayback/available?timestamp=20210316' # after data collection finished
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }
    session = requests.Session()
    output_dir = 'json_20210316'
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    with open('links.csv') as links_input_file:
        for link in csv.reader(links_input_file):
            time.sleep(randint(1000, 5000)/1000)
            parsed_url = urlparse(link[0])
            url = re.sub('\\.\\)-:', '', f'{parsed_url.scheme}://{parsed_url.hostname}{parsed_url.path}')
            filename = re.sub('[^\\w.-]+', '_', url)
            print(url)
            query_url = base_url + f'&url={url}'
            response = get_wayback_availability()
            retries = 0
            while not response:
                retries = retries + 1
                time.sleep(randint(5000, 10000) / 1000)
                response = get_wayback_availability()
                if retries >= 10:
                    print("failure after 10 retries")
                    break
            if response.status_code == 200:
                print("success")
                json_response = json.loads(response.text)
                with open(os.path.join(output_dir, f"{filename}.json"), "w") as response_output_file:
                    response_output_file.write(json.dumps(json_response, sort_keys=False, indent=4))
            else:
                print("failure")
    print("done")
