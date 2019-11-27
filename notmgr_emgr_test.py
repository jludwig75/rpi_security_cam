#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.abspath('test_overrides/'))

import unittest
import logging

from emailnotify import EmailNotifier
from notificationmgr import NotificationManager
from dummymailer import DummyMailer

from runlock import allow_run


class NotificationManagerEmailNotifierIntegrationTest(unittest.TestCase):
    TEST_SETTINGS = {'TO_ADDRESS': 'nobody@nowhere.com'}

    def testHandleVideoRecordedRequestsSendEmail(self):
        allow_run(True)
        mailer = DummyMailer()
        enotifier = EmailNotifier(NotificationManagerEmailNotifierIntegrationTest.TEST_SETTINGS, mailer)
        notmgr = NotificationManager(enotifier)
        self.assertEqual(0, len(mailer.messages))

        TEST_FILE_NAME = 'test.mkv'

        notmgr.handle_movie_recorded(TEST_FILE_NAME)

        self.assertEqual(1, len(mailer.messages))
        self.assertEqual(NotificationManagerEmailNotifierIntegrationTest.TEST_SETTINGS['TO_ADDRESS'], mailer.messages[0]['to'])
        self.assertTrue('Motion Video Captured' in mailer.messages[0]['subject'])
        self.assertTrue('Motion was recorded on camera' in mailer.messages[0]['message'])
        self.assertEqual(TEST_FILE_NAME, mailer.messages[0]['file_name'])

    def testHandleMotionDetectedRequestSendEmail(self):
        allow_run(True)
        mailer = DummyMailer()
        enotifier = EmailNotifier(NotificationManagerEmailNotifierIntegrationTest.TEST_SETTINGS, mailer)
        notmgr = NotificationManager(enotifier)
        self.assertEqual(0, len(mailer.messages))

        notmgr.handle_motion_detected()

        self.assertEqual(1, len(mailer.messages))
        self.assertEqual(NotificationManagerEmailNotifierIntegrationTest.TEST_SETTINGS['TO_ADDRESS'], mailer.messages[0]['to'])
        self.assertTrue('Motion Detected' in mailer.messages[0]['subject'])
        self.assertTrue('Motion was detected' in mailer.messages[0]['message'])

    def testHandleMotionDetectedDoesNotRequestSendEmailWhenRunlockDoesNotAllow(self):
        allow_run(False)
        mailer = DummyMailer()
        enotifier = EmailNotifier(NotificationManagerEmailNotifierIntegrationTest.TEST_SETTINGS, mailer)
        notmgr = NotificationManager(enotifier)
        self.assertEqual(0, len(mailer.messages))

        notmgr.handle_motion_detected()

        self.assertEqual(0, len(mailer.messages))

if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    unittest.main()    
