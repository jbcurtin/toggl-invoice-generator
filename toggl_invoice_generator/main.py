#!/usr/bin/env python
import aiofiles
import argparse
import asyncio
import enum
import pkg_resources
import jinja2
import json
import logging
import os
import pyppeteer
import typing

from datetime import datetime, timedelta
from urllib.parse import urlparse, urlencode

TOGGL_API_TOKEN = os.environ.get('TOGGL_API_TOKEN', None)
BILLABLE_RATE = float(os.environ.get('BILLABLE_RATE', 0))
NON_BILLABLE_RATE = float(os.environ.get('NON_BILLABLE_RATE', 0))
JINJA2_ENV = None

logger = logging.getLogger('') # <--- Probable a good idea to name your logger. '' is the 'root' logger
sysHandler = logging.StreamHandler()
sysHandler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(sysHandler)
logger.setLevel(logging.INFO)

import aiohttp
import uvloop

EVENT_LOOP = None
HEADERS = {
  'user_agent': 'robots+github@jbcurtin.io',
}
INPUT_FORMAT = '%Y-%m-%dT%H:%M:%S'
INVOICE_FORMAT = '%A %d. %B %Y'
FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'

class Offset(enum.Enum):
  MONTH: str = 'month'
  WEEK: str = 'week'
  CUSTOM: str = 'custom'

OFFSET_VALUES = {
  Offset.MONTH: timedelta(days=30),
  Offset.WEEK: timedelta(days=7),
}
def _validate_datetime_input(input_datetime: str) -> timedelta:
  return datetime.utcnow() - datetime.strptime(input_datetime, INPUT_FORMAT)

def _obtain_event_loop():
  global EVENT_LOOP
  if EVENT_LOOP is None:
    EVENT_LOOP = asyncio.get_event_loop()

  return EVENT_LOOP

async def extract_datums(url: str, session: aiohttp.ClientSession) -> typing.Dict[typing.Any, typing.Any]:
  authen = aiohttp.BasicAuth(TOGGL_API_TOKEN, password='api_token')
  async with aiohttp.ClientSession(headers=HEADERS, auth=authen) as session:
    async with session.get(url) as response:
      result = await response.text()
      if not response.status in [200]:
        raise NotImplementedError(f'HTTPResponse Status[{response.status}]')

      return json.loads(result)

async def extract_toggle_data(offset: timedelta) -> None:
  authen = aiohttp.BasicAuth(TOGGL_API_TOKEN, password='api_token')
  async with aiohttp.ClientSession(headers=HEADERS, auth=authen) as session:
    url = 'https://www.toggl.com/api/v8/time_entries'
    url = '?'.join([url, urlencode({
      'start_date': (datetime.utcnow() - offset).strftime(FORMAT),
      'end_date': datetime.utcnow().strftime(FORMAT)
    })])
    time_entries = await extract_datums(url, session)

    url = 'https://www.toggl.com/api/v8/clients'
    clients = await extract_datums(url, session)
    clients = {client['id']: client for client in clients}

    projects = {}
    for pid in [te['pid'] for te in time_entries]:
      await asyncio.sleep(.1)
      url = f'https://www.toggl.com/api/v8/projects/{pid}'
      projects[pid] = await extract_datums(url, session)

    url = 'https://www.toggl.com/api/v8/workspaces'
    workspaces = await extract_datums(url, session)
    workspaces = {ws['id']: ws for ws in workspaces}

    url = 'https://www.toggl.com/api/v8/me'
    users = await extract_datums(url, session)
    users = {users['data']['id']: users['data']}

    entries = []
    for entry in time_entries:
      datum = {key: value for key, value in entry.items()}
      datum['project'] = projects[entry['pid']]['data']
      datum['client'] = clients[projects[entry['pid']]['data']['cid']]
      datum['workspace'] = workspaces[datum['wid']]
      datum['user'] = users[datum['uid']]

      # Repair Entry Structure
      datum['description'] = datum.get('description', '')
      entries.append(datum)

    return entries

def configure_jinja() -> None:
  global JINJA2_ENV
  JINJA2_ENV = jinja2.Environment(
      trim_blocks = True,
      autoescape = False,
      loader=jinja2.FileSystemLoader(os.path.abspath('.')))

