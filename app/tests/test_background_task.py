from threading import Event, get_ident
import unittest
from app.shared.background_task import BackgroundTask, check_cancelled, CancelledError


class Scheduler:
    def __init__(self):self.jobs={};self.next_id=0
    def after(self, delay, callback):
        self.next_id+=1;self.jobs[self.next_id]=callback;return self.next_id
    def after_cancel(self, token):self.jobs.pop(token,None)
    def run(self):
        jobs,self.jobs=self.jobs,{}
        for callback in jobs.values():callback()


class BackgroundTaskTests(unittest.TestCase):
    def test_closing_screen_during_progress_suppresses_completion(self):
        owner=Scheduler();values=[]
        def work(cancelled,progress):progress(1,1);return 'finished'
        task=BackgroundTask(owner,work,values.append,values.append,lambda *args:task.close()).start()
        task.thread.join(2);owner.run()
        self.assertEqual(values,[])
        self.assertTrue(task.closed)
        self.assertEqual(owner.jobs,{})
    def test_worker_is_separate_but_completion_uses_polling_thread(self):
        owner=Scheduler();threads=[];values=[]
        def work(event, progress):
            threads.append(get_ident());progress(1,2);return 42
        task=BackgroundTask(owner,work,lambda value:values.append((get_ident(),value)),self.fail).start()
        task.thread.join(2);self.assertFalse(task.thread.is_alive())
        self.assertEqual(values,[])
        owner.run()
        self.assertNotEqual(threads[0],get_ident())
        self.assertEqual(values,[(get_ident(),42)])

    def test_closed_owner_receives_no_completion_callback(self):
        owner=Scheduler();event=Event();values=[]
        def work(cancelled,progress):event.wait(1);check_cancelled(cancelled)
        task=BackgroundTask(owner,work,values.append,values.append).start()
        task.close();event.set();task.thread.join(2);owner.run()
        self.assertEqual(values,[])
        self.assertEqual(owner.jobs,{})

    def test_errors_are_delivered_without_worker_tracebacks(self):
        owner=Scheduler();errors=[]
        def work(*args):raise ValueError('failure')
        task=BackgroundTask(owner,work,self.fail,errors.append).start()
        task.thread.join(2);owner.run()
        self.assertIsInstance(errors[0],ValueError)
        self.assertIsNone(errors[0].__traceback__)
