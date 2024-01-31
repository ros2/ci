This folder contains external projects which are needed to run this batch CI script.
The external projects are pulled in using `git-subtree` which allows this script to use a known version of the external projects rather than being potentially impacted by changes made to those projects which are being tested.
The Python projects, for example `orsf_pycommon`, are pulled in and updated manually using `git-subtree`.
The vendor folders are inserted to the front of the path manually to make sure this version of the projects are used.

#### Updating the subtree

The external project is in the vendor folder and is imported using subtree.
This import can be updated by following these steps:

1. From the root of the git repository run:

```
$ git remote -v
```

2. If the upstream (e.g. `https://github.com/osrf/osrf_pycommon.git`) is already remote use that remote name. Otherwise add it as a remote like so (using `osrf_pycommon` as an example):

```
$ git remote add osrf_pycommon_upstream https://github.com/osrf/osrf_pycommon.git
```

3. Now run the update command:

```
$ git subtree pull -P ros2_batch_job/vendor/osrf_pycommon --squash osrf_pycommon_upstream master
```

##### When the subtree update fails

When running `git subtree pull` git looks for a commit history in the form of:

```
    git-subtree-dir: ros2_batch_job/vendor/osrf_pycommon
    git-subtree-split: <commit-hash>
```

This can fail for many reasons and if it does it won't update the git tree.
One easy alternative is to remove and re-add the subtree but this is not great
and leaves the git subtree history a bit fuzzy.
An alternative is to manually create the squash merge and add the corresponding
commit information so future runs of `git subtree pull` can find it.

1. From the root of the git repository run:

```
$ git remote -v
```

2. If the upstream (e.g. `https://github.com/osrf/osrf_pycommon.git`) is already
remote use that remote name. Otherwise add it as a remote like so (using
`osrf_pycommon_upstream` as an example):

```
$ git remote add osrf_pycommon_upstream https://github.com/osrf/osrf_pycommon.git
```

3. Create a branch with the contents of the core repository's branch that you want to update (i.e. master):

```
$ git branch osrf_pycommon_subtreee osrf_pycommon_upstream/master
```

4. Update the core subtree:

```
$ git merge --squash -s subtree --allow-unrelated-histories --no-commit osrf_pycommon_subtreee
```

5. Commit the updates to the subtree:

```
$ git commit -s -m 'Update core subtree to <latest-subtree-commit-short-hash>.' -m 'git-subtree-dir: ros2_batch_job/vendor/osrf_pycommon' -m 'git-subtree-split: <latest-subtree-commit-hash>'
```

You can make sure future runs of `git subtree pull` will be able to find the commit by
running an the command yourself:

```
git subtree pull -P "ros2_batch_job/vendor/osrf_pycommon" --squash osrf_pycommon_upstream master
From https://github.com/osrf/osrf_pycommon
 * branch            master     -> FETCH_HEAD
Subtree is already at commit <latest--subtree-commit-hash>.
```

#### Pushing changes upstream

You can also push to the upstream after first doing a pull as described above:

```
$ git subtree push -P ros2_batch_job/vendor/osrf_pycommon osrf_pycommon_upstream master
```
