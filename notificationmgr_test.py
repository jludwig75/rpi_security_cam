#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.abspath('test_overrides/'))

import unittest
import logging

from notificationmgr import NotificationManager
from runlock import allow_run, get_run_completed, get_run_success
from dummyemailnotify import DummyEmailNotifier


class NotificationManagerTest(unittest.TestCase):
    def testNotificationSentWhenMotionDetected(self):
        notifier = DummyEmailNotifier()
        notmgr = NotificationManager(notifier)
        self.assertEqual(0, len(notifier.notications))
        
        allow_run(True)
        notmgr.handle_motion_detected()

        self.assertEqual(1, len(notifier.notications))
        self.assertTrue(get_run_completed())
        self.assertTrue(get_run_success())

    def testNotificationNotSentWhenRunLockDenies(self):
        notifier = DummyEmailNotifier()
        notmgr = NotificationManager(notifier)
        self.assertEqual(0, len(notifier.notications))
        
        allow_run(False)
        notmgr.handle_motion_detected()

        self.assertEqual(0, len(notifier.notications))
        self.assertTrue(not get_run_completed())

    def testRunCompleteButNotSuccessfulWhenNotificationFails(self):
        notifier = DummyEmailNotifier(fail_notifications=True)
        notmgr = NotificationManager(notifier)
        self.assertEqual(0, len(notifier.notications))
        
        allow_run(True)
        notmgr.handle_motion_detected()

        self.assertEqual(0, len(notifier.notications))
        self.assertTrue(get_run_completed())
        self.assertTrue(not get_run_success())

    def testNotifierIsNotifiedAboutVideoRecorded(self):
        notifier = DummyEmailNotifier()
        notmgr = NotificationManager(notifier)
        self.assertEqual(0, len(notifier.notications))

        TEST_FILE_NAME = 'dummy.mvk'
        notmgr.handle_movie_recorded(TEST_FILE_NAME)

        self.assertEqual(1, len(notifier.notications))
        self.assertEqual(TEST_FILE_NAME, notifier.notications[0]['file_name'])

if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    unittest.main()