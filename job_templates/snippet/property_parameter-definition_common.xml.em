        <hudson.model.StringParameterDefinition>
          <name>CI_BRANCH_TO_TEST</name>
          <description>Branch to test across the repositories in the .repos file that have it.
For example, if you have a few repositories with the &apos;feature&apos; branch.
Then you can set this to &apos;feature&apos;.
The repositories with the &apos;feature&apos; branch will be changed to that branch.
Other repositories will stay on the default branch, usually &apos;master&apos;.
To use the default branch on all repositories, use an empty string.</description>
          <defaultValue></defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>CI_SCRIPTS_BRANCH</name>
          <description>Branch of ros2/ci repository from which to get the ci scripts.</description>
          <defaultValue>@ci_scripts_default_branch</defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>CI_ROS2_REPOS_URL</name>
          <description>Custom .repos file to use instead of the default (@default_repos_url).
For example, copy the content of the .repos file to a GitHub Gist, modify it to your needs, and then pass the raw URL here.</description>
          <defaultValue></defaultValue>
        </hudson.model.StringParameterDefinition>
        <hudson.model.ChoiceParameterDefinition>
          <name>CI_CMAKE_BUILD_TYPE</name>
          <description>Select the CMake build type.</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>@cmake_build_type</string>
@{
choices = ['None', 'Debug', 'Release', 'RelWithDebInfo']
choices.remove(cmake_build_type)
}@
@[for choice in choices]@
              <string>@choice</string>
@[end for]@
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
