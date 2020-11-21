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
#lock/mutex for combineEvents
lock = Lock()

# 2/17 you added summary+datetime checks on sitebuilder then realized you do the same thing here in combine. Redundancy, to remedy later.

# Add this later: HKSA andrew.cmu.edu_b25qoeqpgrml2duvr76ddj0nvk%40group.calendar.google.com

# TODO: Should I add Pitt sites? Here's their main Calendar
# webcal://calendar.pitt.edu/calendar.ics

extras = ["https://calendar.google.com/calendar/ical/bsl9um0icm15p91qfs6f130o28%40group.calendar.google.com/private-ba4910384454db5dea7f348da1870c41/basic.ics","https://thebridge.cmu.edu/events.ics",
            ]

sites = ["https://thebridge.cmu.edu/events.ics",
         "https://www.cs.cmu.edu/calendar/export.ics",
         "https://events.time.ly/vdibqnd/export?format=ics",
         "https://calendar.google.com/calendar/ical/t6ebuir6klabea3q87b5qjs360@group.calendar.google.com/public/basic.ics",
         # "https://athletics.cmu.edu/composite?print=ical", # These events suck
         "https://thebridge.cmu.edu/events.ics"
         ]

forbidden = [ "https://timelyapp.time.ly/api/calendars/54703220/export?format=ics&categories=677430534&timely_id=timely_0.39786058117271694",
            # Physic department link. Broken, but replaced by above"https://events.time.ly/0qe3bmk/export?format=ics&categories=21686&filterGroupItems=8498",
            #Math department link. Broken, but replaced below"https://events.time.ly/0qe3bmk/export?format=ics&categories=21683&filterGroupItems=8498",
            "https://timelyapp.time.ly/api/calendars/54703220/export?format=ics&categories=677430531&filter_groups=677430583&timely_id=timely_0.3689341916690556",
            "https://timelyapp.time.ly/api/calendars/54703220/export?format=ics&categories=677430532&filter_groups=677430583&timely_id=timely_0.14297524898164982",
            #Biology department link. replaced below"https://events.time.ly/0qe3bmk/export?format=ics&categories=21685&filterGroupItems=8498",
            "https://timelyapp.time.ly/api/calendars/54703220/export?format=ics&categories=677430533&filter_groups=677430583&timely_id=timely_0.13951306083680404",
            # Not working "http://www.cbd.cmu.edu/?plugin=all-in-one-event-calendar&controller=ai1ec_exporter_controller&action=export_events&no_html=true",
            "https://hcii.cmu.edu/news/calendar/ical/calendar.ics",
            "https://www.ri.cmu.edu/events/?ical=1",
            "https://tockify.com/api/feeds/ics/cmu.mld",
            "https://tockify.com/api/feeds/ics/carnegie.mellon.student.affairs",
            "https://calendar.google.com/calendar/ical/cmuenglish.events%40gmail.com/public/basic.ics",
            "https://calendar.google.com/calendar/ical/s1j4gise63gmko8hahi0hq6gh4%40group.calendar.google.com/public/basic.ics",
            "https://calendar.google.com/calendar/ical/49jqhf1r1lhmpalcro5gds4cq8@group.calendar.google.com/public/basic.ics",
            "https://calendar.google.com/calendar/ical/oj4bkj3oulrgismispejvvq0q8@group.calendar.google.com/public/basic.ics",
            "https://calendar.google.com/calendar/ical/01l1t6sb5tbaqi66bg8b19k37o%40group.calendar.google.com/public/basic.ics",
            "https://calendar.google.com/calendar/ical/cmuips%40andrew.cmu.edu/public/basic.ics",
            "https://calendar.google.com/calendar/ical/cmu.history%40gmail.com/public/basic.ics",
            #Fails here, not sure what this is"https://calendar.google.com/calendar/ical/sg3f1so6vfkrie3e0f5pbcgte4%40group.calendar.google.com/public/basic.ics",
            "https://calendar.google.com/calendar/ical/n42ba22iiu02508n0h7hnreabk%40group.calendar.google.com/public/basic.ics",
            #Broken "https://calendar.google.com/calendar/ical/6s7ucb5etjine4d1a6ciqai73c%40group.calendar.google.com/public/basic.ics",
            "http://drama.cmu.edu/?plugin=all-in-one-event-calendar&controller=ai1ec_exporter_controller&action=export_events&no_html=true&ai1ec_cat_ids=218",
            "https://calendar.google.com/calendar/ical/soa-faculty%40andrew.cmu.edu/public/basic.ics",
            "https://calendar.google.com/calendar/ical/soa-public%40andrew.cmu.edu/public/basic.ics",
            "https://calendar.google.com/calendar/ical/soa-students%40andrew.cmu.edu/public/basic.ics",
            "https://calendar.google.com/calendar/ical/cmubme1%40gmail.com/public/basic.ics",
            "https://calendar.google.com/calendar/ical/ideate.cmu@gmail.com/public/basic.ics"]

