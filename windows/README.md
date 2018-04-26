# Windows Resources

Windows agents are wrapped with [winsw][] to run as Windows services.

## Swarm client or JNLP Agent

Configurations for both [swarm client plugin](https://plugins.jenkins.io/swarm) and permanent agents connecting via JNLP are provided.
Both are supported by ROS2 CI and the swarm client is recommended since deployment requires no changes to the Jenkins host.
But if you have trouble with the swarm client you may wish to use the JNLP agent.

## Preparing the Jenkins agent

To keep paths as short as possible, we use the directory `C:\J` as our Jenkins home directory because of path length limitations on Windows.

To register our agent as a windows service we use the [winsw .NET4 executable](https://github.com/kohsuke/winsw/releases/) wrapper utility.

If using the swarm client, download the swarm client jar from [this repository][swarm-repo] and place it in the `C:\J` directory.
We're currently using version 3.8.

For JNLP agents, the agent.jar is best downloaded from your running Jenkins.
In a browser on the host visit https://ci.ros2.org/jnlpJars/agent.jar and download the agent.jar file to `C:\J`.

Copy `WinSW.NET4.exe` to the `C:\J` directory.

#### For the swarm client

* Rename `WinSW.NET4.exe` to `jenkins-swarm-client.exe`.
* Copy `jenkins-swarm-client.xml` from this repository to the `C:\J` directory.

#### For the JNLP agent

* Rename `WinSW.NET4.exe` to `jenkins-jnlp-agent.exe`.
* Copy `jenkins-jnlp-agent.xml` from this repository to the `C:\J` directory.

The file contains a few fields that must be updated for the specific CI host.
To find them all run `grep REPLACE_ jenkins-agent.plist`.

- `REPLACE_AGENT_NAME`: The slug name of the CI host in the Jenkins UI without the `windows_` prefix (Example: windshield for windows_windshield).
- `REPLACE_AGENT_DESCRIPTION`: The description of the agent in the Jenkins UI.
- `REPLACE_USERNAME`: The Jenkins username of the user with node creation privileges.
- `REPLACE_PASSWORD`: The password (usually a Jenkins auth token) for the above user.
- `REPLACE_JNLP_SECRET`: The JNLP secret for this host visible to admins in the Jenkins UI.

## Installing the windows service

Open an administrative console window and navigate to `C:\J`

Swarm client: Run `jenkins-swarm-client.exe install`
JNLP agent: Run `jenkins-jnlp-agent.exe install`

Open the Windows Services view (I type "services" in the Start/Search bar to find it) and find the "ROS2 CI Swarm Client" or "ROS2 CI JNLP Agent" service and start it.
You can verify in the Jenkins UI that the node has come online.

[winsw]: https://github.com/kohsuke/winsw
[swarm-repo]: https://repo.jenkins-ci.org/releases/org/jenkins-ci/plugins/swarm-client/
