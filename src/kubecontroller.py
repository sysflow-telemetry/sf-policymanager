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

import kubernetes.client
from kubernetes.client.rest import ApiException
from pprint import pprint
import logging
import glob
import os

CONFIGMAP_NAME='sysflow-policy-config'
NAMESPACE = 'sysflow'


def get_bearer_token():
    """extract secret from vault, if using a vault"""
    try:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as secretFile:
            return secretFile.read().replace('\n', '')
    except FileNotFoundError:
        logging.error('Secret not found in /var/run/secrets/kubernetes.io/serviceaccount/token')
    except IOError as e:
        logging.error('Caught exception while reading secret /var/run/secrets/kubernetes.io/serviceaccount/token: %s' % e)

class KubeController:

    def __init__(self, gitDir):
        self.gitDir = gitDir


    def getKubeConfig(self):
        # Configure API key authorization: BearerToken
        configuration = kubernetes.client.Configuration()
        configuration.api_key['authorization'] = get_bearer_token()
        configuration.api_key_prefix['authorization'] = 'Bearer'
        configuration.host = 'https://kubernetes.default.svc'
        configuration.verify_ssl=False
        return configuration

    def getPolicyConfigMap(self):
        configuration = self.getKubeConfig()
        with kubernetes.client.ApiClient(configuration) as client:
            # Create an instance of the API class
            instance = kubernetes.client.CoreV1Api(client)
            name = CONFIGMAP_NAME # str | name of the ConfigMap
            namespace = NAMESPACE # str | object name and auth scope, such as for teams and projects
            response = None
            try:
                logging.info("Retrieving configmap {0} in {1}".format(name, namespace))
                response = instance.read_namespaced_config_map(name, namespace)
                #pprint(response)
            except ApiException as e:
                logging.error("Exception when calling CoreV1Api->read_namespaced_config_map: %s" % e)
            return response

    def createPolicyConfigMap(self, body):
        configuration = self.getKubeConfig()
        with kubernetes.client.ApiClient(configuration) as client:
            instance = kubernetes.client.CoreV1Api(client)
            namespace = NAMESPACE # str | object name and auth scope, such as for teams and projects
            try:
                response = instance.create_namespaced_config_map(namespace, body)
                #pprint(response)
            except ApiException as e:
               logging.error("Exception when calling CoreV1Api->create_namespaced_config_map: %s" % e)

    def updatePolicyConfigMap(self, body):
        configuration = self.getKubeConfig()
        with kubernetes.client.ApiClient(configuration) as client:
            instance = kubernetes.client.CoreV1Api(client)
            namespace = NAMESPACE # str | object name and auth scope, such as for teams and projects
            name = CONFIGMAP_NAME # str | name of the ConfigMap
            try:
                response = instance.replace_namespaced_config_map(name, namespace, body)
                #pprint(response)
            except ApiException as e:
               logging.error("Exception when calling CoreV1Api->replace_namespaced_config_map: %s" % e)

    def populateBody(self, body):
        body.api_version = 'v1'
        body.kind = 'ConfigMap'
        md = {}
        md['name'] = CONFIGMAP_NAME
        md['namespace'] = NAMESPACE
        body.metadata = md


    def writeConfigMap(self, tags, repo, policyExists):
        tagName = tags[0]
        files = glob.glob(self.gitDir + "/policies/*.yaml") # list of all .yaml files in a directory
        body = kubernetes.client.V1ConfigMap()
        cm = {}
        for fileName in files:
            data = ""
            with open(fileName, 'r') as original: data = original.read()
            data = "#[{0}][{1}]\n".format(tagName, repo.head.target) + data
            cm[os.path.basename(fileName)] = data
        if len(cm) > 0:
            body.data = cm
            self.populateBody(body)
            if policyExists:
                self.updatePolicyConfigMap(body)
            else:
                self.createPolicyConfigMap(body)
        else:
            logging.warn("Unable to find any policies in the policy repo!! Skipping..")
