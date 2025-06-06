<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description>
    Launches a build of the CI job for each supported platform with the same set of parameters.
    Use of RTI Connext will always be disabled on aarch64 jobs.
  </description>
  <keepDependencies>false</keepDependencies>
  <properties>
@[if build_discard]@
@(SNIPPET(
    'property_build-discard',
    days_to_keep=build_discard['days_to_keep'],
    num_to_keep=build_discard['num_to_keep'],
))@
@[end if]@
    <com.sonyericsson.rebuild.RebuildSettings plugin="rebuild@@332.va_1ee476d8f6d">
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
    el_release=el_release,
    ros_distro=ros_distro,
    colcon_mixin_url=colcon_mixin_url,
    cmake_build_type=cmake_build_type,
    build_args_default=build_args_default,
    test_args_default=test_args_default,
    compile_with_clang_default=compile_with_clang_default,
    enable_coverage_default=enable_coverage_default,
    os_name=None,
))@
  </properties>
  <scm class="hudson.scm.NullSCM"/>
  <assignedNode>@(label_expression)</assignedNode>
  <canRoam>false</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.plugins.groovy.SystemGroovy plugin="groovy@@457.v99900cb_85593">
      <source class="hudson.plugins.groovy.StringSystemScriptSource">
        <script plugin="script-security@@1369.v9b_98a_4e95b_2d">
          <script>// PREDICT TRIGGERED BUILDS AND GENERATE MARKDOWN FOR BUILD STATUS

import jenkins.model.Jenkins

def predict_build_number(job_name) {
  p = Jenkins.instance.getItemByFullName(job_name)
  if (!p) {
    return 0
  }
  build_number = p.getNextBuildNumber()
  if (p.isInQueue()) {
    // assuming the queued builds don't get cancelled
    for (item in Jenkins.instance.getQueue().getItems()) {
      if (item.task.getName() == job_name) {
        build_number += 1
      }
    }
  }
  return build_number
}

predicted_jobs = [:]
@[for os_name, os_data in os_specific_data.items()]@
predicted_jobs["@(os_name)"] = new Tuple("@(os_data['job_name'])", predict_build_number("@(os_data['job_name'])"))
@[end for]@

for (item in predicted_jobs) {
  name = item.key[0].toUpperCase() + item.key[1..-1].toLowerCase()
  job_name = item.value[0]
  build_number = item.value[1]
  println "* ${name} [![Build Status](http://ci.ros2.org/buildStatus/icon?job=${job_name}&amp;build=${build_number})](http://ci.ros2.org/job/${job_name}/${build_number}/)"
}
</script>
          <sandbox>false</sandbox>
        </script>
      </source>
    </hudson.plugins.groovy.SystemGroovy>
  </builders>
  <publishers>
@[for os_name, os_data in os_specific_data.items()]@
    <hudson.plugins.parameterizedtrigger.BuildTrigger plugin="parameterized-trigger@@2.35.2">
      <configs>
        <hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
          <configs>
            <hudson.plugins.parameterizedtrigger.CurrentBuildParameters/>
@[  if os_name in ['linux-aarch64']]@
            <hudson.plugins.parameterizedtrigger.BooleanParameters>
              <configs>
                <hudson.plugins.parameterizedtrigger.BooleanParameterConfig>
                  <name>CI_USE_CONNEXTDDS</name>
                  <value>false</value>
                </hudson.plugins.parameterizedtrigger.BooleanParameterConfig>
              </configs>
            </hudson.plugins.parameterizedtrigger.BooleanParameters>
@[  end if]@
@[  if os_name in ['windows', 'windows-2025']]@
            <hudson.plugins.parameterizedtrigger.BooleanParameters>
              <configs>
                <hudson.plugins.parameterizedtrigger.BooleanParameterConfig>
                  <name>CI_ISOLATED</name>
                  <value>@(os_data['use_isolated_default'])</value>
                </hudson.plugins.parameterizedtrigger.BooleanParameterConfig>
              </configs>
            </hudson.plugins.parameterizedtrigger.BooleanParameters>
@[  end if]@
          </configs>
          <projects>@(os_data['job_name'])</projects>
          <condition>SUCCESS</condition>
          <triggerWithNoParameters>false</triggerWithNoParameters>
          <triggerFromChildProjects>false</triggerFromChildProjects>
        </hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
      </configs>
    </hudson.plugins.parameterizedtrigger.BuildTrigger>
@[end for]@
  </publishers>
  <buildWrappers/>
</project>
