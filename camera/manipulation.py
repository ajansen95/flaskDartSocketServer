import math

import cv2
import numpy as np

# Color ranges for the Masks in hsv color system
# green mask
lower_green = np.array([60, 50, 50])
upper_green = np.array([80, 255, 255])

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

object_detector = cv2.createBackgroundSubtractorMOG2(history=600, varThreshold=60, detectShadows=False)

coords = []
point_history = []
dart_thrown = False
counter = 0
current_point = None


# Returns current thrown point value
def get_current_point():
    global current_point
    point = current_point
    current_point = None
    return point


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
        if area > 100:
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


# Detect dart tip and return the coordinates of it
def dart_detection(contours):
    global dart_thrown
    global counter
    global coords
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:
            counter = 0
            dart_thrown = True
            for c in cnt:
                x, y = c[0]
                coords.append((x, y))


# Applies a circular Maks on the incoming image
def circular_mask(frame):
    mask = np.zeros((frame.shape[0], frame.shape[1], 1), dtype=np.uint8)
    cv2.circle(mask, (452, 452), 435, (255, 255, 255), -1, 8, 0)
    out = frame * mask
    white = 255 - mask
    stream = white - out
    return stream


# Calculates the Point value with a given Coordinate
def get_point_value(coord):
    cv2.waitKey(0)
    dst = math.dist(centre, coord)

    lineA = (centre, middle_up)
    lineB = (centre, coord)

    line1Y1 = lineA[0][1]
    line1X1 = lineA[0][0]
    line1Y2 = lineA[1][1]
    line1X2 = lineA[1][0]

    line2Y1 = lineB[0][1]
    line2X1 = lineB[0][0]
    line2Y2 = lineB[1][1]
    line2X2 = lineB[1][0]

    # calculate angle between pairs of lines
    angle1 = math.atan2(line1Y1 - line1Y2, line1X1 - line1X2)
    angle2 = math.atan2(line2Y1 - line2Y2, line2X1 - line2X2)
    angleDegrees = int((angle1 - angle2) * 360 / (2 * math.pi))

    points = 0
    multiplier = 0
    for d in distance:
        if dst > 340:
            print(str(multiplier) + " * " + str(points))
            return 0
        if dst <= d[1]:
            multiplier = d[2]
            if d[2] == 25 or d[2] == 50:
                print(str(multiplier) + " * " + str(points))
                return multiplier
            break

    for ang in angles:
        if angleDegrees >= ang[0]:
            if angleDegrees < ang[1]:
                points = ang[2]
                break

    print(str(multiplier) + " * " + str(points))
    return multiplier * points


# test functions
def calibration_points(frame):
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
        if area > 100:
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

    cv2.drawMarker(frame, (min(coords)[1], min(coords)[0]), (123, 255, 123), cv2.MARKER_CROSS, 20, 5)
    cv2.drawMarker(frame, max(coords2), (123, 255, 123), cv2.MARKER_CROSS, 20, 5)
    cv2.drawMarker(frame, (max(coords)[1], max(coords)[0]), (123, 255, 123), cv2.MARKER_CROSS, 20, 5)
    cv2.drawMarker(frame, min(coords2), (123, 255, 123), cv2.MARKER_CROSS, 20, 5)

    return frame


def get_mask(frame):
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(img_hsv, lower_green, upper_green)
    red_mask = cv2.inRange(img_hsv, lower_red1, upper_red1) + cv2.inRange(img_hsv, lower_red2, upper_red2)
    red_result = cv2.bitwise_and(frame, frame, mask=red_mask)
    green_result = cv2.bitwise_and(frame, frame, mask=green_mask)
    return red_result + green_result


# Manipulate the current Camera frame
def manipulate(current_frame, cam_to_board):
    global counter
    global dart_thrown
    global coords
    global point_history
    global current_point
    warp = cv2.warpPerspective(current_frame, cam_to_board, (906, 906))
    current_frame = circular_mask(warp)
    mask = object_detector.apply(current_frame)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    dart_detection(contours)
    if dart_thrown:
        counter += 1
        if int(counter) > 5:
            counter = 0
            dart_thrown = False
            print(min(coords))
            if min(coords) == (0, 0):
                coords = []
                return
            current_point = get_point_value(min(coords))
            point_history.append((min(coords)))
            coords = []

    if len(point_history) > 0:
        for c in point_history:
            x, y = c
            cv2.drawMarker(current_frame, (x, y), (125, 125, 255), cv2.MARKER_CROSS, 10, 5)
        if len(point_history) == 4:
            point_history = []

    return current_frame
