import sys
import os

from requests import (get, head)
from lxml import html
from json import JSONDecodeError
from requests.exceptions import (ConnectionError, Timeout, MissingSchema)
from utils import utils

abs_dirname = os.path.dirname(os.path.abspath(__file__))
headers = {'X-Requested-With': 'XMLHttpRequest'}

def dramacool(keyword, start_episode=None, end_episode=None):
	response = get('https://watchasian.cc/search?keyword=%s&type=movies' % keyword.replace(' ', '+'), headers=headers)
	try:
		for json in response.json():
			utils.bash_call(json['name'])
			folder = '%s/.temp/.series/%s' % (abs_dirname, utils.clean_filename(json['name']))
			if not os.path.exists(folder):
				os.mkdir(folder)
			episode_list(folder, json['url'])
			utils.bash_call()
	except IndexError:
		print('There is no movie matching your "%s" in our database.' % keyword)
		sys.exit(1) # Return value for bash

def episode_list(folder, url):
	response = get('https://watchasian.cc%s' % url)
	tree = html.fromstring(response.text)
	episodes = tree.xpath('//ul[@class="list-episode-item-2 all-episode"]/li/a/@href')
	for episode in reversed(episodes):
		selected_server(folder, 'https://watchasian.cc%s' % episode, episode[:-5].rsplit('-', 1)[1])

def selected_server(folder, url, episode):
	tree = html.fromstring(get(url).text)
	server = tree.xpath('//li[@class="Standard Server selected"]/@data-video')
	try:
		response = get('https://embed.watchasian.cc/ajax.php?%s' % (server[0].rsplit('?', 1)[1]), headers=headers)
	except ConnectionError:
		response = get('https://embed.watchasian.cc/ajax.php?%s' % (server[0].rsplit('?', 1)[1]), headers=headers)
	try:
		utils.bash_call('Episode %s' % episode)
		for source in response.json()['source']:
			if 'm3u8' in source['file']:
				m3u8(folder, episode, check_m3u8_request(source['file']))
			else:
				googleapis(folder, episode, source['file'])
	except JSONDecodeError:
		utils.bash_call("Service Temporarily Unavailable.")


def m3u8(folder, episode, url):
	try:
		response = get(url, timeout=5)
		txt = open('%s/Episode %s.txt' % (folder, episode), 'w+')
		txt.write('# %s\n' % url)
		folder_new = '%s/%s' % (abs_dirname, folder.rsplit('/', 1)[1])
		count = 0
		for line in response.text.splitlines():
			if not '#' in line:
				txt.write('%s/%s\n dir=%s\n out=%s.ts\n' % (url.rsplit('/', 1)[0], line, folder_new, count))
				count += 1
		txt.close()
	except Timeout:
		txt = open('%s/Episode %s.txt' % (folder, episode), 'w+')
		txt.write('# %s\n' % url)
		txt.close()
	except MissingSchema:
		pass

def check_m3u8_request(m3u8):
	if head('%s.1080.m3u8' % m3u8[:-5]).status_code == 200:
		return '%s.1080.m3u8' % m3u8[:-5]
	elif head('%s.720.m3u8' % m3u8[:-5]).status_code == 200:
		return '%s.720.m3u8' % m3u8[:-5]
	elif head('%s.360.m3u8' % m3u8[:-5]).status_code == 200:
		return '%s.360.m3u8' % m3u8[:-5]
	return

def googleapis(folder, episode, url):
	txt = open('%s/Episode %s.txt' % (folder, episode), 'w+')
	folder_new = '%s/%s' % (abs_dirname, folder.rsplit('/', 1)[1])
	txt.write('# %s\n%s\n dir=%s\n out=Episode %s.mp4\n' % (url, url, folder_new, episode))
	txt.close()

if __name__ == "__main__":
	keyword = sys.argv[1]
	try:
		start_episode = int(sys.argv[2])
		end_episode = int(sys.argv[3])
	except IndexError:
		start_episode = None
		end_episode = None
	dramacool(keyword, start_episode, end_episode)