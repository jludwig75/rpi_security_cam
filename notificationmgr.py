from runlock import TimedRunLock
import logging

class NotificationManager:
    def __init__(self, mailer, notifier):
        self._mailer = mailer
        self._notifier = notifier
    def handle_motion_detected(self):
        logging.info('Motion detected.')
        with TimedRunLock(os.path.split(sys.argv[0])[-1], 15) as lock:
            if lock.can_i_run():
                logging.info('Sending email')
                notification_sent = notifier.notify_motion_detected()
                lock.run_complete(notification_sent)
            else:
                logging.info("not sending email, because an email was sent within the last 15 seconds.")
    def handle_movie_recorded(self, movie):
        logging.info('Video file "%s" captured. Sending email' % movie)
        notifier.send_recorded_video(movie)
    