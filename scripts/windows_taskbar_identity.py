"""Restore taskbar identity for unpackaged launches of the Store Codex executable."""
from pathlib import Path
import psutil,win32gui,win32process
from win32com.propsys import propsys,pscon

def repair_debug_taskbar():
    targets={}
    for p in psutil.process_iter(['name','exe','cmdline']):
        try:
            exe=Path(p.info['exe'] or '')
            args=p.info['cmdline'] or []
            if (p.info['name'] or '').lower()!='chatgpt.exe':continue
            if not any(a.startswith('--remote-debugging-port=') for a in args):continue
            if any(a.startswith('--type=') for a in args):continue
            package=exe.parent.parent.name
            if not package.startswith('OpenAI.Codex_'):continue
            family='OpenAI.Codex_'+package.rsplit('_',1)[-1]
            targets[p.pid]=(family+'!App',exe.parent/'resources/chatgpt-app-dark.ico')
        except (psutil.Error,OSError):continue
    repaired=[]
    def visit(hwnd,_):
        _,pid=win32process.GetWindowThreadProcessId(hwnd)
        if pid not in targets or not win32gui.IsWindowVisible(hwnd):return
        appid,icon=targets[pid]
        store=propsys.SHGetPropertyStoreForWindow(hwnd)
        if store.GetValue(pscon.PKEY_AppUserModel_ID).GetValue()==appid:return
        if icon.is_file():
            store.SetValue(pscon.PKEY_AppUserModel_RelaunchIconResource,propsys.PROPVARIANTType(str(icon)))
        store.SetValue(pscon.PKEY_AppUserModel_ID,propsys.PROPVARIANTType(appid))
        store.Commit()
        repaired.append(hwnd)
    win32gui.EnumWindows(visit,None)
    return repaired
if __name__=='__main__':print(repair_debug_taskbar())
