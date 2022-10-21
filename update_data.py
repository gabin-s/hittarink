#!/bin/env python3
import lxml.html
import re
import datetime
import difflib
import json
import logging
import os.path
import sys
import argparse

import urllib3

from zoneinfo import ZoneInfo

from constants import *

def parse_hours(t):
    h, m = t.split('.')
    delta_start = datetime.timedelta(hours=int(h), minutes=int(m))

    return delta_start

def find_week_startdate(month, day, today):
    """
    We find a valid date as "monday <day> <month> <year>", by varying the year value.
    The first valid date is returned as a datetime.date
    If no such date is found in the previous, current and next year, ValueError is raised.
    """

    this_monday = today - datetime.timedelta(days=today.weekday())

    for i in range(-1, 2):
        try:
            t = datetime.date(year=today.year + i, day=day, month=month)
        except ValueError:
            continue # probably february 29

        if t.weekday() == 0: # check that it is a monday
            return t

    raise ValueError('no matching week found')

def extract_day_month_button(text):
    day   = int(re.search('\d+', text)[0])
    month = MONTHS.index(re.search('|'.join(MONTHS), text)[0]) + 1

    return month, day

# the accordion contains information on open hours for a week, and follows the button
def parse_btns(btns, capture_date):
    for btn in btns:
        accordion = btn.getnext()

        month, day = extract_day_month_button(btn.text_content())
        monday = find_week_startdate(month, day, capture_date)

        # create a `datetime` from `date`
        monday_dt = datetime.datetime.combine(monday, datetime.datetime.min.time())

        logging.debug(f'found schedule for week starting {monday}')

        yield monday, list(parse_accordion(accordion, monday_dt))

def parse_accordion(accordion, monday):
    first_h  = None
    second_h = None
    
    # we found the end of the block (one place)
    end_found = True

    for node in accordion:
        if node.tag == 'h3' or node.tag == 'h4':
            if end_found:
                first_h   = node.text.strip(',')
                end_found = False
            else:
                second_h = node.text.strip(',')

        elif node.tag == 'ul' and first_h is not None:
            place    = first_h
            subplace = second_h

            # correct eventual mistakes in place/subplace name
            id_place = get_place_id(place, subplace)

            for li in node.findall('li'):
                l = parse_li(li.text, monday)
                yield from [(id_place, *e) for e in l]

        elif node.tag == 'p' and 'arrow-link' in node.classes:
            first_h  = None
            second_h = None

            end_found = True

def parse_li(t, monday):
    day, rest = re.split(r'\W+', t, 1)

    offset = monday + DAYS.index(day) * ONE_DAY

    matches = re.finditer(r'(\d{2}\.\d{2}).(\d{2}\.\d{2})', rest)
    matches = list(matches)

    # group by groups of [start, end]
    for i in range(len(matches)):
        m = matches[i]

        h_start = m.group(1)
        h_end   = m.group(2)

        a = m.span(0)[1]
        b = matches[i+1].span(0)[0] if i + 1 < len(matches) else None

        delta_start = datetime.timedelta(hours=int(h_start[:2]), minutes=int(h_start[3:]))
        delta_end   = datetime.timedelta(hours=int(h_end[:2]),   minutes=int(h_end[3:]))

        comment = rest[a:b].lower()
        # remove " och ", " + ", and ", "
        comment = comment.strip(',').strip()
        comment = re.sub(r'(\+|och)$', '', comment).strip()

        yield offset + delta_start, offset + delta_end, comment

def find_candidates_btn(parsed):
    candidates = []

    for e in parsed.find_class('accordion-item__header'):
        text = e.text_content().strip()

        for m in MONTHS:
            if m in text: 
                candidates.append(e)
                break

    return candidates

def get_place_id(place, subplace):
    id_place, possible_subplaces = next(
        (i, l) for i, (x, l) in enumerate(PLACES) if x == place)

    offset = PLACES_OFFSETS[id_place]

    if possible_subplaces is None:
        return id_place + offset
        
    best_match = difflib.get_close_matches(
        subplace, possible_subplaces, n=1, cutoff=0.2)[0]

    return possible_subplaces.index(best_match) + offset

def json_default(o):
    if isinstance(o, datetime.datetime):
        return o.astimezone(ZoneInfo(TIMEZONE)).timestamp() * 1000

def eprint(*args, **kwargs):
    print('error:', *args, file=sys.stderr, *kwargs)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Fetch and parse schedule for Stockholm City ice skating areas')
    parser.add_argument('-u', '--url',
        help="URL from which to get the schedule",
        default=URL)
    parser.add_argument('-d', '--destdir', 
        help='destination of the produced machine-readable schedule', 
        default=DESTDIR_DEFAULT)
    parser.add_argument('-v', '--verbose', 
        help='show debug informations',
        action='store_true')
    args = parser.parse_args()

    destdir = args.destdir
    url     = args.url

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not os.path.exists(destdir):
        eprint(f"folder '{destdir}' does not exist")
        exit(1)
    elif not os.path.isdir(destdir):
        eprint(f"destination directory '{destdir}' is not a directory")
        exit(1)

    logging.debug(f"output to '{args.destdir}'")
    logging.debug(f"fetching data from '{url}'")

    # get data from Stockholm stad
    try:
        http = urllib3.PoolManager()
        res = http.request('GET', url)
    except urllib3.exceptions.HTTPError as e:
        eprint(e)
        exit(1)

    if res.status != 200:
        eprint(f"unable to fetch data: HTTP {res.status}")
        exit(1)

    logging.debug('fetched page')

    parsed = lxml.html.document_fromstring(res.data.decode('utf-8'))

    # 1 - find buttons matching accordion header
    candidates = find_candidates_btn(parsed)

    # 2 - parse the accordion content
    all_schedules = parse_btns(candidates, datetime.date.today())

    # 3 - dump schedule
    for day, schedules in all_schedules:
        fname = day.isoformat() + '.json'

        with open(os.path.join(destdir, fname), 'w') as f:
            json.dump(schedules, f, default=json_default)