<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description>
    Note: The Windows jobs ignore the middleware selection flags.
  </description>
  <keepDependencies>false</keepDependencies>
  <properties>
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
  <scm class="hudson.scm.NullSCM"/>
  <assignedNode>@(label_expression)</assignedNode>
  <canRoam>false</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders/>
  <publishers>
@[for os_name, os_data in os_specific_data.items()]@
    <hudson.plugins.parameterizedtrigger.BuildTrigger plugin="parameterized-trigger@@2.32">
      <configs>
        <hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
          <configs>
            <hudson.plugins.parameterizedtrigger.CurrentBuildParameters/>
@[if os_name == 'linux-aarch64']@
            <hudson.plugins.parameterizedtrigger.BooleanParameters>
              <configs>
                <hudson.plugins.parameterizedtrigger.BooleanParameterConfig>
                  <name>CI_USE_CONNEXT</name>
                  <value>false</value>
                </hudson.plugins.parameterizedtrigger.BooleanParameterConfig>
              </configs>
            </hudson.plugins.parameterizedtrigger.BooleanParameters>
@[end if]
          </configs>
          <projects>@(os_data['job_name'])</projects>
          <condition>SUCCESS</condition>
          <triggerWithNoParameters>false</triggerWithNoParameters>
        </hudson.plugins.parameterizedtrigger.BuildTriggerConfig>
      </configs>
    </hudson.plugins.parameterizedtrigger.BuildTrigger>
@[end for]@
  </publishers>
  <buildWrappers/>
</project>
