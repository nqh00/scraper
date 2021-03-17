import os
import string

from platform import system
from unicodedata import normalize
from subprocess import check_call

class utils():
	"""docstring for utils"""
	def __init__(self, arg):
		super(utils, self).__init__()
		self.arg = arg

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

	# This method determine system platform and execute bash script
	def bash_call(command=None):
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
