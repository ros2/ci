<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
@[if build_discard]@
@(SNIPPET(
    'property_build-discard',
    days_to_keep=build_discard['days_to_keep'],
    num_to_keep=build_discard['num_to_keep'],
))@
@[end if]@
    <com.coravy.hudson.plugins.github.GithubProjectProperty plugin="github@@1.40.0">
      <projectUrl>@(ci_scripts_repository)/</projectUrl>
      <displayName />
    </com.coravy.hudson.plugins.github.GithubProjectProperty>
    <com.sonyericsson.rebuild.RebuildSettings plugin="rebuild@@332.va_1ee476d8f6d">
      <autoRebuild>false</autoRebuild>
      <rebuildDisabled>false</rebuildDisabled>
    </com.sonyericsson.rebuild.RebuildSettings>
    <org.jenkinsci.plugins.requeuejob.RequeueJobProperty plugin="jobrequeue@@1.1">
      <requeueJob>true</requeueJob>
    </org.jenkinsci.plugins.requeuejob.RequeueJobProperty>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
@(SNIPPET(
    'property_parameter-definition_common',
    ci_scripts_default_branch=ci_scripts_default_branch,
    default_repos_url=default_repos_url,
    supplemental_repos_url=supplemental_repos_url,
    ubuntu_distro=ubuntu_distro,
    el_release=el_release,
    ros_distro=ros_distro,
    colcon_mixin_url=colcon_mixin_url,
    cmake_build_type=cmake_build_type,
    build_args_default=build_args_default,
    os_name=os_name,
    use_isolated_default=False,
))@
@(SNIPPET(
    'property_parameter-definition_rmw_implementations',
    ignore_rmw_default=ignore_rmw_default,
    use_connext_debs_default=use_connext_debs_default,
))@
        <hudson.model.StringParameterDefinition>
          <name>CI_TEST_ARGS</name>
          <description>Additional arguments passed to the 'test' verb.</description>
          <defaultValue>@(test_args_default)</defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <scm class="hudson.plugins.git.GitSCM" plugin="git@@5.6.0">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>@(ci_scripts_repository)</url>
        <credentialsId>github-access-key</credentialsId>
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
    <submoduleCfg class="empty-list"/>
    <extensions>
      <hudson.plugins.git.extensions.impl.SubmoduleOption>
        <disableSubmodules>false</disableSubmodules>
        <recursiveSubmodules>true</recursiveSubmodules>
        <trackingSubmodules>false</trackingSubmodules>
        <reference/>
        <parentCredentials>@[if os_name in ['windows', 'windows-2025']]true@[else]false@[end if]</parentCredentials>
        <shallow>false</shallow>
      </hudson.plugins.git.extensions.impl.SubmoduleOption>
    </extensions>
  </scm>
  <assignedNode>@(label_expression)</assignedNode>
  <canRoam>false</canRoam>
  <disabled>@('true' if vars().get('disabled') else 'false')</disabled>
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
    <hudson.plugins.groovy.SystemGroovy plugin="groovy@@457.v99900cb_85593">
      <source class="hudson.plugins.groovy.StringSystemScriptSource">
        <script plugin="script-security@@1369.v9b_98a_4e95b_2d">
          <script><![CDATA[build.setDescription("""\
@[if 'linux' in os_name]@
ubuntu_distro: ${build.buildVariableResolver.resolve('CI_UBUNTU_DISTRO')}, <br/>
el_release: ${build.buildVariableResolver.resolve('CI_EL_RELEASE')}, <br/>
@[end if]@
ros_distro: ${build.buildVariableResolver.resolve('CI_ROS_DISTRO')}, <br/>
branch: ${build.buildVariableResolver.resolve('CI_BRANCH_TO_TEST')}, <br/>
ci_branch: ${build.buildVariableResolver.resolve('CI_SCRIPTS_BRANCH')}, <br/>
repos_url: ${build.buildVariableResolver.resolve('CI_ROS2_REPOS_URL')}, <br/>
use_connextdds: ${build.buildVariableResolver.resolve('CI_USE_CONNEXTDDS')}, <br/>
use_connext_debs: ${build.buildVariableResolver.resolve('CI_USE_CONNEXT_DEBS')}, <br/>
use_cyclonedds: ${build.buildVariableResolver.resolve('CI_USE_CYCLONEDDS')}, <br/>
use_fastrtps_static: ${build.buildVariableResolver.resolve('CI_USE_FASTRTPS_STATIC')}, <br/>
use_fastrtps_dynamic: ${build.buildVariableResolver.resolve('CI_USE_FASTRTPS_DYNAMIC')}, <br/>
isolated: ${build.buildVariableResolver.resolve('CI_ISOLATED')}, <br/>
colcon_mixin_url: ${build.buildVariableResolver.resolve('CI_COLCON_MIXIN_URL')}, <br/>
cmake_build_type: ${build.buildVariableResolver.resolve('CI_CMAKE_BUILD_TYPE')}, <br/>
build_args: ${build.buildVariableResolver.resolve('CI_BUILD_ARGS')}, <br/>
test_args: ${build.buildVariableResolver.resolve('CI_TEST_ARGS')}\
""");]]>
        </script>
          <sandbox>false</sandbox>
        </script>
      </source>
    </hudson.plugins.groovy.SystemGroovy>
    <hudson.tasks.@(shell_type)>
      <command>@
