<p align="center"><b><ins> Camera Pose Estimation </ins></b></p>

<br>

---

<br>

<b><u>Usage</u></b>

```
Undistort Images:

python undistort_imgs.py --path /path_to_/assets/calibration_images/high_resolution
```

```
Render Cube on Chessboard corner:

python pose.py --path ./corrected --calib-params ./calibration_params
```

![](../assets/camera_pose_output.png)

<br>

---

<br>

- We already have the camera matrix and the distortion coefficients.
- Given a pattern image, we can use the above information to calculate the pose, orientation, rotation,displacement, etc.

<br>

- For a planar object, we assume $Z = 0$, such that, the problem becomes how the camera is placed in space to see the image.
- In effect, if we know how the object lies in space, we can overlay 2D diagrams on it to simulate a 3D effect.

<br>

- This problem is approached by first finding the chessboard's first corner, and drawing a 3D coordinate axis on top of it such that the Z-axis is perpendicular to the chess board plane.

