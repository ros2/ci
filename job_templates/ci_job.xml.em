<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <com.coravy.hudson.plugins.github.GithubProjectProperty plugin="github@@1.29.3">
      <projectUrl>@(ci_scripts_repository)/</projectUrl>
      <displayName />
    </com.coravy.hudson.plugins.github.GithubProjectProperty>
    <com.sonyericsson.rebuild.RebuildSettings plugin="rebuild@@1.29">
      <autoRebuild>false</autoRebuild>
      <rebuildDisabled>false</rebuildDisabled>
    </com.sonyericsson.rebuild.RebuildSettings>
    <org.jenkinsci.plugins.requeuejob.RequeueJobProperty plugin="jobrequeue@@1.1">
      <requeueJob>true</requeueJob>
    </org.jenkinsci.plugins.requeuejob.RequeueJobProperty>
@(SNIPPET(
    'property_parameter-definition',
    ci_scripts_default_branch=ci_scripts_default_branch,
    default_repos_url=default_repos_url,
    supplemental_repos_url=supplemental_repos_url,
    ignore_rmw_default=ignore_rmw_default,
    use_connext_debs_default=use_connext_debs_default,
    use_isolated_default=use_isolated_default,
    ubuntu_distro=ubuntu_distro,
    cmake_build_type=cmake_build_type,
    build_args_default=build_args_default,
    test_args_default=test_args_default,
    enable_c_coverage_default=enable_c_coverage_default,
))@
  </properties>
  <scm class="hudson.plugins.git.GitSCM" plugin="git@@3.9.1">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>@(ci_scripts_repository)</url>
        <credentialsId>1c2004f6-2e00-425d-a421-2e1ba62ca7a7</credentialsId>
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
    <branches>
      <hudson.plugins.git.BranchSpec>
        <name>refs/heads/${CI_SCRIPTS_BRANCH}</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
    <browser class="hudson.plugins.git.browser.GithubWeb">
      <url></url>
    </browser>
    <submoduleCfg class="list"/>
    <extensions>@
@[if os_name != 'windows']
      <hudson.plugins.git.extensions.impl.SubmoduleOption>
        <disableSubmodules>false</disableSubmodules>
        <recursiveSubmodules>true</recursiveSubmodules>
        <trackingSubmodules>false</trackingSubmodules>
        <reference/>
        <parentCredentials>false</parentCredentials>
      </hudson.plugins.git.extensions.impl.SubmoduleOption>
    @
@[end if]</extensions>
  </scm>
  <assignedNode>@(label_expression)</assignedNode>
  <canRoam>false</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>@
@[if time_trigger_spec]
    <hudson.triggers.TimerTrigger>
      <spec>@(time_trigger_spec)</spec>
    </hudson.triggers.TimerTrigger>
  @
@[end if]</triggers>
  <concurrentBuild>true</concurrentBuild>
  <builders>
    <hudson.plugins.groovy.SystemGroovy plugin="groovy@@2.0">
      <source class="hudson.plugins.groovy.StringSystemScriptSource">
        <script plugin="script-security@@1.49">
          <script><![CDATA[build.setDescription("""\
branch: ${build.buildVariableResolver.resolve('CI_BRANCH_TO_TEST')}, <br/>
use_connext_static: ${build.buildVariableResolver.resolve('CI_USE_CONNEXT_STATIC')}, <br/>
@# use_connext_dynamic: ${build.buildVariableResolver.resolve('CI_USE_CONNEXT_DYNAMIC')}, <br/>
use_connext_debs: ${build.buildVariableResolver.resolve('CI_USE_CONNEXT_DEBS')}, <br/>
use_fastrtps_static: ${build.buildVariableResolver.resolve('CI_USE_FASTRTPS_STATIC')}, <br/>
use_fastrtps_dynamic: ${build.buildVariableResolver.resolve('CI_USE_FASTRTPS_DYNAMIC')}, <br/>
use_opensplice: ${build.buildVariableResolver.resolve('CI_USE_OPENSPLICE')}, <br/>
ci_branch: ${build.buildVariableResolver.resolve('CI_SCRIPTS_BRANCH')}, <br/>
repos_url: ${build.buildVariableResolver.resolve('CI_ROS2_REPOS_URL')}, <br/>
supplemental_repos_url: ${build.buildVariableResolver.resolve('CI_ROS2_SUPPLEMENTAL_REPOS_URL')}, <br/>
colcon_branch: ${build.buildVariableResolver.resolve('CI_COLCON_BRANCH')}, <br/>
use_whitespace: ${build.buildVariableResolver.resolve('CI_USE_WHITESPACE_IN_PATHS')}, <br/>
isolated: ${build.buildVariableResolver.resolve('CI_ISOLATED')}, <br/>
ubuntu_distro: ${build.buildVariableResolver.resolve('CI_UBUNTU_DISTRO')}, <br/>
cmake_build_type: ${build.buildVariableResolver.resolve('CI_CMAKE_BUILD_TYPE')}, <br/>
build_args: ${build.buildVariableResolver.resolve('CI_BUILD_ARGS')}, <br/>
test_args: ${build.buildVariableResolver.resolve('CI_TEST_ARGS')}, <br/>
coverage: ${build.buildVariableResolver.resolve('CI_ENABLE_C_COVERAGE')}\
""");]]>
        </script>
          <sandbox>false</sandbox>
        </script>
      </source>
    </hudson.plugins.groovy.SystemGroovy>
    <hudson.tasks.@(shell_type)>
      <command>@
