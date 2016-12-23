#!/usr/bin/env bash
PYTHONPATH=$( dirname "${BASH_SOURCE[0]}" ) python -c "from config import *; print $1,"