def capture_options() -> typing.Any:
  parser = argparse.ArgumentParser()
  parser.add_argument('-o', '--offset', default=Offset.MONTH, type=Offset)
  parser.add_argument('-d', '--delta', default=None, required=False, type=_validate_datetime_input)
  parser.add_argument('-g', '--generate-env-file', default=False, action="store_true", dest="gen_envfile")
  return parser.parse_args()

async def load_template(template_path: str) -> str:
  # template_path = os.path.join(os.path.dirname(__file__), 'templates/invoice.html')
  return pkg_resources.resource_string(__name__, template_path)

async def render(time_entries: typing.Dict[str, typing.Any], billing_total: str) -> None:
  # from pyppeteer import launch
  browser = await pyppeteer.launch()
  page = await browser.newPage()
  template_path = 'templates/invoice.html'
  logger.info(f'Using template[{template_path}]')
  template_string = await load_template(template_path)
  template = JINJA2_ENV.from_string(template_string.decode('utf-8'))
  template_context = {
    'billing_total': billing_total,
    'created_date': datetime.utcnow().strftime(INVOICE_FORMAT),
    'due_date': (datetime.utcnow() + timedelta(days=30)).strftime(INVOICE_FORMAT),
    'time_entries': time_entries,
    'logo_data_url': '',
  }
  for var_name in [
      'INVOICE_NUMBER',
      # Service Provider
      'SERVICE_PROVIDER', 'SERVICE_PROVIDER_EMAIL', 'SERVICE_PROVIDER_PHONE',
      'SERVICE_PROVIDER_ADDRESS', 'SERVICE_PROVIDER_ADDRESS_TWO',
      'SERVICE_PROVIDER_CITY', 'SERVICE_PROVIDER_STATE', 'SERVICE_PROVIDER_POSTAL',
      # Recipient
      'RECIPIENT', 'RECIPIENT_EMAIL', 'RECIPIENT_PHONE',
      'RECIPIENT_ADDRESS', 'RECIPIENT_ADDRESS_TWO',
      'RECIPIENT_CITY', 'RECIPIENT_STATE', 'RECIPIENT_POSTAL',
      # Misc
      'FULFILLMENT_DELAY',
    ]:
    template_context[var_name.lower()] = os.environ[var_name]

  await page.setContent(template.render(template_context))
  options = {'scale': 1, 'format': 'Letter'}
  output_path = os.path.join(os.environ['OUTPUT_DIR'], os.environ['INVOICE_FILENAME'])
  printed_pdf = await page.pdf(options)
  logger.info(f'Writing PDF to FilePath[{output_path}]')
  async with aiofiles.open(output_path, 'wb') as stream:
    await stream.write(printed_pdf)

async def main(options: typing.Any) -> None:
  if options.offset is Offset.CUSTOM:
    time_entries = await extract_toggle_data(options.delta)

  else:
    time_entries = await extract_toggle_data(OFFSET_VALUES[options.offset])

  billing_total = 0
  for entry in time_entries:
    entry['description'] = entry.get('description', '')
    entry['duration_human'] = timedelta(seconds=entry['duration']).__str__()
    if entry['billable']:
      billing = BILLABLE_RATE * ( entry['duration'] / 60 / 60 )
      entry['billing'] = '${:20,.2f}'.format(billing)

    else:
      billing = NON_BILLABLE_RATE * ( entry['duration'] / 60 / 60 )
      entry['billing'] = '${:20,.2f}'.format(billing)

    billing_total = billing_total + billing

  billing_total = '${:20,.2f}'.format(billing_total)
  await render(time_entries, billing_total)

def run() -> None:
  configure_jinja()
  asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
  options = capture_options()
  if options.gen_envfile:
    from toggl_api_bill_generator import toggl_constants
    output_path = os.path.join(os.getcwd(), 'dev.sh')
    with open(output_path, 'w') as stream:
      stream.write(toggl_constants.ENVFileTemplate)

    logger.info(f'Generated ENVVars here[{output_path}]')
    import sys; sys.exit(0)

  loop = _obtain_event_loop()
  loop.run_until_complete(main(options))

if __name__ in ['__main__']:
  run()

