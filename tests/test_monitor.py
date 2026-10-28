import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from weekly_monitor_windows import weekly_window
from cdp_client import select_target,CDPError
class MonitorTests(unittest.TestCase):
    def window(self):return {'usedPercent':42,'windowDurationMins':10080,'resetsAt':2000000000}
    def test_primary_and_secondary(self):
        for name in ['primary','secondary']:
            r=weekly_window({'rateLimitsByLimitId':{'codex':{name:self.window()}}})
            self.assertEqual(r,{'usedPercent':42,'resetsAt':2000000000})
    def test_other_pool_and_missing(self):
        self.assertIsNone(weekly_window({'rateLimits':{'limitId':'spark','primary':self.window()}}))
        self.assertIsNone(weekly_window({}))
        self.assertIsNone(weekly_window({'rateLimits':{'primary':{'windowDurationMins':300}}}))
    def test_legacy(self):
        self.assertEqual(weekly_window({'rateLimits':{'secondary':self.window()}})['usedPercent'],42)
    def test_target_excludes_web_and_prefers_main(self):
        targets=[{'type':'page','url':'https://chatgpt.com','title':'ChatGPT','webSocketDebuggerUrl':'ws://127.0.0.1/web'},
          {'type':'page','url':'app://-/index.html?initialRoute=avatar-overlay','title':'ChatGPT','webSocketDebuggerUrl':'ws://127.0.0.1/overlay'},
          {'type':'page','url':'app://-/index.html','title':'ChatGPT','webSocketDebuggerUrl':'ws://127.0.0.1/main'}]
        self.assertEqual(select_target(targets)['webSocketDebuggerUrl'],'ws://127.0.0.1/main')
        with self.assertRaises(CDPError):select_target(targets[:1])
if __name__=='__main__':unittest.main()
