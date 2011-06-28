#!/usr/bin/python

import csv, ConfigParser
import numpy
import urllib2, time, datetime
import tweepy
#from BeautifulSoup import BeautifulSoup
from pyquery import PyQuery

CONFIG_FILE = 'utah_pollen.cfg'
TWITTER_SCREEN_NAME = 'neilkod2'

TESTDATA = {u'Cattail': 80, u'Willow': 80, u'BoxElder/Maple': 80, 
						u'Sycamore': 80, u'Oak': 80, u'Sagebrush': 80,
						u'Mulberry': 320, u'Cedar': 80, u'Chenopods': 80,
						u'Grass': 80, u'Mold': 80}

scale = {40: 'Extra Low', 
				 80: 'Low', 
				120: 'Moderate-Low', 
				160: 'Moderate', 
				240: 'High-moderate', 
				320: 'High', 
				400 : 'Extra High'}
				
today_str = time.strftime('%b-%d',time.localtime())

def get_twitter_config(config_file = CONFIG_FILE, screen_name = 'neilkod2'):
	twitter_params = {}

	config = ConfigParser.ConfigParser()
	config.readfp(open(config_file))
	
	twitter_params['consumer_key'] = config.get('TwitterOauth','CONSUMER_KEY')
	twitter_params['consumer_secret'] = config.get('TwitterOauth','CONSUMER_SECRET')

	twitter_params['access_key'] = config.get(screen_name,'ACCESS_KEY')
	twitter_params['access_secret'] = config.get(screen_name,'ACCESS_SECRET')
	return twitter_params

def get_pollen_count():
	SOURCE_URL = 'http://intermountainallergy.com/pollen.html'
	pollen_data = {}
	source = urllib2.urlopen(SOURCE_URL)

	
	# retrieve the last-modified http header
	# convert it to a date
	# and write it to a file
	
	lm = source.headers['last-modified']
	last_modified_date = datetime.datetime.strptime(lm,'%a, %d %b %Y %H:%M:%S %Z')
	# save the last-modified date
	last_modified_file = open('last_modified.txt','wb')
	last_modified_file.write(lm + '\n')
	last_modified_file.close()

	# 23-jun-2011 commenting out BeautifulSoup Code, replacing
	# with newly-learned pyquery.
	# disclaimer - I know next to nothing about jquery so my
	# pyquery won't be the best.
	
	# soup = BeautifulSoup(page)
	# pollentable = soup.find('table',{'class':'pollentable'})
	# rows = pollentable.findAll('tr')
	# print rows
	# for row in rows[1:-2]:
	# 	cols = row.findAll('td')
	# 	pollen_type = cols[0].text.replace(' ','')
	# 	width = dict(cols[1].img.attrs)['width']
	# 	result =  "%s\t%s\t%s" % (today_str,pollen_type, width)
	# 	print result
	# 	pollen_data[pollen_type] = int(width)

	# create the pyquery object
	d = PyQuery(source.read())
	pollen_table = d('table.pollentable')
	pollen_rows = pollen_table('tr')[1:-1]
	for row in pollen_rows:
		fields = row.getchildren()
		pollen_source = fields[0].text_content().replace('*','')
		pollen_value = fields[1].getchildren()[0].get('width')
		pollen_data[pollen_source] = int(pollen_value)
	
	print pollen_data
	return pollen_data

def send_tweet(tweet_string):
	
	# retrieve configuration for oauth
	try:
		config = get_twitter_config(CONFIG_FILE, TWITTER_SCREEN_NAME)
		auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
		auth.set_access_token(config['access_key'], config['access_secret'])
		api = tweepy.API(auth)
		api.update_status(tweet_string)
		return True
	except:
		raise

def write_pollen_data(pollen_data):
	today_str = time.strftime('%Y-%m-%d',time.localtime())
	datafile = 'data/utahpollen.tsv'
	file_handle = open(datafile, 'a')
	dict_keys = ('pollen_source')
	writer = csv.writer(file_handle, delimiter='\t')
	for k,v in pollen_data.iteritems():
		row = [today_str, k, v]
		writer.writerow(row)

def report_pollen_data(pollen_data):
	
	# determine the median pollen score for trees
	tweet_string = '%s pollen report: ' % today_str
	warnings = []

	#categories
	special_classes = ['Mold', 'Grass', 'Chenopods']
	for itm in special_classes:
		if itm in pollen_data.keys():
			warnings.append('%s: %s' % (itm, scale[pollen_data[itm]]))
			del pollen_data[itm]
	
	print warnings
	print pollen_data
	median_score = numpy.median(pollen_data.values())
	warnings.append('Trees: %s' % scale[median_score])
	for k,v in pollen_data.iteritems():
		if v > 160:
			warnings.append('%s: %s' % (k,scale[v]))
	print tweet_string
	print warnings
	tweet_string = tweet_string + ', '.join(warnings)
	return tweet_string
			
def main():

	pollen_data = get_pollen_count()
#	pollen_data = TESTDATA
	write_pollen_data(pollen_data)
	tweet_string = report_pollen_data(pollen_data)
	print tweet_string
	success = send_tweet(tweet_string)
	if success:
		print "tweet successfully sent: %s"  % tweet_string

if __name__ == '__main__':
	main()