clubs = ["https://calendar.google.com/calendar/ical/andrew.cmu.edu_qlki4fofh1c88b923gi3smserk%40group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/hrhf352iju0ji55vj827dbu2fk@group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/carnegiemellonbmes%40gmail.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/andrew.cmu.edu_ot9dhr61gp27kqlsb96mlabkjc%40group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/eifn0motia6k9qv22g9b2cc4dk%40group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/andrew.cmu.edu_e67sdhltdrfbcck8u28fui745o%40group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/cmu.shpe%40gmail.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/85bf0h78fidsgkkgmkktrqasm8@group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/cmu.scottylabs@gmail.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/utd7jhfrl48p37jth64hue0lis%40group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/studioforcreativeinquiry%40gmail.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/andrew.cmu.edu_j1rdb53mqfj67ch9477hcpl2s8%40group.calendar.google.com/public/basic.ics",
#Private, so will need to find out more before doing anything"https://calendar.google.com/calendar/ical/andrew.cmu.edu_b25qoeqpgrml2duvr76ddj0nvk%40group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/efrdv449m13u8atk9fl8hhv8o4@group.calendar.google.com/public/basic.ics"
]



labs = ["https://calendar.google.com/calendar/ical/cmuips%40andrew.cmu.edu/public/basic.ics",
"https://calendar.google.com/calendar/ical/leonard.gelfand.center@gmail.com/public/basic.ics",
#ICC Calendar, replaced below #"https://calendar.google.com/calendar/ical/cmu.icc%40gmail.com/public/basic.ics",
"https://tockify.com/api/feeds/ics/student.success",
#No documentation, so I don't know what to do"https://calendar.google.com/calendar/ical/bm3mt8r4784bi563b1jg4tgijo@group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/86cvp8rs4pbcnfvc8t4v7ku05o@group.calendar.google.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/ehilrdcr39kf3p7lrtnck0vvs8@group.calendar.google.com/public/basic.ics",
"https://tockify.com/api/feeds/ics/swartzcalendar",
"https://www.trumba.com/calendars/SMU_LARC.ics?filterview=Publish+to+NextWeb&filter4=_798882_&filterfield4=37908",
"https://mobility21.cmu.edu/events/?ical=1&tribe_display=month",
"https://tockify.com/api/feeds/ics/cmu.mld",
"https://hcii.cmu.edu/news/calendar/ical/calendar.ics",
"https://calendar.google.com/calendar/ical/cmu.etc.pgh.events%40gmail.com/public/basic.ics",
"https://calendar.google.com/calendar/ical/o67cde9racfa9ss5vcvafvokss%40group.calendar.google.com/public/basic.ics"]

data = {}
with open('sources.json') as f: data = json.load(f)

# Create Timezone object
EST = pytz.timezone('America/New_York')

# Make a event ref from example.ics
g = open('example.ics', 'rb')
cal = Calendar.from_ical(g.read())
eventTypeRef = type(cal.walk()[-1])

TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)

def saveICS(name,calendar):
    if not os.path.exists("calendars"):
        os.makedirs("calendars")
    calendar.add('prodid', name)
    calendar.add('version', '2.0')

    f = open("calendars/" + name + ".ics",'wb+')
    f.write(calendar.to_ical())
    f.close()

