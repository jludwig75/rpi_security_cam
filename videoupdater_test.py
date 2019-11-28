#!/usr/bin/env python
import unittest
import logging
import os
from datetime import datetime, timedelta

from videoupdater import VideoUpdater
from dummyemailnotify import DummyEmailNotifier


class VideoUpdaterTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists('test_file*.mkv'):
            os.system('rm test_file*.mkv')

    def tearDown(self):
        if os.path.exists('test_file*.mkv'):
            os.system('rm test_file*.mkv')

    def testOlderVideosUploaded(self):
        # setup
        notifier = DummyEmailNotifier()
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
        self.assertEqual(0, len(notifier.notications))

        # test
        video_updater = VideoUpdater(notifier)
        video_updater.catch_up_videos('.')

        # make sure the notifications were sent
        self.assertEqual(FILES_TO_SEND, len(notifier.notications))


if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    unittest.main()
