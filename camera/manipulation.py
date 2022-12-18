import cv2
import numpy as np

object_detector = cv2.createBackgroundSubtractorMOG2(history=0, varThreshold=0, detectShadows=False)


def manipulate(current_frame):
    # "Perfect" Dartboard used for Calibration
    board_height, board_width = 906, 906

    # Distort the incoming Video
    board_points = [[453, 120], [785, 450], [453, 785], [120, 450]]  # Fixed Points, DO NOT CHANGE

    cam_points = [[400, 200], [600, 400], [400, 600], [200, 400]]  # Dummy Points

    board_points = np.array([board_points[0], board_points[1], board_points[2], board_points[3]], dtype=np.float32)
    cam_points = np.array([cam_points[0], cam_points[1], cam_points[2], cam_points[3]], dtype=np.float32)

    cam_to_board = cv2.getPerspectiveTransform(cam_points, board_points)
    warp = cv2.warpPerspective(current_frame, cam_to_board, (board_width, board_height))

    # Crop out everything outside og the Dartboard
    mask = np.zeros((board_width, board_height, 1), dtype=np.uint8)
    # (452, 452) is the centre, 425 is the radius
    cv2.circle(mask, (452, 452), 425, (255, 255, 255), -1, 8, 0)
    out = warp * mask
    return mask - out
