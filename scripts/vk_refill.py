"""Publish/schedule a reviewed VK batch with a durable local delivery journal.

Prepare a JSON plan, then run: python3 scripts/vk_refill.py PLAN [--send]
An uncertain response remains pending and must be checked before resuming.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bot.vk_client import html_caption_to_vk_text
from bot.validate import validate_caption

JOURNAL = ROOT / 'data/vk_delivery.json'


def save_journal(data):
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    temp = JOURNAL.with_suffix('.tmp')
    with temp.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    temp.replace(JOURNAL)


def run(plan, send=False):
    load_dotenv(ROOT / '.env')
    journal = json.loads(JOURNAL.read_text()) if JOURNAL.exists() else {}
    prepared = []
    keys = set()
    for item in plan:
        channel, slug = item['channel'], item['slug']
        if channel not in ('pitanie', 'blizko'):
            raise ValueError('Unknown channel')
        prefix = 'BLIZKO_' if channel == 'blizko' else ''
        group = os.environ[prefix + 'VK_GROUP_ID']
        token = os.environ[prefix + 'VK_ACCESS_TOKEN']
        base = ROOT / 'channels/blizko' if channel == 'blizko' else ROOT
        if Path(slug).name != slug:
            raise ValueError('Invalid slug')
        caption = (base / 'posts' / (slug + '_caption.html')).read_text().strip()
        validate_caption(caption)
        message = html_caption_to_vk_text(caption)
        key = channel + ':' + slug
        if key in keys:
            raise ValueError('Duplicate plan entry: ' + key)
        keys.add(key)
        previous = journal.get(key)
        if previous:
            if previous['status'] == 'sent':
                continue
            raise RuntimeError('Uncertain previous send; check VK before retrying: ' + key)
        when = item.get('publish_date')
        if when and int(when) <= time.time() + 60:
            raise ValueError('Scheduled date is in the past or too near: ' + key)
        prepared.append((key, item, group, token, message))
    print('New entries:', len(prepared), flush=True)
    if not send:
        return
    for key, item, group, token, message in prepared:
        entry = dict(item, group_id=group, status='pending',
                     content_sha256=hashlib.sha256(message.encode()).hexdigest(),
                     attempted_at=dt.datetime.now(dt.timezone.utc).isoformat())
        journal[key] = entry
        save_journal(journal)
        params = dict(owner_id='-' + group, from_group=1, message=message,
                      access_token=token, v='5.199')
        if item.get('publish_date'):
            params['publish_date'] = int(item['publish_date'])
        try:
            response = requests.post('https://api.vk.com/method/wall.post', data=params, timeout=60)
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError):
            raise RuntimeError('Uncertain VK response; stopped without retry: ' + key) from None
        if 'error' in result:
            # Do not print VK request_params, which can contain the access token.
            code = result['error'].get('error_code')
            entry.update(status='rejected', error_code=code)
            save_journal(journal)
            raise RuntimeError('VK rejected entry, error code %s: %s' % (code, key))
        post_id = result.get('response', {}).get('post_id')
        if not post_id:
            raise RuntimeError('No post_id; stopped without retry: ' + key)
        entry.update(status='sent', post_id=post_id)
        save_journal(journal)
        print(key, '->', post_id, 'scheduled' if item.get('publish_date') else 'published', flush=True)
        time.sleep(3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--send', action='store_true')
    args = parser.parse_args()
    run(json.loads(args.plan.read_text()), send=args.send)
