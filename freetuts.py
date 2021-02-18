from requests import get
from requests.utils import quote
from requests.utils import unquote
from lxml import html

course_link = {}
services = {}

# This method search all course contains your keyword
def search(keyword):
	request_search('https://%s%s%s' % ('dl.freetutsdownload.net/', '?s=', quote(keyword)))
	for course, link in course_link.items():
		print(course + '\t\t' + link)

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

# This method reformat url
def unquoted(url):
	return unquote(url.split('/')[4][5:])

# This method extract all download service available
def request_download(url):
	response = get(url)
	tree = html.fromstring(response.text)
	href = tree.xpath("//a[@target='_blank']/@href")
	links = []

	for link in href:
		links.append(unquoted(link))

	for link in links:
		services.update(
			{
			'DRIVE' if 'drive' in link
					and 'drive' in services.keys()
					else link.split('/')[2].split('.')[0] 
			: link
			}
		)

# This method scrape download link with id provided
def freetuts(id):
	url = id if 'https' in id else '%s%s' % ('https://dl.freetutsdownload.net/tutsID-', id)
	request_download(url)
	for service, url in services.items():
		print(service + ': ' + url)