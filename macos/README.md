# MacOS Resources

MacOS agents can be configured to run as supervised launchd processes.
By default it seems that launchd de-prioritizes processes as "background" tasks assuming that user-spawned processes are more valuable.

For our CI hosts we consider the jenkins agent process to be the most critical thing on the machine so we must give it special flags to override the default behavior.

## Preparing the Jenkins agent property list

The agent plist was written when dosa was reimaged December 2017 and updated to use the Swarm client in Feb 2018.
It expects that the directory `$HOME/jenkins-agent` exists and that it contains the Jenkins agent program `swarm-client-3.8.jar`.
If you need the swarm client, which when combined with the [Swarm plugin](https://plugins.jenkins.io/swarm) allows for easier addition and removal of temporary Jenkins nodes, you can get it from [this repository](https://repo.jenkins-ci.org/releases/org/jenkins-ci/plugins/swarm-client/).
This directory will also contain the agent `stdout.log` and `stderr.log` streams from launchd.

The file contains a few fields that must be updated for the specific CI host.
To find them all run `grep REPLACE_ jenkins-agent.plist`.

They are documented here

- `REPLACE_HOSTNAME`: The hostname of the CI host.
- `REPLACE_AGENT_NAME`: The slug name of the CI host in the Jenkins UI.
- `REPLACE_AGENT_DESCRIPTION`: The description fof the agent in the Jenkins UI.
- `REPLACE_USERNAME`: The Jenkins username of the user with node creation privileges.
- `REPLACE_PASSWORD`: The password (usually a GitHub auth token for us) for the above user.
- `REPLACE_DOMAIN_ID`: The DDS domain ID to use by setting `ROS_DOMAIN_ID`.


## Installing the jenkins agent property list (.plist file)

Once the property list has been updated, you can install and run it with the following command.
Be sure to stop any manually started Jenkins agent before doing so.

Check to be sure the local user's LaunchAgents directory exists.

```
test -d ~/Library/LaunchAgents || mkdir -p ~/Library/LaunchAgents
```

```
cp ~/jenkins-agent/jenkins-agent.plist ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist
launchctl load -w ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist
```

## Stopping the jenkins agent

```
launchctl unload ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist
```

## Disabling the jenkins agent permanently

```
launchctl unload -w ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist
rm ~/Library/LaunchAgents/org.ros2.ci.REPLACE_HOSTNAME-agent.plist
```
