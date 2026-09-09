# Contributing changes to Windows CI

ROS 2 Windows CI uses [pixi](https://pixi.sh/latest/) to manage dependencies in a pixi.toml file, one per ROS distribution.
These pixi.toml files are stored in a centralized repository at https://github.com/ros2/ros2 on the branches that correspond to the ROS distribution.
They are stored separately from this repository so they can be referenced both by this CI, as well as the installation instructions.

Thus, in order to update dependencies for this ROS 2 CI, the only required step is to open a PR to the appropriate pixi.toml file on https://github.com/ros2/ros2 .
Once that PR has been approved and merged, subsequent builds on ROS 2 CI will automatically fetch that dependency file.

## The Ninja generator

Windows CI builds generate Ninja build files rather than a Visual Studio solution.
The `ninja` binary comes from the same pixi.toml as everything else, out of the `buildfarm` environment, which is why the image installs and runs `-e buildfarm` rather than the default one.

Ninja is a single configuration generator, so the build type is chosen at configure time.
Jobs that pass `--cmake-build-type` are unaffected; the rest now say `Release` explicitly, which is what colcon was already building with `--config Release` under the Visual Studio generator.

The packaging jobs are deliberately left on the Visual Studio generator.

Ninja writes object files to `CMakeFiles/<target>.dir/<hash>/<source>.obj`, where the Visual Studio generator wrote `<target>.dir/<config>/<source>.obj` -- roughly 37 characters more per object, which is enough to push the longest rosidl generated sources past `MAX_PATH`.
The batch job therefore always shortens the build space to `b` and `subst`s the workspace onto `W:`, rather than relying on long path support being enabled.
If the drive mapping fails the build still runs from the long path, with a warning.

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

rclcpp may not be the correct package to test for your change.
Choose a package to test up to that adequately ensures your change works as intended.
