    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
@(SNIPPET(
    'property_parameter-definition_common',
    ci_scripts_default_branch=ci_scripts_default_branch,
    default_repos_url=default_repos_url,
    supplemental_repos_url=supplemental_repos_url,
    ubuntu_distro=ubuntu_distro,
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
@(SNIPPET(
    'property_parameter-definition_rmw_implementations',
    ignore_rmw_default=ignore_rmw_default,
    use_connext_debs_default=use_connext_debs_default,
))@
        <hudson.model.BooleanParameterDefinition>
          <name>CI_ISOLATED</name>
          <description>By setting this to True, the build will use the --isolated option.</description>
          <defaultValue>@(use_isolated_default)</defaultValue>
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
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
