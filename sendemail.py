#!/usr/bin/env python
import sys
import os
import time
import json

from lockfile import LockFile

import argparse
import logging
import smtplib

from email import encoders
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class RunLock:
    def __init__(self, process_name):
        self._process_name = process_name
        self._lock_file_name = '/var/lock/%s.lock' % self._process_name
        self._lock = LockFile(self._lock_file_name, 'w')
    def __enter__(self):
        self._lock != None
        logging.debug('RunLock.__enter__')
        self._lock.acquire()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._lock != None
        logging.debug('RunLock.__eixt__')
        self._lock.release()

class TimedRunLock(RunLock):
    def __init__(self, process_name, min_run_interval):
        RunLock.__init__(self, process_name)
        self._process_name = process_name
        self._time_file_name = '/var/lock/%s.time' % self._process_name
        self._min_run_interval = min_run_interval
    def store_time(self, t = None):
        if t == None:
            t = int(time.time())
        logging.debug("storing time to %s" % self._time_file_name)
        with open(self._time_file_name, 'w') as tf:
            tf.write(str(t))
    def get_time(self):
        logging.debug("getting time from %s" % self._time_file_name)
        with open(self._time_file_name, 'r') as tf:
            data = tf.read()
        if len(data) == 0:
            return 0
        return int(data)
    def check_can_run(self):
        if not os.path.exists(self._time_file_name):
            logging.debug("time file %s does not exist, creating" % self._time_file_name)
            self.store_time()
            logging.debug('can run')
            return True
        if time.time() - self.get_time() > self._min_run_interval:
            logging.debug('can run')
            return True
        logging.debug('cannot run')
        return False
    def can_i_run(self):
        return self.check_can_run()
    def run_complete(self, run_success):
        logging.debug('marking run complete')
        if run_success:
            self.store_time()

class Gmailer:
    def __init__(self, gmail_account, gmail_password):
        self._gmail_account = gmail_account
        self._gmail_password = gmail_password
    def _send_gmail(self, to_address, msg):
        logging.info('Sending email from %s to %s' % (self._gmail_account, to_address))
        try:
            logging.info('Connecting to gmail SMTP server')
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            logging.info('Logging into gmail SMTP server as %s' % self._gmail_account)
            server.login(self._gmail_account, self._gmail_password)
            logging.info('Sending email to %s' % to_address)
            server.sendmail(self._gmail_account, to_address, msg.as_string())    
            logging.info('Closing connection to gmail SMTP server')
            server.close()
            return True
        except Exception as e:
            logging.error('Exception sending email: %s' % str(e))
            return False

    def send_gmail(self, to_address, subject, message):
        try:
            msg = MIMEText(message)
            msg['From'] = '"Raspberry Pi Security Camera" <%s>' % self._gmail_account
            msg['To'] = to_address
            msg['Subject'] = subject
            return self._send_gmail(to_address, msg)
        except Exception as e:
            logging.error('Exception sending email: %s' % str(e))
            return False

    def send_gmail_with_attached_file(self, to_address, subject, message, file_name):
        try:
            msg = MIMEMultipart(message)
            msg['From'] = '"Raspberry Pi Security Camera" <%s>' % self._gmail_account
            msg['To'] = to_address
            msg['Subject'] = subject
            with open(file_name, 'rb') as fd:
                img = MIMEBase('video', 'x-matroska')
                img.set_payload(fd.read())
                encoders.encode_base64(img)
                img.add_header('Content-Disposition', 'attachment', filename=os.path.split(file_name)[-1])
                msg.attach(img)
            return self._send_gmail(to_address, msg)
        except Exception as e:
            logging.error('Exception sending email with attachment %s: %s' % (file_name, str(e)))
            return False
    
class EmailNotifier:
    def __init__(self, settings, mailer):
        self._settings = settings
        self._mailer = mailer
    def notify_motion_detected(self):
        return self._mailer.send_gmail(self._settings['TO_ADDRESS'],
                    subject='Motion Detected in Garage',
                    message='Motion was detected on camera in the garage. You should receive a video with the footage soon.')
    def send_recorded_video(self, movie_file_name):
        if self._mailer.send_gmail_with_attached_file(self._settings['TO_ADDRESS'],
                    subject='Motion Video Captured in Garage',
                    message='Motion was recorded on camera in the garage. The video is attached.',
                    file_name=args.movie):
            logging.info('Video file %s successfully sent. Deleting video file form disk' % movie_file_name)
            try:
                os.unlink(movie_file_name)
            except Exception as e:
                logging.error('Exception deleting video file %s: %s' % (movie_file_name, str(e)))
            return True
        else:
            return False

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
if args.detected:
    assert args.movie == None
    logging.info('Motion detected.')
    with TimedRunLock(os.path.split(sys.argv[0])[-1], 15) as lock:
        if lock.can_i_run():
            logging.info('Sending email')
            notification_sent = notifier.notify_motion_detected()
            lock.run_complete(notification_sent)
        else:
            logging.info("not sending email, because an email was sent within the last 15 seconds.")
else:
    assert not args.detected
    assert args.movie != None
    logging.info('Video file "%s" captured. Sending email' % args.movie)
    notifier.send_recorded_video(args.movie)
