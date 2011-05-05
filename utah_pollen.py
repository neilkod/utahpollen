import tweepy
from BeautifulSoup import BeautifulSoup
import urllib2

def get_pollen_count():
	page = urllib2.urlopen('http://intermountainallergy.com/pollen.html')
	soup = BeautifulSoup(page)
	pollentable = soup.find('table',{'class':'pollentable'})
	rows = pollentable.findAll('tr')
	for row in rows[1:-2]:
		cols = row.findAll('td')
		pollen_type = cols[0].text
		width = dict(cols[1].img.attrs)['width']
		print "%s\t%s" % (pollen_type, width)

def main():
	get_pollen_count()
if __name__ == '__main__':
	main()