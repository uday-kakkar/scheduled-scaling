# kubernetes-scheduled-scaler

For automated scheduled scaling of kubernetes pods we need a solution that treats existing kube deployments as black box and defines a spec/manifest that can schedule the pods at defined target levels. The second part of this effort it to orchestrate the manifest files/specs that use cron syntax to schedule the pods scaling action.


## Introduction

In order to use the ScheduledScaler you will need to install the CRD and deploy the Scaling Controller into your Kubernetes cluster. The details about the scaling solution implementation can be found on [Scaling Solution](https://ssense.atlassian.net/wiki/spaces/TD/pages/1481015321/Automated+Scheduled+Scaling+Decision ) confluence page.

## Prerequisites

- Kubernetes 1.13+


## Installing the Chart

To install the chart with the release name `scheduled-scaler`:

```console
$ helm iinstall -n scheduled-scaler helm
```

The command deploys Scheduled-scaling CRD resource on the Kubernetes cluster in the default configuration.

RBAC role/rolebinding creation
RBAC resources are enabled by default. To disable RBAC do the following:

```
$ helm install . -n scheduled-scaler --set rbac.create=false
```

## Scheduled Scaler Spec

> **Note:** This controller uses the following [Cron Expression Format](https://godoc.org/github.com/robfig/cron#hdr-CRON_Expression_Format)

### HPA

```yaml
apiVersion: "scaling.k8s.restdev.com/v1alpha1"
kind: ScheduledScaler
metadata:
  name: my-scheduled-scaler-1
spec:
  timeZone: America/Los_Angeles
  target:
    kind: HorizontalPodAutoscaler
    name: my-hpa
    apiVersion: autoscaling/v1
  steps:
  #run at 5:30am PST
  - runat: '0 30 5 * * *'
    mode: range
    minReplicas: 1
    maxReplicas: 5
```

## Options

| Option | Description | Required |
|--|--|--|
| spec.timeZone | Timezone to run crons in | False |
| spec.target.kind | Type of target (InstanceGroup/HorizontalPodAutoscaler) | True
| spec.target.name | Name of the target resource | True
| spec.target.apiVersion | API Version of the target | True
| spec.steps | List of steps | True
| spec.steps[].runat | Cronjob time string (gocron) | True
| spec.steps[].mode | Type of scaling to run (fixed/range) | True
| spec.steps[].replicas | Defined if mode is 'fixed' | False
| spec.steps[].minReplicas | Defined if mode is 'range' | False
| spec.steps[].maxReplicas | Defined if mode is 'range' | False

Note: Not all the options here need to be exposed via Jenkins / these are for documentation purpose and will be exposed on as needed basis.

## Architecture
The overall architecture is to use Jenkins pipeline to pass parameters in order to trigger a pythonic generate-kube spec job that will produce HPA spec files for Single Or multiple microservices.

The objective is to data drive the spec creation via templates.
So we have 3 tmplates:
1. template-scaleup-replicas : To scale up an existing bumped up minReplica for single / multiple microservices
2. template-scaledown-replicas : To scale down an existing bumped up minReplica for single / multiple microservices
3. template-scaleup-down-replicas : When we want tpo define both scale up and down activity we can use this template that in turn will produce both scape up and scale down specs

### Single / Multiple microservice solution
The solution shall scale for single as well as multiple microservices. if a single named microservice is selected , it will produce and apply specs Only for that ms , Otherwise a preconfigured declarative config can be used (example htl-spec.yml) that can in bulk produce and apply specs for many microservices at once

## Jenkins Automation

Jenkins will have two jobs. One for Single Microservice Scaling
Second for multiple microservices scaling as per a template

### Jenkins Parameters Definition
TODO (Define params)