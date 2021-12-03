import codecs
import json
from concurrent.futures import ThreadPoolExecutor

import redis
import requests
from dotenv import load_dotenv
import os

from spdx_license_matcher.normalize import normalize
from spdx_license_matcher.utils import compressStringToBytes

load_dotenv()

r = redis.StrictRedis(host=os.environ.get(key="SPDX_REDIS_HOST", default="localhost"), port=6379, db=0)


def get_url(url):
    """GET URL and return response"""
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    headers = {'User-Agent': user_agent }
    url = url.replace('./', 'https://raw.githubusercontent.com/spdx/license-list-data/master/json/details/')
    res = requests.get(url, headers=headers)
    # json_data = json.loads(res.text)

    return res


def get_license_text(id):
    """GET URL and return response"""
    if id == 'BCL' or id == 'Lil-1.0':
        return 'rgmrmgir'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    headers = {'User-Agent': user_agent}
    url = 'https://spdx.org/licenses/' + id + '.json'

    res = requests.get(url, headers=headers)
    # json_data = json.loads(res.text)

    licenseJson = res.json()
    return licenseJson['licenseText']



def build_spdx_licenses():
    """ Get data from SPDX license list and set data in redis.
    """
    import time
    start_time = time.time()
    url = 'https://spdx.org/licenses/licenses.json'

    # Delete all the keys in the current database
    r.flushdb()

    # response = requests.get(url)
    # licensesJson = response.json()
    # licenses = licensesJson['licenses']
    # # print(licensesJson)
    # licensesUrl = [license.get('reference') for license in licenses]
    #
    # # print(licensesUrl)
    # with ThreadPoolExecutor(max_workers=2) as pool:
    #     # print(licensesUrl)
    #     responses = list(pool.map(get_url, licensesUrl))
    #
    # for response in responses:
    #     try:
    #         if response.status_code == 200 and response.content:
    #             licenseJson = response.json()
    #             licenseName = licenseJson['licenseId']
    #             licenseText = licenseJson['licenseText']
    #             normalizeText = normalize(licenseText)
    #             compressedText = compressStringToBytes(normalizeText)
    #             r.set(licenseName, compressedText)
    #     except Exception as e:
    #         print("response", e)
    #         raise
    r.flushdb()

    for file in os.listdir("./licenses"):
        if file.endswith(".txt"):
            licenseName = file.split('.txt')[0]
            file = os.path.join("./licenses", file)
            licenseText = codecs.open(file, 'r', encoding='unicode_escape').read()
            normalizeText = normalize(licenseText)
            compressedText = compressStringToBytes(normalizeText)
            r.set(licenseName, compressedText)
    print("--- %s seconds ---" % (time.time() - start_time))

def is_keys_empty():
    """To check if the keys in redis is present or not.

    Returns:
        bool -- returns if the spdx licenses is present in the redis database or not.
    """
    return True if r.keys('*') == [] else False
