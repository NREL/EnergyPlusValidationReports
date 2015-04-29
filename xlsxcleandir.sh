#!/bin/bash

cd $1
find . -name "*.xlsx" | xargs -I '{}' -n1 ../xlsxclean.sh '{}'
cd -
