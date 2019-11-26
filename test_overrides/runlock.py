allow_run = True
run_completed = False
run_success = None

def allow_run(allow):
    global allow_run
    allow_run = allow

def get_run_completed():
    return run_completed

def get_run_success():
    return run_success

class TimedRunLock:
    def __init__(self, process_name, min_run_interval):
        global run_completed
        global run_success
        run_completed = False
        run_success = None
    def __exit__(self, exception_type, exception_value, traceback):
        pass
    def __enter__(self):
        return self
    def can_i_run(self):
        global allow_run
        return allow_run
    def run_complete(self, run_result):
        global run_completed
        global run_success
        run_completed = True
        run_success = run_result
