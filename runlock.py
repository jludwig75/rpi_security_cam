from lockfile import LockFile
import logging
import time

class RunLock:
    def __init__(self, process_name):
        self._process_name = process_name
        self._lock_file_name = '/var/lock/%s.lock' % self._process_name
        self._lock = LockFile(self._lock_file_name, 'w')
    def __enter__(self):
        self._lock != None
        logging.debug('RunLock.__enter__')
        self._lock.acquire()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._lock != None
        logging.debug('RunLock.__eixt__')
        self._lock.release()

class TimedRunLock(RunLock):
    def __init__(self, process_name, min_run_interval):
        RunLock.__init__(self, process_name)
        self._process_name = process_name
        self._time_file_name = '/var/lock/%s.time' % self._process_name
        self._min_run_interval = min_run_interval
    def store_time(self, t = None):
        if t == None:
            t = int(time.time())
        logging.debug("storing time to %s" % self._time_file_name)
        with open(self._time_file_name, 'w') as tf:
            tf.write(str(t))
    def get_time(self):
        logging.debug("getting time from %s" % self._time_file_name)
        with open(self._time_file_name, 'r') as tf:
            data = tf.read()
        if len(data) == 0:
            return 0
        return int(data)
    def check_can_run(self):
        if not os.path.exists(self._time_file_name):
            logging.debug("time file %s does not exist, creating" % self._time_file_name)
            self.store_time()
            logging.debug('can run')
            return True
        if time.time() - self.get_time() > self._min_run_interval:
            logging.debug('can run')
            return True
        logging.debug('cannot run')
        return False
    def can_i_run(self):
        return self.check_can_run()
    def run_complete(self, run_success):
        logging.debug('marking run complete')
        if run_success:
            self.store_time()
