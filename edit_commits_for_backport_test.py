'''We keep a branch that is just the whamcloud
commits on top of whamcloud tag 2.14.0. (my_bitbucket/2.14.0-llnl_upstream_only)
That branch should be directyl pushable to the
b2_14 branch of whamcloud for testing.

The problem is that there are requirements to push to that branch,
and pushing the branch created a separate, build, test and review for each commit.
Also, there are backporting requirements in general here https://wiki.whamcloud.com/display/PUB/Commit
So really, each patch in the stack need to be verified for backporting in gereral.
Also, for some patches, we may want to prevent building, testing, or maybe even having a gerrit number
made if possible.
We also add what tests to used
In the case where it should not be reviewed, put "fortestonly" in the Test-Parameters
and in those cases you also need testlist=<comma separated test names>
Also, if you have multiple Test-Parametes lines, fortestonly seems to have not effect on lines
it's not it
e.g.
Test-Parameters: trivial clientdistro=el8.4
Test_parameters: fortestonly
still ran the test trivial


'''
