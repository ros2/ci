# Contributing changes to Windows CI

ROS 2 Windows CI uses [pixi](https://pixi.sh/latest/) to manage dependencies in a pixi.toml file, one per ROS distribution.
These pixi.toml files are stored in a centralized repository at https://github.com/ros2/ros2 on the branches that correspond to the ROS distribution.
They are stored separately from this repository so they can be referenced both by this CI, as well as the installation instructions.

Thus, in order to update dependencies for this ROS 2 CI, the only required step is to open a PR to the appropriate pixi.toml file on https://github.com/ros2/ros2 .
Once that PR has been approved and merged, subsequent builds on ROS 2 CI will automatically fetch that dependency file.
