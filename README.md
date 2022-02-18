# sf-policymanager
[![Build Status](https://img.shields.io/github/workflow/status/sysflow-telemetry/sf-policymanager/ci)](https://github.com/sysflow-telemetry/sf-policymanager/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/sysflowtelemetry/sf-policymanager)](https://hub.docker.com/r/sysflowtelemetry/sf-policymanager)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/sysflow-telemetry/sf-policymanager)
[![Documentation Status](https://readthedocs.org/projects/sysflow/badge/?version=latest)](https://sysflow.readthedocs.io/en/latest/?badge=latest)
[![GitHub](https://img.shields.io/github/license/sysflow-telemetry/sf-policymanager)](https://github.com/sysflow-telemetry/sf-policymanager/blob/master/LICENSE.md)

# Supported tags and respective `Dockerfile` links

-	[`0.4.0`, `latest`](https://github.com/sysflow-telemetry/sf-policymanager/blob/0.4.0/Dockerfile), [`edge`](https://github.com/sysflow-telemetry/sf-policymanager/blob/master/Dockerfile), [`dev`](https://github.com/sysflow-telemetry/sf-policymanager/blob/dev/Dockerfile)

> Note: This is an experimental utility.

# Quick reference

-	**Documentation**:  
	[the SysFlow Documentation](https://sysflow.readthedocs.io)
  
-	**Where to get help**:  
	[the SysFlow Community Slack](https://join.slack.com/t/sysflow-telemetry/shared_invite/enQtODA5OTA3NjE0MTAzLTlkMGJlZDQzYTc3MzhjMzUwNDExNmYyNWY0NWIwODNjYmRhYWEwNGU0ZmFkNGQ2NzVmYjYxMWFjYTM1MzA5YWQ)

-	**Where to file issues**:  
	[the github issue tracker](https://github.com/sysflow-telemetry/sysflow/issues) (include the `sf-policymanager` tag)

-	**Source of this description**:  
	[repo's readme](https://github.com/sysflow-telemetry/sf-policymanager/edit/master/README.md) ([history](https://github.com/sysflow-telemetry/sf-policymanager/commits/master))

-	**Docker images**:  
	[docker hub](https://hub.docker.com/u/sysflowtelemetry) | [GHCR](https://github.com/orgs/sysflow-telemetry/packages)

# What is SysFlow?

The SysFlow Telemetry Pipeline is a framework for monitoring cloud workloads and for creating performance and security analytics. The goal of this project is to build all the plumbing required for system telemetry so that users can focus on writing and sharing analytics on a scalable, common open-source platform. The backbone of the telemetry pipeline is a new data format called SysFlow, which lifts raw system event information into an abstraction that describes process behaviors, and their relationships with containers, files, and network. This object-relational format is highly compact, yet it provides broad visibility into container clouds. We have also built several APIs that allow users to process SysFlow with their favorite toolkits. Learn more about SysFlow in the [SysFlow specification document](https://sysflow.readthedocs.io/en/latest/spec.html).

The SysFlow framework consists of the following sub-projects:

- [sf-apis](https://github.com/sysflow-telemetry/sf-apis) provides the SysFlow schema and programatic APIs in go, python, and C++.
- [sf-collector](https://github.com/sysflow-telemetry/sf-collector) monitors and collects system call and event information from hosts and exports them in the SysFlow format using Apache Avro object serialization.
- [sf-processor](https://github.com/sysflow-telemetry/sf-processor) provides a performance optimized policy engine for processing, enriching, filtering SysFlow events, generating alerts, and exporting the processed data to various targets.
- [sf-exporter](https://github.com/sysflow-telemetry/sf-exporter) exports SysFlow traces to S3-compliant storage systems for archival purposes.
- [sf-deployments](https://github.com/sysflow-telemetry/sf-deployments) contains deployment packages for SysFlow, including Docker, Helm, and OpenShift.
- [sysflow](https://github.com/sysflow-telemetry/sysflow) is the documentation repository and issue tracker for the SysFlow framework.

# About This Image

This image packages the SysFlow Policy Manager operator, which manages policies mapped from a git repository for k8s deployments.

# License

View [license information](https://github.com/sysflow-telemetry/sf-policymanager/blob/master/LICENSE.md) for the software contained in this image.

As with all Docker images, these likely also contain other software which may be under other licenses (such as Bash, etc from the base distribution, along with any direct or indirect dependencies of the primary software being contained).

As for any pre-built image usage, it is the image user's responsibility to ensure that any use of this image complies with any relevant licenses for all software contained within.
