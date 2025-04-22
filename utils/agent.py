from utils.func import *

import time


class Agent:
    def __init__(self):
        self.board_info = "." * (19 * 19)

    def get_board_info(self, screenshot) -> tuple[bool, str]:
        clipped_img = get_board_clipped_img(screenshot)
        cur_board_info = get_board_info(clipped_img)
        if self.board_info == cur_board_info:
            return False, cur_board_info
        return True, cur_board_info

    def get_new_move(self, cur_board_info: str) -> tuple[int, int]:
        old_board_list = list(self.board_info)
        new_board_list = list(cur_board_info)
        for i in range(len(old_board_list)):
            if old_board_list[i] == "." and new_board_list[i] != ".":
                self.board_info = cur_board_info
                return i // 19, i % 19
        return -1, -1

    def run(self):
        if is_fox_go_in_foreground():
            screenshot = get_screenshot()
            if board_detected(screenshot):
                # print("Board detected!")
                is_board_changed, cur_board_info = self.get_board_info(screenshot)
                if is_board_changed:
                    x, y = self.get_new_move(cur_board_info)
                    if x < 0 or y < 0:
                        return
                    print(f"new move: {chr(ord('A') + x)}, {y + 1}")
                else:
                    print("board not changed")
            else:
                print("foxwq.exe is running but no board detected.")
        else:
            print("foxwq.exe is not running.")
        time.sleep(0.5)


if __name__ == '__main__':
    agent = Agent()
    while True:
        agent.run()
