import http.client
import glob

import json
import logging
import os
from os import listdir
import pandas as pd
import shutil

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def test_getCaptVerifCSV(getToken):
  """retrieves daily capt verif csv"""


  url = 'wfo.a31.verintcloudservices.com'
  url_api = '/api/av/capture_verification/v1/call_segments/issues/search/csv'
  s='null'  # requests session variable
  # create an Empty DataFrame object, holds capt verif results
  df = pd.DataFrame()

  LOGGER.debug('test_getCaptVerifCSV:: started')
  token = 'null'
  conn = http.client.HTTPSConnection(url)
  token = os.environ["TOKEN"]
  assert(token),'token not retrieved'

  LOGGER.debug('test_getCaptVerifCSV:: token retrieved')
  payload = json.dumps({
    "org_id": 708000501,
    "start_time": "2023-12-01T05:00:00-04:00",
    "end_time": "2023-12-06T05:00:00-04:00",
    "page_size": 2000,
    "issue_filter": {}
  })
  headers = {
    'Verint-Session-ID': '42334',
    'Verint-Time-Zone': 'ACST',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Impact360AuthToken': token
  }
  #conn.request("POST", "/api/av/capture_verification/v1/call_segments/issues/search/csv", payload, headers)
  #res = conn.getresponse()

  # create a sessions object
  session = requests.Session()
  assert session,'session not created'
  # Set the Content-Type header to application/json for all requests in the session
  # session.headers.update({'Content-Type': 'application/json'})

  retry = Retry(connect=25, backoff_factor=0.5)

  adapter = HTTPAdapter(max_retries=retry)
  session.mount('https://', adapter)
  session.mount('http://', adapter)
  # Set the Content-Type header to application/json for all requests in the session
  session.headers.update(headers)
  try:
    s=session.post('https://'+url+url_api, data=payload, timeout=25, verify=False)
    s.raise_for_status()
  except requests.exceptions.HTTPError as errh:
    print("Http Error:", errh)
  except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:", errc)
  except requests.exceptions.Timeout as errt:
    print("Timeout Error:", errt)
  except requests.exceptions.RequestException as err:
    print("OOps: Something Else", err)

  assert s.status_code==200, 'session request response not 200 OK'
  # access session cookies
  #print(f'session cookies: {s.cookies}')

  #print(f'***test_getCaptVerifCSV() resp received code: {res.code}')
  print(f'***test_getCaptVerifCSV() session resp received code: {s.status_code}')
  LOGGER.debug('test_getCaptVerifCSV:: response received')

  # delete previous zip files, csv

  folderPath = './output/CaptVerif/'

  for fileName in listdir(folderPath):
    # Check file extension
    if fileName.endswith('.zip') or fileName.endswith('.csv'):
      # Remove File
      os.remove(folderPath + fileName)


  zipPath = '.\output\CaptVerif' + '\CaptVerifCSV_session' + '.zip'
  with open(zipPath, 'wb') as zipFile:
      zipFile.write(s.content)

  # need to unzip Capt Verif csv and import to DF
  # extract the file
  shutil.unpack_archive(zipPath, '.\output\CaptVerif')
  # determine the zip file name
  path = r'.\output\CaptVerif\*.csv'
  csv_file = glob.glob(path)

  # read the csv into a df
  df_CaptVerifDaily = pd.read_csv(csv_file[0])

