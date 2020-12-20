from icalendar import *
import datetime
import pytz
import requests as r
import time
import re
import os
import json
from threading import Thread,Lock
import pymongo
import settings
import urllib

data = {}
with open('sources.json') as f: data = json.load(f)

# Create Timezone object
EST = pytz.timezone('America/New_York')

# Make a event ref from example.ics
g = open('api/example.ics', 'rb')
cal = Calendar.from_ical(g.read())
eventTypeRef = type(cal.walk()[-1])

TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

def filterByDate(eventList,mindate):
    mindate = mindate-datetime.timedelta(days=1)
    datetimenow = mindate.replace(tzinfo = pytz.UTC)
    datenow = datetimenow.date()
    filtered = []
    for event in eventList:
        try:
            if event.get('dtstart').dt > datetimenow:
                filtered.append(event)
        except:
            try:
                if event.get('dtstart').dt > datenow:
                    filtered.append(event)
            except:
                print('event add date fail')
    return filtered

#converts the a item of type eventTypeRef to the format in the database
def transform(item, tags):
    copy_tags = [x for x in tags]
    obj = {
        "summary": item.get('SUMMARY'), 
        "description": remove_tags(item.get('DESCRIPTION')),
        "location": item.get('LOCATION'),
        "start_time": time.mktime(item.get('DTSTART').dt.timetuple()), 
        "end_time": time.mktime(item.get('DTEND').dt.timetuple()), 
        "url": item.get('URL'),
        "tags": copy_tags
    }
    return obj

#mines the events in a given url and assigns them tags
def eventMineUrlTags(url, tags):
    eventsList = []
    cal = Calendar.from_ical(r.get(url).text)
    for item in cal.walk():
        if type(item) == eventTypeRef:
            if type(item['DTSTART'].dt) == datetime.datetime:
                try:
                    item['DTSTART'] = prop.vDatetime(item['DTSTART'].dt.astimezone(EST))
                    item['DTEND'] = prop.vDatetime(item['DTEND'].dt.astimezone(EST))
                except:
                    pass
            eventsList.append(item)
    eventsList = filterByDate(eventsList, datetime.datetime.now())
    res = [transform(x, tags) for x in eventsList]
    return res

#copied original scrape function except for a single url
def scrape(url, tags):
    try:
        print(url)
        a = eventMineUrlTags(url, tags)
        return a, 1
    except Exception as e:
        print(str(e))
        print("combine failed on " + url)
        return [], 0

#traverses the json and scrapes each calendar
#returns a list of parsed events
def fetchEvents(par, tags):
    res = []
    numsuccess = 0
    for key in par:
        tags.append(key)
        if (isinstance(par[key], str)): 
            temp, succ = scrape(par[key], tags)
            res += temp
            numsuccess += succ
        elif (isinstance(par[key], list)):
            for each in par[key]:
                temp, succ = scrape(each, tags)
                res += temp
                numsuccess += succ
        else: 
            temp, succ = fetchEvents(par[key], tags)
            res += temp
            numsuccess += succ
        tags.pop(-1)
    return res, numsuccess

#filter out the events with very short descriptions or possible duplicates
def filterEvents(eventList):
    temp = [x for x in eventList if len(x["description"].strip()) >= 1]
    uniques = set()
    res = []
    for each in temp:
        if each["description"]+str(each["start_time"]) not in uniques:
            uniques.add(each["description"]+str(each["start_time"]))
            res.append(each)
    return res

#returns the number of urls
def treeLeafCnt(par):
    res = 0
    for key in par:
        if (isinstance(par[key], str)): res += 1
        elif (isinstance(par[key], list)): res += len(par[key])
        else: res += treeLeafCnt(par[key])
    return res

def getAllTags(par):
    res = []
    for key in par:
        res += [key]
        if (isinstance(par[key], dict)): res += getAllTags(par[key])
    return res

def fetchToDB():
    #connect to db
    print("Connecting to host:", settings.DB_HOST)
    client = pymongo.MongoClient(settings.DB_HOST)
    db = client["carnegiecalendar"]
    col = db["events"]

    #delete all existing events
    cnt = col.delete_many({})
    print(cnt.deleted_count, " documents deleted")

    s = []
    output, succ = fetchEvents(data, s)
    output = filterEvents(output)

    numcals = treeLeafCnt(data)
    print("number of calendars parsed: ", numcals)
    print("success rate: ", 100*succ/numcals)

    #insert new events
    col.insert_many(output)
    
if __name__ == "__main__":
    fetchToDB()