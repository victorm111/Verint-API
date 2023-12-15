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

def test_getSearchAndReplay(getToken):
  """retrieves daily search and replay"""

  url = 'wfo.a31.verintcloudservices.com'
  url_api = '/daswebapi/Query/ExecuteDynamicQuery'
  s='null'  # requests session variable
  # create an Empty DataFrame object, holds capt verif results
  df = pd.DataFrame()

  LOGGER.debug('test_getSearchAndReplay:: started')
  token = 'null'

  token = os.environ["TOKEN"]
  assert(token),'token not retrieved'

  LOGGER.debug('test_getSearchAndReplay:: token retrieved')
  payload = json.dumps({
    "org_id": 708000501,
    "start_time": "2023-12-12T05:00:00-04:00",
    "end_time": "2023-12-13T05:00:00-04:00",
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

  print(f'test_getSearchAndReplay() session resp received code: {s.status_code}')
  LOGGER.debug('test_getSearchAndReplay:: response received')

  response_dict = json.loads(s.text)
  s.raise_for_status()
  SR_df = pd.json_normalize(response_dict)
  SR_df.to_json('./output/SR/SR_daily.json')

  assert not len(SR_df) == 0, 'No SR_df returned'



