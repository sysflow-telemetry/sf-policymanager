#!/usr/bin/env python3
#
# Copyright (C) 2021 IBM Corporation.
#
# Authors:
# Frederico Araujo <frederico.araujo@ibm.com>
# Teryl Taylor <terylt@ibm.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from github import Github
import pygit2
import glob
import re
import os
import logging
import shutil
from kubecontroller import KubeController


def get_secret(secret_name):
    """extract secret from vault, if using a vault"""
    try:
        secrets_dir = '/run/secrets' if not (os.path.isdir('/run/secrets/k8s')) else '/run/secrets/k8s'
        with open('%s/%s' % (secrets_dir, secret_name), 'r') as secret_file:
            return secret_file.read().replace('\n', '')
    except FileNotFoundError:
        logging.error('Secret not found in %s/%s', secrets_dir, secret_name)
    except IOError:
        logging.error('Caught exception while reading secret \'%s\'', secret_name)


class PolicyProcessor:
    def __init__(self, args):
        self.policiesDir = args.policiesdir
        self.gitURL = args.gitapiurl
        self.baseRepoName = args.basereponame
        self.baseGitRepoURL = args.basegithubrepourl
        self.envType = args.envtype
        self.gitDir = 'policies'
        self.tagsEnabled = args.usetags
        self.accessToken = get_secret('github_access_token') if not args.accesstoken else args.accesstoken
        self.localInstall = args.installtype == 'local'
        self.kubeController = KubeController(self.gitDir)

    def policyExistsLocal(self):
        files = glob.glob(self.policiesDir + "/*.yaml")  # list of all .yaml files in a directory
        logging.debug(files)
        return (len(files) > 0, None)

    def policyExistsConfigMap(self):
        cm = self.kubeController.getPolicyConfigMap()
        logging.info('Received config map ')
        if cm.data:
            return (True, cm)
        return (False, None)

    def policyExists(self):
        if self.localInstall:
            return self.policyExistsLocal()
        return self.policyExistsConfigMap()

    def getConfigTagsK8sConfigMap(self, tup):
        cm = tup[1]
        tags = []
        for key, value in cm.data.items():
            logging.info('Checking configmap policy {0} for tags.'.format(key))
            for line in value.splitlines():
                firstLine = line.strip()
                logging.info('Searching {0} for version tag {1}'.format(key, firstLine))
                m = re.search('^#\[([\w\.]*)\]\[([\w\.]+)\]$', firstLine)
                if m:
                    grps = m.groups()
                    if grps and len(grps) == 2:
                        logging.info('Found tags: {0}'.format(grps))
                        tags.append(grps)
                break
        return tags

    def getConfigTags(self, tup):
        if self.localInstall:
            return self.getConfigTagsLocal()
        return self.getConfigTagsK8sConfigMap(tup)

    def getConfigTagsLocal(self):
        files = glob.glob(self.policiesDir + '/*.yaml')  # list of all .yaml files in a directory
        tags = []
        for fileName in files:
            with open(fileName, 'r') as f:
                firstLine = f.readline().strip()
                logging.debug('Searching {0} for version tag {1}'.format(fileName, firstLine))
                m = re.search('^#\[([\w\.]*)\]\[([\w\.]+)\]$', firstLine)
                if m:
                    grps = m.groups()
                    if grps and len(grps) == 2:
                        logging.debug('Found tags: {0}'.format(grps))
                        tags.append(grps)

        return tags

    def validateTags(self, tags):
        numTags = len(tags)
        if numTags == 0:
            logging.info('No tags in existing policies. Pulling down latest policies')
            return False
        tag = tags[0][0]
        sha = tags[0][1]
        for t in tags:
            if tag != t[0] or sha != t[1]:
                logging.info('Tags across all .yaml files don\'t match. Pulling down latest policies')
                logging.debug(tags)
                return False
        return True

    def tagsUpToDate(self, tags, latestGit):
        tag = tags[0][0]
        sha = tags[0][1]
        return tag == latestGit[0] and sha == latestGit[1]

    def writeLocal(self, tags, repo):
        tagName = tags[0]
        files = glob.glob(self.gitDir + '/policies/*.yaml')  # list of all .yaml files in a directory
        for fileName in files:
            with open(fileName, 'r') as original:
                data = original.read()
            with open(self.policiesDir + '/' + os.path.basename(fileName), 'w') as modified:
                modified.write('#[{0}][{1}]\n'.format(tagName, repo.head.target) + data)

    def writeConfigMap(self, tags, repo, policyExists):
        self.kubeController.writeConfigMap(tags, repo, policyExists)

    def updatePolicies(self, tags, tup):
        policyExists = tup[0]
        tagName = tags[0]
        sha = tags[1]
        gitRepo = self.baseGitRepoURL + self.envType + '.git'
        logging.info('Trying to Clone repo: {0}, with Tag: {1}, SHA {2}'.format(gitRepo, tagName, sha))
        authMethod = 'x-access-token'
        callbacks = pygit2.RemoteCallbacks(pygit2.UserPass(authMethod, self.accessToken))
        if os.path.exists(self.gitDir) and os.path.isdir(self.gitDir):
            shutil.rmtree(self.gitDir)
        repo = pygit2.clone_repository(gitRepo, self.gitDir, callbacks=callbacks)
        if tagName != '':
            remote = repo.remotes['origin']
            remote.fetch(callbacks=callbacks)
            ref = repo.lookup_reference('refs/tags/' + tagName)
            repo.checkout(ref)
        logging.info('Cloned repository and checked out  Tag: {0}, Sha: {1}'.format(tagName, repo.head.target))
        if self.localInstall:
            self.writeLocal(tags, repo)
        else:
            self.writeConfigMap(tags, repo, policyExists)

        return (tagName, repo.head.target)

    def getLatestGitTags(self):
        # Github Enterprise with custom hostname
        repoName = self.baseRepoName + self.envType
        logging.info(
            'Get Latest Git Tag, Git URL: {0}, Repo Name: {1}, Env Type: {2}'.format(
                self.gitURL, repoName, self.envType
            )
        )
        # logging.info('Access Token: {0}'.format(self.accessToken))
        g = Github(base_url=self.gitURL, login_or_token=self.accessToken)
        repo = g.get_repo(repoName)
        logging.debug(repo.git_url)
        tags = repo.get_tags()
        tagName = ''
        numTags = 0
        for tag in tags:
            logging.debug('Name: {0}, Commmit: {1}'.format(tag.name, tag.commit.sha))
            numTags += 1

        if self.tagsEnabled and numTags > 0:
            return (tags[0].name, tags[0].commit.sha)

        numCommits = repo.get_commits().totalCount
        if numCommits > 0:
            latestCommit = repo.get_commits()[0]
            if self.tagsEnabled:
                logging.warn(
                    'Tags enabled, but no tag available in repo {0}.  Returning latest commit. Latest commit: {1}'.format(
                        repo.git_url, latestCommit.sha
                    )
                )
            return ('', latestCommit.sha)
        return ('', '')
