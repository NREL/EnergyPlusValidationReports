#!/bin/bash

mkdir "$1.dir"
cd "$1.dir"
unzip ../"$1"
rm -rf xl/drawings/ xl/chartsheets/ xl/printerSettings/ xl/media xl/charts xl/calcChain.xml
zip -9 -r  ../"$1".zip *
cd -
mv "$1.zip" "$1"
rm -rf "$1.dir"


