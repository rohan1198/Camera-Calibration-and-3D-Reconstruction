import os
import cv2
import glob
import argparse
import numpy as np


def save_calibrated_images(args) -> None:
    ret = np.load("./calibration_params/ret.npy")
    mat = np.load("./calibration_params/mat.npy")
    dist = np.load("./calibration_params/dist.npy")
    rvecs = np.load("./calibration_params/rvecs.npy")
    tvecs = np.load("./calibration_params/tvecs.npy")

    os.makedirs("./corrected/", exist_ok=True)

    imgs = glob.glob(f"{args.path}/*.jpg")

    for i in imgs:
        img = cv2.imread(i)
        h, w = img.shape[:2]

        new_camera_mat, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix=mat,
                                                            distCoeffs=dist,
                                                            imageSize=(w, h),
                                                            alpha=1,
                                                            newImgSize=(w, h)
                                                            )

        dst = cv2.undistort(img, mat, dist, None, new_camera_mat)

        x, y, w, h = roi
        dst = dst[y: y + h, x: x + w]

        w, h = img.shape[:2]

        resized_img = cv2.resize(dst, (h, w), interpolation=cv2.INTER_AREA)

        cv2.imwrite(f"./corrected/{os.path.basename(i)}", resized_img)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to the image")
    parser.add_argument(
        "--params",
        type=str,
        default="calibration_params",
        help="Path to the calibration parameters")

    args = parser.parse_args()

    calibrated_img = save_calibrated_images(args)
