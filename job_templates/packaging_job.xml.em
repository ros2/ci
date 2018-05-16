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
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
@(SNIPPET(
    'property_parameter-definition_common',
    ci_scripts_default_branch=ci_scripts_default_branch,
    default_repos_url=default_repos_url,
    supplemental_repos_url=supplemental_repos_url,
    cmake_build_type=cmake_build_type,
    build_args_default=build_args_default,
))@
        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_FASTRTPS</name>
          <description>By setting this to True, the build will attempt to use eProsima&apos;s FastRTPS.</description>
          <defaultValue>@(use_fastrtps_default)</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_OPENSPLICE</name>
          <description>By setting this to True, the build will attempt to use PrismTech&apos;s OpenSplice.</description>
          <defaultValue>@(use_opensplice_default)</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_TEST_BRIDGE</name>
          <description>By setting this to True, the tests for the ros1_bridge will be run.</description>
          <defaultValue>@(test_bridge_default)</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>CI_TEST_ARGS</name>
          <description>Additional arguments passed to the 'test' verb if testing the bridge.</description>
          <defaultValue>@(test_args_default)</defaultValue>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
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
ci_branch: ${build.buildVariableResolver.resolve('CI_SCRIPTS_BRANCH')}, <br/>
repos_url: ${build.buildVariableResolver.resolve('CI_ROS2_REPOS_URL')}, <br/>
use_fastrtps: ${build.buildVariableResolver.resolve('CI_USE_FASTRTPS')}, <br/>
use_opensplice: ${build.buildVariableResolver.resolve('CI_USE_OPENSPLICE')}, <br/>
cmake_build_type: ${build.buildVariableResolver.resolve('CI_CMAKE_BUILD_TYPE')}, <br/>
build_args: ${build.buildVariableResolver.resolve('CI_BUILD_ARGS')}, <br/>
test_bridge: ${build.buildVariableResolver.resolve('CI_TEST_BRIDGE')}, <br/>
test_args: ${build.buildVariableResolver.resolve('CI_TEST_ARGS')}\
""");]]>
        </script>
          <sandbox>false</sandbox>
        </script>
      </source>
    </hudson.plugins.groovy.SystemGroovy>
    <hudson.tasks.@(shell_type)>
      <command>@
@[if os_name in ['linux', 'linux-aarch64', 'osx']]@
rm -rf ws workspace

echo "# BEGIN SECTION: Determine arguments"
export CI_ARGS="--packaging --do-venv --force-ansi-color"
if [ -n "${CI_BRANCH_TO_TEST+x}" ]; then
  export CI_ARGS="$CI_ARGS --test-branch $CI_BRANCH_TO_TEST"
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
if [ "$CI_TEST_BRIDGE" = "true" ]; then
  export CI_ARGS="$CI_ARGS --test-bridge"
fi
@[if os_name in ['linux', 'linux-aarch64']]@
export CI_ARGS="$CI_ARGS --ros1-path /opt/ros/kinetic"
@[else]@
echo "not building/testing the ros1_bridge on MacOS"
# export CI_ARGS="$CI_ARGS --ros1-path /Users/osrf/kinetic/install_isolated"
@[end if]@
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

@[if os_name in ['linux', 'linux-aarch64']]@
mkdir -p $HOME/.ccache
echo "# BEGIN SECTION: docker version"
docker version
echo "# END SECTION"
echo "# BEGIN SECTION: docker info"
docker info
echo "# END SECTION"
echo "# BEGIN SECTION: Build Dockerfile"
@[if os_name == 'linux-aarch64']@
sed -i 's+^FROM.*$+FROM aarch64/ubuntu:xenial+' linux_docker_resources/Dockerfile
sed -i 's+apt-get update+(apt-get update || true)+' linux_docker_resources/Dockerfile
docker build --build-arg PLATFORM=arm --build-arg BRIDGE=true -t ros2_packaging_aarch64 linux_docker_resources
@[elif os_name == 'linux']@
docker build --build-arg BRIDGE=true -t ros2_packaging linux_docker_resources
@[else]@
@{ assert False, 'Unknown os_name: ' + os_name }@
@[end if]@
echo "# END SECTION"
echo "# BEGIN SECTION: Run Dockerfile"
@[if os_name == 'linux']@
export CONTAINER_NAME=ros2_packaging
@[elif os_name == 'linux-aarch64']@
export CONTAINER_NAME=ros2_packaging_aarch64
@[else]@
@{ assert False, 'Unknown os_name: ' + os_name }@
@[end if]@
docker run --rm --privileged -e UID=`id -u` -e GID=`id -g` -e CI_ARGS="$CI_ARGS" -e CCACHE_DIR=/home/rosbuild/.ccache -i -v `pwd`:/home/rosbuild/ci_scripts -v $HOME/.ccache:/home/rosbuild/.ccache $CONTAINER_NAME
echo "# END SECTION"
@[else]@
echo "# BEGIN SECTION: Run packaging script"
/usr/local/bin/python3 -u run_ros2_batch.py $CI_ARGS
echo "# END SECTION"
@[end if]@
@[elif os_name == 'windows']@
setlocal enableDelayedExpansion
rmdir /S /Q ws workspace

echo "# BEGIN SECTION: Determine arguments"
set "PATH=!PATH:"=!"
set "CI_ARGS=--packaging --force-ansi-color"
if "!CI_BRANCH_TO_TEST!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --test-branch !CI_BRANCH_TO_TEST!"
)
if "!CI_USE_FASTRTPS!" == "true" (
  set "CI_ARGS=!CI_ARGS! --fastrtps"
)
if "!CI_USE_OPENSPLICE!" == "true" (
  set "CI_ARGS=!CI_ARGS! --opensplice"
)
if "!CI_ROS2_REPOS_URL!" EQU "" (
  set "CI_ROS2_REPOS_URL=@default_repos_url"
)
set "CI_ARGS=!CI_ARGS! --repo-file-url !CI_ROS2_REPOS_URL!"
if "!CI_TEST_BRIDGE!" == "true" (
  set "CI_ARGS=!CI_ARGS! --test-bridge"
)
if "!CI_CMAKE_BUILD_TYPE!" NEQ "None" (
  set "CI_ARGS=!CI_ARGS! --cmake-build-type !CI_CMAKE_BUILD_TYPE!"
)
if "!CI_BUILD_ARGS!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --build-args !CI_BUILD_ARGS!"
)
if "!CI_TEST_ARGS!" NEQ "" (
  set "CI_ARGS=!CI_ARGS! --test-args !CI_TEST_ARGS!"
)
echo Using args: !CI_ARGS!
echo "# END SECTION"

echo "# BEGIN SECTION: Run packaging script"
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
    <hudson.tasks.ArtifactArchiver>
      <artifacts>ws/ros2-package-*.*</artifacts>
      <allowEmptyArchive>false</allowEmptyArchive>
      <onlyIfSuccessful>true</onlyIfSuccessful>
      <fingerprint>false</fingerprint>
      <defaultExcludes>true</defaultExcludes>
      <caseSensitive>true</caseSensitive>
    </hudson.tasks.ArtifactArchiver>
@[if mailer_recipients]@
    <hudson.tasks.Mailer plugin="mailer@@1.20">
      <recipients>@(mailer_recipients)</recipients>
      <dontNotifyEveryUnstableBuild>false</dontNotifyEveryUnstableBuild>
      <sendToIndividuals>false</sendToIndividuals>
    </hudson.tasks.Mailer>
@[end if]@
  </publishers>
  <buildWrappers>
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
