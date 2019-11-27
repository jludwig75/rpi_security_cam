#!/usr/bin/env python
import unittest
import logging
from testsmtpd import SSLSMTPServer, TestCredentialValidator
import os
import secure_smtpd

class RpiSecurityCamTest(unittest.TestCase):
    _smtp_server = None
    def _cleanup_file(self, file_name):
        if os.path.exists(file_name):
            os.unlink(file_name)

    def setUp(self):
        os.system('cp mail_settings.test.json mail_settings.json')
        self._cleanup_file('/var/lock/sendemail.py.time')
        messages = self._smtp_server.pop_messages()

    def tearDown(self):
        self._cleanup_file('/var/lock/sendemail.py.time')

    def testMotionDetectedSendsEmail(self):
        # test
        os.system('./sendemail.py -d')

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
        os.system('./sendemail.py -m %s' % TEST_ATTACHMENT_FILE_NAME)

        # test validation
        messages = self._smtp_server.pop_messages()
        self.assertEqual(1, len(messages))
        self.assertTrue('Subject: Motion Video Captured' in messages[0])
        self.assertTrue('Motion was recorded on' in messages[0])
        self.assertTrue('Content-Disposition: attachment' in messages[0])
        self.assertTrue('filename="test.mkv"' in messages[0])

        # make sure the file was deleted
        self.assertFalse(os.path.exists(TEST_ATTACHMENT_FILE_NAME))

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
