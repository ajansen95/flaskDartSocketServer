import cv2 as cv


def manipulate(current_frame):
    # Der Parameter current frame ist der frame der aus "ret, frame = self.camera.read()" (OpenCV)
    manipulated_frame = cv.cvtColor(current_frame, cv.COLOR_BGR2GRAY)
    return manipulated_frame
