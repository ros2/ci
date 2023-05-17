@# RECOVERY PROCESS SNIPPET
@# This adds 
@# 

@{
code = FILE('scripts/add_recovery_label_on_regex')
}@

<org.jenkinsci.plugins.postbuildscript.PostBuildScript plugin="postbuildscript@2.9.1">
    <config>
    <scriptFiles/>
    <groovyScripts/>
    <buildSteps>
        <org.jenkinsci.plugins.postbuildscript.model.PostBuildStep>
            <results>
                <string>FAILURE</string>
            </results>
            <role>BOTH</role>
            @# Groovy script that changes label of node to recovery-process if regex found in log
            @()
            @(SNIPPET(
                'system_groovy_script_block',
                command=code,
            ))@
            @# Schedules a shutdown after 1 min of the agent
            <hudson.tasks.Shell>
            @[if os_name not in ['windows']]@
                <command>sudo shutdown -r +1</command>
            @[endif]@
            @[if os_name in ['windows']]@
                @# TODO: 
                <command>shutdown /r /t 600</command>
            @[endif]@
            <configuredLocalRules/>
            </hudson.tasks.Shell>
        </org.jenkinsci.plugins.postbuildscript.model.PostBuildStep>
    </buildSteps>
    </config>
</org.jenkinsci.plugins.postbuildscript.PostBuildScript plugin="postbuildscript@2.9.1">

@# Rebuilds job if regex is matched
<com.chikli.hudson.plugin.naginator.NaginatorPublisher plugin="naginator@1.18">
    <regexpForRerun>@ESCAPE(regex)</regexpForRerun>
    <rerunIfUnstable>false</rerunIfUnstable>
    <rerunMatrixPart>false</rerunMatrixPart>
    <checkRegexp>true</checkRegexp>
    <regexpForMatrixStrategy>TestParent</regexpForMatrixStrategy>
    <delay class="com.chikli.hudson.plugin.naginator.FixedDelay">
        <delay>70</delay>
    </delay>
    <maxSchedule>1</maxSchedule>
</com.chikli.hudson.plugin.naginator.NaginatorPublisher>