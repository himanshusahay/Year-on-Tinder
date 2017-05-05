from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from .models import Line, Tag, PictureTag
from . import tinder
import pynder
import requests
import json
import re
import robobrowser
import operator
import random
import phonenumbers
from .image import generate_tags
from .recommender import Recommender
import functools
MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; U; en-gb; KFTHWI Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Silk/3.16 Safari/535.19"
FB_AUTH = "https://www.facebook.com/v2.6/dialog/oauth?redirect_uri=fb464891386855067%3A%2F%2Fauthorize%2F&display=touch&state=%7B%22challenge%22%3A%22IUUkEUqIGud332lfu%252BMJhxL4Wlc%253D%22%2C%220_auth_logger_id%22%3A%2230F06532-A1B9-4B10-BB28-B29956C71AB1%22%2C%22com.facebook.sdk_client_state%22%3Atrue%2C%223_method%22%3A%22sfvc_auth%22%7D&scope=user_birthday%2Cuser_photos%2Cuser_education_history%2Cemail%2Cuser_relationship_details%2Cuser_friends%2Cuser_work_history%2Cuser_likes&response_type=token%2Csigned_request&default_audience=friends&return_scopes=true&auth_type=rerequest&client_id=464891386855067&ret=login&sdk=ios&logger_id=30F06532-A1B9-4B10-BB28-B29956C71AB1&ext=1470840777&hash=AeZqkIcf-NEW6vBd"

def index(request):
	return render(request, 'app/index.html')

def login(request):
	# request.session['facebook_id'] = request.POST['facebook_id']
	# request.session['facebook_auth_token'] = request.POST['facebook_access_token']

	return HttpResponse("Success")

def get_access_token(email, password):
    s = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="lxml")
    s.open(FB_AUTH)
    ##submit login form##
    f = s.get_form()
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)
    ##click the 'ok' button on the dialog informing you that you have already authenticated with the Tinder app##
    f = s.get_form()
    s.submit_form(f, submit=f.submit_fields['__CONFIRM__'])
    ##get access token from the html response##
    access_token = re.search(r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
    print "Access token", access_token
    #print  s.response.content.decode()
    return access_token


def landing(request):
	if request.POST.get('facebook_id'):
		request.session['facebook_id'] = request.POST['facebook_id']

	if request.POST.get('email'):
		request.session['facebook_token'] = get_access_token(request.POST['email'], request.POST['password'])

	# r = requests.post("https://api.gotinder.com/auth", 
	# 	{'facebook_token': request.session['facebook_token'], 'facebook_id': request.session['facebook_id']})
	# # print r.json()

	# get matches
	# last_activity_date = "100000"
	# url = 'https://api.gotinder.com/updates/'
	# headers = {
	# ''
	# 'X-Auth-Token': request.session['facebook_token'],
	# 'Content-type': 'application/json',
	# 'User-agent': 'Tinder/4.7.1 (iPhone; iOS 9.2; Scale/2.00)',
	# }

	# r = requests.get(url, headers=headers)
	# print r.json()

	AUTH_TOKEN = request.session['facebook_token']
	USER_ID = request.session['facebook_id']
	tinder.get_auth_token(AUTH_TOKEN, USER_ID)

	# single matches (messages, info about matches), group matches
	updates = tinder.get_updates()
	
	# your profile
	self = tinder.get_self()

	# your metadata
	meta = tinder.get_meta()

	# # ping data (lat, long)
	# ping = tinder.get_ping(42.270668, -71.806974)

	data = {
		"updates": updates,
		"self":	self,
		"meta": meta,
		# "ping": ping,
	}

	self_id = self["_id"]

	for match in updates["matches"]:
		phone_number = False
		match_id = match["_id"]
		if len(match["messages"]) > 1:
			for message in match["messages"]:
				matcher = phonenumbers.PhoneNumberMatcher(message["message"], "US")
				if matcher.has_next():
					phone_number = True
					break
		

	num_matches = len(updates["matches"])
	num_messaged = 0 # 1 message to or from
	num_interactions = 0 # 2 messages on either side
	num_messaged_first = 0
	num_received_message_from_first = 0
	num_interactions_GIF = 0
	num_interactions_phone_number = 0

	for match in updates["matches"]:
		match_id = match["_id"]

		if len(match["messages"]) > 0:
			num_messaged += 1
			interaction = False
			gif = False
			phone_number = False

			if match["messages"][0]["from"] != self_id:
				num_received_message_from_first += 1
			
			else:
				num_messaged_first += 1

			from_list = {}
			if len(match["messages"]) > 1:
				from_list.clear()
				for each in match["messages"]:
					from_list[each["from"]] = 1
					for message in match["messages"]:
						if ".giphy.com" in message["message"]:
							gif = True
						matcher = phonenumbers.PhoneNumberMatcher(message["message"], "US")
						if matcher.has_next():
							phone_number = True
							break
		
			if len(from_list) > 1:
				num_interactions += 1
				match["interaction"] = True
				if gif:
					num_interactions_GIF += 1
				if phone_number:
					num_interactions_phone_number += 1
					match["phone_number"] = True
				else:
					match["phone_number"] = False
			else:
				match["interaction"] = False

	info = []
	info.append({ "stat": "Matches", "value" : num_matches})
	info.append({ "stat": "Messaged", "value" : num_messaged})
	info.append({ "stat": "Interactions", "value" : num_interactions})
	info.append({ "stat": "Interactions (GIF)", "value" : num_interactions_GIF})
	info.append({ "stat": "You messaged first", "value" : num_messaged_first})
	info.append({ "stat": "Match messaged first", "value" : num_received_message_from_first})
	info.append({ "stat": "Interactions (phone number)", "value" : num_interactions_phone_number})

	with open('stats.json', 'w') as fp:
		json.dump(info, fp)

	with open('data.json', 'w') as fp:
		json.dump(data, fp)

	# return render(request, 'app/landing.html', {})
	return render(request, 'app/index.html')
