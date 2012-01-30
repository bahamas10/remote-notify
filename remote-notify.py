#!/usr/bin/env python
# Copyright (c) 2012, Dave Eddy <dave@daveeddy.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#	 * Redistributions of source code must retain the above copyright
#	   notice, this list of conditions and the following disclaimer.
#	 * Redistributions in binary form must reproduce the above copyright
#	   notice, this list of conditions and the following disclaimer in the
#	   documentation and/or other materials provided with the distribution.
#	 * Neither the name of the project nor the
#	   names of its contributors may be used to endorse or promote products
#	   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Allow remote notifications for weechat in growl/osd-notify
#
# :: To use ::
# On the remote machine running weechat:
#	Enable the plugin
#	/python load remote-notify.py
# On the machine you are connecting from:
#	Start the service.
#	~$ ./remote-notify.py
#	* This starts the web service listening on localhost
#	Then, ssh to the host running weechat and forward the port
#	~$ ssh -R 4235:localhost:4235 user@host
#

__program__     = 'remote-notify'
__author__      = 'David Eddy'
__credits__     = ['Michael Zeller']
__license__     = 'BSD 3-Clause'
__version__     = '0.1'
__maintainer__  = 'David Eddy'
__email__       = 'dave@daveeddy.com'
__status__      = 'Release'
__description__ = 'Send remote notifications to growl/osd-notify'

from os import uname

in_weechat = True
try:
	import weechat
except:
	in_weechat = False

DEFAULT_PORT = 4235
DEFAULT_HOST = '127.0.0.1'
UNAME = uname()[0]

def r_callback(data, signal, signal_data):
	"""
	Called from weechat

	Take the data passed from weechat and
	attempt to send the data to the server
	"""
	msg_sender, message = signal_data.split('\t', 1)
	data = {
		'title'   : 'Mentioned by %s' % (msg_sender),
		'message' : message,
	}
	url = 'http://localhost:%d?%s' % (DEFAULT_PORT, urllib.urlencode(data))
	try:
		# Try to make the request
		output = urllib2.urlopen(url)
	except:
		weechat.prnt('', 'Failed to send remote notification')
	# Do nothing with output
	return weechat.WEECHAT_RC_OK

def notify(title, message):
	"""
	Send a notification on a system
	"""
	if UNAME == 'Darwin':
		# Use growl on a mac
		cmd = ['growlnotify', '-m', message, '-t', title]
	else:
		# Otherwise default to notify-send
		cmd = ['notify-send', title, message]
	try:
		# Call the subprocess
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	except OSError:
		return None
	# Return the Popen object
	return p

if __name__ == '__main__':
	if in_weechat:
		# Running inside weechat
		if weechat.register(__program__, __author__, __version__, __license__, __description__, '', ''):
			import urllib, urllib2
			weechat.hook_signal('weechat_highlight', 'r_callback', '')
	else:
		# Running from the command line
		import BaseHTTPServer
		import urlparse
		import cgi
		import subprocess

		class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
			"""
			Simple HTTP class to listen for GET requests
			"""
			def do_GET(s):
				"""Respond to a GET request."""
				try:
					# try to parse the request
					parsed_path = urlparse.urlparse(s.path)
					q = cgi.parse_qs(parsed_path.query)
					title = q['title'][0]
					message = q['message'][0]
					# Send the notification
					p = notify(title, message)
					# Check for errors
					if not p:
						send = 'Command not found'
					else:
						err = p.stderr.read()
						if err:
							send = err
						else:
							send = 'Message Sent Successfully'
				except:
					send = 'Error: Error parsing message'
				s.send_response(200)
				s.send_header("Content-type", "text/html")
				s.end_headers()
				s.wfile.write('<status>%s</status>' % (send))
				print send

		# Create the httpd service
		server_class = BaseHTTPServer.HTTPServer
		httpd = server_class((DEFAULT_HOST, DEFAULT_PORT), MyHandler)
		try:
			# Start the service
			print 'Listening on %s:%d' % (DEFAULT_HOST, DEFAULT_PORT)
			httpd.serve_forever()
		except KeyboardInterrupt:
			httpd.socket.close()
