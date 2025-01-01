import cv2
import numpy as np
import pyautogui


class ScreenProcess:
    def __init__(self):
        self.screen_image = self.capture_screen()
        self.grey_image = self.get_grey_image(self.screen_image)
        self.thresh_image = self.get_thresh_image(self.grey_image)

    def refresh(self):
        self.screen_image = self.capture_screen()
        self.grey_image = self.get_grey_image(self.screen_image)
        self.thresh_image = self.get_thresh_image(self.grey_image)

    @staticmethod
    def capture_screen():
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    @staticmethod
    def get_grey_image(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def get_thresh_image(grey_image):
        _, thresh_image = cv2.threshold(grey_image, 0, 255,
                                        cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh_image

    def get_board(self) -> bool:
        contours, _ = cv2.findContours(self.thresh_image,
                                       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        squares = []

        # 遍历轮廓
        for contour in contours:
            # 近似轮廓
            approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
            # 检查轮廓是否为四边形
            if len(approx) == 4:
                # 计算轮廓的面积
                area = cv2.contourArea(approx)
                if area > 10000:  # 过滤掉面积较小的轮廓
                    # 计算轮廓的周长
                    perimeter = cv2.arcLength(approx, True)
                    # 使用等周长公式计算正方形的比例（正方形的对角线长度与边长的比例约为sqrt(2)）
                    ratio = perimeter / (4 * np.sqrt(area))
                    # 如果比例接近1，则认为是正方形
                    if 0.999 < ratio < 1.001:
                        squares.append(approx)

        board_found = True if len(squares) > 0 else False

        if board_found:
            for square in squares:
                cv2.drawContours(self.screen_image, [square],
                                 0, (0, 255, 0), 2)

            # 显示结果
            cv2.imshow('Detected Squares', self.screen_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return board_found