def eventmineFILE(filepath):
    eventsList = []
    try:
        cal = Calendar.from_ical(open(filepath,'rb').read())
    except:
        print("failed")
    for item in cal.walk():
        if type(item) == eventTypeRef:
            eventsList.append(item)
    return eventsList

def eventmineURL(url):
    eventsList = []
    cal = Calendar.from_ical(r.get(url).text)
    for item in cal.walk():
        if type(item) == eventTypeRef:
            if type(item['DTSTART'].dt)  == datetime.datetime:
                try:
                    item['DTSTART'] = prop.vDatetime(item['DTSTART'].dt.astimezone(EST))
                    item['DTEND'] = prop.vDatetime(item['DTEND'].dt.astimezone(EST))
                except:
                    pass
            eventsList.append(item)
    return eventsList

#Threading function 
def scrapeInParallel(url,l,eventsList,succ):
    try:
        a = eventmineURL(url)
        l.acquire()
        eventsList.extend(a)
        succ[0]=succ[0]+1
        l.release()
    except Exception as e:
        print(str(e))
        print("combine failed on " + url)
# Copied previous function, except ran it as threading function
def combineEvents(urlList):
    eventsList = []
    succ = [0]
    for url in urlList:
        print(url)
        p = Thread(target=scrapeInParallel,args=(url,lock,eventsList,succ))
        p.start()
        p.join()

    return filterByDate(eventsList,datetime.datetime.now()), succ


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
            # pass
            try:
                if event.get('dtstart').dt > datenow:
                    filtered.append(event)
            except:
                print('event add date fail')
    return filtered

def combine(eventsList):
    cal = Calendar()
    eventNames = set()
    for event in eventsList:
        try:
            name = event['SUMMARY']+str(event.get("DTSTART").dt) # Eliminates redundant events from eventsList
            if (name not in eventNames) and len(event['DESCRIPTION']) > 0:
                cal.add_component(event)
                eventNames.add(name)
        except:
            print("event had no summary and/or description: ", event)
    return cal

# Gets the url for the ics of a google calendar from its uid and id
def goog(strList):
    for thing in strList:
        print("https://calendar.google.com/calendar/ical/" + thing + "/public/basic.ics")

# Gets the url for the ics of a facebook event
def face(str):
    return "https://www.facebook.com/events/ical/export/?eid=" + str[str.find("events/") + 7:-1]

def fetchCurrentCalendar():
    eventList,[err1] = combineEvents(sites)
    forbiddenList,[err2] = combineEvents(forbidden)
    clubList,[err3] = combineEvents(clubs)
    labsList,[err4] = combineEvents(labs)
    manualList,[err5] = combineEvents(extras)
    
    numcals = len(sites) + len(forbidden) + len(clubs) + len(labs) + len(manualList)
    print("number of calendars parsed: ", numcals)
    print("success rate: ", 100*(err1+err2+err3+err4+err5)/numcals)
    
    print("combining")
    combined = eventList + forbiddenList + clubList + labsList + manualList

    print("filtering")
    current = filterByDate(combined, datetime.datetime.now()) # Take only events that are after yesterday, to get the most recent ones
    print(len(current), "current events")
    
    print("saving")
    saveICS("current",combine(current))

# fetchCurrentCalendar()
# manualList,err5 = combineEvents(extras)
# saveICS("current",combine(filterByDate(manualList,datetime.datetime.now())))
# manualList[0]['DTSTART'].dt.astimezone(pytz.timezone('America/New_York'))


####ADDED FUNCTIONS FOR TAGS######
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
    s = []
    output, succ = fetchEvents(data, s)
    output = filterEvents(output)

    numcals = treeLeafCnt(data)
    print("number of calendars parsed: ", numcals)
    print("success rate: ", 100*succ/numcals)

    #connect to db
    client = pymongo.MongoClient(settings.DB_HOST)
    db = client["carnegiecalendar"]
    col = db["events"]

    #delete all existing events
    cnt = col.delete_many({})
    print(cnt.deleted_count, " documents deleted")

    #insert new events
    col.insert_many(output)
    

# fetchToDB()





# Mailing events:
# https://nanofab.ece.cmu.edu/news-events/index.html
# https://lists.andrew.cmu.edu/mailman/listinfo/calcm-list


                                    # Labs and stuff like them

