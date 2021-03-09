import sys
import os
import string

from requests import get
from re import findall
from random import choice
from string import ascii_letters
from base64 import b64encode
from unicodedata import normalize
from platform import system

HDV_USER = 'rdMbGniOGTu6pCLlNaTbozthPskWaILGURY831OUKtm9UmTgXCFBc5n_TkqOExm2' # User cookies, unimportant
abs_dirname = os.path.dirname(os.path.abspath(__file__))
imdb_list = []

# This method search your keyword and save all chunked download link to text file
def vikv(keyword):
	imdb_search(keyword)
	m3u8_request(keyword)

# This method search for keyword in imdb database
def imdb_search(keyword):
	response = get('https://v2.sg.media-imdb.com/suggestion/%s/%s.json' % (keyword[0].lower(), keyword.replace(" ", "_")))
	data = response.json()
	try:
		for d in data['d']:
			try:
				if d["q"] == "feature":
					imdb_list.append({'name': d['l'], 'id': d['id'], 'year': d['y']})
			except KeyError:
				pass
	except KeyError:
		print('There is no movie matching your "%s".' % (keyword))
		sys.exit(1) # Return value for bash

# This method get the m3u8 file of the best quality movie that found in database
def m3u8_request(keyword):
	found = False
	for imdb in imdb_list:
		if check_database(imdb['id']):
			bash_call("%s - %s" % (imdb['name'], imdb['year']))
			response = get('https://hls.hdv.fun/imdb/%s' % (imdb['id']))
			regex = findall(r'"name": "([a-zA-Z0-9]{11})", "quality": "([a-zA-Z]{0,})", "res": ([0-9]{,4})', response.text)
			m3u8(	clean_filename(imdb['name']),
					clean_moviename(
						clean_filename(imdb['name']),
						imdb['year'],
						regex[0][1],
						regex[0][2]
						),
					'https://hls.hdv.fun/m3u8/%s.m3u8?u=%s' % (regex[0][0], query_parameter()
					)
				)
			found = True
	if not found:
		print('There is no movie matching your "%s" in our database.' % (keyword))
		sys.exit(2) # Return value for bash

# This method extract the m3u8 file and reformat structure for aria to download
def m3u8(foldername, filename, url):
	response = get(url)
	txt = open('%s/.temp/.feature/%s.txt' % (abs_dirname, filename), 'w+')
	count = 0
	for line in response.text.splitlines():
		if 'https' in line:
			txt.write('%s\n dir=%s/%s\n out=%s.ts\n' % (line, abs_dirname, foldername, count))
			count = count + 1
	txt.close()

# This method check if the database has the movie
def check_database(imdb):
	response = get('https://hls.hdv.fun/api/list')
	data = response.json()
	for _id in data:
		if _id == imdb:
			return True;
	return False;

"""
Make sure the string is a valid file name
https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8
"""
def clean_filename(filename):
	# Keep only valid ASCII characters
	cleaned_filename = normalize('NFKD', filename).encode('ASCII', 'ignore').decode()

	# Keep only valid chararacters
	valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	cleaned_filename = ''.join(c for c in cleaned_filename if c in valid_filename_chars)

	return cleaned_filename

# This method format the movie name with its codec properties
def clean_moviename(moviename, year, quality, resolution):
	moviename = moviename.replace(".", "").replace(" ", ".")
	if not quality is None:
		quality = quality.replace(" ", ".").upper()
		return '%s.%s.%sp.%s.AAC.x264-HYUQ' % (moviename, year, resolution, quality)
	return '%s.%s.%sp.AAC.x264-HYUQ' % (moviename, year, resolution)

"""
This method extract from javascript of the website.
It encode the cookie with base64 and reverse the string.
Use it as query parameter to send request.
"""
def query_parameter():
	# Append 10 random char to the cookie hdv_user
	rand = ('%s%s' % (''.join(choice(ascii_letters) for i in range(10)), HDV_USER))
	# Reverse string
	rand = rand[::-1]
	# Base64 encode
	btoa = b64encode(rand.encode('ascii'))
	# Base 64 encode reverse string
	return b64encode(btoa[::-1]).decode('ascii')

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

if __name__ == '__main__':
	vikv(sys.argv[1])