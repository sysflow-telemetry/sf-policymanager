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

#
# Watches for updates to a github policy repo, and pushes them either to a
# configmap (k8s) or to a local policy directory.
#
# Instructions:
#      ./policymanager.py -h for help and command line options
#

import sys
import logging, argparse
from policyprocessor import PolicyProcessor
from executor import PeriodicExecutor

HEALTH = logging.CRITICAL + 10


def run_tests(args):
    return True


def install(args):
    policyProcessor = PolicyProcessor(args)
    latestGit = policyProcessor.getLatestGitTags()
    tup = policyProcessor.policyExists()
    if tup[0]:
        tags = policyProcessor.getConfigTags(tup)
        if not policyProcessor.validateTags(tags) or not policyProcessor.tagsUpToDate(tags, latestGit):
            policyProcessor.updatePolicies(latestGit, tup)
        else:
            logging.info(
                'Tags: {0} SHA: {1} match github Tags: {2}, SHA: {1}'.format(
                    tags[0][0], tags[0][1], latestGit[0], latestGit[1]
                )
            )
            logging.info('No configmap update required!')
    else:
        policyProcessor.updatePolicies(latestGit, tup)


def get_runner(installtype):
    """
    Returns the main logic for main thread. Must be only invoked in starting
    thread and not reentrantable.
    """
    if installtype == 'local':
        return install
    elif installtype == 'k8s':
        return install
    raise argparse.ArgumentTypeError('Unknown install type.')


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == '__main__':
    # setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]\t%(message)s')
    logging.addLevelName(level=HEALTH, levelName='HEALTH')
    logging.info('Read configuration from \'%s\'; logging to \'%s\'' % ('stdin', 'stdout'))
    # set command line args
    parser = argparse.ArgumentParser(
        description='gitop: monitors policy files in github, and updates kubernetes policy configmap on updates.'
    )
    parser.add_argument(
        '--installtype',
        help='type of installation: either local (local file)  or k8s (configmap)',
        default='k8s',
        choices=['local', 'k8s'],
    )
    parser.add_argument(
        '--policiesdir', help='location of policy files to be written in local mode', default='/mnt/policies'
    )
    parser.add_argument('--gitapiurl', help='github restapi URL for monitoring.', default='https://github.com/v3/api')
    parser.add_argument(
        '--githubrepourl',
        help='URL of the git repo to monitor (please use https URL with .git suffix)',
        default=None,
    )
    parser.add_argument(
        '--usetags',
        help='when present, gitoperator will only reload when it sees a new tag in the rep. Otherwise, it reloads on a new commit',
        action='store_true',
    )
    parser.add_argument(
        '--accesstoken',
        help='github user access token.  User should only have read rights on the repo for best security',
        default=None,
    )
    parser.add_argument('--scaninterval', help='interval between github scans in minutes', type=float, default=60)

    # parse args and configuration
    args = parser.parse_args()
    logging.info(
        'Running policymanager with install type {0}, gitapiurl {1}, githubrepourl {2}, and usetags {3}'.format(
            args.installtype, args.gitapiurl, args.githubrepourl, args.usetags
        )
    )

    try:
        if run_tests(args):
            logging.log(level=HEALTH, msg='Health checks: passed')
            exporter = PeriodicExecutor(args.scaninterval * 60, get_runner(args.installtype), [args])
            exporter.run()
        else:
            logging.log(level=HEALTH, msg='Health checks: failed')
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        logging.exception('Error while executing policymanager')
    else:
        sys.exit(0)
