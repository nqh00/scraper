import base64

from requests import get
from requests.utils import quote
from hashlib import md5
from Cryptodome.Cipher import AES

KEY = b'267041df55ca2b36f2e322d05ee2c9cf'
headers = {'X-Access-Token': '0df14814b9e590a1f26d3071a4ed7974'}
title = {}
cryptoEpisode = []

# This method return episode and its stream casting web service
def twistmoe(url):
	name = url.split('/')[4]
	request_info(name)
	print(title['title']) if title['season'] == 0 else print('%s - Season %s' % (title['title'], title['season']))
	request_episode(name)
	for eps in cryptoEpisode:
		print('Episode %s: %s'  % (eps['episode'], extract(eps['url'])))

# This method sends request to retrieve gerenal info
def request_info(name):
	response = get('https://api.twist.moe/api/anime/' + name, headers=headers)
	data = response.json()
	title.update({'title': data['title']}) if data['alt_title'] is None else title.update({'title': data['alt_title']})
	title.update({'season': data['season']})

# This method sends request to retrieve episodes json
def request_episode(name):
	response = get('https://api.twist.moe/api/anime/' + name + '/sources', headers=headers)
	data = response.json()
	for src in data:
		cryptoEpisode.append({'episode': src['number'], 'url': src['source']})

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

twistmoe('https://twist.moe/a/hanasaku-iroha/1')