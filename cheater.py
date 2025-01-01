import psutil
import time

from screen_process import ScreenProcess


class Cheater:
    def __init__(self):
        self.progress_name: str = "foxwq.exe"
        self.screen_process = ScreenProcess()

    def is_progress_running(self) -> bool:
        for proc in psutil.process_iter(['name']):
            try:
                if self.progress_name.lower() in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def run(self):
        while True:
            try:
                if self.is_progress_running():
                    print(f"{self.progress_name} is running.")
                    self.cheat()
                    break
                else:
                    print(f"{self.progress_name} is not running.")
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Exiting...")
                break

    def cheat(self):
        self.screen_process.refresh()
        while not self.screen_process.get_board():
            self.screen_process.refresh()
            time.sleep(0.1)

