        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_CONNEXT_STATIC</name>
          <description>By setting this to True, the build will attempt to use RTI&apos;s Connext (static type support).</description>
          <defaultValue>@('false' if 'rmw_connext_cpp' in ignore_rmw_default else 'true')</defaultValue>
        </hudson.model.BooleanParameterDefinition>
@#        <hudson.model.BooleanParameterDefinition>
@#          <name>CI_USE_CONNEXT_DYNAMIC</name>
@#          <description>By setting this to True, the build will attempt to use RTI&apos;s Connext (dynamic type support).</description>
@#          <defaultValue>@('false' if 'rmw_connext_dynamic_cpp' in ignore_rmw_default else 'true')</defaultValue>
@#        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_CONNEXT_DEBS</name>
          <description>By setting this to True, the build will use the Debian packages for Connext, instead of the binaries off the RTI website (applies to Linux only).</description>
          <defaultValue>@(use_connext_debs_default)</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_CYCLONEDDS</name>
          <description>By setting this to True, the build will attempt to use Eclipse&apos;s Cyclone DDS.</description>
          <defaultValue>@('false' if 'rmw_cyclonedds_cpp' in ignore_rmw_default else 'true')</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_FASTRTPS_STATIC</name>
          <description>By setting this to True, the build will attempt to use eProsima&apos;s FastRTPS (static type support).</description>
          <defaultValue>@('false' if 'rmw_fastrtps_cpp' in ignore_rmw_default else 'true')</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_FASTRTPS_DYNAMIC</name>
          <description>By setting this to True, the build will attempt to use eProsima&apos;s FastRTPS (dynamic type support).</description>
          <defaultValue>@('false' if 'rmw_fastrtps_dynamic_cpp' in ignore_rmw_default else 'true')</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_OPENSPLICE</name>
          <description>By setting this to True, the build will attempt to use ADLINK&apos;s OpenSplice.</description>
          <defaultValue>@('false' if 'rmw_opensplice_cpp' in ignore_rmw_default else 'true')</defaultValue>
        </hudson.model.BooleanParameterDefinition>
