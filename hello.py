import os
import re
from flask import Flask, render_template, request
import oauth2 as oauth
import urllib2 as urllib
import simplejson as json
from cStringIO import StringIO
import unicodedata

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def hello():
  if request.method == "POST":
    return do_submit()
  else:
    return render_template('index.html')

def do_submit():
  form = request.form
  query_response=fetchquery(form["search"])
  data, d3d, pos_set, neg_set=sentiment(query_response["statuses"])
  pos_list = list(pos_set)
  neg_list = list(neg_set)
  return render_template('results.html',
	                      search=form["search"],
	                      responses=query_response,
	                      poslist=data[::-1][:3],
                          neglist=data[:3],
                          d3d=d3d,
                          finaldata=data[::-1],
                          posxList=json.dumps(pos_list),
                          negxList=json.dumps(neg_list))
                                                            
# See Assignment 1 instructions or README for how to get these credentials
access_token_key = "access_token_key" 
access_token_secret = "access_token_secret"

consumer_key = "consumer_key"
consumer_secret = "consumer_secret"

_debug = 0

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"

http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method=http_method,
                                             http_url=url, 
                                             parameters=parameters)

  req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

  headers = req.to_header()

  if http_method == "POST":
    encoded_post_data = req.to_postdata()
  else:
    encoded_post_data = None
    url = req.to_url()

  opener = urllib.OpenerDirector()
  opener.add_handler(http_handler)
  opener.add_handler(https_handler)

  response = opener.open(url, encoded_post_data)

  return response
    
def fetchquery(query):
  url = "https://api.twitter.com/1.1/search/tweets.json?lang=en&count=100&q="
  url += query
  parameters = []
  strresponse=twitterreq(url, "GET", parameters)
  return json.load(strresponse)

def sentiment(responses_dict):
    data = []
    terms = {}
    intensifier_terms = []
    negation_terms = []
    positive_tweets = []
    negative_tweets = []
    neutral_tweets = []
    pos_word_set = set()
    neg_word_set = set()
    for line in responses_dict:
        datadict = {}
        if "text" in line.keys():
            datadict["text"] = line["text"]
            pass
        if "user" in line.keys():
            datadict["user"] = line["user"]["screen_name"]
            data.append(datadict)
            continue
    opener = urllib.OpenerDirector()
    opener.add_handler(http_handler)
    response = opener.open("http://twittersentiment.s3.amazonaws.com/sentiment3.txt")
    filedata = StringIO(response.read())
    for sent_line in filedata:
        term, score  = sent_line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
        terms[term] = int(score)  # Convert the score to an integer
        continue
    intensifier_response = opener.open("http://twittersentiment.s3.amazonaws.com/intensifiers.txt")
    intensifier_data = StringIO(intensifier_response.read())
    for int_line in intensifier_data:
    	int_term = int_line.strip()
    	intensifier_terms.append(int_term)
    negation_response = opener.open("http://twittersentiment.s3.amazonaws.com/negation1.txt")
    negation_data = StringIO(negation_response.read())
    for neg_line in negation_data:
    	neg_term = neg_line.strip()
    	negation_terms.append(neg_term)
    for tweet in data:
        if "text" in tweet.keys():
            tweet_split = tweet["text"].split()
            score=0
            for i, word in enumerate(tweet_split):
                new_score,i_term,n_term = rec_unicode_check(0,i,word,terms,tweet_split,intensifier_terms,negation_terms)
                if new_score > 0:
                	if i_term != "" or n_term!="":
                		pos_word_set.add(i_term+n_term+" "+word.lower())
                	else:
                		pos_word_set.add(word.lower())
                elif new_score < 0:
                	if i_term != "" or n_term!="":
                		neg_word_set.add(i_term+n_term+" "+word.lower())
                	else:
                		neg_word_set.add(word.lower())        	
                score += new_score
                continue
            print pos_word_set
            print neg_word_set
            tweet["score"] = score
            if score >0:
                positive_tweets.append(tweet)
            elif score <0:
                negative_tweets.append(tweet)
            else:
            	neutral_tweets.append(tweet)
    final_list = sorted(data, key=lambda k: k['score'])
    d3data = [len(positive_tweets),len(neutral_tweets),len(negative_tweets)]
    return final_list,d3data,pos_word_set,neg_word_set

def rec_unicode_check(score,index_word,word,terms,data,intensifier_terms,negation_terms):
	i_multiplier=1
	n_multiplier=1
	i_term=""
	n_term=""
	if word.lower() in terms.keys():
		score = terms[word.lower()]
		if index_word>0:
			i_multiplier,i_term=intensify(index_word,data,intensifier_terms,negation_terms)
			n_multiplier,n_term=negation(index_word,data,intensifier_terms,negation_terms)
	else:
		try:
			if unicodedata.category(word[-1]) == 'Po':
				rec_unicode_check(score,index_word,word[:-1],terms,data,intensifier_terms,negation_terms)
			else:
				pass
		except:
			pass
	return score*i_multiplier*n_multiplier,i_term,n_term

def intensify(index_word,data,intensifier_terms,negation_terms):
	multiplier = 1
	for sent_line in intensifier_terms:
		if data[index_word-1].lower() == sent_line:
			if index_word>1:
				for sent_line2 in negation_terms:
					if data[index_word-2].lower() == sent_line2:
						multiplier=-0.5
						return multiplier,data[index_word-1].lower() + " " + data[index_word-2].lower()
				multiplier=2
				return multiplier,data[index_word-1].lower()
			else:
				multiplier=2
				return multiplier,data[index_word-1].lower()
	return multiplier,""

def negation(index_word,data,intensifier_terms,negation_terms):
	multiplier = 1
	for sent_line in negation_terms:
		if data[index_word-1].lower() == sent_line:
			if index_word>1:
				for sent_line2 in intensifier_terms:
					if data[index_word-2].lower() == sent_line2:
						multiplier=-2
						return multiplier,data[index_word-1].lower() + " " + data[index_word-2].lower()
				multiplier=-1
				return multiplier,data[index_word-1].lower()
			else:
				multiplier=-1
				return multiplier,data[index_word-1].lower()
	return multiplier,""