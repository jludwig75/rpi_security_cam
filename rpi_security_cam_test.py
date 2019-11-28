#!/usr/bin/env python
import unittest
import logging
from testsmtpd import SSLSMTPServer, TestCredentialValidator
import os
import secure_smtpd
from datetime import datetime, timedelta

class RpiSecurityCamTest(unittest.TestCase):
    _smtp_server = None
    def _cleanup_file(self, file_name):
        if os.path.exists(file_name):
            os.unlink(file_name)

    def setUp(self):
        os.system('cp mail_settings.test.json mail_settings.json')
        os.system('cp settings.template.json settings.json')
        self._cleanup_file('sendemail.py.time')
        if os.path.exists('test_file*.mkv'):
            os.system('rm test_file*.mkv')
        messages = self._smtp_server.pop_messages()

    def tearDown(self):
        self._cleanup_file('sendemail.py.time')
        if os.path.exists('test_file*.mkv'):
            os.system('rm test_file*.mkv')

    def testMotionDetectedSendsEmail(self):
        # test
        os.system('./sendemail.py -q -d')

        # test validation
        messages = self._smtp_server.pop_messages()
        self.assertEqual(1, len(messages))
        self.assertTrue('Motion was detected on' in messages[0])

    def testMotionRecordedSendsEmail(self):
        # setup
        TEST_ATTACHMENT_FILE_NAME = 'test.mkv'
        with open(TEST_ATTACHMENT_FILE_NAME, 'wt') as file:
            file.write('This is a test file\n')
        self.assertTrue(os.path.exists(TEST_ATTACHMENT_FILE_NAME))

        # test
        os.system('./sendemail.py -q -m %s' % TEST_ATTACHMENT_FILE_NAME)

        # test validation
        messages = self._smtp_server.pop_messages()
        self.assertEqual(1, len(messages))
        self.assertTrue('Subject: Motion Video Captured' in messages[0])
        self.assertTrue('Motion was recorded on' in messages[0])
        self.assertTrue('Content-Disposition: attachment' in messages[0])
        self.assertTrue('filename="test.mkv"' in messages[0])

        # make sure the file was deleted
        self.assertFalse(os.path.exists(TEST_ATTACHMENT_FILE_NAME))
    
    def testCatchupOldMovies(self):
        NUM_TEST_FILES = 10
        FILES_TO_SEND = 8
        # create some movie files with old dates
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        for i in range(NUM_TEST_FILES):
            file_name = 'test_file%u.mkv' % i
            file_time = ((five_minutes_ago - timedelta(minutes=i)) - datetime.fromtimestamp(0)).total_seconds()
            with open(file_name, 'wt') as file:
                file.write('This is test file %u.\n' % i)
            if i < FILES_TO_SEND:
                os.utime(file_name, (file_time, file_time))

        # Run catch up
        os.system('./sendemail.py -q -c .')

        # Make sure an email was received for each file
        messages = self._smtp_server.pop_messages()
        self.assertEqual(FILES_TO_SEND, len(messages))
        for message in messages:
            self.assertTrue('Subject: Motion Video Captured' in message)

        # Make sure the test files older than 5 minutes were deleted
        for i in range(NUM_TEST_FILES):
            file_name = 'test_file%u.mkv' % i
            if i < FILES_TO_SEND:
                self.assertFalse(os.path.exists(file_name))
            else:
                self.assertTrue(os.path.exists(file_name))


if __name__ == '__main__':
    logger = logging.getLogger( secure_smtpd.LOG_NAME )
    logger.setLevel(logging.CRITICAL)
    logging.basicConfig(level=logging.CRITICAL)

    RpiSecurityCamTest._smtp_server = SSLSMTPServer(
                                                    ('0.0.0.0', 1025),
                                                    None,
                                                    require_authentication=True,
                                                    ssl=True,
                                                    certfile='server.crt',
                                                    keyfile='server.key',
                                                    credential_validator=TestCredentialValidator(),
                                                    maximum_execution_time = 1.0
                                                )
    RpiSecurityCamTest._smtp_server.start()

    unittest.main()    