@[if os_name in ['linux', 'osx', 'linux-aarch64']]@
rm -rf ws workspace "work space"

echo "# BEGIN SECTION: Determine arguments"
export CI_ARGS="--do-venv --force-ansi-color --workspace-path $WORKSPACE"
if [ -n "${CI_BRANCH_TO_TEST+x}" ]; then
  export CI_ARGS="$CI_ARGS --test-branch $CI_BRANCH_TO_TEST"
fi
if [ -n "${CI_COLCON_BRANCH+x}" ]; then
  export CI_ARGS="$CI_ARGS --colcon-branch $CI_COLCON_BRANCH"
fi
if [ "$CI_USE_WHITESPACE_IN_PATHS" = "true" ]; then
  export CI_ARGS="$CI_ARGS --white-space-in sourcespace buildspace installspace workspace"
fi
export CI_ARGS="$CI_ARGS --ignore-rmw"
if [ "$CI_USE_CONNEXT_STATIC" = "false" ]; then
  export CI_ARGS="$CI_ARGS rmw_connext_cpp"
fi
if [ "$CI_USE_CONNEXT_DYNAMIC" = "false" ]; then
  export CI_ARGS="$CI_ARGS rmw_connext_dynamic_cpp"
fi
if [ "$CI_USE_FASTRTPS_STATIC" = "false" ]; then
  export CI_ARGS="$CI_ARGS rmw_fastrtps_cpp"
fi
if [ "$CI_USE_FASTRTPS_DYNAMIC" = "false" ]; then
  export CI_ARGS="$CI_ARGS rmw_fastrtps_dynamic_cpp"
fi
if [ "$CI_USE_OPENSPLICE" = "false" ]; then
  export CI_ARGS="$CI_ARGS rmw_opensplice_cpp"
fi
if [ "$CI_USE_CONNEXT_DEBS" = "true" ]; then
  export CI_ARGS="$CI_ARGS --connext-debs"
  export DOCKER_BUILD_ARGS="$DOCKER_BUILD_ARGS --build-arg INSTALL_CONNEXT_DEBS=$CI_USE_CONNEXT_DEBS"
fi
if [ -z "${CI_ROS2_REPOS_URL+x}" ]; then
  CI_ROS2_REPOS_URL="@default_repos_url"
fi
export CI_ARGS="$CI_ARGS --repo-file-url $CI_ROS2_REPOS_URL"
if [ -n "${CI_ROS2_SUPPLEMENTAL_REPOS_URL+x}" ]; then
  export CI_ARGS="$CI_ARGS --supplemental-repo-file-url $CI_ROS2_SUPPLEMENTAL_REPOS_URL"
fi
if [ "$CI_ISOLATED" = "true" ]; then
  export CI_ARGS="$CI_ARGS --isolated"
fi
if [ "${CI_UBUNTU_DISTRO}" = "bionic" ]; then
  export CI_ROS1_DISTRO=melodic
elif [ "${CI_UBUNTU_DISTRO}" = "xenial" ]; then
  export CI_ROS1_DISTRO=kinetic
fi
if [ "${CI_CMAKE_BUILD_TYPE}" != "None" ]; then
  export CI_ARGS="$CI_ARGS --cmake-build-type $CI_CMAKE_BUILD_TYPE"
fi
if [ "$CI_ENABLE_C_COVERAGE" = "true" ]; then
  export CI_ARGS="$CI_ARGS --coverage"
fi
@[  if os_name in ['linux', 'linux-aarch64'] and turtlebot_demo]@
export CI_ARGS="$CI_ARGS --ros1-path /opt/ros/$CI_ROS1_DISTRO"
@[  end if]@
if [ -n "${CI_BUILD_ARGS+x}" ]; then
  export CI_ARGS="$CI_ARGS --build-args $CI_BUILD_ARGS"
