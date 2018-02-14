# Windows Resources

Windows agents can be wrapped with [winsw][] to run as Windows services.

## Preparing the Jenkins agent

To set up a Windows agent requires downloading the [winsw .NET4 executable](https://github.com/kohsuke/winsw/releases/).
To keep paths as short as possible, we use the directory `C:\J` as our Jenkins home directory.

0. Copy `WinSW.NET4.exe` to the `C:\J` directory.
0. Rename `WinSW.NET4.exe` to `jenkins-swarm-client.exe`.
0. Copy `jenkins-swarm-client.xml` from this repository to the `C:\J` directory.

The file contains a few fields that must be updated for the specific CI host.
To find them all run `grep REPLACE_ jenkins-agent.plist`.

- `REPLACE_AGENT_NAME`: The slug name of the CI host in the Jenkins UI.
- `REPLACE_AGENT_DESCRIPTION`: The description fof the agent in the Jenkins UI.
- `REPLACE_USERNAME`: The Jenkins username of the user with node creation privileges.
- `REPLACE_PASSWORD`: The password (usually a GitHub auth token for us) for the above user.

## Installing the windows service

Open an administrative console window and navigate to `C:\J`
Run
```
jenkins-swarm-client.exe install
```

Open the Windows Services view (I type "services" in the Start/Search bar to find it) and find the "ROS2 CI Swarm Client" service and start it.
You can verify in the Jenkins UI that the node has come online.

[winsw]: https://github.com/kohsuke/winsw

