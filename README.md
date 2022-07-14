# ROS 2 CI Infrastructure

This repository contains all of the scripts and resources for running batch CI jobs of ROS 2 repositories on a Jenkins build farm.

## Setting up on a Jenkins build farm

You can run the `create_jenkins_job.py` Python3 script to create the jobs on your Jenkins build farm.
This assumes you have a Jenkins build farm with at least one Linux agent, OS X agent, and Windows agent.
However, even if you do not have the agents setup yet, you can create the jobs.

Before you run the script to create the jobs, you'll need to setup your environment according to this document:

https://github.com/ros-infrastructure/ros_buildfarm/blob/master/doc/environment.rst

This document will tell you what dependencies to install/setup like `jenkinsapi` and `ros_buildfarm`, as well as tell you how to setup authentication for Jenkins so that the script can login into your Jenkins build farm.

Once you've setup your environment, you can do a dry run with the following:

```
$ python3 create_jenkins_job.py --jenkins-url http://jenkins.example.com
```

The above will contact the Jenkins master at the provided url and try to authenticate.
If successful, it will output the changes that would be made, but not commit them.

If the changes look good, then run the same command with the `--commit` option to actually make the changes:

```
$ python3 create_jenkins_job.py --jenkins-url http://jenkins.example.com --commit
```

You can also change the default location from which these CI scripts are pulled with options `--ci-scripts-repository` and `--ci-scripts-default-branch`.
They allow you to change the default location from which to get the CI scripts, which is useful if you have forked ros2/ci.
The defaults are `git@github.com:ros2/ci.git` and `master` respectively.
The branch can be changed when running the job (it's a job parameter) to make it easy to test changes to the CI scripts using a branch on the main repository.

## Adjusting batch CI jobs

The jobs will be mostly setup, but you may need to adjust some settings for your farm.

First you'll need to look at each job configuration and make sure that the 'Label Expression' for the 'Restrict where this project can be run' option matches some build agent label or build agent name for the operating system.
For example, the default value for this in the Windows job is 'windows' because we (OSRF) run multiple Jenkins agents all with this label.
You may want your job to run on a specific Windows agent in which case you can update the label to match the agent name/label you want to use.

Another thing to check is the credentials settings.
The RTI binaries are provided by a git submodule which points to a private GitHub repository.
You'll need to setup at least one ssh key in the Jenkins Credentials plugin and add the public part of that key as a deploy key on the private GitHub repository, currently https://github.com/osrf/rticonnextdds-src.
Then on each job you'll want to make sure that this key is selected in two places.
First under the 'Source Code Management' section, there is a 'Credentials' drop down box under the 'Repositories' section.
Select the appropriate ssh key from that list.
Second, under the 'SSH Agent' option, select the same ssh key from the drop down list called 'Credentials'.
Note this option will not be there for Windows because I could not get the ssh-agent to work on Windows correctly and it is not needed anyways.


## Using the batch CI jobs

Each of the batch CI jobs have the same set of parameters.
The parameters have their own descriptions, but the main one to look at is the `CI_BRANCH_TO_TEST` parameter.
It allows you to select a branch name across all of the repositories in the `.repos` file that should be tested.
Repositories which have this branch will be switched to it, others will be left on the default branch, usually `rolling`.

### Notes about MacOS, Windows Agents

Configuration details for running the Jenkins agent process via the Jenkins Swarm Client can be found in the [configuration](https://github.com/ros2/ci/tree/configuration) branch of this repository.
