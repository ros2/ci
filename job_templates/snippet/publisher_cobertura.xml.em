<io.jenkins.plugins.coverage.metrics.steps.CoverageRecorder plugin="coverage@@1.16.1">
<tools class="java.util.ImmutableCollections$List12" resolves-to="java.util.CollSer" serialization="custom">
<java.util.CollSer>
<default>
<tag>1</tag>
</default>
<int>1</int>
<io.jenkins.plugins.coverage.metrics.steps.CoverageTool>
<jenkins plugin="plugin-util-api@@5.1.0"/>
<pattern>ws/build*/**/*coverage.xml</pattern>
<parser>COBERTURA</parser>
</io.jenkins.plugins.coverage.metrics.steps.CoverageTool>
</java.util.CollSer>
</tools>
<qualityGates class="java.util.ImmutableCollections$ListN" resolves-to="java.util.CollSer" serialization="custom">
<java.util.CollSer>
<default>
<tag>1</tag>
</default>
<int>3</int>
<io.jenkins.plugins.coverage.metrics.steps.CoverageQualityGate>
<threshold>0.0</threshold>
<criticality>UNSTABLE</criticality>
<metric>METHOD</metric>
<baseline>PROJECT</baseline>
</io.jenkins.plugins.coverage.metrics.steps.CoverageQualityGate>
<io.jenkins.plugins.coverage.metrics.steps.CoverageQualityGate>
<threshold>0.0</threshold>
<criticality>UNSTABLE</criticality>
<metric>LINE</metric>
<baseline>PROJECT</baseline>
</io.jenkins.plugins.coverage.metrics.steps.CoverageQualityGate>
<io.jenkins.plugins.coverage.metrics.steps.CoverageQualityGate>
<threshold>0.0</threshold>
<criticality>FAILURE</criticality>
<metric>MODULE</metric>
<baseline>PROJECT</baseline>
</io.jenkins.plugins.coverage.metrics.steps.CoverageQualityGate>
</java.util.CollSer>
</qualityGates>
<id/>
<name/>
<skipPublishingChecks>false</skipPublishingChecks>
<checksName/>
<checksAnnotationScope>MODIFIED_LINES</checksAnnotationScope>
<ignoreParsingErrors>false</ignoreParsingErrors>
<failOnError>false</failOnError>
<enabledForFailure>false</enabledForFailure>
<skipSymbolicLinks>false</skipSymbolicLinks>
<scm/>
<sourceCodeEncoding/>
<sourceDirectories class="java.util.ImmutableCollections$Set12" resolves-to="java.util.CollSer" serialization="custom">	
<java.util.CollSer>	
<default>	
<tag>2</tag>	
</default>
<int>1</int>
<io.jenkins.plugins.prism.SourceCodeDirectory plugin="prism-api@@1.29.0-18">
<path>ws</path>
</io.jenkins.plugins.prism.SourceCodeDirectory>
</java.util.CollSer>
</sourceDirectories>
<sourceCodeRetention>LAST_BUILD</sourceCodeRetention>
</io.jenkins.plugins.coverage.metrics.steps.CoverageRecorder>
