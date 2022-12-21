import math

import cv2
import numpy as np

# Color ranges for the Masks in hsv color system
# green mask
lower_green = np.array([65, 50, 50])
upper_green = np.array([95, 255, 255])

# lower red mask (0-10)
lower_red1 = np.array([0, 50, 50])
upper_red1 = np.array([10, 255, 255])

# upper red mask (165-180)
lower_red2 = np.array([165, 50, 50])
upper_red2 = np.array([180, 255, 255])

# mapped dartboard
centre = (452, 452)
middle_up = (452, 111)
angles = [(-9, 9, 20), (9, 27, 5), (27, 45, 12), (45, 63, 9), (63, 81, 14), (81, 99, 11), (99, 117, 8),
          (117, 135, 16),
          (135, 153, 7), (153, 171, 19), (171, 189, 3), (189, 207, 17), (207, 225, 2), (225, 243, 15),
          (243, 261, 10), (261, -81, 6), (-81, -63, 13), (-63, -45, 4), (-45, -27, 18), (-27, -9, 1)]

distance = [(0, 15, 50), (16, 31, 25), (32, 194, 1), (194, 215, 3), (216, 325, 1), (326, 340, 2)]

object_detector = cv2.createBackgroundSubtractorMOG2(history=0, varThreshold=0, detectShadows=False)


# Calibrate a given frame
def calibrate_dartboard(frame):
    board_points = [[453, 120], [785, 450], [453, 785], [120, 450]]
    cam_points = []
    # Put masks on the frame
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(img_hsv, lower_green, upper_green)
    red_mask = cv2.inRange(img_hsv, lower_red1, upper_red1) + cv2.inRange(img_hsv, lower_red2, upper_red2)

    contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    coords = []
    # Iterate through all contours and append the mid of each contour in an array
    # First for the contours of the red mask
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            coords.append((int(y + (h / 2)), int(x + (w / 2))))

    contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    coords2 = []
    # Iterate through the green mask
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            coords2.append((int(x + (w / 2)), int(y + (h / 2))))

    # add calibration Points to the array
    # 20, 6, 3, 11 in that order
    cam_points.append((min(coords)[1], min(coords)[0]))
    cam_points.append(max(coords2))
    cam_points.append((max(coords)[1], max(coords)[0]))
    cam_points.append(min(coords2))

    # Calibrate the Image via these two arrays
    board_points = np.array([board_points[0], board_points[1], board_points[2], board_points[3]], dtype=np.float32)
    cam_points = np.array([cam_points[0], cam_points[1], cam_points[2], cam_points[3]], dtype=np.float32)

    cam_to_board = cv2.getPerspectiveTransform(cam_points, board_points)
    return cam_to_board


def get_mask(frame):
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(img_hsv, lower_green, upper_green)
    red_mask = cv2.inRange(img_hsv, lower_red1, upper_red1) + cv2.inRange(img_hsv, lower_red2, upper_red2)
    red_result = cv2.bitwise_and(frame, frame, mask=red_mask)
    green_result = cv2.bitwise_and(frame, frame, mask=green_mask)
    return red_result + green_result


# Applies a circular Maks on the incoming image
def circular_mask(frame):
    mask = np.zeros((frame.shape[0], frame.shape[1], 1), dtype=np.uint8)
    cv2.circle(mask, (452, 452), 435, (255, 255, 255), -1, 8, 0)
    out = frame * mask
    white = 255 - mask
    stream = white - out
    return stream


def manipulate(current_frame, cam_to_board):
    warp = cv2.warpPerspective(current_frame, cam_to_board, (906, 906))
    mask = object_detector.apply(warp)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    current_frame = circular_mask(warp)
    return current_frame