# Center for International Relations and Politics: https://www.cmu.edu/ir/top-nav/calendar.html
# cmuips%40andrew.cmu.edu

# Gelfand Center: https://www.cmu.edu/gelfand/calendar.html
# leonard.gelfand.center@gmail.com

# Intercultural Communications Center: https://www.cmu.edu/icc/calendar/index.html
# cmu.icc%40gmail.com

# Swartz: https://www.cmu.edu/swartz-center-for-entrepreneurship/events/index.html
# https://tockify.com/api/feeds/ics/swartzcalendar

# Techspark: https://engineering.cmu.edu/techspark/facilities/calendar.html
# bm3mt8r4784bi563b1jg4tgijo@group.calendar.google.com

# Block Center: https://www.cmu.edu/block-center/news-events/index.html
# TODO: One of those weird CMU custom text calendars

# Heinz College : https://www.heinz.cmu.edu/events/#category=Featured%20Events&category=Admissions&category=Alumni&category=Conferences&category=Current%20Student%20Events&category=Speakers&pageIndex=0&pageSize=9
# TODO: Text CMU calendar

# Cylab: https://www.cylab.cmu.edu/events/index.html
# TODO: Text fucking calendar

# Living Analytics Research Center
# https://www.trumba.com/calendars/SMU_LARC.ics?filterview=Publish+to+NextWeb&filter4=_798882_&filterfield4=37908

# Heinz Progress: https://progress.heinz.cmu.edu/events/
# single events, not often

# Mobility21/Traffic 21:
# https://mobility21.cmu.edu/events/?ical=1&tribe_display=month

# ML  department:
# https://tockify.com/api/feeds/ics/cmu.mld

# HCII:https://hcii.cmu.edu/news/calendar
# https://hcii.cmu.edu/news/calendar/ical/calendar.ics

# Software Engineering Institute: https://www.sei.cmu.edu/news-events/events/index.cfm
# TODO: Custom-loaded calendar

# iii: https://www.cmu.edu/iii/about/events/index.html
# only virtual admissions events

# Environmental stuff: https://www.cmu.edu/environment/events/index.html
# monthly boring events

# Steinbrenner institute: https://www.cmu.edu/steinbrenner/events/index.html
# TODO: some manually parsed events

# Scott Energy stuff: https://www.cmu.edu/energy/events/index.html
# 86cvp8rs4pbcnfvc8t4v7ku05o@group.calendar.google.com

# Pittsburgh Supercomputing Center: https://www.psc.edu/
# TODO: Strange text calendar

# McWilliams Cosmology: https://www.cmu.edu/cosmology/events/index.html
# TODO: Weekly astro lunch

# Center for Nonlinear Analysis: https://www.cmu.edu/math/cna/events/index.html
# OVERLAPS WITH MATH: https://events.time.ly/0qe3bmk/export?format=ics&tags=146498&categories=21683&filterGroupItems=8498

# Data storage group: http://www.dssc.ece.cmu.edu/news/events/index.html
# has a few conferences

# Center for the Arts in Society: https://www.cmu.edu/cas/
# ehilrdcr39kf3p7lrtnck0vvs8@group.calendar.google.com

# CAUSE: https://www.cmu.edu/history/cause/events/
# TODO: a few talks occasionally, text

# center for ethics and policy: http://centerforethicsandpolicy.com/events.html
# TODO: text talks

# Entertainment Tech Center (Randy Pausch's final project): http://www.etc.cmu.edu/
# lots of events, but RPIS means 700 technology drive
# general pburgh events
# https://calendar.google.com/calendar/embed?src=cmu.etc.pgh.events%40gmail.com&ctz=America/New_York
# https://calendar.google.com/calendar/ical/cmu.etc.pgh.events%40gmail.com/public/basic.ics
# visiting seminars i think
# https://calendar.google.com/calendar/embed?src=o67cde9racfa9ss5vcvafvokss%40group.calendar.google.com&ctz=America/New_York
# https://calendar.google.com/calendar/ical/o67cde9racfa9ss5vcvafvokss%40group.calendar.google.com/public/basic.ics



                                    # Student Orgs and other campus activities
