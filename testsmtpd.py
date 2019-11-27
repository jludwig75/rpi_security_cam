import logging
import threading
import os
import smtpd, ssl
import sys
sys.path.append('./secure-smtpd')
from secure_smtpd import SMTPServer, FakeCredentialValidator, LOG_NAME

class TestCredentialValidator(object):
    
    def validate(self, username, password):
        if username == 'bcoe' and password == 'foobar':
            return True
        return False

class SSLSMTPServer(SMTPServer, threading.Thread):
    def __init__(self, localaddr, remoteaddr, ssl=False, certfile=None, keyfile=None, ssl_version=ssl.PROTOCOL_SSLv23, require_authentication=False, credential_validator=None, maximum_execution_time=30, process_count=5):
        SMTPServer.__init__(self,
                                    localaddr,
                                    remoteaddr,
                                    ssl=ssl,
                                    certfile=certfile,
                                    keyfile=keyfile,
                                    ssl_version=ssl_version,
                                    require_authentication=require_authentication,
                                    credential_validator=credential_validator,
                                    maximum_execution_time=maximum_execution_time,
                                    process_count=process_count)
        threading.Thread.__init__(self)
        self._message_file_name = 'dummy.msg'
        self._lock = threading.Lock()
        with open(self._message_file_name, 'wt') as msg_file:
            msg_file.truncate(0)
    def process_message(self, peer, mailfrom, rcpttos, message_data):
        self._lock.acquire()
        message_text = message_data.split('\n\n')[-1]
        with open(self._message_file_name, 'at') as msg_file:
            msg_file.write(message_text + '\n')
        self._lock.release()
    def pop_messages(self):
        self._lock.acquire()
        if os.path.exists(self._message_file_name):
            with open(self._message_file_name, 'rt') as msg_file:
                messages = msg_file.readlines()
            with open(self._message_file_name, 'wt') as msg_file:
                msg_file.truncate(0)
        else:
            messages = []
        self._lock.release()
        return messages
    def thread_func(self):
        self.run()

if __name__ == '__main__':
    logger = logging.getLogger( LOG_NAME )
    logger.setLevel(logging.INFO)

    server = SSLSMTPServer(
        ('0.0.0.0', 1025),
        None,
        require_authentication=True,
        ssl=True,
        certfile='server.crt',
        keyfile='server.key',
        credential_validator=FakeCredentialValidator(),
        maximum_execution_time = 1.0
        )

    server.run()