@[if os_name in ['linux', 'linux-aarch64', 'linux-rhel']]@
rm -rf ws workspace

echo "# BEGIN SECTION: Determine arguments"
export CI_ARGS="--packaging --force-ansi-color"
if [ -n "${CI_BRANCH_TO_TEST+x}" ]; then
  export CI_ARGS="$CI_ARGS --test-branch $CI_BRANCH_TO_TEST"
fi
if [ -n "${CI_COLCON_BRANCH+x}" ]; then
  export CI_ARGS="$CI_ARGS --colcon-branch $CI_COLCON_BRANCH"
fi
if [ "$CI_USE_CONNEXTDDS" = "false" ]; then
  export CI_ARGS="$CI_ARGS --ignore-rmw rmw_connextdds"
fi
if [ "$CI_USE_CYCLONEDDS" = "false" ]; then
  export CI_ARGS="$CI_ARGS --ignore-rmw rmw_cyclonedds_cpp"
fi
if [ "$CI_USE_FASTRTPS_STATIC" = "false" ]; then
  export CI_ARGS="$CI_ARGS --ignore-rmw rmw_fastrtps_cpp"
fi
if [ "$CI_USE_FASTRTPS_DYNAMIC" = "false" ]; then
  export CI_ARGS="$CI_ARGS --ignore-rmw rmw_fastrtps_dynamic_cpp"
fi
if [ "$CI_USE_CONNEXT_DEBS" = "true" ]; then
  export DOCKER_BUILD_ARGS="${DOCKER_BUILD_ARGS} --build-arg INSTALL_CONNEXT_DEBS=$CI_USE_CONNEXT_DEBS"
  export CI_ARGS="$CI_ARGS --connext-debs"
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
if [ -n "${CI_ROS_DISTRO+x}" ]; then
  export DOCKER_BUILD_ARGS="${DOCKER_BUILD_ARGS} --build-arg ROS_DISTRO=${CI_ROS_DISTRO}"
fi
if [ -n "${CI_COLCON_MIXIN_URL+x}" ]; then
  export CI_ARGS="$CI_ARGS --colcon-mixin-url $CI_COLCON_MIXIN_URL"
fi
if [ "${CI_CMAKE_BUILD_TYPE}" != "None" ]; then
  export CI_ARGS="$CI_ARGS --cmake-build-type $CI_CMAKE_BUILD_TYPE"
fi
if [ -n "${CI_BUILD_ARGS+x}" ]; then
  export CI_ARGS="$CI_ARGS --build-args $CI_BUILD_ARGS"
fi
if [ -n "${CI_TEST_ARGS+x}" ]; then
  export CI_ARGS="$CI_ARGS --test-args $CI_TEST_ARGS"
fi
echo "Using args: $CI_ARGS"
echo "# END SECTION"

@[  if os_name in ['linux', 'linux-aarch64', 'linux-rhel']]@
@[    if os_name in ['linux', 'linux-aarch64']]@
sed -i "s+^FROM.*$+FROM ubuntu:$CI_UBUNTU_DISTRO+" linux_docker_resources/Dockerfile
export DOCKER_BUILD_ARGS="${DOCKER_BUILD_ARGS} --build-arg UBUNTU_DISTRO=$CI_UBUNTU_DISTRO"
@[    elif os_name == 'linux-rhel']@
sed -i "s+^FROM.*$+FROM almalinux:$CI_EL_RELEASE+" linux_docker_resources/Dockerfile-RHEL
export DOCKER_BUILD_ARGS="${DOCKER_BUILD_ARGS} --build-arg EL_RELEASE=$CI_EL_RELEASE"
@[    end if]@

