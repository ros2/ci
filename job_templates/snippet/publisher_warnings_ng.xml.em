<io.jenkins.plugins.analysis.core.steps.IssuesRecorder plugin="warnings-ng@@13.10258.va_17d49a_78c3b_">
  <analysisTools>
    <io.jenkins.plugins.analysis.warnings.Cmake>
      <id></id>
      <name></name>
      <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
      <reportEncoding></reportEncoding>
      <skipSymbolicLinks>false</skipSymbolicLinks>
    </io.jenkins.plugins.analysis.warnings.Cmake>
@[if os_name in ['linux', 'linux-aarch64', 'linux-rhel']]@
   <io.jenkins.plugins.analysis.warnings.Gcc4>
      <id></id>
      <name></name>
      <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
      <reportEncoding></reportEncoding>
      <skipSymbolicLinks>false</skipSymbolicLinks>
    </io.jenkins.plugins.analysis.warnings.Gcc4>
@[end if]
@[if os_name in ['linux', 'linux-aarch64', 'linux-rhel']]@
    <io.jenkins.plugins.analysis.warnings.Clang>
      <id></id>
      <name></name>
      <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
      <reportEncoding></reportEncoding>
      <skipSymbolicLinks>false</skipSymbolicLinks>
    </io.jenkins.plugins.analysis.warnings.Clang>
    <io.jenkins.plugins.analysis.warnings.ClangTidy>
      <id></id>
      <name></name>
      <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
      <reportEncoding></reportEncoding>
      <skipSymbolicLinks>false</skipSymbolicLinks>
    </io.jenkins.plugins.analysis.warnings.ClangTidy>
@[elif os_name in ['windows']]@
    <io.jenkins.plugins.analysis.warnings.MsBuild>
      <id></id>
      <name></name>
      <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
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
  <minimumSeverity plugin="analysis-model-api@@14.16.0-1014.v2802998b_7789">
    <name>LOW</name>
  </minimumSeverity>
  <filters/>
  <isEnabledForFailure>false</isEnabledForFailure>
  <isAggregatingResults>false</isAggregatingResults>
  <isBlameDisabled>false</isBlameDisabled>
  <isForensicsDisabled>false</isForensicsDisabled>
  <qualityGates>
    <io.jenkins.plugins.analysis.core.util.QualityGate>
      <threshold>1</threshold>
      <type>TOTAL</type>
      <status>WARNING</status>
    </io.jenkins.plugins.analysis.core.util.QualityGate>
  </qualityGates>
  <trendChartType>AGGREGATION_TOOLS</trendChartType>
</io.jenkins.plugins.analysis.core.steps.IssuesRecorder>
