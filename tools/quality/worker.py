"""Instrument existing unittest suites without changing their sources."""
import argparse
import io
import os
from pathlib import Path
import sys
import time
import traceback
import unittest
import weakref


def guard(production, shadow, output):
    production,shadow,output=(Path(p).resolve() for p in (production,shadow,output))
    def check(path):
        if path is None or isinstance(path,int):return
        path=Path(os.fsdecode(path)).resolve()
        if path.is_relative_to(shadow) or (path.is_relative_to(production) and not path.is_relative_to(output)):
            raise AssertionError('Quality isolation blocked a write to protected project files.')
    def audit(event,args):
        if event=='open':
            path,mode,flags=args
            if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):check(path)
        elif event in ('os.remove','os.rmdir','os.mkdir','os.chmod','os.truncate'):check(args[0])
        elif event in ('os.rename','os.link'):check(args[0]);check(args[1])
        elif event=='os.symlink':check(args[1])
        elif event in ('socket.connect','socket.bind','subprocess.Popen','os.system','os.startfile','os.startfile/2'):
            raise AssertionError('Quality isolation blocked real network/process activity.')
    sys.addaudithook(audit)


class Result(unittest.TextTestResult):
    def __init__(self,*args,output,**kwargs):
        super().__init__(*args,**kwargs)
        self.records=[];self.current=None;self.roots=[];self.output=Path(output)

    def startTest(self,test):
        super().startTest(test)
        self.current={'id':test.id(),'status':'passed','gui':False,'duration':0,'details':[],'screenshots':[]}
        self.started=time.perf_counter()

    def _problem(self,test,status,error=None,reason=None):
        record=self.current
        if record is None:
            record={'id':str(test),'status':status,'gui':False,'duration':0,'details':[],'screenshots':[],'fixture':True}
            self.records.append(record)
        record['status']=status
        if reason:record['details'].append(reason)
        if error:
            from tools.quality.common import redact
            record['details'].append(redact(''.join(traceback.format_exception(*error))))
        if status=='failed' and record['gui'] and not record['screenshots']:
            self.screenshot(record)

    def screenshot(self,record):
        # PrintWindow captures only our HWND; never take a desktop screenshot.
        try:
            import inspect
            import ctypes
            from PIL import ImageGrab
            if os.name!='nt' or 'window' not in inspect.signature(ImageGrab.grab).parameters:
                raise RuntimeError('Own-window capture is unavailable.')
            root=next(ref() for ref in reversed(self.roots) if ref() is not None and ref().winfo_exists())
            hwnd=ctypes.windll.user32.GetParent(root.winfo_id()) or root.winfo_id()
            filename='failure-'+str(len(list(self.output.glob('failure-*.png')))+1)+'.png'
            ImageGrab.grab(window=hwnd).save(self.output/filename)
            record['screenshots'].append(filename)
        except Exception as error:
            record['screenshot_unavailable']=type(error).__name__

    def addFailure(self,test,error):
        super().addFailure(test,error);self._problem(test,'failed',error)

    def addError(self,test,error):
        super().addError(test,error);self._problem(test,'failed',error)

    def addSubTest(self,test,subtest,error):
        super().addSubTest(test,subtest,error)
        if error:self._problem(test,'failed',error,reason=str(subtest))

    def addSkip(self,test,reason):
        super().addSkip(test,reason);self._problem(test,'skipped',reason=reason)

    def addExpectedFailure(self,test,error):
        super().addExpectedFailure(test,error);self._problem(test,'expected_failure',error)

    def addUnexpectedSuccess(self,test):
        super().addUnexpectedSuccess(test);self._problem(test,'failed',reason='Unexpected success: review obsolete expectedFailure annotation.')

    def stopTest(self,test):
        self.current['duration']=time.perf_counter()-self.started
        self.current['metrics']=getattr(test,'quality_metrics',{})
        self.records.append(self.current);self.current=None
        super().stopTest(test)