mkdir -p $HOME/.ccache
echo "# BEGIN SECTION: docker version"
docker version
echo "# END SECTION"
echo "# BEGIN SECTION: docker info"
docker info
echo "# END SECTION"
echo "# BEGIN SECTION: Inject date into Dockerfile"
sed -i "s/@@today_str/`date +%Y-%m-%d`/" linux_docker_resources/Dockerfile*
echo "# END SECTION"
echo "# BEGIN SECTION: Build Dockerfile"
@[    if os_name == 'linux-aarch64']@
docker build --pull ${DOCKER_BUILD_ARGS} --build-arg PLATFORM=aarch64 -t ros2_packaging_aarch64 linux_docker_resources
@[    elif os_name == 'linux-rhel']@
docker build --pull ${DOCKER_BUILD_ARGS} -t ros2_packaging_rhel linux_docker_resources -f linux_docker_resources/Dockerfile-RHEL
@[    elif os_name == 'linux']@
docker build --pull ${DOCKER_BUILD_ARGS} -t ros2_packaging linux_docker_resources
@[    else]@
@{ assert False, 'Unknown os_name: ' + os_name }@
@[    end if]@
echo "# END SECTION"
echo "# BEGIN SECTION: Run Dockerfile"
@[    if os_name == 'linux']@
export CONTAINER_NAME=ros2_packaging
@[    elif os_name == 'linux-aarch64']@
export CONTAINER_NAME=ros2_packaging_aarch64
@[    elif os_name == 'linux-rhel']@
export CONTAINER_NAME=ros2_packaging_rhel
@[    else]@
@{ assert False, 'Unknown os_name: ' + os_name }@
@[    end if]@
# Create a network that prevents docker containers on the same host from communicating.
# This prevents cross-talk between builds running in parallel on different executors on a single host.
# It may have already been created.
docker network create -o com.docker.network.bridge.enable_icc=false isolated_network || true
docker run --rm --net=isolated_network --cap-add NET_ADMIN -e BUILD_URL="$BUILD_URL" -e UID=`id -u` -e GID=`id -g` -e CI_ARGS="$CI_ARGS" -e CCACHE_DIR=/home/rosbuild/.ccache -i --workdir=`pwd` -v `pwd`:`pwd` -v $HOME/.ccache:/home/rosbuild/.ccache $CONTAINER_NAME
echo "# END SECTION"
@[  else]@
echo "# BEGIN SECTION: Run packaging script"
/usr/local/bin/python3 -u run_ros2_batch.py $CI_ARGS
echo "# END SECTION"
@[  end if]@
@[elif os_name in ['windows', 'windows-2025']]@
setlocal enableDelayedExpansion
rmdir /S /Q ws workspace

set CONTAINER_NAME=ros2_windows_ci_%CI_ROS_DISTRO%
set DOCKERFILE=windows_docker_resources\Dockerfile

rem "Finding the Release Version is much easier with powershell than cmd"
powershell $(Get-ItemProperty -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\Update\TargetingInfo\Installed\Server.OS.amd64' -Name Version).Version > release_version.txt
set /p RELEASE_VERSION=&lt; release_version.txt
rem "Put current date in Dockerfile to force cache invalidation once per day"
powershell "(Get-Content ${Env:DOCKERFILE}).replace('@@today_str', $(Get-Date).ToLongDateString()) | Set-Content ${Env:DOCKERFILE}"
set BUILD_ARGS=--build-arg WINDOWS_RELEASE_VERSION=%RELEASE_VERSION% --build-arg ROS_DISTRO=%CI_ROS_DISTRO%
docker build  %BUILD_ARGS% -t %CONTAINER_NAME% -f %DOCKERFILE% windows_docker_resources  || exit /b !ERRORLEVEL!
echo "# END SECTION"

echo "# BEGIN SECTION: Determine arguments"
set "PATH=!PATH:"=!"
set "CI_ARGS=--packaging --force-ansi-color"
if "!CI_BRANCH_TO_TEST!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --test-branch !CI_BRANCH_TO_TEST!"
)
if "!CI_COLCON_BRANCH!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --colcon-branch !CI_COLCON_BRANCH!"
)
if "!CI_USE_CONNEXTDDS!" == "false" (
  set "CI_ARGS=!CI_ARGS! --ignore-rmw rmw_connextdds"
)
if "!CI_USE_CYCLONEDDS!" == "false" (
  set "CI_ARGS=!CI_ARGS! --ignore-rmw rmw_cyclonedds_cpp"
)
if "!CI_USE_FASTRTPS_STATIC!" == "false" (
  set "CI_ARGS=!CI_ARGS! --ignore-rmw rmw_fastrtps_cpp"
)
if "!CI_USE_FASTRTPS_DYNAMIC!" == "false" (
  set "CI_ARGS=!CI_ARGS! --ignore-rmw rmw_fastrtps_dynamic_cpp"
)
if "!CI_USE_CONNEXT_DEBS!" == "true" (
  set "CI_ARGS=!CI_ARGS! --connext-debs"
)
if "!CI_ROS2_REPOS_URL!" EQU "" (
  set "CI_ROS2_REPOS_URL=@default_repos_url"
)
set "CI_ARGS=!CI_ARGS! --repo-file-url !CI_ROS2_REPOS_URL!"
if "!CI_ISOLATED!" == "true" (
  set "CI_ARGS=!CI_ARGS! --isolated"
)
if "!CI_COLCON_MIXIN_URL!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --colcon-mixin-url !CI_COLCON_MIXIN_URL!"
)
if "!CI_CMAKE_BUILD_TYPE!" NEQ "None" (
  set "CI_ARGS=!CI_ARGS! --cmake-build-type !CI_CMAKE_BUILD_TYPE!"
)
set "CI_ARGS=!CI_ARGS! --visual-studio-version !CI_VISUAL_STUDIO_VERSION!"
if "!CI_BUILD_ARGS!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --build-args !CI_BUILD_ARGS!"
)
if "!CI_TEST_ARGS!" NEQ "" (
  set "CI_TEST_ARGS=!CI_TEST_ARGS:"=\"!"
  set "CI_TEST_ARGS=!CI_TEST_ARGS:|=^|!"
  set "CI_ARGS=!CI_ARGS! --test-args !CI_TEST_ARGS!"
)
echo Using args: !CI_ARGS!
echo "# END SECTION"

