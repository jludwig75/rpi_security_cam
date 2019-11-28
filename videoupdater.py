import os
import time
import logging
from datetime import datetime

class VideoUpdater:
    def __init__(self, notifier):
        self._notifier = notifier
    def catch_up_videos(self, video_dir):
        logging.info('Catching up videos in "%s"' % video_dir)
        now = time.time()
        for file_name in os.listdir(video_dir):
            if file_name.endswith('.mkv'):
                file_name = os.path.join(video_dir, file_name)
                mtime = os.path.getmtime(file_name)
                if mtime < now - 5 * 60:
                    logging.info('file "%s" is older than 5 minutes. Sending video.')
                    self._notifier.send_recorded_video(file_name, event_time=datetime.fromtimestamp(mtime))
                else:
                    logging.info('file "%s" is newer than 5 minutes. Not sending video now.')
