# CLAUDE.md — Project Guidelines

## Update Documentation Convention

Each significant change must be documented as follows:

1. **One-sentence summary** added to `docs/updates.md` with a date and reference to a detail file.
2. **Detail file** at `docs/<topic>.md` with full explanation — architecture decisions, gotchas, commands used, and rationale.
3. If a new change is closely related to an existing topic, **edit the existing files** rather than creating new ones.

## Key Facts

- Package: `wheelchair_navigation` at `src/wheelchair_navigation/`
- ROS 2 Jazzy, Gazebo Harmonic (Gz Sim 16), native Linux
- Gazebo spawns from **SDF** (not URDF) — `ros_gz_sim create -string` strips sensor plugins
- SDF regeneration command: `gz sdf -p wheelchair.urdf 2>/dev/null | sed "s/<sdf version='1.12'>/<sdf version='1.11'>/" > wheelchair.sdf`
- World file must include `gz-sim-sensors-system` with `ogre2` render engine or cameras produce no data
- Build: `colcon build --packages-select wheelchair_navigation --symlink-install`
- Source: `source /opt/ros/jazzy/setup.sh && source install/setup.sh`
