from requests import get
from requests.utils import quote
from requests.utils import unquote
from lxml import html

course_link = {}
download_link = {}

# This method search all course contains your keyword
def search(keyword):
	request_search('https://%s%s%s' % ('dl.freetutsdownload.net/', '?s=', quote(keyword)))
	for course, link in course_link.items():
		print(course + '{ }' + link)

# This method extract all course link in the search page 
def request_search(url):
	response = get(url)
	tree = html.fromstring(response.text)
	bookmark = tree.xpath("//a[@rel='bookmark']/text()")
	entry_title = tree.xpath("//a[@rel='bookmark']/@href")

	# Zip the two lists together, and create a dictionary out of the zipped lists
	course_link.update(dict(zip(bookmark, entry_title)))

	next_page = tree.xpath("//div[@class='nav-previous']/a/@href")
	try:
		request_search(next_page[0])
	except IndexError:
		pass

# This method extract all download service available
def request_download(url):
	response = get(url)
	tree = html.fromstring(response.text)
	one = tree.xpath("//a[@title='Download Link OneDrive']/@href")
	drive = tree.xpath("//a[@title='Download Link Google Drive']/@href")
	for link in one:
		if 'sharepoint' in link:
			download_link.update({'onedrive': unquote(link.split('/')[4][5:])})
	for link in drive:
		if 'bayfiles' in link:
			download_link.update({'bayfiles': unquote(link.split('/')[4][5:])})
		if 'drive' in link:
			if 'drive' in download_link:
				download_link.update({'drive backup': unquote(link.split('/')[4][5:])})
			else:
				download_link.update({'drive': unquote(link.split('/')[4][5:])})
		if 'uptobox' in link:
			download_link.update({'uptobox': unquote(link.split('/')[4][5:])})

# This method scrape download link with id provided
def freetuts(id):
	url = id if 'https' in id else '%s%s' % ('https://dl.freetutsdownload.net/tutsID-', id)
	request_download(url)
	for k, v in download_link.items():
		print(k + ': ' + v)

# search('machine learning')
freetuts('5442')