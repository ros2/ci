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
          <name>CI_COMPILE_WITH_CLANG</name>
          <description>By setting this to true, the build will run with clang compiler on Linux (currently ignored on non-Linux).</description>
          <defaultValue>@(compile_with_clang_default)</defaultValue>
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
        <hudson.model.ChoiceParameterDefinition>
          <name>CI_ENABLE_SANITIZER_TYPE</name>
          <description>This can be used to enable sanitizer based builds and tests</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>@enable_sanitizer_type_default</string>
@{
sanitizer_types.remove(enable_sanitizer_type_default)
}@
              <string>@sanitizer_types[0]</string>
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>CI_RESTRICT_SANITIZER_TO_PKGS_REGEX</name>
          <description>Restrict sanitizer instrumentation and testing to packages based on a particular regex</description>
          <defaultValue>@(restrict_sanitizer_to_pkgs_regex_default)</defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
