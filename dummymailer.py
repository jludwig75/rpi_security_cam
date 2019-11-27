class DummyMailer:
    def __init__(self, fail_sends = False):
        self.messages = []
        self._fail_sends = fail_sends
    def send_mail(self, to_address, subject, message):
        if self._fail_sends:
            return False
        self.messages.append({'to': to_address, 'subject' : subject, 'message': message})
        return True
    def send_mail_with_attached_file(self, to_address, subject, message, file_name):
        if self._fail_sends:
            return False
        self.messages.append({'to': to_address, 'subject' : subject, 'message': message, 'file_name': file_name})
        return True
