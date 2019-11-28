from runlock import TimedRunLock
import logging
import os
import sys

class NotificationManager:
    def __init__(self, notifier, run_local=False):
        self._notifier = notifier
        self._run_local = run_local
    def handle_motion_detected(self):
        logging.info('Motion detected.')
        with TimedRunLock(os.path.split(sys.argv[0])[-1], 15, use_local_dir=self._run_local) as lock:
            if lock.can_i_run():
                logging.info('Sending email')
                notification_sent = self._notifier.notify_motion_detected()
                lock.run_complete(notification_sent)
            else:
                logging.info("not sending email, because an email was already sent within the last 15 seconds.")
    def handle_movie_recorded(self, movie):
        logging.info('Video file "%s" captured. Sending email' % movie)
        self._notifier.send_recorded_video(movie)
    
