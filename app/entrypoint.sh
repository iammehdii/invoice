#!/bin/bash

ray start --head --num-cpus 2 --include-dashboard false
sleep 1
serve run serve:deployment
