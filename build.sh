#!/bin/bash

pip3 install -r requirements.txt
pip3 install -U python-dotnet
tar -zxvf redis-5.0.8.tar.gz
cd redis-5.0.8
make
cd ../