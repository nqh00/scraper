import base64

from requests import get
from requests.utils import quote
from hashlib import md5
from Cryptodome.Cipher import AES
from json import JSONDecodeError

KEY = b'267041df55ca2b36f2e322d05ee2c9cf'
# headers = {'X-Access-Token': '0df14814b9e590a1f26d3071a4ed7974'}
title = {}
cryptoEpisode = []
json = {}

# This method search your keyword and return all available anime with following media link
def twistmoe(keyword):
	response = get('https://api.twist.moe/api/anime')
	json = response.json()
	for anime in json:
		if anime['alt_title'] is None:
			if check(keyword, anime['title']):
				print(anime['title']) if anime['season'] == 0 else print('%s - Season %s' % (anime['title'], anime['season']))
				request_episode(anime['slug']['slug'])
		elif check(keyword, anime['title']) or check(keyword, anime['alt_title']):
			print(anime['alt_title']) if anime['season'] == 0 else print('%s - Season %s' % (anime['alt_title'], anime['season']))
			request_episode(anime['slug']['slug'])

# This method check if keyword and title shares the similar
def check(keyword, title):
	keywords = keyword.lower().split(' ')
	title = title.lower()
	for word in keywords:
		if not word in title:
			return False
	return True

# This method sends request to retrieve episodes json
def request_episode(slug):
	# response = get('%s%s%s' % ('https://api.twist.moe/api/anime/', slug, '/sources'), headers=headers, timeout=10)
	response = get('%s%s%s' % ('https://api.twist.moe/api/anime/', slug, '/sources'))
	try:
		data = response.json()
		for src in data:
			cryptoEpisode.append({'episode': src['number'], 'url': src['source']})
	except JSONDecodeError:
		pass

	for episode in cryptoEpisode:
		print('Episode %s: %s'  % (episode['episode'], extract(episode['url'])))
	print('\n')

# (CryptoJS decipher)[https://stackoverflow.com/a/36780727]
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

def extract(source):
	decrypt_ed = decrypt(source.encode('UTF-8'), KEY).decode('UTF-8').lstrip(' ')
	url = 'https://cdn.twist.moe' + quote(decrypt_ed, safe='~@#$&()*!+=:;,.?/\'')
	return url

# curl -L -o $name -C - $i -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36" -H "Referer: https://twist.moe/"