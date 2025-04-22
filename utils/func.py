import psutil
import win32gui
import win32process
import cv2
import cv2
import numpy as np
from PIL import ImageGrab


def is_fox_go_in_foreground():
    foreground_window = win32gui.GetForegroundWindow()
    _, foreground_pid = win32process.GetWindowThreadProcessId(foreground_window)

    try:
        process = psutil.Process(foreground_pid)
        if process.name().lower() == "foxwq.exe":
            return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

    return False


def show_pic(pic_array, window_name):
    resized_display = cv2.resize(pic_array, None,
                                 fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    cv2.imshow(window_name, resized_display)
    cv2.waitKey(0)


def get_screenshot():
    screenshot = ImageGrab.grab()
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    return screenshot_cv


def board_detected(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            if 0.99 <= aspect_ratio <= 1.01 and cv2.contourArea(cnt) > 250000:
                return True
    return False


def get_board_clipped_img(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    max_x = -1
    max_y = -1
    max_w = -1
    max_h = -1

    for cnt in contours:
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            if 0.99 <= aspect_ratio <= 1.01 and cv2.contourArea(cnt) > 100:
                if w * h > max_area:
                    max_area = w * h
                    max_x = x
                    max_y = y
                    max_w = w
                    max_h = h
    clipped_img = img[max_y:max_y + max_h, max_x:max_x + max_w]
    return clipped_img


def identify_stones(clipped_image):
    height, width = clipped_image.shape[:2]

    x_start = int(width / 2)
    y_start = int(height / 2)
    width_delta = int(width * 0.95 / 18)
    height_delta = int(height * 0.95 / 18)

    half_width_delta = int(width_delta / 2)
    half_height_delta = int(height_delta / 2)

    board_unvisited = [[True for _ in range(19)] for _ in range(19)]

    for i in range(19):
        for j in range(19):
            x = x_start + (i - 9) * width_delta
            y = y_start + (j - 9) * height_delta
            cv2.rectangle(clipped_image,
                          (x - half_width_delta, y - half_height_delta),
                          (x + half_width_delta, y + half_height_delta),
                          (0, 0, 255), 2)
            local_img = clipped_image[y - half_height_delta: y + half_height_delta,
                        x - half_width_delta: x + half_width_delta]

            gray = cv2.cvtColor(local_img, cv2.COLOR_BGR2GRAY)
            _, binary_white = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)
            _, binary_black = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
            local_height, local_width = binary_white.shape[:2]

            for iter_i in range(local_width):
                for iter_j in range(local_height):
                    if binary_white[iter_i, iter_j] == 255:
                        cv2.circle(clipped_image,
                                   (x, y), 5, (0, 255, 0), -1)
                        board_unvisited[i][j] = False
            for iter_i in range(local_width):
                for iter_j in range(local_height):
                    if binary_black[iter_i, iter_j] == 0:
                        if board_unvisited[i][j]:
                            cv2.circle(clipped_image,
                                       (x, y), 5, (255, 255, 255), -1)
                            board_unvisited[i][j] = False

    show_pic(clipped_image, "identified_board")
    cv2.destroyAllWindows()


def get_board_info(clipped_image):
    height, width = clipped_image.shape[:2]

    x_start = int(width / 2)
    y_start = int(height / 2)
    width_delta = int(width * 0.95 / 18)
    height_delta = int(height * 0.95 / 18)

    half_width_delta = int(width_delta / 2)
    half_height_delta = int(height_delta / 2)

    board_unvisited = [[True for _ in range(19)] for _ in range(19)]
    board_info = "." * (19 * 19)
    board_info_list = list(board_info)

    for i in range(19):
        for j in range(19):
            x = x_start + (i - 9) * width_delta
            y = y_start + (j - 9) * height_delta
            cv2.rectangle(clipped_image,
                          (x - half_width_delta, y - half_height_delta),
                          (x + half_width_delta, y + half_height_delta),
                          (0, 0, 255), 2)
            local_img = clipped_image[y - half_height_delta: y + half_height_delta,
                        x - half_width_delta: x + half_width_delta]

            gray = cv2.cvtColor(local_img, cv2.COLOR_BGR2GRAY)
            _, binary_white = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY)
            _, binary_black = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

            local_height, local_width = binary_white.shape[:2]

            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            sign = False

            for cnt in contours:
                epsilon = 0.02 * cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, epsilon, True)

                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = w / float(h)
                    if 0.99 <= aspect_ratio <= 1.01:
                        sign = True
                        break
            if sign:
                continue

            for iter_i in range(local_width):
                for iter_j in range(local_height):
                    if binary_white[iter_i, iter_j] == 255:
                        # cv2.circle(clipped_image,
                        #            (x, y), 5, (0, 255, 0), -1)
                        board_info_list[i * 19 + j] = "O"
                        board_unvisited[i][j] = False
            for iter_i in range(local_width):
                for iter_j in range(local_height):
                    if binary_black[iter_i, iter_j] == 0:
                        if board_unvisited[i][j]:
                            # cv2.circle(clipped_image,
                            #            (x, y), 5, (255, 255, 255), -1)
                            board_info_list[i * 19 + j] = "X"
                            board_unvisited[i][j] = False

    real_board_info = "".join(board_info_list)
    return real_board_info
