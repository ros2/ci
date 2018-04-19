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
          <name>CI_USE_WHITESPACE_IN_PATHS</name>
          <description>By setting this to True white space will be inserted into the paths.
The paths include the workspace, plus the source, build and install spaces.
This tests the robustness to whitespace being within the different paths.</description>
          <defaultValue>false</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_CONNEXT</name>
          <description>By setting this to True, the build will attempt to use RTI&apos;s Connext.</description>
          <defaultValue>@(use_connext_default)</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_DISABLE_CONNEXT_STATIC</name>
          <description>By setting this to True, the build will disable the Connext static rmw implementation.</description>
          <defaultValue>@(disable_connext_static_default)</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_DISABLE_CONNEXT_DYNAMIC</name>
          <description>By setting this to True, the build will disable the Connext dynamic rmw implementation.</description>
          <defaultValue>@(disable_connext_dynamic_default)</defaultValue>
        </hudson.model.BooleanParameterDefinition>
@#        <hudson.model.BooleanParameterDefinition>
@#          <name>CI_USE_OSRF_CONNEXT_DEBS</name>
@#          <description>By setting this to True, the build will use the deb packages built by OSRF for Connext, instead of the binaries off the RTI website (applies to linux only).</description>
@#          <defaultValue>@(use_osrf_connext_debs_default)</defaultValue>
@#        </hudson.model.BooleanParameterDefinition>
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
          <name>CI_ISOLATED</name>
          <description>By setting this to True, the build will use the --isolated option.</description>
          <defaultValue>true</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_ENABLE_C_COVERAGE</name>
          <description>By setting this to true, the build will report test coverage for C/C++ code (currently ignored on non-Linux).</description>
          <defaultValue>@(enable_c_coverage_default)</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>CI_TEST_ARGS</name>
          <description>Additional arguments passed to the 'test' verb.</description>
          <defaultValue>@(test_args_default)</defaultValue>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
