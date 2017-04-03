#!/usr/bin/env bash
kubectl create -f ./bot-secrets.yaml
kubectl create -f ./bot-pod.yaml
kubectl get pods,secrets
