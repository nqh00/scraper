from requests import get
from requests.utils import (quote, unquote)
from lxml import html

course_link = {}
services = {}

# This method search all course contains your keyword and return all available download services
def freetuts(keyword):
	request_search('https://%s%s%s' % ('dl.freetutsdownload.net/', '?s=', quote(keyword)))
	for course, link in course_link.items():
		print(course)
		request_download(link)
		for service, url in services.items():
			print(service + ': ' + url)
		print()
		services.clear()


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
	response = get(url, timeout=5)
	tree = html.fromstring(response.text)
	href = tree.xpath("//a[@target='_blank']/@href")
	links = []

	for link in href:
		if link != 'javascript:void(0);':
			links.append(unquoted(link))

	for link in links:
		services.update(
			{
			'DRIVE' if 'drive' in link
					and 'drive' in services.keys()
					else (
						link.split('/')[2].split('.')[1] 
						if '-' in link.split('/')[2]
						else link.split('/')[2].split('.')[0]
					) 
			: link
			}
		)