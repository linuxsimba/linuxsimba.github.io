---
title: Troubleshooting Kubernetes - Failed to add Node due to MatchNodeSelector
tags:
  - kubernetes
  - troubleshooting
---

Was busy installing a pod and got an error, where the pod failed to deploy because of the `MatchNodeSelector` error.

```
# cat registry-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: registry
  labels:
    app: registry
spec:
  containers:
    - name: registry
      image: registry:2
      imagePullPolicy: Always
      ports:
        - containerPort: 5000
          hostPort: 5000
      volumeMounts:
        - mountPath: /var/lib/registry
          name: registry-volume
      readinessProbe:
        httpGet:
          path: /v2/_catalog
          port: 5000
        initialDelaySeconds: 3
        timeoutSeconds: 1
      env:
        - name: REGISTRY_STORAGE_DELETE_ENABLED
          value: "true"
  nodeSelector:
    app: ccp-registry
  volumes:
    - name: registry-volume
      hostPath:
        path: /var/lib/ccp-registry


# kubectl describe pod registry

Name:           registry
Namespace:      default
Node:           /
Labels:         app=registry
Status:         Pending
IP:
Controllers:    <none>
Containers:
  registry:
    Image:      registry:2
    Port:       5000/TCP
    Readiness:  http-get http://:5000/v2/_catalog delay=3s timeout=1s period=10s #success=1 #failure=3
    Volume Mounts:
      /var/lib/registry from registry-volume (rw)
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-9dbww (ro)
    Environment Variables:
      REGISTRY_STORAGE_DELETE_ENABLED:  true
Conditions:
  Type          Status
  PodScheduled  False
Volumes:
  registry-volume:
    Type:       HostPath (bare host directory volume)
    Path:       /var/lib/ccp-registry
  default-token-9dbww:
    Type:       Secret (a volume populated by a Secret)
    SecretName: default-token-9dbww
QoS Class:      BestEffort
Tolerations:    <none>
Events:
  FirstSeen     LastSeen        Count   From                    SubObjectPath   Type  Reason                   Message
  ---------     --------        -----   ----                    -------------   --------       ------                  -------
  4h            46m             6       {default-scheduler }                    WarningFailedScheduling        pod (registry) failed to fit in any node fit failure summary on nodes : MatchNodeSelector (4)
  5h    1s      1058    {default-scheduler }            Warning FailedScheduling      pod (registry) failed to fit in any node fit failure summary on nodes : MatchNodeSelector (5)
```

# What does MatchNodeSelector mean?

After some web searching I found a document about [Kubernetes node selection](https://kubernetes.io/docs/user-guide/node-selection/). The error reported is due to the scheduling agent error. The scheduler is unable to locate a node with the label "app=ccp-registry". _I wish it would just say that!_.

Look above at the pod definition file, `registry-pod.yaml`. It has the attribute `NodeSelector` which says `app: ccp-registry`.

So how do you view Kubernetes node labels?

# Viewing Kubernetes node Labels

```
# kubectl get nodes --show-labels
NAME      STATUS                     AGE       LABELS
k8s1      Ready,SchedulingDisabled   3d        app=ccp-registry,beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s1
k8s2      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s2
k8s3      Ready,SchedulingDisabled   3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s3
k8s4      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s4
k8s5      Ready,SchedulingDisabled   3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s5
k8s6      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s6
k8s7      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s7
k8s8      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s8
```

Notice that the ``app=ccp-registry is only on k8s1 node. This node has **scheduling disabled**. So clearly no pod will be deployed there.

# Fix: Create Node Label on the correct host

Add the appropriate label to a Kubernetes minion.

```
# kubectl labal nodes k8s2 app=ccp-registry
node "k8s2" labeled

# kubectl get nodes --show-labels
NAME      STATUS                     AGE       LABELS
k8s1      Ready,SchedulingDisabled   3d        app=ccp-registry,beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s1
k8s2      Ready                      3d        app=ccp-registry,beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s2
k8s3      Ready,SchedulingDisabled   3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s3
k8s4      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s4
k8s5      Ready,SchedulingDisabled   3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s5
k8s6      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s6
k8s7      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s7
k8s8      Ready                      3d        beta.kubernetes.io/arch=amd64,beta.kubernetes.io/os=linux,externalip=true,kubernetes.io/hostname=k8s8
```

Now the node can be properly deployed

```
# kubectl delete -f registry-pod.yaml
# kubectl create -f registry-pod.yaml
pod "registry" created
# kubectl describe pod registry
Name:           registry
Namespace:      default
Node:           k8s2/
Labels:         app=registry
Status:         Pending
IP:
Controllers:    <none>
Containers:
  registry:
    Image:      registry:2
    Port:       5000/TCP
    Readiness:  http-get http://:5000/v2/_catalog delay=3s timeout=1s period=10s #success=1 #failure=3
    Volume Mounts:
      /var/lib/registry from registry-volume (rw)
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-9dbww (ro)
    Environment Variables:
      REGISTRY_STORAGE_DELETE_ENABLED:  true
Conditions:
  Type          Status
  PodScheduled  True
Volumes:
  registry-volume:
    Type:       HostPath (bare host directory volume)
    Path:       /var/lib/ccp-registry
  default-token-9dbww:
    Type:       Secret (a volume populated by a Secret)
    SecretName: default-token-9dbww
QoS Class:      BestEffort
Tolerations:    <none>
Events:
  FirstSeen     LastSeen        Count   From                    SubObjectPath   Type  Reason           Message
  ---------     --------        -----   ----                    -------------   --------       ------          -------
  10s           10s             1       {default-scheduler }                    NormalScheduled        Successfully assigned registry to k8s2
```
