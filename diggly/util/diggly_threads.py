import threading

class FuncThread(threading.Thread):
    def __init__(self, thread_id, target, *args):
        self.thread_id = thread_id
        self._target = target
        self._args = args
        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)