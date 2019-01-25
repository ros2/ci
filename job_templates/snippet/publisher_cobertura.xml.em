    <hudson.plugins.cobertura.CoberturaPublisher plugin="cobertura@@1.13">
      <coberturaReportFile>ws/build*/**/*coverage.xml</coberturaReportFile>
      <onlyStable>false</onlyStable>
      <failUnhealthy>false</failUnhealthy>
      <failUnstable>false</failUnstable>
      <autoUpdateHealth>false</autoUpdateHealth>
      <autoUpdateStability>false</autoUpdateStability>
      <zoomCoverageChart>false</zoomCoverageChart>
      <maxNumberOfBuilds>0</maxNumberOfBuilds>
      <failNoReports>false</failNoReports>
      @# CoverageTargets values consist of three decimal numbers.
      @#  First: The target value above which a build is considered "100% healthy/sunny".
      @#  Second: The target value below which a build is considered "0% healthy/stormy".
      @#  Third: The target value below which a build is considered "Unstable".
      @# The values below are the plugin defaults.
      <lineCoverageTargets>80, 0, 0</lineCoverageTargets>
      <methodCoverageTargets>80, 0, 0</methodCoverageTargets>
      <conditionalCoverageTargets>70, 0, 0</conditionalCoverageTargets>
      <healthyTarget>
        <targets class="enum-map" enum-type="hudson.plugins.cobertura.targets.CoverageMetric">
          <entry>
            <hudson.plugins.cobertura.targets.CoverageMetric>METHOD</hudson.plugins.cobertura.targets.CoverageMetric>
            <int>8000000</int>
          </entry>
          <entry>
            <hudson.plugins.cobertura.targets.CoverageMetric>LINE</hudson.plugins.cobertura.targets.CoverageMetric>
            <int>8000000</int>
          </entry>
          <entry>
            <hudson.plugins.cobertura.targets.CoverageMetric>CONDITIONAL</hudson.plugins.cobertura.targets.CoverageMetric>
            <int>7000000</int>
          </entry>
        </targets>
      </healthyTarget>
      <unhealthyTarget>
        <targets class="enum-map" enum-type="hudson.plugins.cobertura.targets.CoverageMetric">
          <entry>
            <hudson.plugins.cobertura.targets.CoverageMetric>METHOD</hudson.plugins.cobertura.targets.CoverageMetric>
            <int>0</int>
          </entry>
          <entry>
            <hudson.plugins.cobertura.targets.CoverageMetric>LINE</hudson.plugins.cobertura.targets.CoverageMetric>
            <int>0</int>
          </entry>
          <entry>
            <hudson.plugins.cobertura.targets.CoverageMetric>CONDITIONAL</hudson.plugins.cobertura.targets.CoverageMetric>
            <int>0</int>
          </entry>
        </targets>
      </unhealthyTarget>
      <failingTarget>
        <targets class="enum-map" enum-type="hudson.plugins.cobertura.targets.CoverageMetric">
          <entry>
            <hudson.plugins.cobertura.targets.CoverageMetric>METHOD</hudson.plugins.cobertura.targets.CoverageMetric>
            <int>0</int>
          </entry>
          <entry>
            <hudson.plugins.cobertura.targets.CoverageMetric>LINE</hudson.plugins.cobertura.targets.CoverageMetric>
            <int>0</int>
          </entry>
          <entry>
            <hudson.plugins.cobertura.targets.CoverageMetric>CONDITIONAL</hudson.plugins.cobertura.targets.CoverageMetric>
            <int>0</int>
          </entry>
        </targets>
      </failingTarget>
      <sourceEncoding>ASCII</sourceEncoding>
    </hudson.plugins.cobertura.CoberturaPublisher>
