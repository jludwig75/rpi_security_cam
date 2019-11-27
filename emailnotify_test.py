#!/usr/bin/env python
import unittest
import logging
import os
import stat
import sys
from emailnotify import EmailNotifier
from dummymailer import DummyMailer


class testEmaliNotifier(unittest.TestCase):
    TEST_SETTINGS = {'TO_ADDRESS': 'nobody@nowhere.com'}
    def testEmailSentWhenMotionDetected(self):
        mailer = DummyMailer()
        self.assertEqual(0, len(mailer.messages))

        enotifier = EmailNotifier(testEmaliNotifier.TEST_SETTINGS, mailer)

        self.assertTrue(enotifier.notify_motion_detected())

        self.assertEqual(1, len(mailer.messages))
        self.assertEqual(testEmaliNotifier.TEST_SETTINGS['TO_ADDRESS'], mailer.messages[0]['to'])
        self.assertTrue('Motion Detected' in mailer.messages[0]['subject'])
        self.assertTrue('Motion was detected' in mailer.messages[0]['message'])
    
    def testnotify_motion_detectedReturnsFalseWhenEmailFailsToSend(self):
        mailer = DummyMailer(fail_sends = True)
        self.assertEqual(0, len(mailer.messages))

        enotifier = EmailNotifier(testEmaliNotifier.TEST_SETTINGS, mailer)

        self.assertFalse(enotifier.notify_motion_detected())
        self.assertEqual(0, len(mailer.messages))

    def testEmailSentWithVideoWhenRecordedVideoSent(self):
        mailer = DummyMailer()
        self.assertEqual(0, len(mailer.messages))

        TEST_FILE_NAME = 'delme.test'
        with open(TEST_FILE_NAME, 'wt') as file:
            file.write('Delete me, please.')
        self.assertTrue(os.path.exists(TEST_FILE_NAME))

        enotifier = EmailNotifier(testEmaliNotifier.TEST_SETTINGS, mailer)

        self.assertTrue(enotifier.send_recorded_video(TEST_FILE_NAME))

        self.assertFalse(os.path.exists(TEST_FILE_NAME))
        self.assertEqual(1, len(mailer.messages))
        self.assertEqual(testEmaliNotifier.TEST_SETTINGS['TO_ADDRESS'], mailer.messages[0]['to'])
        self.assertTrue('Motion Video Captured' in mailer.messages[0]['subject'])
        self.assertTrue('Motion was recorded on camera' in mailer.messages[0]['message'])
        self.assertEqual(TEST_FILE_NAME, mailer.messages[0]['file_name'])

    def testsend_recorded_videoReturnsFalseWhenEmailFailsToSendAndFileNotDeleted(self):
        mailer = DummyMailer(fail_sends=True)
        self.assertEqual(0, len(mailer.messages))

        TEST_FILE_NAME = 'delme.test'
        with open(TEST_FILE_NAME, 'wt') as file:
            file.write('Delete me, please.')
        self.assertTrue(os.path.exists(TEST_FILE_NAME))

        enotifier = EmailNotifier(testEmaliNotifier.TEST_SETTINGS, mailer)

        self.assertFalse(enotifier.send_recorded_video(TEST_FILE_NAME))

        self.assertEqual(0, len(mailer.messages))
        # make sure the file was not deleted.
        self.assertTrue(os.path.exists(TEST_FILE_NAME))
        os.unlink(TEST_FILE_NAME)

    def testsend_recorded_videoReturnsFalseAndEmailIsSentWhenFileCannotBeDelete(self):
        mailer = DummyMailer()
        self.assertEqual(0, len(mailer.messages))

        # Make sure the test file does not exist.
        # This is not the ideal way to test this. Ideally we would like the file,
        # but I cannot get this to work.
        TEST_FILE_NAME = 'delme.test'
        if os.path.exists(TEST_FILE_NAME):
            os.unlink(TEST_FILE_NAME)
        self.assertFalse(os.path.exists(TEST_FILE_NAME))

        enotifier = EmailNotifier(testEmaliNotifier.TEST_SETTINGS, mailer)

        self.assertFalse(enotifier.send_recorded_video(TEST_FILE_NAME))

        self.assertEqual(1, len(mailer.messages))
        self.assertEqual(testEmaliNotifier.TEST_SETTINGS['TO_ADDRESS'], mailer.messages[0]['to'])
        self.assertTrue('Motion Video Captured' in mailer.messages[0]['subject'])
        self.assertTrue('Motion was recorded on camera' in mailer.messages[0]['message'])
        self.assertEqual(TEST_FILE_NAME, mailer.messages[0]['file_name'])

if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    unittest.main()    