echo "# BEGIN SECTION: Run packaging script with DockerFile"
rem Kill any running docker containers, which may be leftover from aborted jobs
powershell -Command "if ($(docker ps -q) -ne $null) { docker stop $(docker ps -q)}"

rem If isolated_network doesn't already exist, create it
set NETWORK_NAME=isolated_network
docker network inspect %NETWORK_NAME% 2>nul 1>nul || docker network create -d nat -o com.docker.network.bridge.enable_icc=false %NETWORK_NAME%  || exit /b !ERRORLEVEL!
docker run --isolation=process --rm --net=%NETWORK_NAME% -e BUILD_URL="%BUILD_URL%" -e ROS_DOMAIN_ID=1 -e CI_ARGS="%CI_ARGS%" -v "%cd%":"C:\ci" %CONTAINER_NAME%  || exit /b !ERRORLEVEL!
echo "# END SECTION"
@[else]@
@{ assert False, 'Unknown os_name: ' + os_name }@
@[end if]</command>
    </hudson.tasks.@(shell_type)>
  </builders>
  <publishers>
@(SNIPPET(
    'publisher_warnings_ng',
    os_name=os_name,
))@
@(SNIPPET(
    'publisher_cobertura',
))@
@(SNIPPET(
    'publisher_xunit',
))@
    <hudson.tasks.ArtifactArchiver>
      <artifacts>ws/ros2-package-*.*</artifacts>
      <allowEmptyArchive>false</allowEmptyArchive>
      <onlyIfSuccessful>true</onlyIfSuccessful>
      <fingerprint>false</fingerprint>
      <defaultExcludes>true</defaultExcludes>
      <caseSensitive>true</caseSensitive>
    </hudson.tasks.ArtifactArchiver>
@[if mailer_recipients]@
    <hudson.tasks.Mailer plugin="mailer@@1.29">
      <recipients>@(mailer_recipients)</recipients>
      <dontNotifyEveryUnstableBuild>false</dontNotifyEveryUnstableBuild>
      <sendToIndividuals>false</sendToIndividuals>
    </hudson.tasks.Mailer>
@[end if]@
  </publishers>
  <buildWrappers>
    <hudson.plugins.timestamper.TimestamperBuildWrapper plugin="timestamper@@1.28" />
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper plugin="ansicolor@@1.0.5">
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
@[if os_name not in ['windows', 'windows-2025']]@
    <com.cloudbees.jenkins.plugins.sshagent.SSHAgentBuildWrapper plugin="ssh-agent@@376.v8933585c69d3">
      <credentialIds>
        <string>github-access-key</string>
      </credentialIds>
      <ignoreMissing>false</ignoreMissing>
    </com.cloudbees.jenkins.plugins.sshagent.SSHAgentBuildWrapper>
@[end if]@
  </buildWrappers>
</project>
