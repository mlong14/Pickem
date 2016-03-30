import web
import time

db = web.database(dbn='sqlite',
        db='PickEm.db' #TODO: add your SQLite database filename
    )

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

def getResults():
    query_string = ' \
    select Events.EventName as Event, c1.AthName as First, c2.AthName as Second, c3.AthName as Third, c4.AthName as Fourth\
    from Events, Results, Contestants c1, Contestants c2, Contestants c3, Contestants c4\
    where Events.EventID = Results.EventID and \
    Results.First = c1.AthID and \
    Results.Second = c2.AthID and \
    Results.Third = c3.AthId and \
    Results.Fourth = c4.AthId'

    return query_string,{}

def getUserPicks(user_name):
	query_string = ' \
	select Users.UserName as Username, Events.EventName as Event, c1.AthName as First, c2.AthName as Second, c3.AthName as Third, c4.AthName as Fourth, Users.Eligible as Eligible\
	from Picks, Users, Events, Contestants c1, Contestants c2, Contestants c3, Contestants c4\
	where Picks.UserID = Users.UserID and  \
    UPPER(Users.UserName) LIKE UPPER($userName) and \
	Events.EventID = Picks.EventID and \
	Picks.First = c1.AthID and \
	Picks.Second = c2.AthID and \
	Picks.Third = c3.AthId and \
	Picks.Fourth = c4.AthId'

	return query_string,{'userName': user_name}

def getPossiblePicks():
	query_string = " \
	select Contestants.AthName as Name, Events.EventName as Event, Events.EventID as EID, Contestants.AthID as AID\
	from Contestants, Events, Entries\
	where Contestants.AthID = Entries.AthID and  \
	Entries.EventID = Events.EventID and \
	Contestants.AthName != 'NULL'"

	return query_string,{}

def pickKeySplit(key):
	key_split = key.split("_")
	event = int(key_split[0])
	if key_split[1] == "first":
		place = 1
	elif key_split[1] == "second":
		place = 2
	elif key_split[1] == "third":
		place = 3
	elif key_split[1] == "fourth":
		place = 4
	else:
		raise Exception("Invalid key " + key)

	return event,place

def addPicks(post_params):
	# need to update Picks, Users
	queries = []
	vars = []

	picks = {}
	username = post_params["username"]
	if "eligible" in post_params:
		eligible = True
	else:
		eligible = False 

	for key, aid in post_params.iteritems():
		if key != "eligible" and key != "username":
			event, place = pickKeySplit(key)
			if event not in picks:
				picks[event] = {}
			picks[event][place] = int(aid)

	queries.append("select max(UserID) as maxID from Users")
	vars.append({})

	queries.append("insert into Users(UserID,UserName,Eligible) values ($userid,$username,$eligible)")
	vars.append({"userid":-1,"username":username,"eligible":eligible})

	for event, place_data in picks.iteritems():
		queries.append(" \
			insert into Picks(UserID,EventID,First,Second,Third,Fourth) \
			values($userid,$eventid,$first,$second,$third,$fourth) \
			")
		#placeholder for userID
		vars.append({"userid":-1,"eventid":event,"first":place_data[1],"second":place_data[2],"third":place_data[3],"fourth":place_data[4]})

	return zip(queries,vars)

def getScoringData():
    res_query = "select * from Results"
    results = db.query(res_query,{})
    parsed_results = {}
    for r in results:
        parsed_results[int(r["EventID"])] = {
            1: int(r["First"]),
            2: int(r["Second"]),
            3: int(r["Third"]),
            4: int(r["Fourth"])
        }

    pick_query = "select * from Picks, Users where Users.UserID = Picks.UserID"
    picks = db.query(pick_query,{})
    parsed_picks = {}
    for p in picks:
        if p["UserName"] not in parsed_picks:
            parsed_picks[p["UserName"]] = {}
        parsed_picks[p["UserName"]][int(p["EventID"])] = {
            1: int(p["First"]),
            2: int(p["Second"]),
            3: int(p["Third"]),
            4: int(p["Fourth"])
        }

    return parsed_results, parsed_picks

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

