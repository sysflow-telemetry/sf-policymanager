#!/bin/bash
#
# Copyright (C) 2019 IBM Corporation.
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


if [ "$#" -ne 2 ]; then
    echo "Required arguments missing!"
    echo "Usage : ./installChart <gitapiurl> <gitrepourl>"
    echo "<gitapiurl> github api url"
    echo "<gitrepourl> URL of the git repo (please use https URL and .git suffix)"
    exit 1
fi

gitapiurl=$1
gitrepourl=$2

# Don't run if any of the prerequisites are not installed.
prerequisites=( "kubectl" "helm" )
for i in "${prerequisites[@]}"
do
  isExist=$(command -v $i)
  if [ -z "$isExist" ]
  then
    echo "$i not installed. Please install the required pre-requisites first (kubectl, helm)"
    exit 1
  fi
done

tls='--tls'
enabled='N'
tlsStatus=$(helm ls 2>&1)
if [[ "$tlsStatus" != "Error: transport is closing" ]]; then
    read -p 'Warning: Helm TLS is not enabled. Do you want to continue? [y/N] ' enabled
    if [ "$enabled" != "y" ]
    then
        echo "Setup helm TLS. Follow https://helm.sh/docs/tiller_ssl/"
        exit 1
    fi
fi

nsCreateCmd=$(kubectl create namespace sysflow 2>&1)
if [[ "$nsCreateCmd" =~ "already exists" ]]; then
    echo "Warning: Namespace 'sysflow' already exists. Proceeding with existing namespace."
else
    echo "Namespace 'sysflow' created successfully"
fi

# sf-deployments/helm/scripts/
REALPATH=$(dirname $(realpath $0))
cd $REALPATH/../charts

helm install gitops ./sf-gitops-chart -f sf-gitops-chart/values.yaml --namespace sysflow \
     --set sfgitops.gitapiurl=$gitapiurl \
     --set sfgitops.gitrepourl=$gitrepourl \
     --debug
