import psutil

def check_app_running():
    running = False
    processCMDLine = ['c:/Users/jakes/Programs/sheep-behaviour/venv/Scripts/python.exe', 'c:/Users/jakes/Programs/sheep-behaviour/main.py']

    for process in psutil.process_iter(attrs=['cmdline']):
        if process.info['cmdline'] == processCMDLine:
            running = True
            break

    if running:
        print("All tests passed - Application is open and running")
        return True
    else:
        print(f"Tests failed - Application not running as expected")
        return False

check_app_running()