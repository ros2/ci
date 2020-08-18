## Contributing changes to Windows ROS 2 Chef Cookbook

Running the Windows CI agent as a configurable chef cookbook follows the general benefits of "infrastructure as software".
Making changes can be submitted as pull requests, which in turn can be reviewed and tested before they are deployed.
Below is the recommended process for submitting changes to the ROS 2 chef cookbook for Windows for use with ci.ros2.org.

### Step 1. Create a ros2-cookbooks PR
Open a PR at github.com/ros-infrastructure/ros2-cookbooks for your desired change.

### Step 2. Create a ros2/ci PR
Open corresponding PR at github.com/ros2/ci which updates the ros2-cookbooks git submodule to your new branch of the ros2-cookbooks repo.

### Step 3. Verify the ros2-cookbooks PR
It can take a while to test changes to the cookbook directly on CI, so it is strongly advised to test locally and verify your change inside a representative docker container.
See the following section for information on local testing.
After you have tested it locally, submit jobs to https://ci.ros2.org/job/ci_windows and set CI_SCRIPTS_BRANCH to your ros2/ci PR branch.
You may need to verify the PR for several different ROS 2 releases.
You can set `CI_ROS_DISTRO` on ci.ros2.org, which will choose the corresponding chef cookbook configuration to test your updates.
If testing on different releases, don't forget to specify the correct ros2.repos file.

#### Testing locally
Do the following on your own machine or VM.

Get the Windows release version with the following powershell command
```
powershell $(Get-ItemProperty -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\Update\TargetingInfo\Installed\Server.OS.amd64' -Name Version).Version
```

Change your directory to ci repo directory and run the following docker build command.
Replace the value of WINDOWS_RELEASE_VERSION with the string you found above.
```
docker build  --build-arg WINDOWS_RELEASE_VERSION=10.0.18363.900 -t ros2_windows_ci windows_docker_resources
```

If it builds correctly, you can be assured your changes to the chef cookbook has been parsed and used by chef correctly.
However, you should also check that your change doesn't affect the build of ros2.
To do that, you need to run the docker container with representative arguments.

You will need to run the following from a developer command prompt with administrator privileges.
Set a variable with the appropriate CI_ARGS, to test up to rclcpp.

```
set CI_ARGS=--force-ansi-color --workspace-path C:\J\workspace\ci_windows --ros-distro foxy --ignore-rmw rmw_fastrtps_dynamic_cpp  --colcon-mixin-url https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml --visual-studio-version 2019 --build-args --event-handlers console_cohesion+ console_package_list+ --cmake-args -DINSTALL_EXAMPLES=OFF -DSECURITY=ON --packages-up-to rclcpp --test-args --event-handlers console_direct+ --executor sequential --retest-until-pass 2 --ctest-args -LE xfail --pytest-args -m \"not xfail\" --packages-up-to rclcpp```
```

Run the docker container with these arguments
```
docker run --isolation=process -e ROS_DOMAIN_ID=1 -e CI_ARGS=%CI_ARGS% -v "C:\J\workspace\ci_windows":"C:\ci" ros2_windows_ci
```

rclcpp may not be the correct package to test for your change.
Choose a package to test up to that adequately ensures your change works as intended.

### Step 4. Merge the ros2-cookbooks PR
After your ros2-cookbooks PR is approved and passes testing, merge this PR first.
Because the git submodule has not yet been updated in ros2/ci, this merge will not change the behavior of ci.ros2.org.

### Step 5. Update the ros2/ci PR
You will need to update your ros2/ci PR to use the master branch of ros2-cookbooks.
Update the submodule with the latest commit from your PR and target the main branch.

### Step 6. Rerun the ci job for the ros2/ci PR
This will help verify that that the updated git submodule points to the correct commit.

### Step 7. Merge the ros2/ci PR
Once you merge the PR, the docker containers will need to be rebuilt on the ci_windows nodes.
This can take some time and will slow down the first build for each node.
Choose a time of day when activity is low, so your change doesn't negatively impact other contributors.
This author uses 5-6PM US Pacific (1am GMT), which gives some time to revert your change before the nigthly builds should it have introduced an issue.
