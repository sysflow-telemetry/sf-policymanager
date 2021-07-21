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
ARG UBI_VER=8.4-205
FROM registry.access.redhat.com/ubi8/ubi-minimal:${UBI_VER}

ARG VERSION=dev
ARG RELEASE=dev

# Update Labels
LABEL "name"="SysFlow Policy Manager operator"
LABEL "vendor"="SysFlow"
LABEL "maintainer"="The SysFlow team"
LABEL "documentation"="https://sysflow.readthedocs.io"
LABEL "version"="${VERSION}"
LABEL "release"="${RELEASE}"
LABEL "summary"="The SysFlow Policy Manager operator deploys processor policy updates to k8s clusters as a configmap."
LABEL "description"="The SysFlow Policy Manager operator deploys processor policy updates to k8s clusters as a configmap."
LABEL "io.k8s.display-name"="SysFlow Policy Manager Operator"
LABEL "io.k8s.description"="The SysFlow Policy Manager operator deploys processor policy updates to k8s clusters as a configmap."

# Update License
RUN mkdir /licenses
COPY ./LICENSE.md /licenses/

# Install Python environment
RUN microdnf install -y --disableplugin=subscription-manager \
        python38 && \
    microdnf -y clean all && rm -rf /var/cache/dnf && \
    mkdir -p /usr/local/lib/python3.8/site-packages  && \
    mkdir -p /tmp/build/

# working directory
WORKDIR /usr/local/sysflow/gitop

# sources
COPY src/* .

# dependencies
RUN python3 -m pip install -r requirements.txt

# environment variables
ENV TZ=UTC

ARG installtype=k8s
ENV INSTALL_TYPE=$installtype

ARG gitapiurl=
ENV GIT_API_URL=https://github.com/v3/api

ARG interval=1
ENV INTERVAL=$interval

#ARG usetags=False
#ENV USE_TAGS=$usetags

ARG exporterid=
ENV EXPORTER_ID=$exporterid

ARG nodeip=
ENV NODE_IP=$nodeip

ARG podname=
ENV POD_NAME=$podname

ARG podnamespace=
ENV POD_NAMESPACE=$podnamespace

ARG podip=
ENV POD_IP=$podip

ARG podserviceaccount=
ENV POD_SERVICE_ACCOUNT=$podserviceaccount

ARG poduuid=
ENV POD_UUID=$poduuid

ARG clusterid=
ENV CLUSTER_ID=$clusterid

# entrypoint
CMD python3 ./gitop.py --installtype=${INSTALL_TYPE} --gitapiurl=${GIT_API_URL}  \
                       --basereponame=${BASE_REPO_NAME} \
                       --basegithubrepourl=${BASE_GIT_REPO_URL} \
                       --envtype=${ENV_TYPE} \
                       --scaninterval=${INTERVAL} \
                       ${USE_TAGS:+--usetags} \
                       ${ACCESS_TOKEN:+--accesstoken} ${ACCESS_TOKEN}
