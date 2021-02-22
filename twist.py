import base64

from requests import get
from requests.utils import quote
from hashlib import md5
from Cryptodome.Cipher import AES
from json import JSONDecodeError
from requests import head
from os import path
import sys

abs_dirname = path.dirname(path.abspath(__file__))
KEY = b'267041df55ca2b36f2e322d05ee2c9cf'
headers = {'X-Access-Token': '0df14814b9e590a1f26d3071a4ed7974'}
title = {}
cryptoEpisode = []
json = {}

# This method search your keyword and return all available anime with following media link
def main(keyword):
	response = get('https://api.twist.moe/api/anime')
	json = response.json()
	for anime in json:
		if anime['alt_title'] is None:
			if check_keyword(keyword, anime['title']):
				if anime['season'] == 0:
					title = anime['title']
				else:
					title = '%s - Season %s' % (anime['title'], anime['season'])
				txt_title = '%s%s%s%s' % (abs_dirname, '\\__temp__\\', title, '.txt')
				print(title)
				request_episode(anime['slug']['slug'], txt_title)
		elif check_keyword(keyword, anime['title']) or check_keyword(keyword, anime['alt_title']):
			if anime['season'] == 0:
				alt_title = anime['alt_title']
			else:
				alt_title = '%s - Season %s' % (anime['alt_title'], anime['season'])
			txt_alt_title = '%s%s%s%s' % (abs_dirname, '\\__temp__\\', alt_title, '.txt')
			print(alt_title)
			request_episode(anime['slug']['slug'], txt_alt_title)

# This method check if keyword and title shares the similar
def check_keyword(keyword, title):
	keywords = keyword.lower().split(' ')
	title = title.lower()
	for word in keywords:
		if not word in title:
			return False
	return True

# This method check status of the request
def check_request(url):
	if head(url, headers={'Referer': 'https://twist.moe/'}).status_code == 200:
		return True
	return False

# This method sends request to retrieve episodes json
def request_episode(slug, textfile):
	response = get('%s%s%s' % ('https://api.twist.moe/api/anime/', slug, '/sources'), headers=headers)
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
			print('Episode %s: %s'  % (episode['episode'], 'No links available!'))
		else:
			print('Episode %s: %s'  % (episode['episode'], url))
			txt.write('%s %s\n'  % (episode['episode'], url))
	print() # Space for each season
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
	cdn = 'https://cdn.twist.moe'
	aircdn = 'https://air-cdn.twist.moe'
	if check_request('%s%s' % (cdn, suffix)):
		return '%s%s' % (cdn, suffix)
	if check_request('%s%s' % (aircdn, suffix)):
		return '%s%s' % (aircdn, suffix)
	return 0

if __name__ == "__main__":
	main(sys.argv[1])