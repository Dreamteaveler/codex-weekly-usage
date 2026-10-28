from pathlib import Path
root=Path(__file__).resolve().parent
(root/'weekly-monitor.stop').write_text('stop',encoding='utf-8')
