
import sys
from json import loads
import re
from re import sub
import os
import time

columnSeparator = "|"

RESULTS_FN = "results.dat"
PICKS_FN = "picks.dat"
USERS_FN = "users.dat"
CONTESTANTS_FN = "contestants.dat"
EVENTS_FN = "events.dat"
ENTRIES_FN = "entries.dat"

def processQuotes(text):
    out_text = []
    for c in text:
        if c == "\"":
            out_text.append("\"\"")
        else:
            out_text.append(c)

    return "".join(out_text)

def parseText(data):
    out_data = []
    for d in data:
        if d is None:
            d = "NULL"

        if type(d)==str or type(d)==unicode:
            out_data.append("".join(["\"",processQuotes(d),"\""]))
        else:
            out_data.append(str(d))

    return out_data

def write2file(data,fn): # needs [[data1,data2, ...],[data3, data4, ...]]
    file_handle = open(fn,"a")
    for element in data:
        string = "|".join(parseText(element))
        file_handle.write(string+"\n")

    file_handle.flush()

def check_file(fn):
    # if not os.path.exists(fn):
    #     open(fn,"w")
    open(fn,"w")

def parse_headers(data):

    #first create event/eventid mapping
    col2eventid = {}
    event2eventid = {}
    contestant2id = {}
    eventid = 0
    contestantid = 0

    for i,ent in enumerate(data[1].split("\t")[2:]):
        event = ent.split("-")[0].strip()
        place = int(sub("[^0-9]", "", ent.split("-")[1].strip()))

        if event not in event2eventid:
            event2eventid[event]=eventid
            eventid = eventid+1

        col2eventid[i+2] = (event2eventid[event],place)

    #then get results
    results = {}

    for i,ent in enumerate(data[0].split("\t")[2:]):
        eventid,place = col2eventid[i+2]
        victor = parse_contestant(ent)

        if eventid not in results:
            results[eventid] = {}

        if victor not in contestant2id:
            contestant2id[victor] = contestantid
            contestantid = contestantid + 1

        results[eventid][place] = contestant2id[victor]

    return col2eventid,event2eventid,results,contestant2id,contestantid

def parse_contestant(entry):
    # 1 Smith, Clark   Texas-ST 4:08.82
    # 5 Michigan-MI   A 6:14.96

    if entry == "":
        return None

    entry = entry.split("   ")[0]
    e_out = sub("[0-9]","", entry).strip()

    m = re.match(r"([a-zA-Z- ']+), ([a-zA-Z'-]+)", e_out)
    
    if m:
        e_out = m.group(2) + " " + m.group(1)

    return e_out

def parseCSV(fn):

    '''
    TODO: Fix Contestant/Entry system
    '''

    picks = {}
    users = {}
    entries = set()
    userid = 0

    with open(fn,"r") as f:
        data = f.readlines()[0]
        data = data.split("\r")

        col2eventid,event2eventid,results,contestant2id,contestantid = parse_headers(data[0:2])
            
        for row in data[2:]:
            row = row.split("\t")
            if row[1].strip().lower() == "yes":
                eligible = True
            else:
                eligible = False

            users[userid] = (row[0], eligible)
            picks[userid] = {}

            for i,ent in enumerate(row):
                if i != 0 and i != 1:
                    eventid,place = col2eventid[i]
                    victor = parse_contestant(ent)
                    if eventid not in picks[userid]:
                        picks[userid][eventid] = {}
                    if victor not in contestant2id:
                        contestant2id[victor] = contestantid
                        contestantid = contestantid+1

                    picks[userid][eventid][place] = contestant2id[victor]

            userid = userid + 1

        '''
        Hack for entries
        '''
        for eventid, places in results.iteritems():
            for place, c_id in places.iteritems():
                entries.add((eventid,c_id))
        for userid, pick_data in picks.iteritems():
            for eventid, places in pick_data.iteritems():
                for place, c_id in places.iteritems():
                    entries.add((eventid,c_id))
    
        writepicks(picks)
        writeresults(results)
        writeusers(users)
        writeevents(event2eventid)
        writecontestants(contestant2id)
        writeentries(entries)

def writeentries(entry_data):
    out_data = []
    for eventid,c_id in entry_data:
        out_data.append([eventid,c_id])

    out_data.sort(key = lambda tup: tup[0])

    write2file(out_data,ENTRIES_FN)

def writecontestants(contestant_data):
    out_data = []
    for contestant,c_id in contestant_data.iteritems():
        out_data.append([c_id,contestant])

    out_data.sort(key = lambda tup: tup[0])

    write2file(out_data,CONTESTANTS_FN)

def writeevents(event_data):
    out_data = []
    for event,eventid in event_data.iteritems():
        out_data.append([eventid,event])

    out_data.sort(key = lambda tup: tup[0])

    write2file(out_data,EVENTS_FN)

def writeusers(user_data):
    usernames = set()
    out_data = []
    for userid, (username, eligible) in user_data.iteritems():
        if username not in usernames and username != "":
            usernames.add(username)
            out_data.append([userid,username,eligible])

    out_data.sort(key = lambda tup: tup[0])

    write2file(out_data,USERS_FN)

def writeresults(result_data):
    out_data = []
    for eventid, places in result_data.iteritems():
        out_data.append([eventid,places[1],places[2],places[3],places[4]])

    out_data.sort(key = lambda tup: tup[0])

    write2file(out_data,RESULTS_FN)

def writepicks(pick_data):
    out_data = []
    for userid, picks in pick_data.iteritems():
        for eventid, places in picks.iteritems():
            out_data.append([userid,eventid,places[1],places[2],places[3],places[4]])

    out_data.sort(key = lambda tup: tup[0])
    
    write2file(out_data,PICKS_FN)


def main(argv):
    # if len(argv) < 2:
    #     print >> sys.stderr, 'Usage: pickem_parser.py <path to csv files>'
    #     sys.exit(1)

    map(check_file,[RESULTS_FN,USERS_FN,PICKS_FN,ENTRIES_FN,CONTESTANTS_FN,EVENTS_FN])

    argv = ["_", "pickem_data.txt"]

    for f in argv[1:]:
        parseCSV(f)
        print "Success parsing " + f


if __name__ == '__main__':
    main(sys.argv)
