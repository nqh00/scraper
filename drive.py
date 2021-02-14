import re
from requests import session
import os
import json
import six
import tempfile
import tqdm
import shutil

CHUNK_SIZE = 512 * 1024

def regex_url_drive(page):
	url = ""
	for line in page.splitlines():
		m = re.search(r'href="(\/uc\?export=download[^"]+)', line)
		if m:
			url = "https://docs.google.com" + m.groups()[0]
			url = url.replace("&amp;", "&")
			return url
		m = re.search("confirm=([^;&]+)", line)
		if m:
			confirm = m.groups()[0]
			url = re.sub(r"confirm=([^;&]+)", r"confirm={}".format(confirm), url)
			return url
		m = re.search('"downloadUrl":"([^"]+)', line)
		if m:
			url = m.groups()[0]
			url = url.replace("\\u003d", "=")
			url = url.replace("\\u0026", "&")
			return url
		m = re.search('<p class="uc-error-subcaption">(.*)</p>', line)
		if m:
			error = m.group()[0]
			raise RuntimeError(error)

def parse_url(url):
	parsed = six.moves.urllib_parse.urlparse(url)
	query = six.moves.urllib_parse.parse_qs(parsed.query)
	is_drive = parsed.hostname == "drive.google.com"
	is_download_link = parsed.path.endswith("/uc")

	file_id = None

	if is_drive and "id" in query:
		file_ids = query["id"]
		if len(file_ids) == 1:
			file_id = file_ids[0]

	match = re.match(r'^/file/d/(.*?)/view$', parsed.path)

	if match:
		file_id = match.groups()[0]

	return file_id, is_download_link

def download(url, output=None, proxy=None, use_cookies=None):
	url_origin = url
	sess = session()

	# Load cookies
	cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "scrape")
	if not os.path.exists(cache_dir):
		os.makedirs(cache_dir)
	cookies_file = os.path.join(cache_dir, "cookies.json")
	if os.path.exists(cookies_file) and use_cookies:
		with open(cookies_file) as file:
			cookies = json.load(file)
		for key, value in cookies:
			sess.cookies[key] = value

	if proxy is not None:
		sess.proxies = {"http": proxy, "https": proxy}

	file_id, is_download_link = parse_url(url)

	while True:
		try:
			respone = sess.get(url, stream=True)
		except requests.exceptions.ProxyError as ex:
			raise Exception(ex)
			return

		# Save cookies
		with open(cookies_file, "w") as file:
			cookies = [(key, value) for key, value in sess.cookies.items() if not key.startswith("download_warning_")]
			json.dump(cookies, file, indent=2)

		if "Content-Disposition" in respone.headers:
			# This is the file
			break
		if not (file_id and is_download_link):
			break

		try:
			url = regex_url_drive(respone.text)
		except RuntimeError as ex:
			raise Exception(ex)

		if url is None:
			return

	if file_id and is_download_link:
		m = re.search('filename="(.*)"', respone.headers["Content-Disposition"])
		filename_from_url = m.groups()[0]
	else:
		filename_from_url = os.path.basename(url)

	if output is None:
		output = filename_from_url

	output_is_path = isinstance(output, six.string_types)
	if output_is_path and output.endswith(os.path.sep):
		if not os.path.exists(output):
			os.makedirs(output)
		output = os.path.join(output, filename_from_url)

	if output_is_path:
		temp_file = tempfile.mktemp(
			suffix=tempfile.template,
			prefix=os.path.basename(output),
			dir=os.path.dirname(output),
		)
		file = open(temp_file, "wb")
	else:
		temp_file = None
		file = output

	try:
		total = respone.headers.get("Content-Length")

		if total is not None:
			total = int(total)

		bar = tqdm.tqdm(total=total, unit="B", unit_scale=True)

		for chunk in respone.iter_content(chunk_size=CHUNK_SIZE):
			file.write(chunk)
			bar.update(len(chunk))
		bar.close()
		if temp_file:
			file.close()
			shutil.move(temp_file, output)
	except IOError as ex:
		raise Exception(ex)
	finally:
		sess.close()
		try:
			if temp_file:
				os.remove(temp_file)
		except OSError:
			pass

	return output