# Documentation for CI Builders

Members of the ros2/ci-builders team on GitHub.com can trigger builds on <https://ci.ros2.org> when signed in via GitHub.com.
This team is primarily composed of collaborators from other projects that work closely with the ROS 2 core so they can verify their changes remain compatible with ROS 2.


## Testing pull requests

For pull requests, use the [CI launcher job](https://ci.ros2.org/job/ci_launcher) to trigger builds against Ubuntu AMD64, Ubuntu ARM64, macOS, and Windows.
Once triggered, the output of the CI launcher job will include a markdown snippet embedding the build status links for each platform.
When first rendered, a build may be displayed as "Not run" which indicates that the build is queued but is not yet running on a worker.

When changes are part of the default repository use the `CI_BRANCH_TO_TEST` parameter to checkout and merge that branch against the default branch for all repositories with a matching branch name.
This works well for testing changes in multiple repositories together.
Many of the other arguments should be reasonably self-explanatory and its likely you won't change them from their defaults to do Pull request CI, although you will want to be sure that the `CI_USE_CYCLONEDDS` box is checked.
`CI_BUILD_ARGS` and `CI_TEST_ARGS` are basically passed directly to colcon build and test respectively so you should be familiar with those.

Our CI has limited capacity, and the default `ros2.repos` file is constantly growing.
To save build time limit the scope CI builds to only packages that are changed by the pull request being tested or are likely to be affected by the changes. 

## Nightly and packaging jobs

These jobs share the same underlying configuration as the manual CI jobs but are run on a schedule.
Do not trigger these jobs manually as doing so reduces the accuracy of nightly metrics.
If you want to replicate the results of a nightly job you can trigger a corresponding ci job with the same parameters.
For example to duplicate the [nightly Windows debug](https://ci.ros2.org/view/nightly/job/nightly_win_deb) job with a [CI Windows job](https://ci.ros2.org/job/ci_windows), make sure to set the `CI_CMAKE_BUILD_TYPE` parameter to 'Debug'.


## Testing packaging jobs

In order to test the packaging jobs or generate custom package artifacts you can use the manual `ci_packaging` jobs which exist for each platform.
