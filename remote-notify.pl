#!/usr/bin/env perl
use strict;
use HTTP::Request;
use Irssi;
use LWP::UserAgent;
use POSIX;
use URI::Escape;
use vars qw($VERSION %IRSSI);
$VERSION = '1.00';
%IRSSI = (
    authors     => 'Geoffrey Anderson',
    contact     => 'geoff@geoffreyanderson.net',
    name        => 'Remote Notify',
    description => 'This script allows you to ' .
                   'send notifications from irssi ' .
                   'to a notify-osd or growl (OS X) ' .
                   'through an SSH tunnel.',
    license     => 'GNU GPL v3',
);
my $URL_TEMPLATE = "http://localhost:%d?title=%s&message=%s";
my $NOTIFY_TITLE = "irssi mention";
my $UA = LWP::UserAgent->new;


sub remote_notify {
    # Grab the default values sent to this signal
    my ($dest, $text, $stripped) = @_;

    # get a reference to the active window in irssi
    my $window = Irssi::active_win();

    # grab the port from the settings
    my $port = Irssi::settings_get_int('remotenotify_port');

    # Check if the printed message is a hilight
    if ( ($dest->{level} & (MSGLEVEL_HILIGHT|MSGLEVEL_MSGS)) &&
        ($dest->{level} & MSGLEVEL_NOHILIGHT) == 0)
    {
        # Strip all the funky irssi color coding out of the text
        $text = Irssi::strip_codes($text);

        # if the hilighted message is in a channel, prepend the channel name to
        # the message text
        if ($dest->{level} & MSGLEVEL_PUBLIC) {
            $text = $dest->{target}.": ".$text;
        }

        # Prepend a timestamp to the message text
        $text = strftime(Irssi::settings_get_str('timestamp_format')." ", localtime).$text;

        # Create the HTTP request using the template and parameters collected
        # above
        my $request = HTTP::Request->new(
            GET => sprintf($URL_TEMPLATE, $port, uri_escape($NOTIFY_TITLE), uri_escape($text))
        );

        # Get the response. Print to the irssi window if an error was detected.
        my $response = $UA->request($request);
        if (!$response->is_success) {
            $window->print("Failed to send data to remote notifier.", MSGLEVEL_NEVER) if ($window);
        }
    }
}

Irssi::settings_add_int('remotenotify', 'remotenotify_port', 4235);
Irssi::signal_add("print text", "remote_notify");
