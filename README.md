Remote Notify
=============
Remote notify is a plugin for weechat and irssi that
will send an HTTP request to a specific host on a
specific port whenever your nick is mentioned.

When the python script is invoked on the shell it
will act as a webserver that can recieve requests
and display growl/notify-osd alerts based on those
requests.

Usage
=====
On the remote machine running your irc client:

* Enable the plugin:

weechat
-------
    /python load remote-notify.py

irssi
-----
    /run remote-notify.pl

On the machine you are connecting from, start the service.

    ~$ ./remote-notify.py

This starts the web service listening on localhost

Then, ssh to the host running weechat and forward the port

    ~$ ssh -R 4235:localhost:4235 user@host
