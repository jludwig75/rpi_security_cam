import os
import logging

class EmailNotifier:
    def __init__(self, settings, mailer):
        self._settings = settings
        self._mailer = mailer
    def notify_motion_detected(self):
        return self._mailer.send_mail(self._settings['TO_ADDRESS'],
                    subject='Motion Detected in Garage',
                    message='Motion was detected on camera in the garage. You should receive a video with the footage soon.')
    def send_recorded_video(self, movie_file_name):
        if self._mailer.send_mail_with_attached_file(self._settings['TO_ADDRESS'],
                    subject='Motion Video Captured in Garage',
                    message='Motion was recorded on camera in the garage. The video is attached.',
                    file_name=movie_file_name):
            logging.info('Video file %s successfully sent. Deleting video file form disk' % movie_file_name)
            try:
                os.unlink(movie_file_name)
                return True
            except Exception as e:
                logging.error('Exception deleting video file %s: %s' % (movie_file_name, str(e)))
        return False