fi
if [ -n "${CI_TEST_ARGS+x}" ]; then
  export CI_ARGS="$CI_ARGS --test-args $CI_TEST_ARGS"
fi
echo "Using args: $CI_ARGS"
echo "# END SECTION"

@[  if os_name in ['linux', 'linux-aarch64']]@
sed -i "s+^FROM.*$+FROM ubuntu:$CI_UBUNTU_DISTRO+" linux_docker_resources/Dockerfile
export DOCKER_BUILD_ARGS="${DOCKER_BUILD_ARGS} --build-arg UBUNTU_DISTRO=$CI_UBUNTU_DISTRO --build-arg ROS1_DISTRO=$CI_ROS1_DISTRO"

mkdir -p $HOME/.ccache
echo "# BEGIN SECTION: docker version"
docker version
echo "# END SECTION"
echo "# BEGIN SECTION: docker info"
docker info
echo "# END SECTION"
echo "# BEGIN SECTION: Inject date into Dockerfile"
sed -i "s/@@today_str/`date +%Y-%m-%d`/" linux_docker_resources/Dockerfile
echo "# END SECTION"
echo "# BEGIN SECTION: Build Dockerfile"
@[    if os_name == 'linux-aarch64']@
@[      if turtlebot_demo]@
docker build ${DOCKER_BUILD_ARGS} --build-arg PLATFORM=arm --build-arg INSTALL_TURTLEBOT2_DEMO_DEPS=true -t ros2_batch_ci_turtlebot_demo linux_docker_resources
@[      else]@
docker build ${DOCKER_BUILD_ARGS} --build-arg PLATFORM=arm -t ros2_batch_ci_aarch64 linux_docker_resources
@[      end if]@
@[    elif os_name == 'linux']@
@[      if turtlebot_demo]@
docker build ${DOCKER_BUILD_ARGS} --build-arg INSTALL_TURTLEBOT2_DEMO_DEPS=true -t ros2_batch_ci_turtlebot_demo linux_docker_resources
@[      else]@
docker build ${DOCKER_BUILD_ARGS} -t ros2_batch_ci linux_docker_resources
@[      end if]@
@[    else]@
@{ assert False, 'Unknown os_name: ' + os_name }@
@[    end if]@
echo "# END SECTION"
echo "# BEGIN SECTION: Run Dockerfile"
@[    if turtlebot_demo]@
export CONTAINER_NAME=ros2_batch_ci_turtlebot_demo
@[    elif os_name == 'linux']@
export CONTAINER_NAME=ros2_batch_ci
@[    elif os_name == 'linux-aarch64']@
export CONTAINER_NAME=ros2_batch_ci_aarch64
@[    else]@
@{ assert False, 'Unknown os_name: ' + os_name }@
@[    end if]@
# Create a network that prevents docker containers on the same host from communicating.
# This prevents cross-talk between builds running in parallel on different executors on a single host.
# It may have already been created.
docker network create -o com.docker.network.bridge.enable_icc=false isolated_network || true
docker run --rm --net=isolated_network --privileged -e UID=`id -u` -e GID=`id -g` -e CI_ARGS="$CI_ARGS" -e CCACHE_DIR=/home/rosbuild/.ccache -i -v `pwd`:/home/rosbuild/ci_scripts -v $HOME/.ccache:/home/rosbuild/.ccache $CONTAINER_NAME
echo "# END SECTION"
@[  else]@
echo "# BEGIN SECTION: Run script"
/usr/local/bin/python3 -u run_ros2_batch.py $CI_ARGS
echo "# END SECTION"
@[  end if]@
@[elif os_name == 'windows']@
setlocal enableDelayedExpansion
REM rmdir /S /Q ws workspace "work space"
rmdir /S /Q ws\build ws\install ws\src
del ws\00-ros2.repos ws\env.bat

