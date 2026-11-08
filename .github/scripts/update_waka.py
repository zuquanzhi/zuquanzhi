import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

token = os.environ.get('WAKATIME_TOKEN', '')
if not token:
    sys.exit('WakaTime OAuth token is missing')

request = Request(
    'https://wakatime.com/api/v1/users/current/stats/last_7_days',
    headers={'Authorization': f'Bearer {token}', 'User-Agent': 'github-waka-readme'},
)
for attempt in range(4):
    try:
        with urlopen(request, timeout=30) as response:
            if response.status == 202:
                time.sleep(15)
                continue
            data = json.load(response)['data']
            break
    except HTTPError as error:
        sys.exit(f'WakaTime request failed: HTTP {error.code}')
else:
    sys.exit('WakaTime statistics are still being calculated')

languages = data.get('languages', [])[:5]
lines = ['```text']
for language in languages:
    name = language['name'].replace('\n', ' ').replace('\r', ' ')
    percentage = float(language['percent'])
    blocks = max(0, min(25, round(percentage / 4)))
    lines.append(f"{name:<20} {language['text']:<20} {'█' * blocks}{'░' * (25 - blocks)} {percentage:5.1f}%")
if not languages:
    lines.append('No coding activity recorded in the last 7 days.')
lines.append('```')

path = Path('README.md')
readme = path.read_text(encoding='utf-8')
pattern = r'(<!--START_SECTION:waka-->).*?(<!--END_SECTION:waka-->)'
updated, count = re.subn(pattern, lambda m: m.group(1) + '\n' + '\n'.join(lines) + '\n' + m.group(2), readme, flags=re.S)
if count != 1:
    sys.exit('Expected exactly one Waka README section')
path.write_text(updated, encoding='utf-8')

