import unittest
import psutil

class TestRunningStatus(unittest.TestCase):

    # Checks if the application is open and running.
    def test_app_running(self):
        running = False
        processCMDLine = ['c:/Users/jakes/Programs/sheep-behaviour/venv/Scripts/python.exe', 'c:/Users/jakes/Programs/sheep-behaviour/main.py']
        for process in psutil.process_iter(attrs=['cmdline']):
            if process.info['cmdline'] == processCMDLine:
                running = True
                break
        
        self.assertTrue(running, 'Application not running as expected')

if __name__ == "__main__":
    unittest.main()