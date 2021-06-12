#!/usr/bin/env bash
set -e
CPD="$(dirname $(readlink $0 || echo $0))"

echo "$0 : $@"
