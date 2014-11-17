# -*- coding: utf-8 -*-
import requests
from datetime import datetime, timedelta
from json import dumps
from pytz import timezone
from tzlocal import get_localzone
from iso8601 import parse_date


TZ = timezone(get_localzone().tzname(datetime.now()))


def get_now():
    return datetime.now(TZ)


def check_tender(tender):
    enquiryPeriodEnd = tender.get('enquiryPeriod', {}).get('endDate')
    enquiryPeriodEnd = enquiryPeriodEnd and parse_date(enquiryPeriodEnd, TZ)
    tenderPeriodEnd = tender.get('tenderPeriod', {}).get('endDate')
    tenderPeriodEnd = tenderPeriodEnd and parse_date(tenderPeriodEnd, TZ)
    now = get_now()
    if tender['status'] == 'enquiries' and enquiryPeriodEnd and enquiryPeriodEnd < now:
        return {'status': 'tendering'}, now + timedelta(seconds=5)
    elif tender['status'] == 'tendering' and tenderPeriodEnd and tenderPeriodEnd < now:
        return {'status': 'auction'}, now + timedelta(seconds=5)
    if enquiryPeriodEnd and enquiryPeriodEnd > now:
        return None, enquiryPeriodEnd
    elif tenderPeriodEnd and tenderPeriodEnd > now:
        return None, tenderPeriodEnd
    return None, None


def push(url, params):
    requests.get(url, params=params)


def resync_tender(scheduler, url, callback_url):
    r = requests.get(url)
    json = r.json()
    tender = json['data']
    changes, next_check = check_tender(tender)
    if changes:
        r = requests.patch(url,
                           data=dumps({'data': changes}),
                           headers={'Content-Type': 'application/json'})
    if next_check:
        scheduler.add_job(push, 'date', run_date=next_check, timezone=TZ,
                          id=tender['id'],
                          args=[callback_url, None], replace_existing=True)
    return changes, next_check


def resync_tenders(scheduler, next_url, callback_url):
    while True:
        try:
            r = requests.get(next_url)
            json = r.json()
            next_url = json['next_page']['uri']
            if not json['data']:
                break
            for tender in json['data']:
                run_date = get_now() + timedelta(seconds=5)
                scheduler.add_job(push, 'date', run_date=run_date, timezone=TZ,
                                  id=tender['id'],
                                  args=[callback_url + 'resync/' + tender['id'], None],
                                  replace_existing=True)
        except:
            break
    run_date = get_now() + timedelta(seconds=60)
    scheduler.add_job(push, 'date', run_date=run_date, timezone=TZ,
                      id='resync_all',
                      args=[callback_url + 'resync_all', {'url': next_url}],
                      replace_existing=True)
    return next_url
