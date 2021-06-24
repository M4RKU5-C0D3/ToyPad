#!/usr/bin/env bash
CPD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

systemctl --user $1 toypad.service
