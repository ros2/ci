# Contributing changes to Windows CI

ROS 2 Windows CI uses [pixi](https://pixi.sh/latest/) to manage dependencies in a pixi.toml file, one per ROS distribution.
These pixi.toml files are stored in a centralized repository at https://github.com/ros2/ros2 on the branches that correspond to the ROS distribution.
They are stored separately from this repository so they can be referenced both by this CI, as well as the installation instructions.

Thus, in order to update dependencies for this ROS 2 CI, the only required step is to open a PR to the appropriate pixi.toml file on https://github.com/ros2/ros2 .
Once that PR has been approved and merged, subsequent builds on ROS 2 CI will automatically fetch that dependency file.

## The compiler cache

Windows CI builds generate Ninja build files rather than a Visual Studio solution, and run every MSVC and `rustc` invocation through [sccache](https://github.com/mozilla/sccache).
Both `ninja` and `sccache` come from the same pixi.toml as everything else.

The two pieces have to go together.
CMake only honours `CMAKE_<LANG>_COMPILER_LAUNCHER` for the Ninja and Makefile generators; with the Visual Studio generator that colcon otherwise selects on Windows, the setting is accepted and then ignored, and nothing is cached.

`WindowsBatchJob.pre()` exports the settings rather than passing them as `-D` on the colcon command line.
That is deliberate, and it is what gets the cache to the vendor packages: CMake initialises `CMAKE_<LANG>_COMPILER_LAUNCHER` from the environment variable of the same name, so an exported value also reaches the nested configures that `ament_vendor` and `ExternalProject_Add` run.
`ament_vendor` forwards a fixed list of variables to its sub-builds and the launchers are not on it, so with `-D` alone every vendored package would still compile uncached.

`CMAKE_<LANG>_COMPILER_LAUNCHER` only covers the C and C++ compilers, so `RUSTC_WRAPPER` is exported too: `zenoh_cpp_vendor` builds several hundred Rust crates through cargo.
`CARGO_INCREMENTAL` is turned off alongside it because sccache refuses to cache incremental compilation.

The cache lives in a directory on the agent, one per job, which the job template mounts into the container at `C:\sccache`.
This mirrors the `$HOME/.ccache` mount the Linux jobs use, with the difference that the directory is not shared between jobs: ccache locks its cache and is safe to share, whereas each sccache server keeps its index in memory, so two servers over one directory evict each other's entries.

Each build prints `sccache --show-stats` before and after.
Watch `Non-cacheable compilations` and `Cache errors` there as well as the hit rate -- a cache that is being bypassed rather than missing shows up in those two counters.

## Testing locally

Do the following on your own machine or VM.

Get the Windows release version with the following powershell command
```
powershell $(Get-ItemProperty -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\Update\TargetingInfo\Installed\Server.OS.amd64' -Name Version).Version
```

Change your directory to ci repo directory and run the following docker build command.
Replace the value of WINDOWS_RELEASE_VERSION with the string you found above.
```
docker build --build-arg WINDOWS_RELEASE_VERSION=10.0.18363.900 --build-arg ROS_DISTRO=rolling -t ros2_windows_ci -f windows_docker_resources\Dockerfile windows_docker_resources
```

To actually run a build, you need to run the docker container with with representative arguments.

You will need to run the following from a developer command prompt with administrator privileges.
Set a variable with the appropriate CI_ARGS, to test up to rclcpp.

```
set CI_ARGS=--force-ansi-color --workspace-path C:\J\workspace\ci_windows --ignore-rmw rmw_fastrtps_dynamic_cpp --repo-file-url https://raw.githubusercontent.com/ros2/ros2/rolling/ros2.repos --colcon-mixin-url https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml --visual-studio-version 2022 --build-args --event-handlers console_cohesion+ console_package_list+ --cmake-args -DINSTALL_EXAMPLES=OFF -DSECURITY=ON -DAPPEND_PROJECT_NAME_TO_INCLUDEDIR=ON --packages-up-to rclcpp --test-args --event-handlers console_direct+ --executor sequential --retest-until-pass 2 --ctest-args -LE xfail --pytest-args -m \"not xfail\" --packages-up-to rclcpp```
```

Run the docker container with these arguments
```
docker run --isolation=process --rm -e ROS_DOMAIN_ID=1 -e CI_ARGS="%CI_ARGS%" -v "C:\J\workspace\ci_windows":"C:\ci" ros2_windows_ci
```

Without `-e SCCACHE_DIR` the compiler cache still runs, but it lives inside the container and is discarded with it.
To keep it across runs the way CI does, create a directory and mount it as well.

```
docker run --isolation=process --rm -e ROS_DOMAIN_ID=1 -e CI_ARGS="%CI_ARGS%" -e SCCACHE_DIR=C:\sccache -v "C:\J\sccache\ci_windows":"C:\sccache" -v "C:\J\workspace\ci_windows":"C:\ci" ros2_windows_ci
```

rclcpp may not be the correct package to test for your change.
Choose a package to test up to that adequately ensures your change works as intended.