echo "# BEGIN SECTION: Determine arguments"
set "PATH=!PATH:"=!"
set "CI_ARGS=--force-ansi-color --workspace-path !WORKSPACE!"
if "!CI_BRANCH_TO_TEST!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --test-branch !CI_BRANCH_TO_TEST!"
)
if "!CI_COLCON_BRANCH!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --colcon-branch !CI_COLCON_BRANCH!"
)
if "!CI_USE_WHITESPACE_IN_PATHS!" == "true" (
  set "CI_ARGS=!CI_ARGS! --white-space-in sourcespace buildspace installspace workspace"
)
set "CI_ARGS=!CI_ARGS! --ignore-rmw"
if "!CI_USE_CONNEXT_STATIC!" == "false" (
  set "CI_ARGS=!CI_ARGS! rmw_connext_cpp"
)
if "!CI_USE_CONNEXT_DYNAMIC!" == "false" (
  set "CI_ARGS=!CI_ARGS! rmw_connext_dynamic_cpp"
)
if "!CI_USE_FASTRTPS_STATIC!" == "false" (
  set "CI_ARGS=!CI_ARGS! rmw_fastrtps_cpp"
)
if "!CI_USE_FASTRTPS_DYNAMIC!" == "false" (
  set "CI_ARGS=!CI_ARGS! rmw_fastrtps_dynamic_cpp"
)
if "!CI_USE_OPENSPLICE!" == "false" (
  set "CI_ARGS=!CI_ARGS! rmw_opensplice_cpp"
)
if "!CI_USE_CONNEXT_DEBS!" == "true" (
  set "CI_ARGS=!CI_ARGS! --connext-debs"
)
if "!CI_ROS2_REPOS_URL!" EQU "" (
  set "CI_ROS2_REPOS_URL=@default_repos_url"
)
set "CI_ARGS=!CI_ARGS! --repo-file-url !CI_ROS2_REPOS_URL!"
if "!CI_ROS2_SUPPLEMENTAL_REPOS_URL!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --supplemental-repo-file-url !CI_ROS2_SUPPLEMENTAL_REPOS_URL!"
)
if "!CI_ISOLATED!" == "true" (
  set "CI_ARGS=!CI_ARGS! --isolated"
)
if "!CI_CMAKE_BUILD_TYPE!" NEQ "None" (
  set "CI_ARGS=!CI_ARGS! --cmake-build-type !CI_CMAKE_BUILD_TYPE!"
)
if "!CI_CMAKE_BUILD_TYPE!" == "Debug" (
  where python_d &gt; python_debug_interpreter.txt
  set /p PYTHON_DEBUG_INTERPRETER=&lt;python_debug_interpreter.txt
  set "CI_ARGS=!CI_ARGS! --python-interpreter !PYTHON_DEBUG_INTERPRETER!"
)
if "!CI_ENABLE_C_COVERAGE!" == "true" (
  set "CI_ARGS=!CI_ARGS! --coverage"
)
if "!CI_BUILD_ARGS!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --build-args !CI_BUILD_ARGS!"
)
if "!CI_TEST_ARGS!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --test-args !CI_TEST_ARGS!"
)
echo Using args: !CI_ARGS!
echo "# END SECTION"

echo "# BEGIN SECTION: Run script"
python -u run_ros2_batch.py !CI_ARGS!
echo "# END SECTION"
@[else]@
@{ assert False, 'Unknown os_name: ' + os_name }@
@[end if]</command>
    </hudson.tasks.@(shell_type)>
  </builders>
  <publishers>
@(SNIPPET(
    'publisher_warnings',
    os_name=os_name,
))@
@(SNIPPET(
    'publisher_cobertura',
))@
@(SNIPPET(
    'publisher_xunit',
))@
@[if mailer_recipients]@
    <hudson.tasks.Mailer plugin="mailer@@1.22">
      <recipients>@(mailer_recipients)</recipients>
      <dontNotifyEveryUnstableBuild>@(dont_notify_every_unstable_build)</dontNotifyEveryUnstableBuild>
      <sendToIndividuals>false</sendToIndividuals>
    </hudson.tasks.Mailer>
@[end if]@
  </publishers>
  <buildWrappers>
@[if build_timeout_mins]@
    <hudson.plugins.build__timeout.BuildTimeoutWrapper plugin="build-timeout@@1.19">
      <strategy class="hudson.plugins.build_timeout.impl.AbsoluteTimeOutStrategy">
        <timeoutMinutes>@(build_timeout_mins)</timeoutMinutes>
      </strategy>
      <operationList>
        <hudson.plugins.build__timeout.operations.AbortOperation />
      </operationList>
    </hudson.plugins.build__timeout.BuildTimeoutWrapper>
@[end if]@
    <hudson.plugins.timestamper.TimestamperBuildWrapper plugin="timestamper@@1.8.10" />
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper plugin="ansicolor@@0.5.2">
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
@[if os_name != 'windows']@
    <com.cloudbees.jenkins.plugins.sshagent.SSHAgentBuildWrapper plugin="ssh-agent@@1.17">
      <credentialIds>
        <string>1c2004f6-2e00-425d-a421-2e1ba62ca7a7</string>
      </credentialIds>
      <ignoreMissing>false</ignoreMissing>
    </com.cloudbees.jenkins.plugins.sshagent.SSHAgentBuildWrapper>
@[end if]@
  </buildWrappers>
</project>
