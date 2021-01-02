import asyncio
from aiohttp import ClientSession
import requests
import codecs
import json
import os
class fshare:
	def __init__(self, email, password):
		self.email = email
		self.password = password
		self.token = None
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
		}
		self.items = {}
	def login(self):
		payload_login = {
			'user_email': self.email,
			'password': self.password,
			'app_key': 'L2S7R6ZMagggC5wWkQhX2+aDi467PPuftWUMRFSn'
		}
		response = requests.request("POST", "https://api.fshare.vn/api/user/login", headers=self.headers, data=json.dumps(payload_login))
		try:
			data = response.json()
			cookie = {
				'Cookie': 'session_id=' + data['session_id']
			}
			self.headers.update(cookie)
			self.token = data['token']
			print(data['msg'])
		except(json.JSONDecodeError, KeyError):
			try:
				print(data['msg'])
			except(UnboundLocalError, KeyError):
				print("Login error!")
	def infof(self, url, maxpage):
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.request_folder(url, maxpage))
	def info(self, url):
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.request_file(url))
	def infos(self, filename):
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.info_from_file(filename))
	def download(self, url):
		payload_token = {
			'token': self.token,
			'url': url
		}
		response = requests.request("POST", "https://api.fshare.vn/api/session/download", headers=self.headers, data=json.dumps(payload_token))
		try:
			data = response.json(content_type=None)
			print(data['location'])
		except(json.JSONDecodeError, KeyError):
			try:
				print(data['msg'])
			except(UnboundLocalError, KeyError):
				print("Error getting download link!")
	def downloads(self, filename):
		try:
			loop = asyncio.get_event_loop()
			loop.run_until_complete(self.download_from_file(filename))
			print("Your fshare downloading link is saved at desktop/" + filename + "_dl.txt")
		except FileNotFoundError:
			print("There's no " + filename + ".txt in your desktop.")
	async def login_async(self, session):
		payload_login = {
			'user_email': self.email,
			'password': self.password,
			'app_key': 'L2S7R6ZMagggC5wWkQhX2+aDi467PPuftWUMRFSn'
		}
		async with session.post("https://api.fshare.vn/api/user/login", headers=self.headers, data=json.dumps(payload_login)) as response:
			try:
				data = await response.json()
				cookie = {
					'Cookie': 'session_id' + data['session_id']
				}
				self.headers.update(cookie)
				self.token = data['token']
				print(data['msg'])
			except(json.JSONDecodeError, KeyError):
				try:
					print(data['msg'])
				except(UnboundLocalError, KeyError):
					print("Login error!")
	async def request_download(self, session, url):
		payload_token = {
			'token': self.token,
			'url': url
		}
		async with session.post("https://api.fshare.vn/api/session/download", headers=self.headers, data=json.dumps(payload_token)) as response:
			try:
				data = await response.json(content_type=None)
				print(data['location'])
			except(json.JSONDecodeError, KeyError):
				try:
					print(data['msg'])
				except(UnboundLocalError, KeyError):
					print("Error getting download link!")
	async def request_download_from_file(self, session, filename, url):
		txt = codecs.open('desktop/' + filename + '_dl.txt', 'a', 'utf-8')
		payload_token = {
			'token': self.token,
			'url': url
		}
		async with session.post("https://api.fshare.vn/api/session/download", headers=self.headers, data=json.dumps(payload_token)) as response:
			try:
				data = await response.json(content_type=None)
				txt.write(data['location'])
			except(json.JSONDecodeError, KeyError):
				try:
					print(data['msg'])
				except(UnboundLocalError, KeyError):
					print("Error getting download link!")
		txt.close()
	async def bound_request_download(self, sem, session, filename, url):
		async with sem:
			await self.request_download_from_file(session, filename, url)
			await asyncio.sleep(1)
	async def download_from_url(self, url):
		async with ClientSession() as session:
			if self.token is None:
				task_login = asyncio.ensure_future(self.login_async(session))
				await asyncio.gather(task_login)
			else:
				task_download = (asyncio.ensure_future(self.request_download(session, url)))
				await asyncio.gather(task_download)
	async def download_from_file(self, filename):
		list_of_url = []
		with open('desktop/' + filename + '.txt') as file:
			for line in file:
				stripped_line = line.strip()
				line_list = stripped_line.split()
				list_of_url.extend(line_list)
		tasks = []
		sem = asyncio.Semaphore(100)
		async with ClientSession() as session:
			task_login = asyncio.ensure_future(self.login_async(session))
			await asyncio.gather(task_login)
			for url in list_of_url:
				task = asyncio.ensure_future(self.bound_request_download(sem, session, filename, url))
				tasks.append(task)
			await asyncio.gather(*tasks)
	async def request_info(self, session, url):
		linkcode = url[-12:]
		async with session.get('https://www.fshare.vn/api/v3/files/folder?linkcode=' + linkcode + '&sort=type%2Cname') as response:
			try:
				data = await response.json(content_type=None)
				self.items.update(data['items'])
				self.items.update(data['current'])
				if self.items['type'] == 0:
					print(self.items['name'] + '   ' + 'https://www.fshare.vn/folder/' + self.items['linkcode'])
				if self.items['type'] == 1:
					print(item['name'] + '   ' + 'https://www.fshare.vn/file/' + self.items['linkcode'] + '   ' + '{:0.3f}'.format(self.items['size'] / 1073741824))
			except(json.JSONDecodeError, KeyError):
				try:
					self.items.update(data['current'])
					if self.items['type'] == 0:
						print(self.items['name'] + '   ' + 'https://www.fshare.vn/folder/' + self.items['linkcode'])
					if self.items['type'] == 1:
						print(item['name'] + '   ' + 'https://www.fshare.vn/file/' + self.items['linkcode'] + '   ' + '{:0.3f}'.format(self.items['size'] / 1073741824))
				except(UnboundLocalError, KeyError):
					print("File Not Found")
	async def request_info_from_file(self, session, filename, linkcode, page=None):
		txt = codecs.open(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\' + filename + '_info.txt', 'a', 'utf-8')
		if page:
			async with session.get('https://www.fshare.vn/api/v3/files/folder?linkcode=' + linkcode + '&sort=type%2Cname&page=' + str(page) + '&per-page=50') as response:
				try:
					data = await response.json(content_type=None)
					for item in data['items']:
						if int(item['type']) == 0:
							txt.write(item['name'] + '\t' + 'https://www.fshare.vn/folder/' + item['linkcode'] + '\n')
						if int(item['type']) == 1:
							txt.write(item['name'] + '\t' + 'https://www.fshare.vn/file/' + item['linkcode'] + '\t' + '{:0.3f}'.format(int(item['size']) / 1073741824) + '\n')
					if int(data['current']['type']) == 0:
						txt.write(data['current']['name'] + '\t' + 'https://www.fshare.vn/folder/' + data['current']['linkcode'] + '\n')
					if int(data['current']['type']) == 1:
						txt.write(data['current']['name'] + '\t' + 'https://www.fshare.vn/file/' + data['current']['linkcode'] + '\t' + '{:0.3f}'.format(int(data['current']['size']) / 1073741824) + '\n')
				except(json.JSONDecodeError, KeyError):
					try:
						if int(data['current']['type']) == 0:
							txt.write(data['current']['name'] + '\t' + 'https://www.fshare.vn/folder/' + data['current']['linkcode'] + '\n')
						if int(data['current']['type']) == 1:
							txt.write(data['current']['name'] + '\t' + 'https://www.fshare.vn/file/' + data['current']['linkcode'] + '\t' + '{:0.3f}'.format(int(data['current']['size']) / 1073741824) + '\n')
					except(UnboundLocalError, KeyError):
						txt.write("File Not Found" + '\n')
		else:
			async with session.get('https://www.fshare.vn/api/v3/files/folder?linkcode=' + linkcode + '&sort=type%2Cname') as response:
				try:
					data = await response.json(content_type=None)
					for item in data['items']:
						if int(item['type']) == 0:
							txt.write(item['name'] + '\t' + 'https://www.fshare.vn/folder/' + item['linkcode'] + '\n')
						if int(item['type']) == 1:
							txt.write(item['name'] + '\t' + 'https://www.fshare.vn/file/' + item['linkcode'] + '\t' + '{:0.3f}'.format(int(item['size']) / 1073741824) + '\n')
					if int(data['current']['type']) == 0:
						txt.write(data['current']['name'] + '\t' + 'https://www.fshare.vn/folder/' + data['current']['linkcode'] + '\n')
					if int(data['current']['type']) == 1:
						txt.write(data['current']['name'] + '\t' + 'https://www.fshare.vn/file/' + data['current']['linkcode'] + '\t' + '{:0.3f}'.format(int(data['current']['size']) / 1073741824) + '\n')
				except(json.JSONDecodeError, KeyError):
					try:
						if int(data['current']['type']) == 0:
							txt.write(data['current']['name'] + '\t' + 'https://www.fshare.vn/folder/' + data['current']['linkcode'] + '\n')
						if int(data['current']['type']) == 1:
							txt.write(data['current']['name'] + '\t' + 'https://www.fshare.vn/file/' + data['current']['linkcode'] + '\t' + '{:0.3f}'.format(int(data['current']['size']) / 1073741824) + '\n')
					except(UnboundLocalError, KeyError):
						txt.write("File Not Found" + '\n')
		txt.close()
	async def request_info_massive_folder(self, session, url, page):
		linkcode = url[-12:]
		async with session.get('https://www.fshare.vn/api/v3/files/folder?linkcode=' + linkcode + '&sort=type%2Cname&page=' + str(page) + '&per-page=50') as response:
			try:
				data = await response.json(content_type=None)
				for item in data['items']:
					if int(item['type']) == 0:
						print(item['name'] + '   ' + 'https://www.fshare.vn/folder/' + item['linkcode'])
					if int(item['type']) == 1:
						print(item['name'] + '   ' + 'https://www.fshare.vn/file/' + item['linkcode'] + '   ' + '{:0.3f}'.format(item['size'] / 1073741824))
				if int(data['current']['type']) == 0:
					print(data['current']['name'] + '   ' + 'https://www.fshare.vn/folder/' + data['current']['linkcode'])
				if int(data['current']['type']) == 1:
					print(data['current']['name'] + '   ' + 'https://www.fshare.vn/file/' + data['current']['linkcode'] + '   ' + '{:0.3f}'.format(data['current']['size'] / 1073741824))
			except(json.JSONDecodeError, KeyError):
				try:
					if int(data['current']['type']) == 0:
						print(data['current']['name'] + '   ' + 'https://www.fshare.vn/folder/' + data['current']['linkcode'])
					if int(data['current']['type']) == 1:
						print(data['current']['name'] + '   ' + 'https://www.fshare.vn/file/' + data['current']['linkcode'] + '   ' + '{:0.3f}'.format(data['current']['size'] / 1073741824))
				except(UnboundLocalError, KeyError):
					print("File Not Found")
	async def request_file(self, url):
		async with ClientSession() as session:
			task = asyncio.ensure_future(self.request_info(session, url))
			await asyncio.gather(task)
	async def request_folder(self, url, maxpage):
		tasks = []
		async with ClientSession() as session:
			for page in range(maxpage + 1):
				task = asyncio.ensure_future(self.request_info_massive_folder(session, url, page))
				tasks.append(task)
			await asyncio.gather(*tasks)
	async def bound_request_info(self, sem, session, filename, linkcode):
		async with sem:
			await self.request_info_from_file(session, filename, linkcode)
			await asyncio.sleep(1)
	async def info_from_file(self, filename):
		list_of_code = []
		try:
			with open(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\' + filename + '.txt') as file:
				for line in file:
					stripped_line = line.strip()
					line_list = stripped_line[-12:].split()
					list_of_code.extend(line_list)
			tasks = []
			sem = asyncio.Semaphore(10)
			async with ClientSession() as session:
				for code in list_of_code:
					task = asyncio.ensure_future(self.bound_request_info(sem, session, filename, code))
					tasks.append(task)
				await asyncio.gather(*tasks)
		except FileNotFoundError:
			print("There's no " + filename + ".txt in your desktop.")