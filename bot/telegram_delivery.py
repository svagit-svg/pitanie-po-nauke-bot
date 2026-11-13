"""Best-effort reconciliation against public channel history; never retry a send.

Public history is not an exactly-once API. Stop if history cannot be inspected,
and check it again after an ambiguous transport failure.
"""
from html.parser import HTMLParser
import re

import requests

from bot.telegram_client import CHANNEL, send_photo


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.parts.append(' ')


def normalized(text):
    parser = _Text()
    parser.feed(text)
    return ' '.join(''.join(parser.parts).split())


class _History(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.posts = []
        self.post = None
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-post' in attrs:
            self.post = attrs['data-post']
        if tag == 'div':
            if self.depth:
                self.depth += 1
            elif 'tgme_widget_message_text' in attrs.get('class', '').split():
                self.depth = 1
                self.parts = []
        if self.depth and tag == 'br':
            self.parts.append(' ')

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == 'div' and self.depth:
            self.depth -= 1
            if self.depth == 0:
                self.posts.append((self.post, ' '.join(''.join(self.parts).split())))


def recent_posts(channel):
    username = str(channel).lstrip('@')
    if not re.fullmatch(r'[A-Za-z0-9_]+', username):
        raise RuntimeError('Public @channel required for delivery reconciliation')
    try:
        response = requests.get('https://t.me/s/' + username,
                                headers={'Cache-Control': 'no-cache'}, timeout=30)
        response.raise_for_status()
        parser = _History()
        parser.feed(response.text)
    except requests.RequestException:
        raise RuntimeError('Cannot check public Telegram history; stopped before retrying') from None
    posts = [(ref, text) for ref, text in parser.posts
             if ref and ref.startswith(username + '/')]
    if not posts:
        raise RuntimeError('Public Telegram history has no readable posts; stopped')
    return posts


def _existing(posts, caption):
    wanted = normalized(caption)
    for ref, text in reversed(posts):
        if wanted == text:
            username, message_id = ref.split('/')
            return {'ok': True, 'reconciled': True, 'result': {
                'message_id': int(message_id), 'chat': {'username': username}}}
    return None


def send_photo_checked(photo_path, caption, chat=CHANNEL, bot_token=None):
    existing = _existing(recent_posts(chat), caption)
    if existing:
        print('::notice::Post already visible in Telegram; skipping duplicate upload')
        return existing
    try:
        result = send_photo(photo_path, caption, chat=chat, bot_token=bot_token)
    except requests.RequestException as exc:
        print("::warning::Telegram transport failure: " + type(exc).__name__)
        if isinstance(exc, requests.HTTPError) and exc.response is not None:
            print("::warning::Telegram HTTP status: " + str(exc.response.status_code))
            try:
                description = exc.response.json().get("description", "")
                print("::warning::Telegram API: " + str(description)[:300], flush=True)
            except ValueError:
                pass
            if 400 <= exc.response.status_code < 500:
                raise RuntimeError('Telegram explicitly rejected send (HTTP %s); queue unchanged.' % exc.response.status_code) from None
        existing = _existing(recent_posts(chat), caption)
        if existing:
            print('::notice::Telegram delivery confirmed after transport error')
            return existing
        raise RuntimeError('Telegram delivery uncertain; not retried. Check channel before manual resend.') from None
    if not result.get('ok'):
        raise RuntimeError('Telegram rejected post, error code %s' % result.get('error_code'))
    return result
