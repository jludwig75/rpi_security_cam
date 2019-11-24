#!/usr/bin/env python
import sys
import json

import argparse
import logging

from gmailer import Gmailer
from emailnotify import EmailNotifier
from notificationmgr import NotificationManager

if __name__ = '__main__':
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

    def load_gmail_settings():
        with open('gmail_settings.json', 'r') as f:
            settings = f.read()
        return json.loads(settings)

    settings = load_gmail_settings()
    mailer = Gmailer(settings['GMAIL_ADDRESS'], settings['GMAIL_PASSWORD'])
    notifier = EmailNotifier(settings, mailer)
    manager = NotificationManager(mailer, notifier)
    if args.detected:
        assert args.movie == None
        manager.handle_motion_detected()
    else:
        assert not args.detected
        assert args.movie != None
        manager.handle_movie_recorded(args.movie)
