import sys
import os
import unicodedata
import string

from requests import get
from lxml import html
from json import JSONDecodeError
from requests.exceptions import (ConnectionError, Timeout, MissingSchema)
from platform import system
from subprocess import check_call

abs_dirname = os.path.dirname(os.path.abspath(__file__))
headers = {'X-Requested-With': 'XMLHttpRequest'}

def dramacool(keyword, start_episode=None, end_episode=None):
	response = get('https://www.dramacool.info/search?keyword=%s&type=movies' % (keyword.replace(' ', '+')), headers=headers)

	try:
		bash_call(response.json()[0]['name'])
	except IndexError:
		print('There is no movie matching your "%s" in our database.' % (keyword))
		sys.exit(1) # Return value for bash

	folder = '%s/.temp/.series/%s' % (abs_dirname, clean_filename(response.json()[0]['name']))
	if not os.path.exists(folder):
		os.mkdir(folder)
	if start_episode is None:
		start_episode = 1
	while (start_episode > 0):
		if selected_server(folder, response.json()[0]['alias'], start_episode) == 1 or start_episode == end_episode:
			break
		bash_call('Episode %s' % (start_episode))
		start_episode += 1

def selected_server(folder, alias, episode):
	response = get('https://watchasian.cc/%s-episode-%s.html' % (alias, episode))
	if response.status_code == 200:
		tree = html.fromstring(response.text)
		server = tree.xpath('//li[@class="Standard Server selected"]/@data-video')
		try:
			response = get('https://embed.watchasian.cc/ajax.php?%s' % (server[0].rsplit('?', 1)[1]), headers=headers)
		except ConnectionError:
			response = get('https://embed.watchasian.cc/ajax.php?%s' % (server[0].rsplit('?', 1)[1]), headers=headers)
		try:
			for source in response.json()['source']:
				if 'm3u8' in source['file']:
					return m3u8(folder, episode, check_m3u8_request(source['file']))
				else:
					return googleapis(folder, episode, source['file'])
		except JSONDecodeError:
			return "Service Temporarily Unavailable."
	else:
		return 1

def m3u8(folder, episode, url):
	try:
		response = get(url)
		txt = open('%s/Episode %s.txt' % (folder, episode), 'w+')
		txt.write('# %s\n' % url)
		folder_new = '%s/%s' % (abs_dirname, folder.rsplit('/', 1)[1])
		count = 0
		for line in response.text.splitlines():
			if not '#' in line:
				txt.write('%s/%s\n dir=%s\n out=%s.ts\n' % (url.rsplit('/', 1)[0], line, folder_new, count))
				count += 1
		txt.close()
	except MissingSchema:
		pass
	return 0

def check_m3u8_request(m3u8):
	try:
		if get('%s.1080.m3u8' % m3u8[:-5], timeout=10).status_code == 200:
			return '%s.1080.m3u8' % m3u8[:-5]
	except Timeout:
		pass
	try:
		if get('%s.720.m3u8' % m3u8[:-5], timeout=10).status_code == 200:
			return '%s.720.m3u8' % m3u8[:-5]
	except Timeout:
		pass
	try:
		if get('%s.360.m3u8' % m3u8[:-5], timeout=10).status_code == 200:
			return '%s.360.m3u8' % m3u8[:-5]
	except Timeout:
		pass
	return

def googleapis(folder, episode, url):
	txt = open('%s/Episode %s.txt' % (folder, episode), 'w+')
	txt.write(url)
	txt.close()
	return 0

# This method determine system platform and execute bash script
def bash_call(command):
	if system() == "Linux":
		if command is None:
			check_call('echo', executable='/bin/bash', shell=True)
		else:
			check_call('echo "%s"' % (command), executable='/bin/bash', shell=True)
	if system() == "Windows":
		if command is None:
			os.system('echo.')
		else:
			os.system('echo %s' % (command))

"""
Make sure the string is a valid file name
https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8
"""
def clean_filename(filename):
	# Keep only valid ASCII characters
	cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

	# Keep only valid chararacters
	valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	cleaned_filename = ''.join(c for c in cleaned_filename if c in valid_filename_chars)

	return cleaned_filename

if __name__ == "__main__":
	keyword = sys.argv[1]
	try:
		start_episode = int(sys.argv[2])
		end_episode = int(sys.argv[3])
	except IndexError:
		start_episode = None
		end_episode = None
	dramacool(keyword, start_episode, end_episode)