import os
import sys
import base64
import unicodedata
import string

from requests import get
from requests.utils import quote
from hashlib import md5
from Cryptodome.Cipher import AES
from json import JSONDecodeError
from http.client import HTTPSConnection

abs_dirname = os.path.dirname(os.path.abspath(__file__))
KEY = b'267041df55ca2b36f2e322d05ee2c9cf'
payload = ''
headers = {'X-Access-Token': '0df14814b9e590a1f26d3071a4ed7974'}
json = {}

# This method search your keyword and return all available anime with following media link
def main(keyword):
	response = get('https://api.twist.moe/api/anime')
	json = response.json()
	found = False
	for anime in json:
		if anime['alt_title'] is None:
			if check_keyword(keyword, anime['title']):
				found = True
				if anime['season'] == 0:
					title = anime['title']
				else:
					title = '%s - Season %s' % (anime['title'], anime['season'])
				txt_title = '%s\\__temp__\\%s.txt' % (abs_dirname, clean_filename(title))
				os.system('echo %s' % (title))
				request_episode(anime['slug']['slug'], txt_title)
		elif check_keyword(keyword, anime['title']) or check_keyword(keyword, anime['alt_title']):
			found = True
			if anime['season'] == 0:
				alt_title = anime['alt_title']
			else:
				alt_title = '%s - Season %s' % (anime['alt_title'], anime['season'])
			txt_alt_title = '%s\\__temp__\\%s.txt' % (abs_dirname, clean_filename(alt_title))
			os.system('echo %s' % (alt_title))
			request_episode(anime['slug']['slug'], txt_alt_title)
	if not found:
		os.system('echo There\'s no anime matching your "%s"!' % (keyword))
		sys.exit(1) # Return value for bash


# This method check if keyword and title shares the similar
def check_keyword(keyword, title):
	keywords = keyword.lower().split(' ')
	title = title.lower()
	for word in keywords:
		if not word in title:
			return False
	return True

# This method check status of the request
def check_request(host, suffix):
	conn = HTTPSConnection(host)
	payload = ''
	headers = {
	  'Referer': 'https://twist.moe/'
	}
	conn.request("HEAD", suffix, payload, headers)
	res = conn.getresponse()
	if res.status == 200:
		return True
	return False

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

# This method sends request to retrieve episodes json
def request_episode(slug, textfile):
	cryptoEpisode = []
	response = get('https://api.twist.moe/api/anime/%s/sources' % (slug), headers=headers)
	try:
		data = response.json()
		for src in data:
			cryptoEpisode.append({'episode': src['number'], 'url': src['source']})
	except JSONDecodeError:
		print('Fails to connect to server!')

	txt = open(textfile, 'w')
	for episode in cryptoEpisode:
		url = extract(episode['url'])
		if url == 0:
			os.system('echo Episode %s: No links available!'  % (episode['episode']))
		else:
			os.system('echo Episode %s: %s'  % (episode['episode'], url))
			txt.write('%s %s\n'  % (episode['episode'], url))
	os.system('echo.') # Space for each season
	txt.close()

"""
(CryptoJS decipher)[https://stackoverflow.com/a/36780727]
"""
def unpad(data):
	return data[:-(data[-1] if type(data[-1]) == int else ord(data[data[-1]]))]

def bytes_to_key(data, salt, output=48):
	# Extended from https://gist.github.com/gsakkis/4546068
	assert len(salt) == 8, len(salt)
	data += salt
	key = md5(data).digest()
	final_key = key
	while len(final_key) < output:
		key = md5(key + data).digest()
		final_key += key
	return final_key[:output]

def decrypt(encrypted, passphrase):
	# CryptoJS defaults to 256 bit key size for AES, PKCS#7 padding and CBC mode.
	# AES has a 128 bit block size which is also the IV size.
	encrypted = base64.b64decode(encrypted)
	assert encrypted[0:8] == b"Salted__"
	salt = encrypted[8:16]
	key_iv = bytes_to_key(passphrase, salt, 32+16) 	# This means that we have to request 32+16 = 48 byte from EVP_BytesToKey
	key = key_iv[:32]
	iv = key_iv[32:]
	aes = AES.new(key, AES.MODE_CBC, iv)
	return unpad(aes.decrypt(encrypted[16:]))

# This method return good status link
def extract(source):
	decrypt_ed = decrypt(source.encode('UTF-8'), KEY).decode('UTF-8').lstrip(' ')
	suffix = quote(decrypt_ed, safe='[]~@#$&()*!+=:;,.?/\'')

	if check_request('cdn.twist.moe', suffix):
		return 'https://cdn.twist.moe%s' % (suffix)
	elif check_request('air-cdn.twist.moe', suffix):
		return 'https://air-cdn.twist.moe%s' % (suffix)
	return 0

if __name__ == "__main__":
	main(sys.argv[1])