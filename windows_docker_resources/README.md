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

## The compiler cache

Every MSVC and `rustc` invocation runs through [sccache](https://github.com/mozilla/sccache), which comes from the same `buildfarm` environment in pixi.toml as `ninja`.

The cache depends on the Ninja generator described above.
CMake honours `CMAKE_<LANG>_COMPILER_LAUNCHER` only for the Ninja and Makefile generators; under the Visual Studio generator the setting is accepted and then ignored, and nothing is cached.
That is also why the packaging jobs get no cache: they stay on the Visual Studio generator, and they build RelWithDebInfo, which on MSVC means `/Zi` -- which sccache will not cache in any case.

`WindowsBatchJob._setup_compiler_cache()` exports the settings rather than passing them as `-D` on the colcon command line.
That is deliberate, and it is what gets the cache to the vendor packages: CMake initialises `CMAKE_<LANG>_COMPILER_LAUNCHER` from the environment variable of the same name, so an exported value also reaches the nested configures that `ament_vendor` and `ExternalProject_Add` run.
`ament_vendor` forwards a fixed allow-list of variables to its sub-builds through a `-C` initial-cache file and the launchers are not on it, so with `-D` alone every vendored package would still compile uncached.

`CMAKE_<LANG>_COMPILER_LAUNCHER` only covers the C and C++ compilers, so `RUSTC_WRAPPER` is exported too: `zenoh_cpp_vendor` builds several hundred Rust crates through cargo.
`CARGO_INCREMENTAL` is turned off alongside it because sccache refuses to cache incremental compilation.

`CMAKE_TRY_COMPILE_CONFIGURATION` is set to Release because `try_compile()` otherwise builds Debug, which on MSVC is `/Zi /Od /RTC1`; the feature checks across a workspace this size are hundreds of compilations that would all miss.

The cache lives in `.sccache` beside the workspace, which is to say inside the Jenkins workspace that is bind mounted into the container.
The batch job removes only the `ws` subdirectory of that on each build, so the cache survives from one build to the next, and since every Jenkins job has a workspace of its own, no two jobs share one.
That last part matters: ccache locks its cache and is safe to share, whereas each sccache server keeps its index in memory, so two servers over one directory evict each other's entries.

Wiping the workspace therefore also drops the cache, which is a reasonable way to ask for a cold build.

Note that a mount added to `job_templates/ci_job.xml.em` would *not* be enough on its own.
A Jenkins job's build steps live in Jenkins, put there by `create_jenkins_job.py`, so a change to the template only reaches a running job once someone pushes the job configuration.
Anything under `ros2_batch_job/` takes effect as soon as `CI_SCRIPTS_BRANCH` points at it, which is why the cache directory is chosen there.

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

The compiler cache needs nothing extra here: it defaults to .sccache inside the mounted directory, so it persists across runs for as long as that directory does.
Set -e SCCACHE_DIR to override it, and -e SCCACHE_CACHE_SIZE to change the 8G ceiling.

rclcpp may not be the correct package to test for your change.
Choose a package to test up to that adequately ensures your change works as intended.
