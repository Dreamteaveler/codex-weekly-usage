"""Create a new desktop shortcut using locally installed Codex artwork."""
from pathlib import Path
import sys,subprocess,shutil,runpy
import win32com.client
root=Path(__file__).resolve().parent
if __name__=='__main__':
    launcher=runpy.run_path(str(root/'launch.pyw'),run_name='shortcut_helper')
    app=Path(launcher['installed_app']())
    shell=win32com.client.Dispatch('WScript.Shell')
    path=Path(shell.SpecialFolders('Desktop'))/'Codex Weekly Usage.lnk'
    if path.exists():raise SystemExit('Shortcut already exists; not overwritten.')
    assets=root/'assets';assets.mkdir(exist_ok=True)
    icon=assets/'codex.ico'
    shutil.copy2(app.parent/'resources/chatgpt-app-dark.ico',icon)
    link=shell.CreateShortcut(str(path))
    link.TargetPath=str(Path(sys.executable).with_name('pythonw.exe'))
    link.Arguments=subprocess.list2cmdline([str(root/'launch.pyw')])
    link.WorkingDirectory=str(root)
    link.IconLocation=str(icon)+',0'
    link.Description='Codex weekly allowance footer'
    link.Save()
    print(path)
