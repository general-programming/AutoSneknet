import os
import sys
import re
import time
import random
import sentry_sdk

from sentry_sdk.integrations.excepthook import ExcepthookIntegration

sentry_sdk.init("https://4587d3478b7e4a029ca43fe88985d5ac@sentry.generalprogramming.org/2", integrations=[ExcepthookIntegration(always_run=True)])

from colored import fore, back, style

from api import GremlinsAPI, Sneknet
from logger import log

REDDIT_TOKEN = os.environ.get("REDDIT_TOKEN", None)
if not REDDIT_TOKEN:
    print(back.RED + fore.BLACK)
    print('\n\nYOU MUST SET "REDDIT_TOKEN"\n\n')
    print(style.RESET, end='')
    sys.exit(0)

SNEKNET_TOKEN = os.environ.get("SNEKNET_TOKEN", None)

re_csrf = re.compile(r"<gremlin-app\n\s*csrf=\"(.*)\"")
re_notes_ids = re.compile(r"<gremlin-note id=\"(.*)\"")
re_notes = re.compile(r"<gremlin-note id=\".*\">\n\s*(.*)")
re_plswait = re.compile(r"<gremlin-prompt>\n.*<h1>(.*)</h1>\n.*<p>Please try again in a moment.</p>")

sneknet = Sneknet(SNEKNET_TOKEN)
gremlins = GremlinsAPI(REDDIT_TOKEN)

print(fore.GREEN_YELLOW)
print('🐍  https://snakeroom.org/sneknet 🐍')
print(style.RESET)

x = 0

while x < (42069 - 310):
    log.debug('='*50)
    room = gremlins.room()

    plswait = re_plswait.findall(room.text)
    if plswait:
        for i in range(5):
            print(f'{back.WHITE}{fore.BLACK}{plswait[0]}' + ('' if i % 2 == 0 else back.BLACK) + ' ' + style.RESET, end='\r')
            time.sleep(1)
        continue

    print('', end='')

    csrf = re_csrf.findall(room.text)[0]
    ids = re_notes_ids.findall(room.text)
    notes_content = re_notes.findall(room.text)

    notes = {ids[i]: notes_content[i] for i in range(len(ids))}

    # Query Sneknet for known, and remove known humans from the notes
    known = sneknet.query(notes_content)
    if False in known.values():
        humans = dict(filter(lambda elem: elem[1] is False, known.items()))
        human_id = random.choice(list(humans.keys()))
        print(f'[{fore.GREEN_YELLOW} HUMAN {style.RESET}][{len(notes)}]', end='')
        _id = ids[human_id]
    else:
        print(f'[{fore.YELLOW} YOLO {style.RESET}][{len(notes)}]', end='')
        _id = random.choice(list(notes.keys()))
        log.debug(f'Picking random from {len(notes)} options, {_id=}, {notes=}, "{notes[_id]}"')

    text = notes[_id]

    print(f'[ {text:110} ]', end='')

    is_correct = gremlins.submit_guess(_id, csrf)

    log.debug(f'{is_correct=}')

    if is_correct:
        print(f'[{fore.LIGHT_GREEN} W {style.RESET}]', end='')
    else:
        print(f'[{fore.RED} L {style.RESET}]', end='')


    if len(notes) == 2:
        log.debug(f'50% chance "{notes[_id]}" {is_correct=}')
        del notes[_id] # delete the one we know
        options = [
            {
                "message": text,
                "correct": is_correct
            },
            {
                "message": notes[list(notes.keys())[0]],
                "correct": not is_correct
            }
        ]

    else:
        options = [
            {
                "message": text,
                "correct": True
            },
            *[{
                "message": content,
                "correct": False
            } for i, content in notes.items() if i != _id]
        ] if is_correct else [
            {
                "message": text,
                "correct": False
            }
        ]

    seen = sneknet.submit(options)

    log.debug(f'{seen=}')

    if seen:
        print(f'[{fore.CYAN}  SEEN  {style.RESET}]', end='')
    else:
        print(f'[{fore.MAGENTA} UNSEEN {style.RESET}]', end='')

    print('')