# Carnegie Mellon Tickets:
# https://carnegiemellontickets.universitytickets.com/w/calendar.aspx

# C++ Singing: sent through email
# https://calendar.google.com/calendar/ical/efrdv449m13u8atk9fl8hhv8o4@group.calendar.google.com/public/basic.ics

# ANVIL: https://cmuanvil.wordpress.com/
# andrew.cmu.edu_j1rdb53mqfj67ch9477hcpl2s8%40group.calendar.google.com

# ACM: https://acmatcmu.org/
# TODO: Three manual events

# Moneythink: http://moneythinkcmu.org/
# andrew.cmu.edu_qlki4fofh1c88b923gi3smserk%40group.calendar.google.com

# CMU Computer Club: http://www.cmucc.org/#calendar
# hrhf352iju0ji55vj827dbu2fk@group.calendar.google.com

# CMU Sports Analytics: https://www.cmusportsanalytics.com/calendar/
# EMPTY CALENDAR

# Math club: http://club.math.cmu.edu/Events/index.html
# Text events that are not really updated.

# carnegie mellon racing: https://www.carnegiemellonracing.org/calendar
# No calendar

# Society of Asian Scientists and Engineers: http://www.cmusase.org/events.html
# Empty calendar

# Society of Women Engineers: https://cmuswe.org/calendar
# TODO: Text scraper

# Pugwash
# Shows up on SCS Events page

# BME Society: https://thebridge.cmu.edu/organization/bmes
# carnegiemellonbmes%40gmail.com

# Eta Kappa Nu IEEE Honor Society: http://hkn.ece.cmu.edu/index.php?location=activities
# andrew.cmu.edu_ot9dhr61gp27kqlsb96mlabkjc%40group.calendar.google.com

# Tau Beta Pi Engineering honor society
# eifn0motia6k9qv22g9b2cc4dk%40group.calendar.google.com

# IEEE: https://www.archive.ece.cmu.edu/~ieee/events.html
# andrew.cmu.edu_e67sdhltdrfbcck8u28fui745o%40group.calendar.google.com

# CMU Society of Hispanic Engineers: http://www.cmushpe.com/
# cmu.shpe%40gmail.com

# Roboclub: https://roboticsclub.org/calendar/
# 85bf0h78fidsgkkgmkktrqasm8@group.calendar.google.com

# ScottyLabs: https://scottylabs.org/#calendar
# cmu.scottylabs@gmail.com

# Student Government: https://www.cmu.edu/stugov/gsa/Upcoming-Events/index.html
# https://calendar.google.com/calendar/ical/utd7jhfrl48p37jth64hue0lis%40group.calendar.google.com/public/basic.ics

# Library: http://cmu.libcal.com/calendar/events/?cid=7168&t=m&d=0000-00-00&cal=7168
# TODO: it's a Libcal

# CMU Library TODO: https://cmu.libcal.com/
# Libcal :(

# HSKA: "https://calendar.google.com/calendar/ical/andrew.cmu.edu_b25qoeqpgrml2duvr76ddj0nvk%40group.calendar.google.com/public/basic.ics"
# TODO: Private calendar :(

                                # PUBLIC DOMAIN



# CMU STUDENT AFFAIRS CALENDAR
# "https://tockify.com/api/feeds/ics/carnegie.mellon.student.affairs"

# NOTE: the site below has a calendar corresponding to the link above. Not sure what link below is, but it doesn't work
# CMU Main Events: https://www.cmu.edu/events/
# https://calendar.google.com/calendar/ical/andrew.cmu.edu_333234353933332d373938%40resource.calendar.google.com/public/basic.ics


# SCS Events: https://www.cs.cmu.edu/calendar?page=0
# https://www.cs.cmu.edu/calendar/export.ics

# Mellon College of Science: https://events.mcs.cmu.edu/
# https://timelyapp.time.ly/api/calendars/54703220/export?format=xml&filter_groups=677430583,677430575,677430576,677430580,677430577&timely_id=timely_0.5714552038110052

# School of Music: https://www.cmu.edu/cfa/music/concerts-events/index.html
# https://events.time.ly/vdibqnd/export?format=ics

