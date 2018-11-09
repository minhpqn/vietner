#!/usr/bin/env bash


cur_dir=`cd $(dirname $0) && pwd`

ABSPATH=$( cd $(dirname $1); pwd)/$(basename $1)

cd $cur_dir

cd ./RDRsegmenter

java RDRsegmenter $ABSPATH

