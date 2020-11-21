from flask import Flask, render_template, url_for, render_template_string, Markup, redirect, request, send_file, session, jsonify


import re
import sys
from datetime import datetime
import os
import time
from icalendar import *
import atexit
import calendarfetch
from multiprocessing import Process
import json
import pymongo
from flask_cors import CORS
import settings

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.urandom(16)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

DEBUG = False
FLATPAGES_AUTO_RELOAD = DEBUG
# export FLASK_ENV=development

forbidden_searches = ['pizza', 'lunch', 'food', 'free', 'swag', 'merch', 'dinner'] # Maybe use these if you commercialize

# To get instance of event type, we use example.ics
g = open('example.ics', 'rb')
cal = Calendar.from_ical(g.read())
eventTypeRef = type(cal.walk()[-1])

TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

# def makeICS(eventList, name):
#     calendar = Calendar()
#     for event in eventList:
#         calendar.add_component(event)
#     calendar.add('prodid', "Carnegie Calendar")
#     calendar.add('version', '2.0')

#     f = open("generatedcals/" + name + ".ics",'wb+')

#     f.write(calendar.to_ical())
#     f.close()

# Used in the renderer to make a nice "January 7, 2020" text from the datetime object
def dateconvert(str):
    timezoneoffset = 0
    try:
        str = str.replace(hour=str.hour-timezoneoffset)
    except:
        pass
    return str.strftime("%-I:%M %p, %B %-d, %Y")
app.jinja_env.globals.update(dateconvert=dateconvert)

def getAllEvents():
    #connect to db
    client = pymongo.MongoClient(settings.DB_HOST)
    db = client["carnegiecalendar"]
    col = db["events"]
    eventList = col.find({}, {'_id': False})

    # Sort eventList by date so it displays properly
    try:
        curTime = time.mktime(time.localtime())
        eventList = [x for x in sorted(eventList, key=lambda event:event["start_time"]) if x["start_time"] > curTime]
    except:
        print("sort by date failed", time.localtime())
    return eventList

def shallow_copy(obj):
    res = {}
    for key in obj:
        res[key] = obj[key]
    return res

def filter_by_search_str (eventList, search_str):
    res = []
    terms = [x.strip().lower() for x in search_str.split(" ")]
    for event in eventList:
        matchval = 0
        for term in terms:
            for field in event.values():
                if (field is not None) and (term in str(field).lower()): matchval += str(field).lower().count(term)
        if (matchval == 0): continue
        event["matchval"] = matchval
        res.append(event)
    try:
        res.sort(key=lambda event: event["matchval"], reverse=True) #sort is stable
    except:
        print("sort by matchval failed")
    for event in res:
        event.pop("matchval", None)
    return res

def filter_by_start_time(eventList, start):
    try:
        start = float(start)
    except: 
        print("Invalid type")
        return eventList
    res = [x for x in eventList if x ["start_time"] >= start]
    return res

def filter_by_end_time(eventList, end):
    try:
        end = float(end)
    except:
        print("Invalid type")
        return eventList
    res = [x for x in eventList if x ["end_time"] <= end]
    return res

def intersection (a, b):
    return set([x for x in b if x in a])

def filter_by_tags(eventList, tags):
    res = []
    for x in eventList:
        n = len(intersection(tags, x["tags"]))
        if (n == 0): continue
        x["compval"] = n
        res.append(x)
    try:
        res.sort(key=lambda event: event["compval"], reverse=True) #sort is stable
    except Exception as e:
        print(e)
        print("sort by compval failed")
    for event in res:
        event.pop("compval", None)
    return res

@app.route("/", methods=['GET'])
def index():
    return jsonify(getAllEvents())

@app.route("/tags", methods=['GET'])
def getTags():
    return jsonify(calendarfetch.getAllTags(calendarfetch.data))

#result is sorted based on tags, search string and then date
#if all three filters are applied
@app.route("/search", methods=['GET'])
def search():
    search_str = request.args.get('search_str')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    tags = []
    try: tags = json.loads(request.args.get('tags'))
    except Exception as e: print(e)
    events = getAllEvents()
    if (search_str != ""): 
        events = filter_by_search_str(events, search_str)
    if (start_time != ""): 
        events = filter_by_start_time(events, start_time)
    if (end_time != ""): 
        events = filter_by_end_time(events, end_time)
    if (type(tags) == list):
        events = filter_by_tags(events, tags)
    return jsonify(events)
    
###### FETCH DATA ######
if __name__ == "__main__":
    app.run(port=5050)

def newDataAsync():
    pro = Process(
        target=calendarfetch.fetchToDB,
        daemon=True
    )
    pro.start()

scheduler = BackgroundScheduler()
scheduler.add_job(func=newDataAsync, trigger="interval", seconds=3600)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())




