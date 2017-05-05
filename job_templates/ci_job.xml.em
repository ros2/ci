<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <com.coravy.hudson.plugins.github.GithubProjectProperty plugin="github@@1.25.1">
      <projectUrl>@(ci_scripts_repository)/</projectUrl>
      <displayName />
    </com.coravy.hudson.plugins.github.GithubProjectProperty>
    <com.sonyericsson.rebuild.RebuildSettings plugin="rebuild@@1.25">
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
    use_connext_default=use_connext_default,
    disable_connext_static_default=disable_connext_static_default,
    disable_connext_dynamic_default=disable_connext_dynamic_default,
    use_osrf_connext_debs_default=use_osrf_connext_debs_default,
    use_fastrtps_default=use_fastrtps_default,
    use_opensplice_default=use_opensplice_default,
    cmake_build_type=cmake_build_type,
    ament_build_args_default=ament_build_args_default,
    ament_test_args_default=ament_test_args_default,
    enable_c_coverage_default=enable_c_coverage_default,
))@
  </properties>
  <scm class="hudson.plugins.git.GitSCM" plugin="git@@3.0.1">
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
        <script plugin="script-security@@1.27">
          <script><![CDATA[build.setDescription("""\
branch: ${build.buildVariableResolver.resolve('CI_BRANCH_TO_TEST')}, <br/>
use_connext: ${build.buildVariableResolver.resolve('CI_USE_CONNEXT')}, <br/>
disable_connext_static: ${build.buildVariableResolver.resolve('CI_DISABLE_CONNEXT_STATIC')}, <br/>
disable_connext_dynamic: ${build.buildVariableResolver.resolve('CI_DISABLE_CONNEXT_DYNAMIC')}, <br/>
use_osrf_connext_debs: ${build.buildVariableResolver.resolve('CI_USE_OSRF_CONNEXT_DEBS')}, <br/>`
use_fastrtps: ${build.buildVariableResolver.resolve('CI_USE_FASTRTPS')}, <br/>
use_opensplice: ${build.buildVariableResolver.resolve('CI_USE_OPENSPLICE')}, <br/>
ci_branch: ${build.buildVariableResolver.resolve('CI_SCRIPTS_BRANCH')}, <br/>
repos_url: ${build.buildVariableResolver.resolve('CI_ROS2_REPOS_URL')}, <br/>
supplemental_repos_url: ${build.buildVariableResolver.resolve('CI_ROS2_SUPPLEMENTAL_REPOS_URL')}, <br/>
use_whitespace: ${build.buildVariableResolver.resolve('CI_USE_WHITESPACE_IN_PATHS')}, <br/>
isolated: ${build.buildVariableResolver.resolve('CI_ISOLATED')}, <br/>
cmake_build_type: ${build.buildVariableResolver.resolve('CI_CMAKE_BUILD_TYPE')}, <br/>
ament_build_args: ${build.buildVariableResolver.resolve('CI_AMENT_BUILD_ARGS')}, <br/>
ament_test_args: ${build.buildVariableResolver.resolve('CI_AMENT_TEST_ARGS')}, <br/>
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
if [ "$CI_USE_WHITESPACE_IN_PATHS" = "true" ]; then
  export CI_ARGS="$CI_ARGS --white-space-in sourcespace buildspace installspace workspace"
fi
if [ "$CI_USE_CONNEXT" = "true" ]; then
  export CI_ARGS="$CI_ARGS --connext"
fi
if [ "$CI_DISABLE_CONNEXT_STATIC" = "true" ]; then
  export CI_ARGS="$CI_ARGS --disable-connext-static"
fi
if [ "$CI_DISABLE_CONNEXT_DYNAMIC" = "true" ]; then
  export CI_ARGS="$CI_ARGS --disable-connext-dynamic"
fi
if [ "$CI_USE_OSRF_CONNEXT_DEBS" = "true" ]; then
  export CI_ARGS="$CI_ARGS --osrf-connext-debs"
fi
if [ "$CI_USE_FASTRTPS" = "true" ]; then
  export CI_ARGS="$CI_ARGS --fastrtps"
fi
if [ "$CI_USE_OPENSPLICE" = "true" ]; then
  export CI_ARGS="$CI_ARGS --opensplice"
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
if [ "${CI_CMAKE_BUILD_TYPE}" != "None" ]; then
  export CI_ARGS="$CI_ARGS --cmake-build-type $CI_CMAKE_BUILD_TYPE"
fi
if [ "$CI_ENABLE_C_COVERAGE" = "true" ]; then
  export CI_ARGS="$CI_ARGS --coverage"
fi
if [ -n "${CI_AMENT_BUILD_ARGS+x}" ]; then
  case $CI_AMENT_BUILD_ARGS in
    *-- )
      # delimiter is already appended
      ;;
    * )
      CI_AMENT_BUILD_ARGS="$CI_AMENT_BUILD_ARGS --"
      ;;
  esac
  export CI_ARGS="$CI_ARGS --ament-build-args $CI_AMENT_BUILD_ARGS"
fi
if [ -n "${CI_AMENT_TEST_ARGS+x}" ]; then
  case $CI_AMENT_TEST_ARGS in
    *-- )
      # delimiter is already appended
      ;;
    * )
      CI_AMENT_TEST_ARGS="$CI_AMENT_TEST_ARGS --"
      ;;
  esac
  export CI_ARGS="$CI_ARGS --ament-test-args $CI_AMENT_TEST_ARGS"
fi
@[if os_name in ['linux', 'linux-aarch64'] and turtlebot_demo]@
export CI_ARGS="$CI_ARGS --ros1-path /opt/ros/kinetic"
@[end if]@
echo "Using args: $CI_ARGS"
echo "# END SECTION"

@[if os_name in ['linux', 'linux-aarch64']]@
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
@[if os_name == 'linux-aarch64']@
sed -i 's+^FROM.*$+FROM aarch64/ubuntu:xenial+' linux_docker_resources/Dockerfile
sed -i 's+apt-get update+(apt-get update || true)+' linux_docker_resources/Dockerfile
@[  if turtlebot_demo]@
docker build --build-arg PLATFORM=arm INSTALL_TURTLEBOT2_DEMO_DEPS=true -t ros2_batch_ci_turtlebot_demo linux_docker_resources
@[  else]@
docker build --build-arg PLATFORM=arm -t ros2_batch_ci_aarch64 linux_docker_resources
@[  end if]@
@[elif os_name == 'linux']@
@[  if turtlebot_demo]@
docker build --build-arg INSTALL_TURTLEBOT2_DEMO_DEPS=true -t ros2_batch_ci_turtlebot_demo linux_docker_resources
@[  else]@
docker build -t ros2_batch_ci linux_docker_resources
@[  end if]@
@[else]@
@{ assert 'Unknown os_name: ' + os_name }@
@[end if]@
echo "# END SECTION"
echo "# BEGIN SECTION: Run Dockerfile"
@[if turtlebot_demo]@
export CONTAINER_NAME=ros2_batch_ci_turtlebot_demo
@[elif os_name == 'linux']@
export CONTAINER_NAME=ros2_batch_ci
@[elif os_name == 'linux-aarch64']@
export CONTAINER_NAME=ros2_batch_ci_aarch64
@[else]@
@{ assert 'Unknown os_name: ' + os_name }@
@[end if]@
docker run --privileged -e UID=`id -u` -e GID=`id -g` -e CI_ARGS="$CI_ARGS" -e CCACHE_DIR=/home/rosbuild/.ccache -i -v `pwd`:/home/rosbuild/ci_scripts -v $HOME/.ccache:/home/rosbuild/.ccache $CONTAINER_NAME
echo "# END SECTION"
@[else]@
echo "# BEGIN SECTION: Run script"
/usr/local/bin/python3 -u run_ros2_batch.py $CI_ARGS
echo "# END SECTION"
@[end if]@
@[elif os_name == 'windows']@
rmdir /S /Q ws workspace "work space"

echo "# BEGIN SECTION: Determine arguments"
set "PATH=%PATH:"=%"
set "CI_ARGS=--force-ansi-color --workspace-path %WORKSPACE%"
if "%CI_BRANCH_TO_TEST%" NEQ "" (
  set "CI_ARGS=%CI_ARGS% --test-branch %CI_BRANCH_TO_TEST%"
)
if "%CI_USE_WHITESPACE_IN_PATHS%" == "true" (
  set "CI_ARGS=%CI_ARGS% --white-space-in sourcespace buildspace installspace workspace"
)
if "%CI_USE_CONNEXT%" == "true" (
  set "CI_ARGS=%CI_ARGS% --connext"
)
if "%CI_DISABLE_CONNEXT_STATIC%" == "true" (
  set "CI_ARGS=%CI_ARGS% --disable-connext-static"
)
if "%CI_DISABLE_CONNEXT_DYNAMIC%" == "true" (
  set "CI_ARGS=%CI_ARGS% --disable-connext-dynamic"
)
if "%CI_USE_OSRF_CONNEXT_DEBS%" == "true" (
  set "CI_ARGS=%CI_ARGS% --osrf-connext-debs"
)
if "%CI_USE_FASTRTPS%" == "true" (
  set "CI_ARGS=%CI_ARGS% --fastrtps"
)
if "%CI_USE_OPENSPLICE%" == "true" (
  set "CI_ARGS=%CI_ARGS% --opensplice"
)
if "%CI_ROS2_REPOS_URL%" EQU "" (
  set "CI_ROS2_REPOS_URL=@default_repos_url"
)
set "CI_ARGS=%CI_ARGS% --repo-file-url %CI_ROS2_REPOS_URL%"
if "%CI_ROS2_SUPPLEMENTAL_REPOS_URL%" NEQ "" (
  set "CI_ARGS=%CI_ARGS% --supplemental-repo-file-url %CI_ROS2_SUPPLEMENTAL_REPOS_URL%"
)
if "%CI_ISOLATED%" == "true" (
  set "CI_ARGS=%CI_ARGS% --isolated"
)
if "%CI_CMAKE_BUILD_TYPE%" NEQ "None" (
  set "CI_ARGS=%CI_ARGS% --cmake-build-type %CI_CMAKE_BUILD_TYPE%"
)
if "%CI_ENABLE_C_COVERAGE%" == "true" (
  set "CI_ARGS=%CI_ARGS% --coverage"
)
if "%CI_AMENT_BUILD_ARGS%" NEQ "" (
  if "%CI_AMENT_BUILD_ARGS:~-2%" NEQ "--" (
    set "CI_AMENT_BUILD_ARGS=%CI_AMENT_BUILD_ARGS% --"
  )
  set "CI_ARGS=%CI_ARGS% --ament-build-args %CI_AMENT_BUILD_ARGS%"
)
if "%CI_AMENT_TEST_ARGS%" NEQ "" (
  if "%CI_AMENT_TEST_ARGS:~-2%" NEQ "--" (
    set "CI_AMENT_TEST_ARGS=%CI_AMENT_TEST_ARGS% --"
  )
  set "CI_ARGS=%CI_ARGS% --ament-test-args %CI_AMENT_TEST_ARGS%"
)
echo Using args: %CI_ARGS%
echo "# END SECTION"

echo "# BEGIN SECTION: Run script"
python -u run_ros2_batch.py %CI_ARGS%
echo "# END SECTION"
@[else]@
@{ assert 'Unknown os_name: ' + os_name }@
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
    <hudson.tasks.Mailer plugin="mailer@@1.20">
      <recipients>@(mailer_recipients)</recipients>
      <dontNotifyEveryUnstableBuild>@(dont_notify_every_unstable_build)</dontNotifyEveryUnstableBuild>
      <sendToIndividuals>false</sendToIndividuals>
    </hudson.tasks.Mailer>
@[end if]@
  </publishers>
  <buildWrappers>
@[if build_timeout_mins]@
    <hudson.plugins.build__timeout.BuildTimeoutWrapper plugin="build-timeout@@1.18">
      <strategy class="hudson.plugins.build_timeout.impl.AbsoluteTimeOutStrategy">
        <timeoutMinutes>@(build_timeout_mins)</timeoutMinutes>
      </strategy>
      <operationList>
        <hudson.plugins.build__timeout.operations.AbortOperation />
      </operationList>
    </hudson.plugins.build__timeout.BuildTimeoutWrapper>
@[end if]@
    <hudson.plugins.timestamper.TimestamperBuildWrapper plugin="timestamper@@1.8.8" />
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper plugin="ansicolor@@0.5.0">
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
@[if os_name != 'windows']@
    <com.cloudbees.jenkins.plugins.sshagent.SSHAgentBuildWrapper plugin="ssh-agent@@1.15">
      <credentialIds>
        <string>1c2004f6-2e00-425d-a421-2e1ba62ca7a7</string>
      </credentialIds>
      <ignoreMissing>false</ignoreMissing>
    </com.cloudbees.jenkins.plugins.sshagent.SSHAgentBuildWrapper>
@[end if]@
  </buildWrappers>
</project>
