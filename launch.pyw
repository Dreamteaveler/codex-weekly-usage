from pathlib import Path
import subprocess,sys,time,urllib.request,json,psutil,ctypes
root=Path(__file__).resolve().parent
def show(s):ctypes.windll.user32.MessageBoxW(0,s,'Codex 周用量',0)
def ready_cdp():
    try:
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open('http://127.0.0.1:9222/json',timeout=2) as r: targets=json.load(r)
        return any(t.get('url','').startswith('app://') and t.get('type')=='page' for t in targets)
    except Exception:return False

def installed_app():
    import winreg
    base=r'Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\Repository\Packages'
    candidates=[]
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,base) as k:
        for i in range(winreg.QueryInfoKey(k)[0]):
            name=winreg.EnumKey(k,i)
            if not name.startswith('OpenAI.Codex_'):continue
            with winreg.OpenKey(k,name) as q:
                folder=winreg.QueryValueEx(q,'PackageRootFolder')[0]
            exe=Path(folder)/'app/ChatGPT.exe'
            if exe.is_file():candidates.append((tuple(int(v) for v in name.split('_')[1].split('.')),exe))
    if not candidates:raise RuntimeError('未找到已安装的 Codex。')
    return str(max(candidates)[1])

def main():
    try:
        existing=[p for p in psutil.process_iter(['cmdline']) if any(str(root/'scripts/weekly_monitor_windows.py').lower()==str(a).lower() for a in (p.info['cmdline'] or []))]
        if existing and ready_cdp():
            import win32gui,win32process,win32con
            ids={x.pid for x in psutil.process_iter(['name','cmdline']) if (x.info['name'] or '').lower()=='chatgpt.exe' and any(a.startswith('--remote-debugging-port=') for a in (x.info['cmdline'] or []))}
            def focus(h,_):
                if win32gui.IsWindowVisible(h) and win32process.GetWindowThreadProcessId(h)[1] in ids:
                    win32gui.ShowWindow(h,win32con.SW_RESTORE)
                    try:win32gui.SetForegroundWindow(h)
                    except Exception:pass
            win32gui.EnumWindows(focus,None)
            sys.exit(0)
        stop=root/'weekly-monitor.stop'
        if stop.exists():stop.unlink()
        ready=ready_cdp
        if not ready():
            apps=[installed_app()]
            subprocess.Popen([apps[0],'--remote-debugging-address=127.0.0.1','--remote-debugging-port=9222'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            for _ in range(45):
                if ready():break
                time.sleep(1)
            else:raise RuntimeError('CDP 端口未就绪；没有修改客户端安装文件。')
        bins=list((Path.home()/'AppData/Local/OpenAI/Codex/bin').glob('*/codex.exe'))
        if not bins:raise RuntimeError('未找到 Codex app-server。')
        exe=max(bins,key=lambda p:p.stat().st_mtime)
        pythonw=Path(sys.executable).with_name('pythonw.exe')
        with (root/'weekly-monitor.log').open('a',encoding='utf-8') as log:
            subprocess.Popen([str(pythonw),str(root/'scripts/weekly_monitor_windows.py'),'--codex',str(exe)],cwd=root,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:show(str(e))

if __name__=='__main__':main()
