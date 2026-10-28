"""Windows trial: Codex Monitor CDP transport + account-wide weekly allowance."""
from pathlib import Path
import argparse,json,queue,subprocess,threading,time,sys
from cdp_client import CDPClient, devtools_targets, select_target
from windows_taskbar_identity import repair_debug_taskbar
ROOT=Path(__file__).resolve().parent.parent
STOP=ROOT/'weekly-monitor.stop'
STATUS=ROOT/'weekly-monitor-status.json'
JS=(ROOT/'scripts/weekly_statusbar.js').read_text(encoding='utf-8')
def weekly_window(result):
    limits=result.get('rateLimitsByLimitId') or {}
    limit=limits.get('codex') or result.get('rateLimits') or {}
    if limit.get('limitId') not in (None,'codex'): return None
    for name in ('primary','secondary'):
        v=limit.get(name)
        if v and v.get('windowDurationMins')==10080:
            if isinstance(v.get('usedPercent'),(int,float)) and isinstance(v.get('resetsAt'),(int,float)):
                return {k:v[k] for k in ('usedPercent','resetsAt')}
    return None
class Account:
    def __init__(self,exe):
        self.p=subprocess.Popen([exe,'app-server'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        self.q=queue.Queue();self.id=0
        threading.Thread(target=self.read,daemon=True).start()
        self.call('initialize',{'clientInfo':{'name':'codex_weekly_monitor','version':'0.1.0'}})
        self.send({'method':'initialized'})
    def read(self):
        for line in self.p.stdout:
            try:self.q.put(json.loads(line))
            except ValueError:pass
    def send(self,v):
        self.p.stdin.write(json.dumps(v)+'\n');self.p.stdin.flush()
    def call(self,method,params):
        self.id+=1; self.send({'id':self.id,'method':method,'params':params})
        end=time.monotonic()+20
        while time.monotonic()<end:
            v=self.q.get(timeout=max(.1,end-time.monotonic()))
            if v.get('id')==self.id:
                if 'error' in v:raise RuntimeError('account request failed')
                return v.get('result',{})
        raise TimeoutError()
    def close(self):
        self.p.terminate()
        try:self.p.wait(timeout=3)
        except subprocess.TimeoutExpired:self.p.kill()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--codex',required=True);ap.add_argument('--port',type=int,default=9222);ap.add_argument('--once',action='store_true');a=ap.parse_args()
    account=None; payload={}; due=0; misses=0
    try:
        while not STOP.exists():
            try:target=select_target(devtools_targets(a.port))
            except Exception:
                misses+=1
                if misses>=5:break
                time.sleep(2);continue
            misses=0
            try:repair_debug_taskbar()
            except Exception:pass
            if time.monotonic()>=due:
                try:
                    if account is None:account=Account(a.codex)
                    result=account.call('account/rateLimits/read',{})
                    payload={'weekly':weekly_window(result),'updatedAt':time.time()}
                except Exception as e:
                    payload['error']=type(e).__name__
                    if account:account.close();account=None
                due=time.monotonic()+30
            client=None
            try:
                client=CDPClient(target['webSocketDebuggerUrl'])
                try:
                    result=client.evaluate('('+JS+')('+json.dumps(payload)+')')
                    STATUS.write_text(json.dumps({'checkedAt':time.time(),'payload':payload,'ui':result},ensure_ascii=False,indent=2),encoding='utf-8')
                finally:client.close()
            except (OSError, RuntimeError, ValueError) as exc:
                if a.once:raise
                print("CDP reconnect: "+str(exc),file=sys.stderr,flush=True)
            if a.once:break
            time.sleep(3)
    finally:
        if account:account.close()
        if STOP.exists():
            try:
                c=CDPClient(select_target(devtools_targets(a.port))['webSocketDebuggerUrl'])
                c.evaluate("clearInterval(window.__codexWeeklyMonitor?.timer);delete window.__codexWeeklyMonitor;document.querySelectorAll('[data-codex-weekly-monitor]').forEach(e=>e.remove())");c.close()
            except Exception:pass
if __name__=='__main__':main()
