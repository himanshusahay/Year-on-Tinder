from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from .models import Line
import pynder
import requests
import json
import re
import robobrowser
import operator
import random
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
    #print  s.response.content.decode()
    return access_token


def landing(request):
	if request.POST.get('facebook_id'):
		request.session['facebook_id'] = request.POST['facebook_id']

	if request.POST.get('email'):
		request.session['facebook_auth_token'] = get_access_token(request.POST['email'], request.POST['password'])

	session = pynder.Session(request.session['facebook_id'], request.session['facebook_auth_token'])
	return render(request, 'app/landing.html', {"matches": session.matches()})

def profile(request, match_id, line_option = None):
	session = session = pynder.Session(request.session['facebook_id'], request.session['facebook_auth_token'])
	matches = session.matches()
	match = matches[int(match_id)]
	messages = match.messages
	padding = range(int((12 - (len(match.user.photos) * 2)) / 2))
	return render(request, 'app/profile.html', {"user": match.user, "messages": messages, "padding": padding, "id": match_id, 'line_option': line_option})

def line_selector(request, match_id):
	if request.POST.get('category'):
		category_selected = request.POST['category']
		session = session = pynder.Session(request.session['facebook_id'], request.session['facebook_auth_token'])
		matches = session.matches()
		match = matches[int(match_id)]
		# Create object of Recommender class to tag words and filter by noun, verb and adverb
		rec = Recommender(match.user.bio)
		filtered_tagged_words =	rec.tag_words()
		image_tags = generate_tags(match.user.photos)
		diff = set(image_tags) - set(filtered_tagged_words)
		filtered_tagged_words = set(filtered_tagged_words + list(diff))
		# print("Tags: ", filtered_tagged_words)
		# Now, query the database for messages in the chosen category which match these tags
		# If no tags match, spit out a random  message
		line_tag_count = {}
		tag_match = False
		q = [category_selected]
		query = functools.reduce(operator.and_, (Q(categories__category_name__contains = item) for item in q))
		lines = Line.objects.filter(query)
		for line in lines:
			tags = []
			for tag in line.tags.all():
				tags.append(tag.tag_name)
			line_tag_count[line.line_text] = 0
			# If tag matches found
			if len(set(tags).intersection(filtered_tagged_words)) > 0:
				line_tag_count[line.line_text] += 1
				tag_match = True

		line = None
		# Tag(s) matched
		if tag_match:
			# print ("num matches: ", line_tag_count[0])
			line = sorted(line_tag_count.items(), key=operator.itemgetter(1))[0][0]

		# No tags matched
		else:
			line = random.choice(lines).line_text
			print ("no matches")

	return profile(request, match_id, line)

def send(request, match_id):
	if request.POST.get('message'):
		session = session = pynder.Session(request.session['facebook_id'], request.session['facebook_auth_token'])
		matches = session.matches()
		match = matches[int(match_id)]
		match.message(request.POST['message'])

	return redirect(reverse('profile', args=[match_id]))
