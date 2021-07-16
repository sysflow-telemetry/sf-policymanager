from github import Github
import pygit2
import glob
import re
import os
import sys

accessToken=sys.argv[1]
policiesDir="/mnt/policies"
gitURL = "https://github.ibm.com/api/v3"
baseRepoName = "sysflow/wh-secops-policies-"
baseGitRepoURL ="https://github.ibm.com/sysflow/wh-secops-policies-"
envType ="ris"
gitDir = "wh-secops-policies"
tagsEnabled = True

def policyConfigMapExists():
    files = glob.glob(policiesDir + "/*.yaml") # list of all .yaml files in a directory
    print(files)
    return len(files) > 0

def getConfigTags():
    print("getConfigTags")
    files = glob.glob(policiesDir + "/*.yaml") # list of all .yaml files in a directory
    tags = []
    for fileName in files:
        with open(fileName, 'r') as f:
            firstLine = f.readline().strip()
            print("Searching {0} for version tag {1}".format(fileName, firstLine))
            m = re.search("^#\[([\w\.]*)\]\[([\w\.]+)\]$", firstLine)
            if m:
                grps = m.groups()
                if grps and len(grps) == 2:
                    print("Found tags: {0}".format(grps))
                    tags.append(grps)

    return tags

def validateTags(tags):
    numTags = len(tags)
    if numTags == 0:
        print("No tags in existing policies. Pulling down latest policies")
        return False            
    tag = tags[0][0]
    sha = tags[0][1]
    for t in tags:
        if tag != t[0] or sha != t[1]:
            print("Tags across all .yaml files don't match. Pulling down latest policies")
            print(tags)
            return False
    return True

def tagsUpToDate(tags, latestGit):
    tag = tags[0][0]
    sha = tags[0][1]
    return tag

def updatePolicies(tags):
    tagName = tags[0]
    sha = tags[1]
    gitRepo = baseGitRepoURL + envType + ".git"
    print("Trying to Clone repo: {0}, with Tag: {1}, SHA {2}".format(gitRepo, tagName, sha))
    authMethod = 'x-access-token'
    callbacks = pygit2.RemoteCallbacks(pygit2.UserPass(authMethod, accessToken))
    repo = pygit2.clone_repository(gitRepo, gitDir, callbacks=callbacks)
    if tagName != '':
        remote = repo.remotes["origin"]
        remote.fetch(callbacks=callbacks)
        ref = repo.lookup_reference('refs/tags/' + tagName)
        repo.checkout(ref)
    print("Cloned repository and checked out  Tag: {0}, Sha: {1}".format(tagName, repo.head.target))
    files = glob.glob(gitDir + "/policies/*.yaml") # list of all .yaml files in a directory
    for fileName in files:
        with open(fileName, 'r') as original: data = original.read()
        with open(policiesDir + "/" + os.path.basename(fileName), 'w') as modified: modified.write("#[{0}][{1}]\n".format(tagName, repo.head.target) + data)

    return (tagName, repo.head.target)

def getLatestGitTags():
    # Github Enterprise with custom hostname
    repoName = baseRepoName + envType
    print("Get Latest Git Tag, Git URL: {0}, Access Token: {1}, Repo Name: {2}, Env Type: {3}".format(gitURL, accessToken, repoName, envType))
    g = Github(base_url=gitURL, login_or_token=accessToken)
    repo = g.get_repo(repoName)
    print(repo.git_url)
    tags = repo.get_tags()
    tagName =""
    numTags = 0
    for tag in tags:
        print("Name: {0}, Commmit: {1}".format(tag.name, tag.commit.sha))
        numTags += 1
    
    if tagsEnabled and numTags > 0:
        return (tags[0].name, tags[0].commit.sha)
    
    latestCommit = repo.head.commit
    if tagsEnabled:
        print("Tags enabled, but no tag available in repo {0}.  Returning latest commit. Latest commit: {1}".format(repo.git_url, latestCommit))
    return ('', latestCommit)

latestGit = getLatestGitTags()    
if policyConfigMapExists():
    tags = getConfigTags()
    if not validateTags(tags) or not tagsUpToDate(tags, latestGit):
        updatePolicies(latestGit)
    else:
        print("Tags: {0} SHA: {1} match github Tags: {2}, SHA: {1}".format(tags[0][0], tags[0][1], latestGit[0], latestGit[1]))
        print("No configmap update required!")
else:
    updatePolicies(latestGit)    
        



