from utils import *


while True:
    if is_fox_go_in_foreground():
        screenshot = get_screenshot()
        if board_detected(screenshot):
            print("Board detected!")
            clipped_img = get_board_clipped_img(screenshot)
            identify_stones(clipped_img)
        else:
            print("foxwq.exe is running but no board detected.")
    else:
        print("foxwq.exe is not running.")
    time.sleep(1)

