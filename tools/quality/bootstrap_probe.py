"""Fault-injection check: Windows WMI unavailable, real version fallback cached."""
import argparse
from pathlib import Path
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tools.quality.run import shadow_project,environment,command
from tools.quality.common import atomic,write_json


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--python',required=True);parser.add_argument('--tool-site',required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[2]
    sys.path.append(args.tool_site)
    output=root/'reports/quality/verification/platform-bootstrap'
    output.mkdir(parents=True,exist_ok=True);env=environment(output)
    results=[]
    with tempfile.TemporaryDirectory(prefix='vocabpro-bootstrap-probe-') as directory:
        shadow=Path(directory);shadow_project(root,shadow)
        setup=command([args.python,'-X','utf8','-B',shadow/'tools/quality/fixtures.py','--root',shadow],shadow,env,60)
        if setup['returncode']:raise RuntimeError('Probe fixture preparation failed.')
        for module in ('app.tests.test_grammar_progress','app.tests.test_stats_difficult_words'):
            destination=output/'diagnostics'/module;destination.mkdir(parents=True,exist_ok=True)
            # This patch only simulates unavailable WMI. The standard library's
            # fallback queries the actual OS before the worker enables guards.
            script=('import platform,runpy\nfrom unittest.mock import patch\n'
                'platform._uname_cache=None\n'
                'with patch.object(platform,"_wmi_query",side_effect=OSError("WMI unavailable in bootstrap probe")):\n'
                f'    runpy.run_path({str(shadow/"tools/quality/worker.py")!r},run_name="__main__")\n')
            value=command([args.python,'-X','utf8','-B','-c',script,'--root',shadow,'--production',root,
                '--output',destination,'--tool-site',args.tool_site,'--coverage','--module',module],shadow,env,180)
            atomic(destination/'console.txt',value['stdout']+'\n'+value['stderr'])
            results.append({'module':module,'passed':value['returncode']==0,'probe':'WMI unavailable, actual OS fallback',
                'diagnostic':str(destination/'console.txt')})
            print(module+': '+str(value['returncode']==0),flush=True)
    write_json(output/'probe.json',results)
    return 0 if all(value['passed'] for value in results) else 1


if __name__=='__main__':raise SystemExit(main())
