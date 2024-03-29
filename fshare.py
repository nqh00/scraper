import asyncio
from aiohttp import ClientSession
from requests import request
import codecs
import json
import os
class fshare:

# Default contructor with email and password required
	def __init__(self, email, password):
		self.email = email
		self.password = password
		self.token = None
		self.headers = {'User-Agent': 'FshareClone1-W57IYP'}

# Scrape info of all fshare link
	def info(self, keyword):
		loop = asyncio.get_event_loop()
		if '.txt' in keyword:
			loop.run_until_complete(self.info_from_file(keyword[:-4]))
		else:
			if 'https' in keyword:
				self.linkcode = keyword[-12:]
			else:
				self.linkcode = keyword
			loop.run_until_complete(self.info_from_url(self.linkcode))

# Get download link from fshare api
	def download(self, url):
		loop = asyncio.get_event_loop()
		if 'https' in url:
			loop.run_until_complete(self.download_from_url(url))
		elif '.txt' in url:
			loop.run_until_complete(self.download_from_file(url[:-4]))
		else:
			print('Invalid Fshare URL!')

# Login to fshare using requests
	def login(self):
		payload_login = {
			'user_email': self.email,
			'password': self.password,
			'app_key': 'dMnqMMZMUnN5YpvKENaEhdQQ5jxDqddt'
		}
		response = request('POST', 'https://api.fshare.vn/api/user/login', headers=self.headers, data=json.dumps(payload_login))
		try:
			data = response.json()
			cookie = {
				'Cookie': 'session_id=%s' % data['session_id']
			}
			self.headers.update(cookie)
			self.token = data['token']
			print(data['msg'])
		except(json.JSONDecodeError, KeyError):
			try:
				print(data['msg'])
			except(UnboundLocalError, KeyError):
				print('Invalid credentials!')

# Extract download link using async
	async def request_download_from_url(self, session, url):
		payload_token = {
			'token': self.token,
			'url': url
		}
		async with session.post('https://api.fshare.vn/api/session/download', headers=self.headers, data=json.dumps(payload_token)) as response:
			try:
				data = await response.json()
				print(data['location'])
			except(json.JSONDecodeError, KeyError):
				try:
					print(data['msg'])
				except(UnboundLocalError, KeyError):
					print('Error getting download link!')

# Request all downloads link from text file using async
	async def request_download_from_file(self, session, filename, url):
		txt = codecs.open(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\' + filename + '_dl.txt', 'a', 'utf-8')
		payload_token = {
			'token': self.token,
			'url': url
		}
		async with session.post('https://api.fshare.vn/api/session/download', headers=self.headers, data=json.dumps(payload_token)) as response:
			try:
				data = await response.json()
				txt.write(data['location'] + '\n')
			except(json.JSONDecodeError, KeyError):
				try:
					print(data['msg'])
				except(UnboundLocalError, KeyError):
					print('Error getting download link!')
		txt.close()

# Contrains all downloads link session time using semaphore
	async def bound_request_download(self, sem, session, filename, url):
		async with sem:
			await self.request_download_from_file(session, filename, url)
			await asyncio.sleep(1)

# Asynchronize each session with each asynchronized task 
	async def download_from_url(self, url):
		if self.token is None:
			self.login()
		async with ClientSession() as session:
			task_download = asyncio.ensure_future(self.request_download_from_url(session, url))
			await asyncio.gather(task_download)

# Asynchronize each session with each asynchronized task 
	async def download_from_file(self, filename):
		list_of_url = []
		try:
			with open('%s\\%s.txt' % (os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'), filename)) as file:
				for line in file:
					stripped_line = line.strip()
					if 'file' in stripped_line:
						line_list = stripped_line.split()
						list_of_url.extend(line_list)
			tasks = []
			sem = asyncio.Semaphore(100)
			if self.token is None:
				self.login()
			async with ClientSession() as session:
				for url in list_of_url:
					task = asyncio.ensure_future(self.bound_request_download(sem, session, filename, url))
					tasks.append(task)
				await asyncio.gather(*tasks)
		except FileNotFoundError:
			print("There's no " + filename + '.txt in your desktop.')

# Request info link using async
	async def request_info(self, session, filename, fcode, page=None):
		if not page:
			self.url = 'https://www.fshare.vn/api/v3/files/folder?linkcode=%s' % fcode
		else:
			self.url = 'https://www.fshare.vn/api/v3/files/folder?linkcode=%s&%s' % (fcode, page) # Check for multi-page folder link

		# Info with format: file name, tab, fshare url, tab, file size
		# Saved as text file in desktop
		async with session.get(self.url) as response:
			if response.status == 200:
				txt = codecs.open(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') + '\\' + filename + '_info.txt', 'a', 'utf-8')
				data = await response.json()
				if (data['current']['type']) == 1:
					txt.write('%s\thttps://www.fshare.vn/file/%s\t%s\n' % (
						data['current']['name'],
						data['current']['linkcode'],
						'{:0.3f}'.format(data['current']['size'] / 1073741824)
						)
					)
				else:
					for item in data['items']:
						if int(item['type']) == 1:
							txt.write('%s\thttps://www.fshare.vn/file/%s\t%s\n' % (
								item['name'],
								item['linkcode'],
								'{:0.3f}'.format(item['size'] / 1073741824)
								)
							)
						else:
							await self.request_info(session, filename, item['linkcode']) # Recursive for nested folder
					if 'next' in data['_links']:
						await self.request_info(session, filename, fcode, data['_links']['next'].rsplit('&')[1]) # Getting nextpage number
				txt.close()
			elif response.status == 404:
				print('File Not Found')
			else:
				print('Error code: %s' % str(response.status)) # Async sending request too fast thus fail to connect to server 

# Asynchronize each session with each asynchronized task 
	async def info_from_url(self, url):
		async with ClientSession() as session:
			task = asyncio.ensure_future(self.request_info(session, url, url))
			await asyncio.gather(task)

# Bound the failing requests that sent too fast with semaphore
	async def bound_info_from_file(self, sem, session, filename, code):
		async with sem:
			await self.request_info(session, filename, code)
			await asyncio.sleep(1)

# This method read text file, located in YOUR DESKTOP.
# Then asynchronize each session with each asynchronized task 
	async def info_from_file(self, filename):
		list_of_code = []
		try:
			with open('%s\\%s.txt' % (os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'), filename)) as file:
				for line in file:
					stripped_line = line.strip()
					if 'file' in stripped_line:
						line_list = stripped_line[27:].split()
					else:
						line_list = stripped_line[29:].split()
					list_of_code.extend(line_list)
			tasks = []
			sem = asyncio.Semaphore(20) # Set it slow to avoid failing request
			async with ClientSession() as session:
				for code in list_of_code:
					task = asyncio.ensure_future(self.bound_info_from_file(sem, session, filename, code))
					tasks.append(task)
				await asyncio.gather(*tasks)
		except FileNotFoundError:
			print("There's no " + filename + '.txt in your desktop.')
