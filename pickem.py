#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = (
		'/pick','add_pick',
        '/view','view_picks',
        '/leaders', 'view_leaders',
        '/results', 'view_results',
        '/','view_leaders'
        )

def top4(predicted, actual):
	return predicted.intersection(actual)

def scorePicks(results,picks):
	scores = []
	for username, pick_data in picks.iteritems():
		score = 0
		for event, places in pick_data.iteritems():
			correct_swimmers = top4(set(places.values()), set(results[event].values()))
			counted_swimmers = set()
			if places[1] == results[event][1]:
				score = score + 7
			else:
				if places[1] in correct_swimmers and places[1] not in counted_swimmers:
					score = score + 1
					counted_swimmers.add(places[1])

			if places[2] == results[event][2]:
				score = score + 5
			else:
				if places[2] in correct_swimmers and places[2] not in counted_swimmers:
					score = score + 1
					counted_swimmers.add(places[2])

			if places[3] == results[event][3]:
				score = score + 4
			else:
				if places[3] in correct_swimmers and places[3] not in counted_swimmers:
					score = score + 1
					counted_swimmers.add(places[3])

			if places[4] == results[event][4]:
				score = score + 3
			else:
				if places[4] in correct_swimmers and places[4] not in counted_swimmers:
					score = score + 1
					counted_swimmers.add(places[4])

		scores.append([username, score])
	scores.sort(key = lambda tup: tup[1], reverse=True)

	curr_place = 0
	curr_score = None
	for i,s in enumerate(scores):
		if s[1] != curr_score:
			curr_place = i+1
			curr_score = s[1]
		s.insert(0,curr_place)
	return scores

class view_leaders:
    def GET(self):
    	try:
    		results, picks = sqlitedb.getScoringData()
    		scores = scorePicks(results,picks)

        	return render_template('view_leaders.html', leader_data = scores)
        except Exception as e:
        	return render_template('view_leaders.html', message = str(e))

class view_results:
	def GET(self):

		try:
			query_str,vars = sqlitedb.getResults()
			results = sqlitedb.query(query_str,vars)
			return render_template('view_results.html',results=results)
		except Exception as e:
			return render_template('view_results.html', message = str(e))

class add_pick:
	
	def GET(self):
		query_str, vars = sqlitedb.getPossiblePicks()
		try:
			results = sqlitedb.db.query(query_str,vars)
			r_dict = {}
			out_data = []
			event2id = {}
			for event in results:
				if event["Event"] not in r_dict:
					r_dict[event["Event"]] = []
					event2id[event["Event"]] = int(event["EID"])
				r_dict[event["Event"]].append((event["Name"],event["AID"]))

			for event,entrants in r_dict.iteritems():
				out_data.append({"Event": event, "s_ID": str(event2id[event]), "ID": event2id[event], "Competitors": entrants})

			out_data.sort(key = lambda data: data["ID"])
			return render_template('add_pick.html', data = out_data)

		except Exception as e:
			return render_template('add_pick.html', message = str(e));

	def POST(self):
		post_params = web.input()

		queries = sqlitedb.addPicks(post_params)
		t = sqlitedb.transaction()
		try:
			# first get new user id
			results = sqlitedb.db.query(queries[0][0],queries[0][1])
			userid = int(results[0]["maxID"])+1
			out = []
			for query_str,vars in queries[1:]:
				vars["userid"] = userid
				sqlitedb.db.query(query_str,vars)
		 	t.commit()
			return render_template('add_pick.html', message = "We have recieved your picks!")
		except Exception as e:
			t.rollback()
			return render_template('add_pick.html', message = str(e))


class view_picks:

    def GET(self):
        return render_template('view_picks.html')

    def POST(self):
        post_params = web.input()

        user_name = "%"+post_params["username"]+"%"

        query_str,vars = sqlitedb.getUserPicks(user_name)
        t = sqlitedb.transaction()
        try:
            results = sqlitedb.query(query_str,vars)
            return render_template('view_picks.html',search_result=results)
        except Exception as e:
            return render_template('view_picks.html', message = str(e))


# class view:
#     def GET(self,itemID):
#         try:
#             meta,bids,status = sqlitedb.getAuctionInfo(itemID)
#             if len(bids)!=0:
#                 return render_template('view.html',item_result = meta,bids = bids,status_res = status)
#             else:
#                 return render_template('view.html',item_result = meta,status_res=status)
#         except Exception as e:
#             return render_template('view.html',message = str(e))


###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