# Dietrich: https://www.cmu.edu/dietrich/about/calendar/index.html
# https://calendar.google.com/calendar/ical/t6ebuir6klabea3q87b5qjs360@group.calendar.google.com/public/basic.ics

# Tepper: https://www.cmu.edu/tepper/news/events/index.html # Also has an alumnihub that hosts events?
# TODO: Custom rows that look generated by static site generator. SAD!

# CIT: https://engineering.cmu.edu/news-events/events/index.html
# TODO: Same as Tepper, text parsing necessary

# The Bridge: https://thebridge.cmu.edu/events
# https://thebridge.cmu.edu/events.ics

# University Health Services: https://www.cmu.edu/health-services/news/index.html
# Must be manually input but it is almost completely empty.

# Student activities board: https://www.facebook.com/events/1733630436768968/
# TODO: Active only on facebook. Make a facebook events parser

# Run facebook events through here to download the .ics containing just that event
# https://www.facebook.com/events/ical/export/?eid=896833190715323


# ! ! ! ! ! OFF LIMITS ! ! ! ! ! TODO: Add Lab events

                                        # MCS

# Physics: https://www.cmu.edu/physics/news-events/events/index.html
# https://events.time.ly/0qe3bmk/export?format=ics&categories=21686&filterGroupItems=8498
#Upadted from site: https://timelyapp.time.ly/api/calendars/54703220/export?format=ics&categories=677430534&timely_id=timely_0.39786058117271694

# Mathematics: https://www.cmu.edu/math/news-events/calendar.html
# https://events.time.ly/0qe3bmk/export?format=ics&categories=21683&filterGroupItems=8498
#Updated link: https://timelyapp.time.ly/api/calendars/54703220/export?format=ics&categories=677430531&filter_groups=677430583&timely_id=timely_0.3689341916690556

# Chemistry: https://www.cmu.edu/chemistry/news/calendar.html
# https://events.time.ly/0qe3bmk/export?format=ics&categories=21684&filterGroupItems=8498
#UPDATED from site: https://timelyapp.time.ly/api/calendars/54703220/export?format=ics&categories=677430532&filter_groups=677430583&timely_id=timely_0.14297524898164982

# Biology: https://www.cmu.edu/bio/events/index.html
# https://events.time.ly/0qe3bmk/export?format=ics&categories=21685&filterGroupItems=8498
#UPDATED: https://timelyapp.time.ly/api/calendars/54703220/export?format=ics&categories=677430533&filter_groups=677430583&timely_id=timely_0.13951306083680404
                                        # SCS

# Computational Biology Department: http://www.cbd.cmu.edu/calendar/
# http://www.cbd.cmu.edu/?plugin=all-in-one-event-calendar&controller=ai1ec_exporter_controller&action=export_events&no_html=true

# HCII: https://hcii.cmu.edu/news/calendar
# https://hcii.cmu.edu/news/calendar/ical/calendar.ics

# LTI: https://www.lti.cs.cmu.edu/calendar
# Calendar is blank

# ML: https://www.ml.cmu.edu/calendar/
# https://tockify.com/api/feeds/ics/cmu.mld

# ISR: https://www.isri.cmu.edu/events/index.html
# TODO: A few static events to be manually added, including https://www.isri.cmu.edu/lunchandlearn.html

# RI: https://www.ri.cmu.edu/events/
# https://www.ri.cmu.edu/events/?ical=1


                                        # Dietrich

# English: https://www.cmu.edu/dietrich/english/news/events/index.html
# # https://calendar.google.com/calendar/ical/cmuenglish.events%40gmail.com/public/basic.ics

# Statistics and Data Science: http://www.stat.cmu.edu/calendar
# https://calendar.google.com/calendar/ical/s1j4gise63gmko8hahi0hq6gh4%40group.calendar.google.com/public/basic.ics

# NeuroSAG: https://www.cmu.edu/neuro/neurosac/calendar.html
# TODO: Google Calendar is off-limits

# Psychology: https://www.cmu.edu/dietrich/psychology/events/index.html
# https://calendar.google.com/calendar/ical/49jqhf1r1lhmpalcro5gds4cq8@group.calendar.google.com/public/basic.ics

