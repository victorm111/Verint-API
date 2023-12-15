import requests
import json
import yaml
import hashlib
import platform
import src.__init__     # contains sw version
import os
import os
import pytest
from dotenv import load_dotenv
import logging
import pandas as pd
import pytest_html

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

load_dotenv()  # take environment variables from .env.



@pytest.fixture(scope="function")
def test_read_config_file():

    LOGGER.debug('conftest:: test_read_config_file() start')
    cfgfile_parse_error = 0
    # create an Empty DataFrame object
    df_config = pd.DataFrame()

    try:
        with open("./config/config.yml", 'r') as file:
            test_config = yaml.safe_load(file)
            cfgfile_parse_error = 0

    except yaml.YAMLError as exc:
        print("!!! test_read_config_file(): Error in configuration file loading:", exc)
        cfgfile_parse_error = 1
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            print("**config.yaml file Error position: (%s:%s)" % (mark.line + 1, mark.column + 1))
    else:
        # Convert the YAML data to a Pandas DataFrame
        df_config = pd.DataFrame.from_dict(test_config)
        output_prefix_path = df_config['output_files']['output_prefix_path']

        # create env variable tracking home dir
        os.environ['home_dir'] = str(df_config['dirs']['working'])

    finally:
        # check config file read ok
        assert cfgfile_parse_error == 0, 'assert error test_read_config_file: yaml cfg file not read'  # if cfgfile_parse_error = 1
        print("test_read_config_file(): read finished OK")
        python_version = str(platform.python_version())
        pytest_version = str(pytest.__version__)
        testcode_version = str(src.__init__.__version__)
        LOGGER.debug(f'conftest:: python version: {python_version}')
        LOGGER.debug(f'conftest:: pytest version: , {pytest_version}')
        LOGGER.debug(f'conftest:: test code version: {testcode_version}')
        LOGGER.debug('conftest:: test_read_config_file() finished')

    yield df_config
    
@pytest.fixture(scope='function')
def getToken():

  LOGGER.debug('conftest:: start getToken')
  url = "https://wfo.a31.verintcloudservices.com/wfo/rest/core-api/auth/token"

  payload = json.dumps({
    "user": "api_user@verintnew01.prodreleasev2.com",
    "password": "1_Abc_123"
  })
  headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload, timeout=25, verify=False)

  LOGGER.debug('conftest:: getToken response received')
  print(response.text)
  print("token is:", {response.content})

  json_response = response.json()
  print(f'token is: {json_response["AuthToken"]["token"]}')

  # remove quotes at each end

  os.environ["TOKEN"] = json.dumps(json_response["AuthToken"]["token"])[1:-1]


  LOGGER.debug('conftest:: finish getToken')
  yield



@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])
    if report.when == "call":
        # always add url to report
        extras.append(pytest_html.extras.url("http://www.example.com/"))
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            # only add additional html on failure
            extras.append(pytest_html.extras.html("<div>Additional HTML</div>"))
        report.extras = extras