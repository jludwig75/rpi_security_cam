class DummyEmailNotifier:
    def __init__(self, fail_notifications = False):
        self.notications = []
        self._fail_notifications = fail_notifications
    def notify_motion_detected(self):
        if self._fail_notifications:
            return False
        self.notications.append({})
        return True
    def send_recorded_video(self, movie_file_name, event_time):
        if self._fail_notifications:
            return False
        self.notications.append({'file_name': movie_file_name})
        return True
