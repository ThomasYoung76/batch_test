#!/bin/bash
PWD=`pwd`
site_package=`python3 -c "import site; print(site.getsitepackages()[0])"`
echo `pwd` > batch.pth
mv batch.pth $site_package
cd $PWD
chmod 777 $PWD/run.py