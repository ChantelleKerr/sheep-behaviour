import unittest
import psutil
import platform

system = platform.system()

class TestRunningStatus(unittest.TestCase):

    # Checks if the application is open and running.
    def test_app_running(self):
        running = False
        processDevCMDLine = "sheep-behaviour/main.py"
        processAppCMDLine = ""
        if system == "Darwin":
            processAppCMDLine = "App/Mac/main.exe"
        elif system == "Windows":
            processAppCMDLine = "App/Windows/main.exe"
        
        for process in psutil.process_iter(attrs=['name', 'cmdline']):
            CMDInfo = process.info['cmdline']
            
            if CMDInfo is not None and len(CMDInfo) > 0:
                if system == "Darwin":
                    if process.info['name'] == "main.exe" and ('/'.join(CMDInfo[0].rsplit("/", 3)[1:])) == processAppCMDLine:
                        running = True
                        break
                    elif ('/'.join(CMDInfo[-1].rsplit("/", 2)[1:])) == processDevCMDLine:
                        running = True
                        break
                elif system == "Windows":
                    if process.info['name'] == "main.exe" and ('/'.join(CMDInfo[0].rsplit("\\", 3)[1:])) == processAppCMDLine:
                        running = True
                        break
                    elif ('/'.join(CMDInfo[-1].rsplit("/", 2)[1:])) == processDevCMDLine:
                        running = True
                        break
                    
        
        self.assertTrue(running, 'Application not running as expected')

if __name__ == "__main__":
    unittest.main()