#!/usr/bin/env python
import sys
import json

import argparse
import logging
import json

from mailer import Mailer
from emailnotify import EmailNotifier
from notificationmgr import NotificationManager

def load_json_settings_file(file_name):
    with open(file_name, 'rt') as file:
        return json.loads(file.read())

if __name__ == '__main__':
    logging.basicConfig(filename='/var/log/motion/email.log',
                        level=logging.DEBUG,
                        format='%(asctime)s %(process)d %(levelname)-8s %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    parser = argparse.ArgumentParser(description='Send an email to respond to a camera motion event')
    parser.add_argument('-m', '--movie', type=str, default=None, help='video file recorded')
    parser.add_argument('-d', '--detected', action='store_true', default=False, help="motion detected")
    args = parser.parse_args()

    if args.movie != None and args.detected:
        logging.error('You cannot specify -m and -d together')
    elif args.movie == None and not args.detected:
        logging.error('You must specify either -m or -d')

    settings = load_json_settings_file('settings.json')
    mailer = Mailer('mail_settings.json', 'Raspberry Pi Security Camera', 'jr.ludwig.auto@gmail.com')
    notifier = EmailNotifier(settings, mailer)
    manager = NotificationManager(notifier)
    if args.detected:
        assert args.movie == None
        manager.handle_motion_detected()
    else:
        assert not args.detected
        assert args.movie != None
        manager.handle_movie_recorded(args.movie)
