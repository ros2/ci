<io.jenkins.plugins.analysis.core.steps.IssuesRecorder plugin="warnings-ng@@7.2.2">
  <analysisTools>
    <io.jenkins.plugins.analysis.warnings.Cmake>
      <id></id>
      <name></name>
      <pattern></pattern>
      <reportEncoding></reportEncoding>
      <skipSymbolicLinks>false</skipSymbolicLinks>
    </io.jenkins.plugins.analysis.warnings.Cmake>
@[if os_name in ['linux', 'linux-armhf', 'linux-aarch64', 'linux-centos']]@
   <io.jenkins.plugins.analysis.warnings.Gcc4>
      <id></id>
      <name></name>
      <pattern></pattern>
      <reportEncoding></reportEncoding>
      <skipSymbolicLinks>false</skipSymbolicLinks>
    </io.jenkins.plugins.analysis.warnings.Gcc4>
@[end if]
@[if os_name == 'osx' or os_name in ['linux', 'linux-armhf', 'linux-aarch64', 'linux-centos']]@
    <io.jenkins.plugins.analysis.warnings.Clang>
      <id></id>
      <name></name>
      <pattern></pattern>
      <reportEncoding></reportEncoding>
      <skipSymbolicLinks>false</skipSymbolicLinks>
    </io.jenkins.plugins.analysis.warnings.Clang>
    <io.jenkins.plugins.analysis.warnings.ClangTidy>
      <id></id>
      <name></name>
      <pattern></pattern>
      <reportEncoding></reportEncoding>
      <skipSymbolicLinks>false</skipSymbolicLinks>
    </io.jenkins.plugins.analysis.warnings.ClangTidy>
@[elif os_name in ['windows', 'windows-container']]@
    <io.jenkins.plugins.analysis.warnings.MsBuild>
      <id></id>
      <name></name>
      <pattern></pattern>
      <reportEncoding></reportEncoding>
      <skipSymbolicLinks>false</skipSymbolicLinks>
    </io.jenkins.plugins.analysis.warnings.MsBuild>
@[else]@
@{assert False, 'Unknown os_name: ' + os_name}@
@[end if]@
  </analysisTools>
  <sourceCodeEncoding></sourceCodeEncoding>
  <sourceDirectory></sourceDirectory>
  <ignoreQualityGate>false</ignoreQualityGate>
  <ignoreFailedBuilds>true</ignoreFailedBuilds>
  <referenceJobName>-</referenceJobName>
  <failOnError>false</failOnError>
  <healthy>0</healthy>
  <unhealthy>0</unhealthy>
  <minimumSeverity plugin="analysis-model-api@@7.0.2">
    <name>LOW</name>
  </minimumSeverity>
  <filters/>
  <isEnabledForFailure>false</isEnabledForFailure>
  <isAggregatingResults>false</isAggregatingResults>
  <isBlameDisabled>false</isBlameDisabled>
  <isForensicsDisabled>false</isForensicsDisabled>
  <qualityGates/>
  <trendChartType>AGGREGATION_TOOLS</trendChartType>
</io.jenkins.plugins.analysis.core.steps.IssuesRecorder>
