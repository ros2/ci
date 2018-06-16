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
        <hudson.model.BooleanParameterDefinition>
          <name>CI_USE_CONNEXT_DEBS</name>
          <description>By setting this to True, the build will use the Debian packages for Connext, instead of the binaries off the RTI website (applies to Linux only).</description>
          <defaultValue>@(use_connext_debs_default)</defaultValue>
        </hudson.model.BooleanParameterDefinition>
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
