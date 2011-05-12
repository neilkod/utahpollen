#!/usr/bin/python

import urllib2, time
import tweepy
from BeautifulSoup import BeautifulSoup

TWITTER_ACCESS_KEY = '205504973-zS8dx6D5awBAXVGWuoJjKEMP070mb1oUfSTiyclL'
TWITTER_ACCESS_SECRET = 'QBgg9v7jdSTJORRRHpB7vZBpxAFGGbX8Nn13GqzJs0'

scale = {40: 'extra low', 80: 'low', 160: 'moderate', 400 : 'extra high'}

def get_pollen_count():
	datafile = 'data/utahpollen.tsv'
	file_handle = open(datafile, 'a')
	
	page = urllib2.urlopen('http://intermountainallergy.com/pollen.html')
	soup = BeautifulSoup(page)
	pollentable = soup.find('table',{'class':'pollentable'})
	rows = pollentable.findAll('tr')

	today_str = time.strftime('%Y-%m-%d',time.localtime())

	for row in rows[1:-2]:
		cols = row.findAll('td')
		pollen_type = cols[0].text
		width = dict(cols[1].img.attrs)['width']
		result =  "%s\t%s\t%s" % (today_str,pollen_type, width)
		file_handle.write(result + '\n')
		print result
	
	file_handle .close()


def main():
	get_pollen_count()
if __name__ == '__main__':
	main()
