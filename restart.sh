#!/usr/bin/env bash
CPD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

systemctl --user restart toypad.service
systemctl --user status toypad.service