def benchmark():
    from statistics import median
    import tempfile
    from unittest.mock import patch
    import pandas as pd
    from app.repositories.vocabulary import read_words
    from app.vocabulary.editor_data import filter_vocabulary
    from app.statistics.data import training_statistics
    from app.statistics.cache import StatisticsCache
    from app.shared.integrity import audit
    from app.tests.test_preferences_data import sample_preferences
    def measured(callback,repeats=5):
        values=[]
        for _ in range(repeats):
            start=time.perf_counter();callback();values.append((time.perf_counter()-start)*1000)
        return median(values)
    with tempfile.TemporaryDirectory() as directory:
        directory=Path(directory);size=10000
        frame=pd.DataFrame({'ID':list(range(size)),'English':['word '+str(i) for i in range(size)],
            'Czech':['slovo']*size,'Audio':['No audio']*size,'Description':['']*size,'Example':['']*size,
            'Repetition':['SFS']*size,'Next repetition':['']*size})
        path=directory/'Czech_English_voc.csv';frame.to_csv(path,sep=';',index=False)
        sample_preferences().to_csv(directory/'settings.csv',sep=';',index=False)
        questions=directory/'English_gra.csv'
        pd.DataFrame({'question_id':[str(i) for i in range(size)],'category':['Topic '+str(i%30) for i in range(size)],
            'prompt':['Choose']*size,'anchor':['A sentence']*size,'option_1':['yes']*size,'option_2':['no']*size,
            'option_3':['other']*size,'option_4':['none']*size,'R':['SFS']*size}).to_csv(questions,sep=';',index=False)
        result={'load_10000_ms':measured(lambda:read_words(path)),
            'search_10000_ms':measured(lambda:filter_vocabulary(frame,'English','contains','word 5')),
            'integrity_quick_10000_ms':measured(lambda:audit(directory,quick=True))}
        assert len(read_words(path))==size and len(filter_vocabulary(frame,'English','contains','word 5'))>0
        with patch('app.statistics.data.cache',StatisticsCache()):
            start=time.perf_counter();stats=training_statistics(questions,'grammar')
            result['statistics_cold_10000_ms']=(time.perf_counter()-start)*1000
            assert stats['summary'][0]==size
            result['statistics_cached_10000_ms']=measured(lambda:training_statistics(questions,'grammar'))
        result['records']=size
        return result


def main():
    parser=argparse.ArgumentParser()
    for name in ('root','production','output','tool-site'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--module');parser.add_argument('--coverage',action='store_true');parser.add_argument('--benchmark',action='store_true')
    args=parser.parse_args();shadow=Path(args.root).resolve();output=Path(args.output).resolve()
    sys.path.insert(0,str(shadow));sys.path.append(args.tool_site)
    os.chdir(shadow)
    output.mkdir(parents=True,exist_ok=True)
    from tools.quality.common import write_json
    coverage=None
    if args.coverage:
        from coverage import Coverage
        coverage=Coverage(data_file=str(output/'coverage'),source=[str(shadow)],
            omit=['*/app/tests/*','*/tools/*'],branch=True,config_file=False)
        coverage.start()
    guard(args.production,shadow,output.parents[1])
    from app.tests.safety import isolated_services
    with isolated_services():
        if args.benchmark:
            report={'performance':benchmark(),'status':'passed'}
        else:
            import customtkinter as cst
            original=cst.CTk.__init__
            holder={}
            def init(root,*a,**kw):
                result=holder.get('result')
                if result and result.current:result.current['gui']=True
                original(root,*a,**kw)
                if result:result.roots.append(weakref.ref(root))
            from unittest.mock import patch
            stream=io.StringIO()
            class Runner(unittest.TextTestRunner):
                def _makeResult(self):
                    result=Result(self.stream,self.descriptions,self.verbosity,output=output)
                    holder['result']=result;return result
            with patch.object(cst.CTk,'__init__',init):
                suite=unittest.defaultTestLoader.loadTestsFromName(args.module)
                result=Runner(stream=stream,verbosity=1).run(suite)
            print(stream.getvalue(),flush=True)
            report={'module':args.module,'records':result.records,'tests':result.testsRun,
                'status':'passed' if result.wasSuccessful() else 'failed',
                'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}
    if coverage:coverage.stop();coverage.save()
    write_json(output/'result.json',report)
    return 0 if report['status']=='passed' else 1


if __name__=='__main__':
    raise SystemExit(main())
