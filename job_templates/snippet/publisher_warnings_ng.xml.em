    <io.jenkins.plugins.analysis.core.steps.IssuesRecorder plugin="warnings-ng@@13.10258.va_17d49a_78c3b_">
      <analysisTools>
        <io.jenkins.plugins.analysis.warnings.Cmake>
          <id />
          <name />
          <icon />
          <jenkins plugin="plugin-util-api@@7.1341.v039f146993d9" />
          <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
          <reportEncoding />
          <skipSymbolicLinks>false</skipSymbolicLinks>
          <linesLookAhead>0</linesLookAhead>
        </io.jenkins.plugins.analysis.warnings.Cmake>
@[if os_name in ['linux', 'linux-aarch64', 'linux-rhel']]@
        <io.jenkins.plugins.analysis.warnings.Gcc4>
          <id />
          <name />
          <icon />
          <jenkins plugin="plugin-util-api@@7.1341.v039f146993d9" />
          <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
          <reportEncoding />
          <skipSymbolicLinks>false</skipSymbolicLinks>
          <linesLookAhead>0</linesLookAhead>
        </io.jenkins.plugins.analysis.warnings.Gcc4>
        <io.jenkins.plugins.analysis.warnings.Clang>
          <id />
          <name />
          <icon />
          <jenkins plugin="plugin-util-api@@7.1341.v039f146993d9" />
          <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
          <reportEncoding />
          <skipSymbolicLinks>false</skipSymbolicLinks>
          <linesLookAhead>0</linesLookAhead>
        </io.jenkins.plugins.analysis.warnings.Clang>
        <io.jenkins.plugins.analysis.warnings.ClangTidy>
          <id />
          <name />
          <icon />
          <jenkins plugin="plugin-util-api@@7.1341.v039f146993d9" />
          <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
          <reportEncoding />
          <skipSymbolicLinks>false</skipSymbolicLinks>
          <linesLookAhead>0</linesLookAhead>
        </io.jenkins.plugins.analysis.warnings.ClangTidy>
@[elif os_name in ['windows']]@
        <io.jenkins.plugins.analysis.warnings.MsBuild>
          <id />
          <name />
          <icon />
          <jenkins plugin="plugin-util-api@@7.1341.v039f146993d9" />
          <pattern>*/log/build_*/*/stdout_stderr.log</pattern>
          <reportEncoding />
          <skipSymbolicLinks>false</skipSymbolicLinks>
          <linesLookAhead>0</linesLookAhead>
        </io.jenkins.plugins.analysis.warnings.MsBuild>
@[else]@
@{assert False, 'Unknown os_name: ' + os_name}@
@[end if]@
      </analysisTools>
      <sourceCodeEncoding />
      <sourceDirectories />
      <sourceCodeRetention>EVERY_BUILD</sourceCodeRetention>
      <ignoreQualityGate>false</ignoreQualityGate>
      <failOnError>false</failOnError>
      <stopBuild>false</stopBuild>
      <healthy>0</healthy>
      <unhealthy>0</unhealthy>
      <minimumSeverity plugin="analysis-model-api@@14.16.0-1014.v2802998b_7789">
        <name>LOW</name>
      </minimumSeverity>
      <filters />
      <filesFilter />
      <isEnabledForFailure>false</isEnabledForFailure>
      <isAggregatingResults>false</isAggregatingResults>
      <quiet>false</quiet>
      <isBlameDisabled>false</isBlameDisabled>
      <skipPublishingChecks>false</skipPublishingChecks>
      <checksAnnotationScope>NEW</checksAnnotationScope>
      <skipPostProcessing>false</skipPostProcessing>
      <skipDeltaCalculation>false</skipDeltaCalculation>
      <icon />
      <qualityGates>
        <io.jenkins.plugins.analysis.core.util.WarningsQualityGate>
          <threshold>1.0</threshold>
          <criticality>UNSTABLE</criticality>
          <type>TOTAL</type>
        </io.jenkins.plugins.analysis.core.util.WarningsQualityGate>
      </qualityGates>
      <trendChartType>AGGREGATION_TOOLS</trendChartType>
      <scm />
      <sourcePathPrefix />
      <targetPathPrefix />
    </io.jenkins.plugins.analysis.core.steps.IssuesRecorder>
