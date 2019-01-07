        <hudson.model.StringParameterDefinition>
          <name>CI_BRANCH_TO_TEST</name>
          <description>Branch to test across the repositories in the .repos file that have it.
For example, if you have a few repositories with the &apos;feature&apos; branch.
Then you can set this to &apos;feature&apos;.
The repositories with the &apos;feature&apos; branch will be changed to that branch.
Other repositories will stay on the default branch, usually &apos;master&apos;.
To use the default branch on all repositories, use an empty string.</description>
          <defaultValue></defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>CI_SCRIPTS_BRANCH</name>
          <description>Branch of ros2/ci repository from which to get the ci scripts.</description>
          <defaultValue>@ci_scripts_default_branch</defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>CI_ROS2_REPOS_URL</name>
          <description>Custom .repos file to use instead of the default (@default_repos_url).
For example, copy the content of the .repos file to a GitHub Gist, modify it to your needs, and then pass the raw URL here.</description>
          <defaultValue></defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>CI_ROS2_SUPPLEMENTAL_REPOS_URL</name>
          <description>Supplemental .repos file which will be merged into the default repos file.
Use this instead of the Custom .repos file if you want to add to the default repos file rather than replace it.</description>
          <defaultValue>@supplemental_repos_url</defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>CI_COLCON_BRANCH</name>
          <description>Use a specific branch of the colcon repositories.
If the branch doesn't exist fall back to the default branch.
To use the latest released version, use an empty string.</description>
          <defaultValue></defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
        <hudson.model.ChoiceParameterDefinition>
          <name>CI_UBUNTU_DISTRO</name>
          <description>Select the linux distribution to use.</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              <string>@ubuntu_distro</string>
@{
choices = ['bionic', 'xenial']
choices.remove(ubuntu_distro)
}@
@[for choice in choices]@
              <string>@choice</string>
@[end for]@
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>
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
        <hudson.model.StringParameterDefinition>
          <name>CI_BUILD_ARGS</name>
          <description>Additional arguments passed to the 'build' verb.</description>
          <defaultValue>@(build_args_default)</defaultValue>
          <trim>false</trim>
        </hudson.model.StringParameterDefinition>