# Center for Neural Basis of Cognition (CNBC)
# https://calendar.google.com/calendar/ical/oj4bkj3oulrgismispejvvq0q8@group.calendar.google.com/public/basic.ics
# oj4bkj3oulrgismispejvvq0q8@group.calendar.google.com

# Social and Decision Sciences: https://www.cmu.edu/dietrich/sds/events/index.html
# TODO: There's two, they look manual

# Department of Modern Languages: https://www.cmu.edu/dietrich/modlang/events/index.html
# TODO: Weird ass boxes make it so I need to parse manually

# Philosophy: https://www.cmu.edu/dietrich/philosophy/events/index.html
# https://calendar.google.com/calendar/ical/01l1t6sb5tbaqi66bg8b19k37o%40group.calendar.google.com/public/basic.ics

# Institute for Politics and Strategy: https://www.cmu.edu/ips/index.html
# https://calendar.google.com/calendar/ical/cmuips%40andrew.cmu.edu/public/basic.ics

# History: https://www.cmu.edu/dietrich/history/calendar/index.html
# https://calendar.google.com/calendar/ical/cmu.history%40gmail.com/public/basic.ics
# https://calendar.google.com/calendar/ical/sg3f1so6vfkrie3e0f5pbcgte4%40group.calendar.google.com/public/basic.ics
# https://calendar.google.com/calendar/ical/n42ba22iiu02508n0h7hnreabk%40group.calendar.google.com/public/basic.ics
# Broken, but probably covered by above https://calendar.google.com/calendar/ical/6s7ucb5etjine4d1a6ciqai73c%40group.calendar.google.com/public/basic.ics


                                        # CFA

# Drama: https://drama.cmu.edu/box-office/
# http://drama.cmu.edu/?plugin=all-in-one-event-calendar&controller=ai1ec_exporter_controller&action=export_events&no_html=true&ai1ec_cat_ids=218

# Design: https://design.cmu.edu/events
# TODO: Individual events that are typed. Maybe three a month, usually lectures

# Art: http://www.art.cmu.edu/events/
# TODO: weird format. similar to Tepper

# Architecture
# https://calendar.google.com/calendar/ical/soa-faculty%40andrew.cmu.edu/public/basic.ics
# https://calendar.google.com/calendar/ical/soa-public%40andrew.cmu.edu/public/basic.ics
# https://calendar.google.com/calendar/ical/soa-students%40andrew.cmu.edu/public/basic.ics

                                        # CIT

# Biomedical Engineering
# https://calendar.google.com/calendar/ical/cmubme1%40gmail.com/public/basic.ics

# Civil Engineering: https://www.cmu.edu/cee/events/seminar.html
# TODO: Must be manually parsed, it's  a list :(

# ECE: https://www.ece.cmu.edu/news-and-events/seminars.html
# TODO: Weekly graduate seminar that must be manually entered

# EPP: https://www.cmu.edu/epp/events/
# Doesn't exist

# MSE: https://www.cmu.edu/engineering/materials/news_and_events/departmental_seminar_series/2019-fall.html
# TODO: A fucking HTML table? are you kidding me

# IDeATE: https://calendar.google.com/calendar/embed?src=ideate.cmu@gmail.com&showTitle=0&showPrint=0&showCalendars=0&bgcolor=%23F3F0E9&ctz=America/New_York
# "https://calendar.google.com/calendar/ical/ideate.cmu@gmail.com/public/basic.ics"






# cal = Calendar()
#
# cal.add('prodid', 'Andy Kong Event Calendar')
# cal.add('version', '2.0')
#
# event = Event()
# event.add('summary', 'A Calendar Test')
# event.add('dtstart', datetime(2019,9,6,8,0,0,tzinfo=pytz.timezone('America/New_York')))
# event.add('dtend', datetime(2019,9,6,10,0,0,tzinfo=pytz.timezone('America/New_York')))
# event.add('dtstamp', datetime.now(tz=pytz.timezone('America/New_York')))
# event.add('location',"I'm in scott rn")
# event.add('description', 'We out here!')
#
# cal.add_component(event)
#
# f = open('calendarapi/example.ics','wb')
# f.write(cal.to_ical())
# f.close()
