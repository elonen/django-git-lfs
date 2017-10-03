#!/bin/bash

rm -rf _py_env test_temp 
rm -f *~
for x in "djlfs_batch" "standalone_server" "standalone_server/lfs_standalone"; do
  rm -rf $x/__pycache__ $x/build $x/dist $x/*.egg-info $x/*~ $x/db.sqlite3
done
