#!/bin/bash

#  ASHRAE140-Envelope 
#  ASHRAE140-HVAC-CE100200
#  ASHRAE140-HVAC-CE300545
#  ASHRAE140-HVAC-HE100230
#  ASHRAE140-HERS
#  ASHRAE1052RP
#  HVACComponent
#  GlobalEnergyBalance
#  ASHRAE140-GrndCoup
#  MultizoneBESTEST
#  IEAMechanical
#  BlandTests


tests=(
  IEAMechanical
)


for t in "${tests[@]}"
do
  if [ "$1" != "" ]
  then
    echo "Running Simulations $t"
    cd $t
    echo "Cleaning up existing output directory $t/Outputs"
    rm -rf Outputs
    sh ./dotests.sh $1
    cd -
  fi

  python3 ./template_engine/template_engine.py config.yaml $t/Report/$t.md $t/Report/generated
  pandoc $t/Report/generated/$t.md -o $t/Report/generated/$t.html --toc --mathjax -s --mathjax=https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML -t html -N
  pandoc $t/Report/generated/$t.md -o $t/Report/generated/$t-notoc.html --mathjax -s --mathjax=https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML -t html -N
  wkhtmltopdf --footer-center [page] --javascript-delay 5000  toc $t/Report/generated/$t-notoc.html $t/Report/generated/$t.pdf

  #  cd $t/Report/generated/
#  pandoc $t.md -o $t.pdf
#  cd -
done

