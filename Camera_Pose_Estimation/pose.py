import cv2
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt

from typing import List
from numpy import ndarray


def load_calib_params(path: str):
    ret = np.load(f"./{path}/ret.npy")
    mat = np.load(f"./{path}/mat.npy")
    dist = np.load(f"./{path}/dist.npy")
    rvecs = np.load(f"./{path}/rvecs.npy")
    tvecs = np.load(f"./{path}/tvecs.npy")

    return ret, mat, dist, rvecs, tvecs


def draw_axes(img: ndarray, corners: List, imgpts: List):
    imgpts = np.int32(imgpts).reshape(-1, 2)
    corner = tuple(np.int32(corners)[0].ravel())

    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 10)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 10)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 10)

    return img


def draw(img: ndarray, imgpts: List):
    imgpts = np.int32(imgpts).reshape(-1, 2)

    img = cv2.drawContours(img, [imgpts[:4]], -1, (0, 255, 0), 3)
    img = cv2.drawContours(img, [imgpts[4:]], -1, (0, 0, 255), 3)

    for i, j in zip(range(4), range(4, 8)):
        img = cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]), (255), 3)

    return img


def render_cube(args):
    ret, mat, dist, _, _ = load_calib_params(args.calib_params)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objp = np.zeros((7 * 7, 3), np.float32)
    objp[:, :2] = np.mgrid[0: 7, 0: 7].T.reshape(-1, 2)

    # 8 corners of the cube
    axisBoxes = np.float32([[0, 0, 0], [0, 3, 0], [3, 3, 0], [3, 0, 0], [
                           0, 0, -3], [0, 3, -3], [3, 3, -3], [3, 0, -3]])

    imgs = sorted(glob.glob(f"{args.path}/*.jpg"))

    for image in imgs:
        img = cv2.imread(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (7, 7), None)

        if ret:
            corners2 = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), criteria)

            _, rvecs, tvecs = cv2.solvePnP(objp, corners2, mat, dist)

            imgpts, _ = cv2.projectPoints(axisBoxes, rvecs, tvecs, mat, dist)

            img = draw(img, imgpts)
            # cv2.imshow('img',img)
            plt.imshow(img)
            plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--path", type=str, required=True)
    parser.add_argument(
        "--calib-params",
        type=str,
        default="./calibration_params")

    args = parser.parse_args()

    render_cube(args)
