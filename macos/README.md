# MacOS Resources

MacOS agents can be configured to run as supervised launchd processes.
By default it seems that launchd de-prioritizes processes as "background" tasks assuming that user-spawned processes are more valuable.

For our CI hosts we consider the jenkins agent process to be the most critical thing on the machine so we must give it special flags to override the default behavior.

## Swarm client or JNLP Agent

Configurations for both [swarm client plugin](https://plugins.jenkins.io/swarm) and permanent agents connecting via JNLP are provided.
Both are supported by ROS2 CI and the swarm client is recommended since deployment requires no changes to the Jenkins host.
But if you have trouble with the swarm client you may wish to use the JNLP agent.

## Preparing the Jenkins agent

Create the directory `$HOME/jenkins-agent` if it does not already exist.

If using the swarm client, download the swarm client jar from [this repository][swarm-repo] and place it in the ~/jenkins-agent directory.
We're currently using version 3.8.

For JNLP agents, the agent.jar is best downloaded from your running Jenkins. With wget installed:
```
cd ~/jenkins-agent && wget https://ci.ros2.org/jnlpJars/agent.jar
```

The agent must have at least Java JDK 8 installed.
For best results use the same version as our Jenkins master, currently `1.8.0_162`.

Download the relevant launchd plist for your agent type.

Swarm client: `cd ~/jenkins-agent && wget https://raw.githubusercontent.com/ros2/ci/configuration/macos/jenkins-swarm-client.plist`  
JNLP agent: `cd ~/jenkins-agent && wget https://raw.githubusercontent.com/ros2/ci/configuration/macos/jenkins-jnlp-agent.plist`


Both plist files contain a few fields that must be updated for the specific CI host.
To find them all run `grep REPLACE_ jenkins-agent.plist`.

They are documented here (not all fields are in both files)

- `REPLACE_HOSTNAME`: The hostname of the CI host.
- `REPLACE_AGENT_NAME`: The slug name of the CI host in the Jenkins UI without the `macos_` prefix (Example: mini2 for the machine macos_mini2).
- `REPLACE_AGENT_DESCRIPTION`: The description fof the agent in the Jenkins UI.
- `REPLACE_JNLP_SECRET`: The JNLP secret which is shown to admin users when creating the agent in the Jenkins UI.
- `REPLACE_USERNAME`: The Jenkins username of the user with node creation privileges.
- `REPLACE_PASSWORD`: The password (usually a Jenkins auth token) for the above user.
- `REPLACE_DOMAIN_ID`: The DDS domain ID to use by setting `ROS_DOMAIN_ID`.


## Installing the property list (.plist file)

Once the property list has been updated, you can install and run it with the following command.
Be sure to stop any manually started Jenkins agent before doing so.

Check to be sure the local user's LaunchAgents directory exists.

```
test -d ~/Library/LaunchAgents || mkdir -p ~/Library/LaunchAgents
```

Swarm client: `cp ~/jenkins-agent/jenkins-swarm-client.plist ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist`
JNLP agent: `cp ~/jenkins-agent/jenkins-jnlp-agent.plist ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist`

## Starting the jenkins process and configuring it to start on next boot.

To start a process via launchd use `launchctl load PATH/TO/PLIST`.
The `-w` option sets this to take effect on next boot as well.

```
launchctl load -w ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist
```

The `$HOME/jenkins-agent` directory will contain the agent `stdout.log` and `stderr.log` streams from launchd.

## Stopping the jenkins agent

```
launchctl unload ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist
```

## Disabling the jenkins agent permanently

```
launchctl unload -w ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist
rm ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist
```

[swarm-repo]: https://repo.jenkins-ci.org/releases/org/jenkins-ci/plugins/swarm-client/
