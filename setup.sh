#!/bin/bash

ECHO "<------ RUNNING SETUP SCRIPT ------>"

# Run subsequent setup files for specific AWS modules
scripts/cloudformation/cloudformation.sh
scripts/s3bucket/s3bucket.sh

ECHO "<------ SETUP SCRIPT COMPLETE ------>"