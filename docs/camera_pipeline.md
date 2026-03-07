# Depth Camera Pipeline

## Phase 1 — Single depth camera replacing lidar

**Problem:** Lidar (`gpu_lidar`) replaced with depth camera for richer sensing.

**URDF changes:**
- `lidar_link` → `camera_link` (box geometry)
- `lidar_joint` → `camera_joint` at xyz="0.30 0 0.20" (relative to base_link; +0.20 from base_link z-offset = 0.40m world height)
- Sensor: `depth_camera`, 640×480, 15 Hz, clip 0.3–10.0m, topic `depth_camera/image`

**Key gotcha — SDF version mismatch:**
`gz sdf -p` emits SDF 1.12 but Gazebo Sim 16 on Jazzy errors with "Unable to convert from SDF version 1.12 to 1.11". Fix: pipe through `sed` to patch the version header. Also, warnings go to stdout and corrupt the file unless stderr is redirected: `gz sdf -p wheelchair.urdf 2>/dev/null | sed "s/<sdf version='1.12'>/<sdf version='1.11'>/" > wheelchair.sdf`

**Key gotcha — sensor plugins stripped:**
`ros_gz_sim create -string <urdf>` strips Gazebo sensor plugins. Must spawn with `-file wheelchair.sdf` instead.

**depthimage_to_laserscan:**
Converts depth image to `/scan` for downstream Nav2. Package: `ros-jazzy-depthimage-to-laserscan`.

---

## Phase 2 — 6-camera PointCloud2 + Nav2

**Camera layout (all joints relative to base_link, z=0.20 → 0.40m world height):**

| Name | xyz | rpy |
|------|-----|-----|
| camera_front_link | 0.30 0 0.20 | 0 0 0 |
| camera_front_right_link | 0.15 -0.32 0.20 | 0 0 -1.05 |
| camera_front_left_link | 0.15 0.32 0.20 | 0 0 1.05 |
| camera_back_link | -0.30 0 0.20 | 0 0 3.14159 |
| camera_back_right_link | -0.15 -0.32 0.20 | 0 0 -2.09 |
| camera_back_left_link | -0.15 0.32 0.20 | 0 0 2.09 |

**depth_image_proc:** `point_cloud_xyz_node` converts each camera's depth image → `/camera_<name>/points` (PointCloud2). Package: `ros-jazzy-depth-image-proc`.

**EKF odometry:** `robot_localization` `ekf_node` reads `/odom` (from Gazebo diff-drive) and publishes the real `odom → base_footprint` TF, replacing the static transform hack. Config: `config/ekf.yaml`.

**Nav2:** Launched via `nav2_bringup navigation_launch.py` with `config/nav2_params.yaml`. Uses VoxelLayer with all 6 camera point clouds as observation sources. No map server — global frame is `odom`. Package: `ros-jazzy-navigation2 ros-jazzy-nav2-bringup`.

**Installed packages:**
```
sudo apt install ros-jazzy-depth-image-proc ros-jazzy-robot-localization \
                 ros-jazzy-navigation2 ros-jazzy-nav2-bringup
```

**Files changed:**
- `urdf/wheelchair.urdf` — 6 camera links/joints/sensors
- `urdf/wheelchair.sdf` — regenerated
- `config/ekf.yaml` — EKF parameters
- `config/nav2_params.yaml` — Nav2 costmap + planner + controller params
- `launch/wheelchair_sim.launch.py` — full pipeline launch
- `setup.py` — added config/*.yaml to data_files
- `CLAUDE.md` + `docs/` — project documentation convention

**RViz setup for Nav2:**
1. Fixed Frame: `odom`
2. Add → Map → Topic: `/local_costmap/costmap` or `/global_costmap/costmap`
3. Add → Path → Topic: `/plan`
4. Use "2D Goal Pose" tool to send navigation goals
