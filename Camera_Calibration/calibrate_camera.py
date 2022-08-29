import os
import cv2
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt

from typing import Dict
from numpy import ndarray
from tqdm import tqdm



class CalibrateCamera(object):
    def __init__(self, args):
        self.path = args.path
        self.res = args.res
        self.vis = args.vis
        self.save_params = args.save_params
        self.save_vis = args.save_vis

        if self.res == "low":
            self.frame_size = (640, 480)
        elif self.res == "high":
            self.frame_size = (1920, 1080)

        self.board_size = args.board_size
        
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        self.object_points = np.zeros((self.board_size[0] * self.board_size[1], 3), np.float32)
        self.object_points[:, :2] = np.mgrid[0: self.board_size[0], 0: self.board_size[1]].T.reshape(-1, 2)

        self.object_pts = []
        self.image_pts = []

        self.images = glob.glob(f"{self.path}/*.jpg")

        self.counter = 0
    
        self.board_corner_imgs = []

    
    def format_images(self, image: ndarray) -> ndarray:
        img = cv2.imread(image)
        resized_img = cv2.resize(img, self.frame_size, interpolation = cv2.INTER_AREA)

        gray = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

        return resized_img, gray
    

    def calibrate(self) -> Dict:
        for image in tqdm(self.images, desc = "calibrating..."):
            img, gray = self.format_images(image)

            ret, corners = cv2.findChessboardCorners(image = gray, 
                                                     patternSize = self.board_size, 
                                                     corners = None
                                                     )
    
            if ret:
                self.object_pts.append(self.object_points)
                corners2 = cv2.cornerSubPix(image = gray,
                                            corners = corners,
                                            winSize = (5, 5),
                                            zeroZone = (-1, -1),
                                            criteria = self.criteria
                                            )
                
                self.image_pts.append(corners2)

                if self.vis:
                    self.board_corner_imgs.append(cv2.drawChessboardCorners(image = img, 
                                                                            patternSize = self.board_size, 
                                                                            corners = corners2,
                                                                            patternWasFound = ret))

            self.counter += 1
        
        ret, mat, dist, rvecs, tvecs = cv2.calibrateCamera(objectPoints = self.object_pts,
                                                           imagePoints = self.image_pts,
                                                           imageSize = gray.shape[::-1],
                                                           cameraMatrix = None,
                                                           distCoeffs = None)
        
        calibration_parameters = {"ret": ret,
                                  "mat": mat,
                                  "dist": dist,
                                  "rvecs": rvecs,
                                  "tvecs": tvecs
                                  }

        if self.save_params:
            os.makedirs("./calibration_params", exist_ok = True)
        
            np.save("./calibration_params/ret", ret)
            np.save("./calibration_params/mat", mat)
            np.save("./calibration_params/dist", dist)
            np.save("./calibration_params/rvecs", rvecs)
            np.save("./calibration_params/tvecs", tvecs)

        return calibration_parameters
    

    def visualize(self, limit: int = 9) -> None:
        assert int(int(limit) // int(np.sqrt(limit))) == int(np.sqrt(limit))
        assert len(self.board_corner_imgs) != 0, "Please generate calibration parameters first 'CalibrateCamera.calibrate'"

        r = c = int(np.sqrt(limit))

        plt.figure(figsize = (15, 15))

        for i in range(len(self.images[:limit])):
            plt.subplot(r, c, i+1)
            plt.imshow(self.board_corner_imgs[i])

            if self.save_vis:
                plt.savefig("corners.png")

        plt.show()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--path", type = str, required = True, help = "Path to board images")
    parser.add_argument("--res", type = str, choices = ["low", "high"], required = True, help = "Resolution of the camera (640x480) or (1920x1080)")
    parser.add_argument("--vis", action = "store_true", help = "Visualize the detected board corners")
    parser.add_argument("--save-params", action = "store_true", help = "Save the calibration parameters")
    parser.add_argument("--save-vis", action = "store_true", help = "Save the visualization")
    
    parser.add_argument("--board-size", nargs = "+", type = int, default = [7, 7], help = "Board size")

    args = parser.parse_args()

    calib = CalibrateCamera(args)
    calib.calibrate()

    if args.vis:
        calib.visualize()