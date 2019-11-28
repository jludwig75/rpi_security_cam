#!/usr/bin/env python
import sys
import json

import argparse
import logging
import json
import os
from pwd import getpwnam

from mailer import Mailer
from emailnotify import EmailNotifier
from notificationmgr import NotificationManager

ROOT_SETTINGS_PATH = '/etc/rpi-cam'
ROOT_LOG_PATH = '/var/log/motion'
SERVICE_USER_NAME = 'motion'

def is_service_user():
    try:
        return os.geteuid() == getpwnam(SERVICE_USER_NAME).pw_uid
    except:
        return False

def settings_path(path):
    if is_service_user():
        return os.path.join(ROOT_SETTINGS_PATH, path)
    else:
        return os.path.join(os.path.dirname(sys.argv[0]), path)

def log_path(path):
    if is_service_user():
        return os.path.join(ROOT_LOG_PATH, path)
    else:
        return os.path.join(os.path.dirname(sys.argv[0]), path)

def load_json_settings_file(file_name):
    with open(file_name, 'rt') as file:
        return json.loads(file.read())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send an email to respond to a camera motion event')
    parser.add_argument('-m', '--movie', type=str, default=None, help='video file recorded')
    parser.add_argument('-d', '--detected', action='store_true', default=False, help="motion detected")
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help="suppress debug output to stdout")
    parser.add_argument('-c', '--catch-up', type=str, default=None, help="catch up uploading old videos")
    args = parser.parse_args()

    logging.basicConfig(filename=log_path('email.log'),
                        level=logging.CRITICAL if args.quiet else logging.INFO,
                        format='%(asctime)s %(process)d %(levelname)-8s %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    actions_specified = 0
    if args.detected:
        actions_specified += 1
    if args.movie != None:
        actions_specified += 1
    if args.catch_up != None:
        actions_specified += 1

    if actions_specified > 1:
        logging.error('You can only specify one of either -m, -d or -c')
    elif actions_specified == 0:
        logging.error('You must specify one of either -m, -d or -c')

    settings = load_json_settings_file(settings_path('settings.json'))
    mailer = Mailer(settings_path('mail_settings.json'), 'Raspberry Pi Security Camera', 'jr.ludwig.auto@gmail.com')
    notifier = EmailNotifier(settings, mailer)
    manager = NotificationManager(notifier, run_local=not is_service_user())
    if args.detected:
        assert args.movie == None
        manager.handle_motion_detected()
    elif args.movie != None:
        assert not args.detected
        assert args.movie != None
        manager.handle_movie_recorded(args.movie)
    else:
        sys.stderr.write('Action not supported\n')
        sys.exit(-1)
