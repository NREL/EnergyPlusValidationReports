cmake_minimum_required(VERSION 2.8.11)
find_package(PythonInterp 3.0 REQUIRED)

find_program(WKHTMLTOPDF_EXECUTABLE wkhtmltopdf)

set(ENERGYPLUS_PATH "" CACHE PATH "EnergyPlus installation being validated")
set(ENERGYPLUS_VERSION "" CACHE STRING "EnergyPlus version being validated")


# wkhtmltopdf
execute_process(COMMAND ${WKHTMLTOPDF_EXECUTABLE} -V 
  OUTPUT_VARIABLE wkhtmltopdfversionout)

string(REGEX MATCH "([0-9]+\\.?)+" WKHTMLTOPDF_VER "${wkhtmltopdfversionout}")
string(FIND "${wkhtmltopdfversionout}" "with patched qt" WKHTMLTOPDF_PATCHEDQT )


if (WKHTMLTOPDF_VER VERSION_LESS "0.12.2.1")
  message(FATAL_ERROR "wkhtmltopdf version 0.12.2.1 or greater required")
endif()

if (WKHTMLTOPDF_PATCHEDQT LESS "0")
  message(FATAL_ERROR "wkhtmltopdf with special patchedqt build required")
endif()

# pandoc

find_program(PANDOC_EXECUTABLE pandoc)

file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/Products)

execute_process(COMMAND ${PANDOC_EXECUTABLE} -v 
  OUTPUT_VARIABLE pandocversionout)

string(REGEX MATCH "([0-9]+\\.?)+" PANDOC_VER "${pandocversionout}")

if (PANDOC_VER VERSION_LESS "1.13.2")
  message(FATAL_ERROR "pandoc version 1.13.2 or greater required")
endif()


if (${CMAKE_CURRENT_BINARY_DIR} STREQUAL ${CMAKE_CURRENT_SOURCE_DIR})
  message(FATAL_ERROR "Refusing to build in source dir")
endif()

function(AddSimulation reportName)

endfunction()

function(AddReport reportName)

  list(LENGTH ARGN sheetslens)

  add_custom_target(${reportName}_simulations ALL)

  set(compiled_sheets "")

  if (sheetslens GREATER 0)
    math(EXPR sheetsrange "${sheetslens} - 1")
    math(EXPR maxsheetsrange "${sheetsrange} - 1")

    set(lastxlsxname "")
    set(sheetnames "")

    foreach(xlsxindex RANGE 0 ${sheetsrange} 2)
      math(EXPR sheetindex "${xlsxindex} + 1")
      list(GET ARGN ${xlsxindex} xlsxname)
      list(GET ARGN ${sheetindex} sheetname)


      if ((NOT xlsxname STREQUAL lastxlsxname AND NOT lastxlsxname STREQUAL "") OR xlsxindex EQUAL maxsheetsrange)
        if (xlsxindex EQUAL maxsheetsrange)
          list(APPEND sheetnames ${sheetname})
        endif()


        add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${lastxlsxname}.cache"
          COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/template_engine/sheet_compiler.py  ${ENERGYPLUS_VERSION} ${CMAKE_CURRENT_SOURCE_DIR}/${reportName}/Report/${reportName}.md ${CMAKE_CURRENT_BINARY_DIR}/${reportName} ${lastxlsxname} ${sheetnames}
          COMMAND ${CMAKE_COMMAND} -E touch "${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${lastxlsxname}.cache"
          DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${reportName}/${xlsxname} ${CMAKE_CURRENT_SOURCE_DIR}/template_engine/template_engine_impl.py ${CMAKE_CURRENT_SOURCE_DIR}/template_engine/sheet_compiler.py ${CMAKE_CURRENT_SOURCE_DIR}/${reportName}/${lastxlsxname} ${reportName}_simulations)
        list(APPEND compiled_sheets "${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${lastxlsxname}.cache")
        set(sheetnames ${sheetname})
      else()
        list(APPEND sheetnames ${sheetname})
      endif()

      set(lastxlsxname ${xlsxname})

    endforeach()
  endif()

  configure_file(${CMAKE_CURRENT_SOURCE_DIR}/index.html.in ${CMAKE_CURRENT_BINARY_DIR}/Products/index.html)

  add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}.md
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/template_engine/template_engine.py ${ENERGYPLUS_VERSION} ${CMAKE_CURRENT_SOURCE_DIR}/${reportName}/Report/${reportName}.md ${CMAKE_CURRENT_BINARY_DIR}/${reportName}
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${reportName}/Report/${reportName}.md  ${CMAKE_CURRENT_SOURCE_DIR}/template_engine/template_engine_impl.py ${CMAKE_CURRENT_SOURCE_DIR}/template_engine/template_engine.py ${reportName}_simulations ${compiled_sheets})

  add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}/${reportName}-${ENERGYPLUS_VERSION}.html
    COMMAND ${PANDOC_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}.md -o ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}-${ENERGYPLUS_VERSION}.html --toc --mathjax -s --mathjax=https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML -t html -N -H ${CMAKE_CURRENT_SOURCE_DIR}/header.html -A ${CMAKE_CURRENT_SOURCE_DIR}/footer.html
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}/media
    COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}/generated_media
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/media ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}/media
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/generated_media ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}/generated_media
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}-${ENERGYPLUS_VERSION}.html ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${reportName}
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}.md ${CMAKE_CURRENT_SOURCE_DIR}/header.html ${CMAKE_CURRENT_SOURCE_DIR}/footer.html)

  add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}-notoc.html
    COMMAND ${PANDOC_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}.md -o ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}-notoc.html --mathjax -s --mathjax=https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML -t html -N -H ${CMAKE_CURRENT_SOURCE_DIR}/header.html -A ${CMAKE_CURRENT_SOURCE_DIR}/footer.html
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}.md ${CMAKE_CURRENT_SOURCE_DIR}/header.html ${CMAKE_CURRENT_SOURCE_DIR}/footer.html)

  add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}-${ENERGYPLUS_VERSION}.pdf
    COMMAND ${WKHTMLTOPDF_EXECUTABLE} --page-size Letter --load-error-handling abort --load-media-error-handling abort --minimum-font-size 3 --footer-center [page] --javascript-delay 20000  toc ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}-notoc.html ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}-${ENERGYPLUS_VERSION}.pdf 
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}-notoc.html)


  add_custom_target(${reportName}
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${reportName}.md ${reportName}_simulations)

  add_custom_target(${reportName}_html ALL
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}/${reportName}-${ENERGYPLUS_VERSION}.html ${reportName})

  add_custom_target(${reportName}_pdf ALL
    DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/Products/${reportName}-${ENERGYPLUS_VERSION}.pdf ${reportName})



endfunction()



Function(AddSimulation reportName inputName outputName weatherFile)
  set(completeInputName ${CMAKE_CURRENT_SOURCE_DIR}/${reportName}/${inputName})
  set(completeOutputName  ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${outputName})
  set(idfName ${completeInputName}.idf)
  set(csvName ${completeOutputName}.csv)
  set(completeWeatherFile ${CMAKE_CURRENT_SOURCE_DIR}/WeatherData/${weatherFile})

  if (weatherFile STREQUAL "")
    add_custom_command(OUTPUT ${csvName}
      COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/epsim.py ${completeInputName} ${completeOutputName} "${ENERGYPLUS_PATH}"
      DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/epsim.py ${idfName} )
  else()
    add_custom_command(OUTPUT ${csvName}
      COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/epsim.py ${completeInputName} ${completeOutputName} ${completeWeatherFile} "${ENERGYPLUS_PATH}"
      DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/epsim.py ${completeWeatherFile} ${idfName} )
  endif()


  string(REPLACE "/" "_" simpleName ${inputName})
  string(REPLACE "Inputs_" "" simpleName ${simpleName})
  add_custom_target(${reportName}_${simpleName} DEPENDS ${csvName})
  add_dependencies(${reportName}_simulations ${reportName}_${simpleName})
EndFunction()

Function(AddBlandSimulation reportName idf1 idf2 rvi outputName weatherFile)
  set(completeIdf1 ${CMAKE_CURRENT_SOURCE_DIR}/${reportName}/${idf1})
  set(completeIdf2 ${CMAKE_CURRENT_SOURCE_DIR}/${reportName}/${idf2})
  set(completeRvi ${CMAKE_CURRENT_SOURCE_DIR}/${reportName}/${rvi})
  set(completeOutputName  ${CMAKE_CURRENT_BINARY_DIR}/${reportName}/${outputName})
  set(csvName ${completeOutputName}.csv)
  set(completeWeatherFile ${CMAKE_CURRENT_SOURCE_DIR}/WeatherData/${weatherFile})

  # Disable the use of the RVI, it was accidentally disabled in GARD scripts,
  # this duplicates their behavior
  add_custom_command(OUTPUT ${csvName}
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/epsim.py ${completeIdf1} ${completeIdf2} "" ${completeOutputName} ${completeWeatherFile} "${ENERGYPLUS_PATH}"
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/epsim.py ${completeWeatherFile} ${completeIdf1} ${completeIdf2} )

  string(REPLACE "/" "_" simpleName ${outputName})
  string(REPLACE "Output_" "" simpleName ${simpleName})
  string(REPLACE " " "_" simpleName ${simpleName})
  add_custom_target(${reportName}_${simpleName} DEPENDS ${csvName})
  add_dependencies(${reportName}_simulations ${reportName}_${simpleName})
EndFunction()



# Public 
AddReport(ASHRAE140-Envelope)
AddReport(ASHRAE140-HVAC-CE100200)
AddReport(ASHRAE140-HVAC-CE300545 "NREL Xcomp Charts-With Revised Performance Curves-NoLinks.xlsx" "Tdata" "NREL Xcomp Charts-With Revised Performance Curves-NoLinks.xlsx" "Rdata" "NREL Xcomp Charts-With Revised Performance Curves-NoLinks.xlsx" "Qdata")
AddReport(ASHRAE140-HVAC-HE100230)
AddReport(ASHRAE140-HERS)
AddReport(ASHRAE1052RP)
AddReport(HVACComponent)
AddReport(GlobalEnergyBalance)
AddReport(ASHRAE140-GrndCoup)
AddReport(MultizoneBESTEST)
AddReport(IEAMechanical "hcoilcomp_AllResults_May26_2008-EnergyPlusResultsOnlyB.xlsx" "HX100" "hcoilcomp_AllResults_May26_2008-EnergyPlusResultsOnlyB.xlsx" "HX120" "hcoilcomp_AllResults_May26_2008-EnergyPlusResultsOnlyB.xlsx" "HX200" "hcoilcomp_AllResults_May26_2008-EnergyPlusResultsOnlyB.xlsx" "HX220" "hcoilcomp_AllResults_May26_2008-EnergyPlusResultsOnlyB.xlsx" "HX300" "hcoilcomp_AllResults_May26_2008-EnergyPlusResultsOnlyB.xlsx" "HX320" "hcoilcomp_AllResults_May26_2008-EnergyPlusResultsOnlyB.xlsx" "HX400" "hcoilcomp_AllResults_May26_2008-EnergyPlusResultsOnlyB.xlsx" "HX420" "coilcomp_AllResults_May26_2008-With EplusResults-ShortenedB.xlsx" "Case100" "coilcomp_AllResults_May26_2008-With EplusResults-ShortenedB.xlsx" "Case120" "coilcomp_AllResults_May26_2008-With EplusResults-ShortenedB.xlsx" "Case140" "coilcomp_AllResults_May26_2008-With EplusResults-ShortenedB.xlsx" "Case160" "coilcomp_AllResults_May26_2008-With EplusResults-ShortenedB.xlsx" "Case200" "coilcomp_AllResults_May26_2008-With EplusResults-ShortenedB.xlsx" "Case220" "coilcomp_AllResults_May26_2008-With EplusResults-ShortenedB.xlsx" "Case240" "coilcomp_AllResults_May26_2008-With EplusResults-ShortenedB.xlsx" "Case260")
#AddReport(IEAMechanical)


# Internal
AddReport(BlandTests)
AddReport(CEN13791)
AddReport(CIBSE_TM33)
AddReport(MultizoneBESTESTWithAirflow)
AddReport(Shading)

# Simulations


AddSimulation(ASHRAE1052RP "Inputs/SSConv-1surface" "Outputs/SSConv-1surface" "SSConvTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/SSCond" "Outputs/SSCond" "SSCondTM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/TC1-TS6" "Outputs/TC1-TS6" "TC1TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/TC1-10cmInsul-TS6" "Outputs/TC1-10cmInsul-TS6" "TC1TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/TC2-TS6" "Outputs/TC2-TS6" "TC2TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/TC3-TS6" "Outputs/TC3-TS6" "TC3TM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/ExtSolRad" "Outputs/ExtSolRad" "ExtSolRadTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/ExtSolRad-East" "Outputs/ExtSolRad-East" "ExtSolRadTM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/SolRadGlazing" "Outputs/SolRadGlazing" "SolRadGlazingTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/SolRadGlazing-East" "Outputs/SolRadGlazing-East" "SolRadGlazing-EastTM2.epw")


AddSimulation(ASHRAE1052RP "Inputs/SolRadShade-South-NoShade" "Outputs/SolRadShade-South-NoShade" "SolRadShade-SouthTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/SolRadShade-South-Horiz" "Outputs/SolRadShade-South-Horiz" "SolRadShade-SouthTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/SolRadShade-South-Vert" "Outputs/SolRadShade-South-Vert" "SolRadShade-SouthTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/SolRadShade-South-HorVer" "Outputs/SolRadShade-South-HorVer" "SolRadShade-SouthTM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/SolRadShade-West-NoShade" "Outputs/SolRadShade-West-NoShade" "SolRadShade-WestTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/SolRadShade-West-Horiz" "Outputs/SolRadShade-West-Horiz" "SolRadShade-WestTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/SolRadShade-West-Vert" "Outputs/SolRadShade-West-Vert" "SolRadShade-WestTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/SolRadShade-West-HorVer" "Outputs/SolRadShade-West-HorVer" "SolRadShade-WestTM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/Infil-1" "Outputs/Infil-1" "Infil-1TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/Infil-2" "Outputs/Infil-2" "Infil-2TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/Infil-2-TwoNorthWalls" "Outputs/Infil-2-TwoNorthWalls" "Infil-2TM2.epw")


AddSimulation(ASHRAE1052RP "Inputs/IntHeatGain-50Rad-2XWall-TS6-OpenZone" "Outputs/IntHeatGain-50Rad-2XWall-TS6-OpenZone" "ExtSolRadTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntHeatGain-100Rad-2XWall-TS6-OpenZone" "Outputs/IntHeatGain-100Rad-2XWall-TS6-OpenZone" "ExtSolRadTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntHeatGain-100Conv-2XWall-TS6-OpenZone" "Outputs/IntHeatGain-100Conv-2XWall-TS6-OpenZone" "ExtSolRadTM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/ExtLWRad" "Outputs/ExtLWRad" "ExtLWRadTM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR1" "Outputs/IntRad-AR1" "IntRad-Test1-AR1TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR2" "Outputs/IntRad-AR2" "IntRad-Test1-AR2TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR5" "Outputs/IntRad-AR5" "IntRad-Test1-AR5TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR10" "Outputs/IntRad-AR10" "IntRad-Test1-AR10TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR20" "Outputs/IntRad-AR20" "IntRad-Test1-AR20TM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR1-Test 2" "Outputs/IntRad-AR1-Test 2" "IntRad-Test1-AR1TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR2-Test 2" "Outputs/IntRad-AR2-Test 2" "IntRad-Test1-AR2TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR5-Test 2" "Outputs/IntRad-AR5-Test 2" "IntRad-Test1-AR5TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR10-Test 2" "Outputs/IntRad-AR10-Test 2" "IntRad-Test1-AR10TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR20-Test 2" "Outputs/IntRad-AR20-Test 2" "IntRad-Test1-AR20TM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR1-Test 3" "Outputs/IntRad-AR1-Test 3" "IntRad-Test1-AR1TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR2-Test 3" "Outputs/IntRad-AR2-Test 3" "IntRad-Test1-AR2TM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR5-Test 3" "Outputs/IntRad-AR5-Test 3" "IntRad-Test1-AR5TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR10-Test 3" "Outputs/IntRad-AR10-Test 3" "IntRad-Test1-AR10TM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntRad-AR20-Test 3" "Outputs/IntRad-AR20-Test 3" "IntRad-Test1-AR20TM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/IntSolDist" "Outputs/IntSolDist" "IntSolDistTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/IntSolDist-South" "Outputs/IntSolDist-South" "IntSolDistTM2.epw")

AddSimulation(ASHRAE1052RP "Inputs/GrdCoup" "Outputs/GrdCoup" "USA_GA_Atlanta_TMY2-DB2Slab.epw")

AddSimulation(ASHRAE1052RP "Inputs/WinReveal" "Outputs/WinReveal" "WinRevealTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/WinReveal-NoSetback" "Outputs/WinReveal-NoSetback" "WinRevealTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/WinReveal-East" "Outputs/WinReveal-East" "WinRevealTM2.epw")
AddSimulation(ASHRAE1052RP "Inputs/WinReveal-NoSetback-East" "Outputs/WinReveal-NoSetback-East" "WinRevealTM2.epw")



#    Solar tests for August 21 only, TS=6
AddSimulation(ASHRAE1052RP "Inputs/821ExtSolRad" "Outputs/821ExtSolRad" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821ExtSolRad-East" "Outputs/821ExtSolRad-East" "Atlanta_Aug.epw")
#
AddSimulation(ASHRAE1052RP "Inputs/821SolRadGlazing" "Outputs/821SolRadGlazing" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821SolRadGlazing-East" "Outputs/821SolRadGlazing-East" "Atlanta_Aug.epw")

AddSimulation(ASHRAE1052RP "Inputs/821SolRadShade-South-NoShade" "Outputs/821SolRadShade-South-NoShade" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821SolRadShade-South-Horiz" "Outputs/821SolRadShade-South-Horiz" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821SolRadShade-South-Vert" "Outputs/821SolRadShade-South-Vert" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821SolRadShade-South-HorVer" "Outputs/821SolRadShade-South-HorVer" "Atlanta_Aug.epw")

AddSimulation(ASHRAE1052RP "Inputs/821SolRadShade-West-NoShade" "Outputs/821SolRadShade-West-NoShade" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821SolRadShade-West-Horiz" "Outputs/821SolRadShade-West-Horiz" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821SolRadShade-West-Vert" "Outputs/821SolRadShade-West-Vert" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821SolRadShade-West-HorVer" "Outputs/821SolRadShade-West-HorVer" "Atlanta_Aug.epw")

AddSimulation(ASHRAE1052RP "Inputs/821IntSolDist" "Outputs/821IntSolDist" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821IntSolDist-NoShade" "Outputs/821IntSolDist-NoShade" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821IntSolDist-South" "Outputs/821IntSolDist-South" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821IntSolDist-NoShade-South" "Outputs/821IntSolDist-NoShade-South" "Atlanta_Aug.epw")

AddSimulation(ASHRAE1052RP "Inputs/821WinReveal" "Outputs/821WinReveal" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821WinReveal-NoSetback" "Outputs/821WinReveal-NoSetback" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821WinReveal-East" "Outputs/821WinReveal-East" "Atlanta_Aug.epw")
AddSimulation(ASHRAE1052RP "Inputs/821WinReveal-NoSetback-East" "Outputs/821WinReveal-NoSetback-East" "Atlanta_Aug.epw")


AddSimulation(ASHRAE140-Envelope "Inputs/Case195" "Outputs/case195" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case600" "Outputs/case600" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case600FF" "Outputs/case600FF" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case610" "Outputs/case610" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case620" "Outputs/case620" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case630" "Outputs/case630" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case640" "Outputs/case640" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case650" "Outputs/case650" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case650FF" "Outputs/case650FF" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case900" "Outputs/case900" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case900FF" "Outputs/case900FF" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case910" "Outputs/case910" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case920" "Outputs/case920" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case930" "Outputs/case930" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case940" "Outputs/case940" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case950" "Outputs/case950" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case950FF" "Outputs/case950FF" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case960" "Outputs/case960" "DRYCOLDTMY.epw")

# In-depth Cases required by Standard 140

AddSimulation(ASHRAE140-Envelope "Inputs/Case200" "Outputs/case200" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case210" "Outputs/case210" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case215" "Outputs/case215" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case220" "Outputs/case220" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case230" "Outputs/case230" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case240" "Outputs/case240" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case250" "Outputs/case250" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case270" "Outputs/case270" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case280" "Outputs/case280" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case290" "Outputs/case290" "DRYCOLDTMY.epw")

AddSimulation(ASHRAE140-Envelope "Inputs/Case300" "Outputs/case300" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case310" "Outputs/case310" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case320" "Outputs/case320" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case395" "Outputs/case395" "DRYCOLDTMY.epw")

AddSimulation(ASHRAE140-Envelope "Inputs/Case400" "Outputs/case400" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case410" "Outputs/case410" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case420" "Outputs/case420" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case430" "Outputs/case430" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case440" "Outputs/case440" "DRYCOLDTMY.epw")

AddSimulation(ASHRAE140-Envelope "Inputs/Case800" "Outputs/case800" "DRYCOLDTMY.epw")
AddSimulation(ASHRAE140-Envelope "Inputs/Case810" "Outputs/case810" "DRYCOLDTMY.epw")



AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC30b" "Outputs/EPlus-CaseGC30b" "GCSS-W20TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC30c" "Outputs/EPlus-CaseGC30c" "GCSS-W40TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC40b" "Outputs/EPlus-CaseGC40b" "GCSP-W20TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC40c" "Outputs/EPlus-CaseGC40c" "GCSP-W40TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC45b" "Outputs/EPlus-CaseGC45b" "GCSP-W20TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC45c" "Outputs/EPlus-CaseGC45c" "GCSP-W40TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC50b" "Outputs/EPlus-CaseGC50b" "GCSP-W20TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC55b" "Outputs/EPlus-CaseGC55b" "GCSP-W20TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC55c" "Outputs/EPlus-CaseGC55c" "GCSP-W40TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC60b" "Outputs/EPlus-CaseGC60b" "GCSS-W20TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC65b" "Outputs/EPlus-CaseGC65b" "GCSS-W01TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC70b" "Outputs/EPlus-CaseGC70b" "GCSP-W01TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC80b" "Outputs/EPlus-CaseGC80b" "GCSP-W20TM2.epw")
AddSimulation(ASHRAE140-GrndCoup "Inputs/EPlus-CaseGC80c" "Outputs/EPlus-CaseGC80c" "GCSP-W40TM2.epw")


AddSimulation(ASHRAE140-HERS "Inputs/L100AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L100AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L110AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L110AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L120AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "Outputs/L120AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L130AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L130AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L140AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "Outputs/L140AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L150AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WinAreaPlusDivider" "Outputs/L150AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WinAreaPlusDivider" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L155AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WinAreaPlusDivider" "Outputs/L155AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WinAreaPlusDivider" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L160AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "Outputs/L160AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L165AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "Outputs/L165AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L170AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L170AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L200AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L200AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L202AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L202AC-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L302AC-DOE-2-IntMass-RevMatlProp-ExposedPerimeter" "Outputs/L302AC-DOE-2-IntMass-RevMatlProp-ExposedPerimeter" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L304AC-DOE-2-IntMass-RevMatlProp-ExposedPerimeter" "Outputs/L304AC-DOE-2-IntMass-RevMatlProp-ExposedPerimeter" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L322AC-DOE-2-IntMass-RevMatlProp-FCFactor" "Outputs/L322AC-DOE-2-IntMass-RevMatlProp-FCFactor" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L324AC-DOE-2-IntMass-RevMatlProp-FCFactor" "Outputs/L324AC-DOE-2-IntMass-RevMatlProp-FCFactor" "ColoradTMY-v5.0.epw")


#  ASHRAE 140-HERS Tests-Las Vegas-Cooling

AddSimulation(ASHRAE140-HERS "Inputs/L100AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L100AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L110AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L110AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L120AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "Outputs/L120AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L130AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L130AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L140AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "Outputs/L140AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L150AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WinAreaPlusDivider" "Outputs/L150AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WinAreaPlusDivider" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L155AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WinAreaPlusDivider" "Outputs/L155AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WinAreaPlusDivider" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L160AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "Outputs/L160AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L165AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "Outputs/L165AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L170AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L170AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L200AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L200AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "LasvegaTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/L202AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "Outputs/L202AL-DOE-2-IntMass-RevMatlProp-FullInteriorandExterior-WindowandFrame" "LasvegaTMY-v5.0.epw")
 
 
#   ASHRAE 140-HERS Tests-Passive Cooling-Colorado Springs  

AddSimulation(ASHRAE140-HERS "Inputs/P100AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "Outputs/P100AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/P105AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "Outputs/P105AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/P110AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "Outputs/P110AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/P140AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "Outputs/P140AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "ColoradTMY-v5.0.epw")
AddSimulation(ASHRAE140-HERS "Inputs/P150AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "Outputs/P150AC-DOE-2-IntMassAndIntWalls-RevMatlProp-FullExtAndInt" "ColoradTMY-v5.0.epw")



AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE100" "Outputs/CaseCE100" "CE100ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE110" "Outputs/CaseCE110" "CE110ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE120" "Outputs/CaseCE120" "CE110ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE130" "Outputs/CaseCE130" "CE100ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE140" "Outputs/CaseCE140" "CE110ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE150" "Outputs/CaseCE150" "CE110ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE160" "Outputs/CaseCE160" "CE110ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE165" "Outputs/CaseCE165" "CE165ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE170" "Outputs/CaseCE170" "CE110ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE180" "Outputs/CaseCE180" "CE110ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE185" "Outputs/CaseCE185" "CE100ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE190" "Outputs/CaseCE190" "CE110ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE195" "Outputs/CaseCE195" "CE100ATM2.epw")
AddSimulation(ASHRAE140-HVAC-CE100200 "Inputs/CaseCE200" "Outputs/CaseCE200" "CE200ATM2.epw")




AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE300" "Outputs/CaseCE300" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE310" "Outputs/CaseCE310" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE320" "Outputs/CaseCE320" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE330" "Outputs/CaseCE330" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE340" "Outputs/CaseCE340" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE350" "Outputs/CaseCE350" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE360" "Outputs/CaseCE360" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE400" "Outputs/CaseCE400" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE410" "Outputs/CaseCE410" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE420" "Outputs/CaseCE420" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE430" "Outputs/CaseCE430" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE440" "Outputs/CaseCE440" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE500" "Outputs/CaseCE500" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE510" "Outputs/CaseCE510" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE520" "Outputs/CaseCE520" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE522" "Outputs/CaseCE522" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE525" "Outputs/CaseCE525" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE530" "Outputs/CaseCE530" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE540" "Outputs/CaseCE540" "CE300TM2.epw")
AddSimulation(ASHRAE140-HVAC-CE300545 "Inputs/CaseCE545" "Outputs/CaseCE545" "CE300TM2.epw")


AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE100-SetConvCoeff" "Outputs/CaseHE100" "HE100WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE110-SetConvCoeff" "Outputs/CaseHE110" "HE100WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE120-SetConvCoeff" "Outputs/CaseHE120" "HE120WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE130-SetConvCoeff" "Outputs/CaseHE130" "HE130WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE140-SetConvCoeff" "Outputs/CaseHE140" "HE140WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE150-SetConvCoeff" "Outputs/CaseHE150" "HE140WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE160-SetConvCoeff" "Outputs/CaseHE160" "HE140WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE170-SetConvCoeff" "Outputs/CaseHE170" "HE140WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE210-SetConvCoeff" "Outputs/CaseHE210" "HE210WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE220-SetConvCoeff" "Outputs/CaseHE220" "HE210WWY2.epw")
AddSimulation(ASHRAE140-HVAC-HE100230 "Inputs/CaseHE230-SetConvCoeff" "Outputs/CaseHE230" "HE210WWY2.epw")






#  Run Bland Tests for Conduction Transfer Function Method, Timestep=20


AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 1-1.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 1-1-FF-TS20" "Bland_Excitation_1.epw" )
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 3-1.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 3-1-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 3-2.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 3-2-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 3-3.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 3-3-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 3-4.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 3-4-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 5-1.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 5-1-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 5-2.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 5-2-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 5-3.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 5-3-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 5-4.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 5-4-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 7-1.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 7-1-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 7-2.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 7-2-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 7-3.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 7-3-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 7-4.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 7-4-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 9-1.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 9-1-FF-TS20" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS20/Input/Construction 10-1.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.idf" "Analytical-Bland-TS20/Input/Test Structure 1-FF 0.001m cube-TS20.rvi" "Analytical-Bland-TS20/Output/Test 10-1-FF-TS20" "Bland_Excitation_1.epw")




#  Run Bland Tests for Conduction Transfer Function Method, Timestep=6

AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 1-1.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 1-1-FF-TS6" "Bland_Excitation_1.epw" )
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 3-1.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 3-1-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 3-2.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 3-2-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 3-3.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 3-3-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 3-4.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 3-4-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 5-1.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 5-1-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 5-2.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 5-2-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 5-3.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 5-3-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 5-4.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 5-4-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 7-1.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 7-1-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 7-2.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 7-2-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 7-3.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 7-3-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 7-4.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 7-4-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 9-1.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 9-1-FF-TS6" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 10-1.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 10-1-FF-TS6" "Bland_Excitation_1.epw")
# AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 11-1.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 11-1-FF-TS6" "Bland_Excitation_1.epw")
# AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 11-2.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 11-2-FF-TS6" "Bland_Excitation_1.epw")
# AddBlandSimulation(BlandTests "Analytical-Bland-TS6/Input/Construction 11-3.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.idf" "Analytical-Bland-TS6/Input/Test Structure 1-FF 0.001m cube-TS6.rvi" "Analytical-Bland-TS6/Output/Test 11-3-FF-TS6" "Bland_Excitation_1.epw")



#  Run Bland Tests for Conduction Transfer Function Method, Timestep=4$2


AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 1-1.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 1-1-FF" "Bland_Excitation_1.epw" )
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 3-1.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 3-1-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 3-2.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 3-2-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 3-3.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 3-3-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 3-4.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 3-4-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 5-1.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 5-1-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 5-2.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 5-2-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 5-3.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 5-3-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 5-4.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 5-4-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 7-1.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 7-1-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 7-2.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 7-2-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 7-3.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 7-3-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 7-4.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 7-4-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 9-1.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 9-1-FF" "Bland_Excitation_1.epw")
AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 10-1.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 10-1-FF" "Bland_Excitation_1.epw")
# AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 11-1.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 11-1-FF" "Bland_Excitation_1.epw")
# AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 11-2.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 11-2-FF" "Bland_Excitation_1.epw")
# AddBlandSimulation(BlandTests "Analytical-Bland/Input/Construction 11-3.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.idf" "Analytical-Bland/Input/Test Structure 1-FF 0.001m cube.rvi" "Analytical-Bland/Output/Test 11-3-FF" "Bland_Excitation_1.epw")




AddSimulation(CEN13791 "Inputs/Cond-1" "Outputs/Cond-1" "CEN13791-TestCONDCSV.epw")
AddSimulation(CEN13791 "Inputs/Cond-2" "Outputs/Cond-2" "CEN13791-TestCONDCSV.epw")
AddSimulation(CEN13791 "Inputs/Cond-3" "Outputs/Cond-3" "CEN13791-TestCONDCSV.epw")
AddSimulation(CEN13791 "Inputs/Cond-4" "Outputs/Cond-4" "CEN13791-TestCONDCSV.epw")
AddSimulation(CEN13791 "Inputs/Cond-1-TS60" "Outputs/Cond-1-TS60" "CEN13791-TestCONDCSV.epw")
AddSimulation(CEN13791 "Inputs/Cond-2-TS60" "Outputs/Cond-2-TS60" "CEN13791-TestCONDCSV.epw")
AddSimulation(CEN13791 "Inputs/Cond-3-TS60" "Outputs/Cond-3-TS60" "CEN13791-TestCONDCSV.epw")
AddSimulation(CEN13791 "Inputs/Cond-4-TS60" "Outputs/Cond-4-TS60" "CEN13791-TestCONDCSV.epw")
AddSimulation(CEN13791 "Inputs/IntRad-1" "Outputs/IntRad-1" "CEN13791-TestINTRADCSV.epw")
AddSimulation(CEN13791 "Inputs/IntRad-2" "Outputs/IntRad-2" "CEN13791-TestINTRADCSV.epw")
AddSimulation(CEN13791 "Inputs/IntRad-3" "Outputs/IntRad-3" "CEN13791-TestINTRADCSV.epw")
AddSimulation(CEN13791 "Inputs/IntRad-4" "Outputs/IntRad-4" "CEN13791-TestINTRADCSV.epw")
AddSimulation(CEN13791 "Inputs/Shade-1" "Outputs/Shade-1" "")
AddSimulation(CEN13791 "Inputs/Shade-2" "Outputs/Shade-2" "")
AddSimulation(CEN13791 "Inputs/Shade-3" "Outputs/Shade-3" "")
AddSimulation(CEN13791 "Inputs/Shade-4" "Outputs/Shade-4" "")
AddSimulation(CEN13791 "Inputs/Shade-5" "Outputs/Shade-5" "")
AddSimulation(CEN13791 "Inputs/Shade-6" "Outputs/Shade-6" "")
AddSimulation(CEN13791 "Inputs/A-1a-Long0.0" "Outputs/A-1a-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/A-1b-Long0.0" "Outputs/A-1b-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/A-1c-Long0.0" "Outputs/A-1c-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/A-2a-Long0.0" "Outputs/A-2a-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/A-2b-Long0.0" "Outputs/A-2b-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/A-2c-Long0.0" "Outputs/A-2c-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/A-3a-Long0.0" "Outputs/A-3a-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/A-3b-Long0.0" "Outputs/A-3b-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/A-3c-Long0.0" "Outputs/A-3c-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/B-1a-Long0.0" "Outputs/B-1a-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/B-1b-Long0.0" "Outputs/B-1b-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/B-1c-Long0.0" "Outputs/B-1c-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/B-2a-Long0.0" "Outputs/B-2a-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/B-2b-Long0.0" "Outputs/B-2b-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/B-2c-Long0.0" "Outputs/B-2c-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/B-3a-Long0.0" "Outputs/B-3a-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/B-3b-Long0.0" "Outputs/B-3b-Long0.0" "GBR_London.Gatwick_IWEC.epw")
AddSimulation(CEN13791 "Inputs/B-3c-Long0.0" "Outputs/B-3c-Long0.0" "GBR_London.Gatwick_IWEC.epw")


AddSimulation(CIBSE_TM33 "Inputs/CaseG2-Edinburgh-Dec22-Noon" "Outputs/CaseG2-Edinburgh-Dec22-Noon" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-Edinburgh-Feb27-3PM" "Outputs/CaseG2-Edinburgh-Feb27-3PM" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-Edinburgh-Jun21-Noon" "Outputs/CaseG2-Edinburgh-Jun21-Noon" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-Edinburgh-Oct20-10AM" "Outputs/CaseG2-Edinburgh-Oct20-10AM" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-London-Dec22-Noon" "Outputs/CaseG2-London-Dec22-Noon" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-London-Feb27-3PM" "Outputs/CaseG2-London-Feb27-3PM" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-London-Jun21-Noon" "Outputs/CaseG2-London-Jun21-Noon" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-London-Oct20-10AM" "Outputs/CaseG2-London-Oct20-10AM" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-Manchester-Dec22-Noon" "Outputs/CaseG2-Manchester-Dec22-Noon" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-Manchester-Feb27-3PM" "Outputs/CaseG2-Manchester-Feb27-3PM" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-Manchester-Jun21-Noon" "Outputs/CaseG2-Manchester-Jun21-Noon" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG2-Manchester-Oct20-10AM" "Outputs/CaseG2-Manchester-Oct20-10AM" "")

AddSimulation(CIBSE_TM33 "Inputs/CaseG3-1A-External Wall-FullBldg" "Outputs/CaseG3-1A-External Wall-FullBldg" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-1B-Internal Wall 1-FullBldg" "Outputs/CaseG3-1B-Internal Wall 1-FullBldg" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-1C-Internal Wall 2-FullBldg" "Outputs/CaseG3-1C-Internal Wall 2-FullBldg" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-1D-Ceiling-Floor-FullBldg" "Outputs/CaseG3-1D-Ceiling-Floor-FullBldg" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-1E-Floor 2-FullBldg" "Outputs/CaseG3-1E-Floor 2-FullBldg" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-1F-Floor 1-FullBldg" "Outputs/CaseG3-1F-Floor 1-FullBldg" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-1G-Roof 1-FullBldg" "Outputs/CaseG3-1G-Roof 1-FullBldg" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-1H-Roof 2-FullBldg" "Outputs/CaseG3-1H-Roof 2-FullBldg" "")

AddSimulation(CIBSE_TM33 "Inputs/CaseG3-2-1" "Outputs/CaseG3-2-1" "GBR_London.Gatwick_IWECEPW-TestG3-2.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-2-2" "Outputs/CaseG3-2-2" "GBR_London.Gatwick_IWECEPW-TestG3-2.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-2-3" "Outputs/CaseG3-2-3" "GBR_London.Gatwick_IWECEPW-TestG3-2.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-2-4" "Outputs/CaseG3-2-4" "GBR_London.Gatwick_IWECEPW-TestG3-2.epw")


AddSimulation(CIBSE_TM33 "Inputs/CaseG3-2-1-TS60" "Outputs/CaseG3-2-1-TS60" "GBR_London.Gatwick_IWECEPW-TestG3-2.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-2-2-TS60" "Outputs/CaseG3-2-2-TS60" "GBR_London.Gatwick_IWECEPW-TestG3-2.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-2-3-TS60" "Outputs/CaseG3-2-3-TS60" "GBR_London.Gatwick_IWECEPW-TestG3-2.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG3-2-4-TS60" "Outputs/CaseG3-2-4-TS60" "GBR_London.Gatwick_IWECEPW-TestG3-2.epw")



AddSimulation(CIBSE_TM33 "Inputs/CaseG4-1" "Outputs/CaseG4-1" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG4-2" "Outputs/CaseG4-2" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG4-3" "Outputs/CaseG4-3" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG4-4" "Outputs/CaseG4-4" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG4-5" "Outputs/CaseG4-5" "")
AddSimulation(CIBSE_TM33 "Inputs/CaseG4-6" "Outputs/CaseG4-6" "")

AddSimulation(CIBSE_TM33 "Inputs/CaseG5-1-Air" "Outputs/CaseG5-1-Air" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG5-1-Argon" "Outputs/CaseG5-1-Argon" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG5-2-Air" "Outputs/CaseG5-2-Air" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG5-2-Argon" "Outputs/CaseG5-2-Argon" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG5-3-Air" "Outputs/CaseG5-3-Air" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG5-3-Argon" "Outputs/CaseG5-3-Argon" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG5-4-Air" "Outputs/CaseG5-4-Air" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG5-4-Argon" "Outputs/CaseG5-4-Argon" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG5-5-Air" "Outputs/CaseG5-5-Air" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG5-5-Argon" "Outputs/CaseG5-5-Argon" "GBR_London.Gatwick_IWECEPW-TestG6.epw")

AddSimulation(CIBSE_TM33 "Inputs/CaseG6-A1-Baseboard" "Outputs/CaseG6-A1-Baseboard" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG6-B1-Baseboard" "Outputs/CaseG6-B1-Baseboard" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG6-A2-Baseboard" "Outputs/CaseG6-A2-Baseboard" "GBR_London.Gatwick_IWECEPW-TestG6.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG6-B2-Baseboard" "Outputs/CaseG6-B2-Baseboard" "GBR_London.Gatwick_IWECEPW-TestG6.epw")


AddSimulation(CIBSE_TM33 "Inputs/CaseG7-1WithCIBSEWeather" "Outputs/CaseG7-1WithCIBSEWeather" "GBR_London.Gatwick.037760_IWEC.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG7-2WithCIBSEWeather" "Outputs/CaseG7-2WithCIBSEWeather" "GBR_London.Gatwick.037760_IWEC.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG7-3WithCIBSEWeather" "Outputs/CaseG7-3WithCIBSEWeather" "GBR_London.Gatwick.037760_IWEC.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG7-4WithCIBSEWeather" "Outputs/CaseG7-4WithCIBSEWeather" "GBR_London.Gatwick.037760_IWEC.epw")

AddSimulation(CIBSE_TM33 "Inputs/CaseG7-1WithAndyWeather-Jan2013" "Outputs/CaseG7-1WithAndyWeather-Jan2013" "TM33try.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG7-2WithAndyWeather-Jan2013" "Outputs/CaseG7-2WithAndyWeather-Jan2013" "TM33try.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG7-3WithAndyWeather-Jan2013" "Outputs/CaseG7-3WithAndyWeather-Jan2013" "TM33try.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG7-4WithAndyWeather-Jan2013" "Outputs/CaseG7-4WithAndyWeather-Jan2013" "TM33try.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG7-1WithAndyWeather-Jan2013-SwitchWindowEmiss" "Outputs/CaseG7-1WithAndyWeather-Jan2013-SwitchWindowEmiss" "TM33try.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG7-3WithAndyWeather-Jan2013-SwitchWindowEmiss" "Outputs/CaseG7-3WithAndyWeather-Jan2013-SwitchWindowEmiss" "TM33try.epw")

AddSimulation(CIBSE_TM33 "Inputs/CaseG8-1WithCIBSEWeather" "Outputs/CaseG8-1WithCIBSEWeather" "GBR_London.Gatwick.037760_IWEC.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG8-2WithCIBSEWeather" "Outputs/CaseG8-2WithCIBSEWeather" "GBR_London.Gatwick.037760_IWEC.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG8-3WithCIBSEWeather" "Outputs/CaseG8-3WithCIBSEWeather" "GBR_London.Gatwick.037760_IWEC.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG8-4WithCIBSEWeather" "Outputs/CaseG8-4WithCIBSEWeather" "GBR_London.Gatwick.037760_IWEC.epw")


AddSimulation(CIBSE_TM33 "Inputs/CaseG9-AllTests2-Gu" "Outputs/CaseG9-AllTests2-Gu" "TestG9-AllWeatherPeriods.epw")

AddSimulation(CIBSE_TM33 "Inputs/CaseG10-1" "Outputs/CaseG10-1" "TM33try.epw")
AddSimulation(CIBSE_TM33 "Inputs/CaseG10-2" "Outputs/CaseG10-2" "TM33try.epw")

AddSimulation(CIBSE_TM33 "Inputs/CaseG10-2-Original-IdealLoads-MJW-RHHMods" "Outputs/CaseG10-2-Original-IdealLoads-MJW-RHHMods" "TM33try.epw")



# Window AC
AddSimulation(GlobalEnergyBalance "Inputs/Global CaseE100-OtherZoneSurface-16Days" "Outputs/Global CaseE100-OtherZoneSurface-16Days" "CE100ATM2.epw")
AddSimulation(GlobalEnergyBalance "Inputs/Global CaseE100-OtherZoneSurface-Annual" "Outputs/Global CaseE100-OtherZoneSurface-Annual" "IL_Chicago_TMY2.epw")

# Chiller and Boiler
AddSimulation(GlobalEnergyBalance "Inputs/Global CaseE100-ChillerandBoiler-16Days" "Outputs/Global CaseE100-ChillerandBoiler-16Days" "CE100ATM2.epw")
AddSimulation(GlobalEnergyBalance "Inputs/Global CaseE100-ChillerandBoiler-DesignDaySch1.1-PumpsandFan" "Outputs/Global CaseE100-ChillerandBoiler-DesignDaySch1.1-PumpsandFan" "IL_Chicago_TMY2.epw")





AddSimulation(HVACComponent "Boiler-Inputs/Component Test-Boiler-CaseE100" "Outputs/Component Test-Boiler-CaseE100" "CE200ATM2.epw")


AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW3.33CNW23.89" "Outputs/CompTestCaseE100-FanCoilCHW3.33CNW23.89" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW3.33CNW26.67" "Outputs/CompTestCaseE100-FanCoilCHW3.33CNW26.67" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW3.33CNW29.44" "Outputs/CompTestCaseE100-FanCoilCHW3.33CNW29.44" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW3.33CNW32.22" "Outputs/CompTestCaseE100-FanCoilCHW3.33CNW32.22" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW3.33CNW35.0" "Outputs/CompTestCaseE100-FanCoilCHW3.33CNW35.0" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW3.33CNW37.78" "Outputs/CompTestCaseE100-FanCoilCHW3.33CNW37.78" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW4.44CNW23.89" "Outputs/CompTestCaseE100-FanCoilCHW4.44CNW23.89" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW4.44CNW26.67" "Outputs/CompTestCaseE100-FanCoilCHW4.44CNW26.67" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW4.44CNW29.44" "Outputs/CompTestCaseE100-FanCoilCHW4.44CNW29.44" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW4.44CNW32.22" "Outputs/CompTestCaseE100-FanCoilCHW4.44CNW32.22" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW4.44CNW35.0" "Outputs/CompTestCaseE100-FanCoilCHW4.44CNW35.0" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW4.44CNW37.78" "Outputs/CompTestCaseE100-FanCoilCHW4.44CNW37.78" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW5.56CNW23.89" "Outputs/CompTestCaseE100-FanCoilCHW5.56CNW23.89" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW5.56CNW26.67" "Outputs/CompTestCaseE100-FanCoilCHW5.56CNW26.67" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW5.56CNW29.44" "Outputs/CompTestCaseE100-FanCoilCHW5.56CNW29.44" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW5.56CNW32.22" "Outputs/CompTestCaseE100-FanCoilCHW5.56CNW32.22" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW5.56CNW35.0" "Outputs/CompTestCaseE100-FanCoilCHW5.56CNW35.0" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW5.56CNW37.78" "Outputs/CompTestCaseE100-FanCoilCHW5.56CNW37.78" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW23.89-PLR" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW23.89-PLR" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW23.89" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW23.89" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW26.67-PLR" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW26.67-PLR" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW26.67" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW26.67" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW29.44-PLR" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW29.44-PLR" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW29.44" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW29.44" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW32.22-PLR" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW32.22-PLR" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW32.22" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW32.22" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW35.0-PLR" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW35.0-PLR" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW35.0" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW35.0" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW37.78-PLR" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW37.78-PLR" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW6.67CNW37.78" "Outputs/CompTestCaseE100-FanCoilCHW6.67CNW37.78" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.22CNW23.89" "Outputs/CompTestCaseE100-FanCoilCHW7.22CNW23.89" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.22CNW26.67" "Outputs/CompTestCaseE100-FanCoilCHW7.22CNW26.67" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.22CNW29.44" "Outputs/CompTestCaseE100-FanCoilCHW7.22CNW29.44" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.22CNW32.22" "Outputs/CompTestCaseE100-FanCoilCHW7.22CNW32.22" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.22CNW35.0" "Outputs/CompTestCaseE100-FanCoilCHW7.22CNW35.0" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.22CNW37.78" "Outputs/CompTestCaseE100-FanCoilCHW7.22CNW37.78" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.78CNW23.89" "Outputs/CompTestCaseE100-FanCoilCHW7.78CNW23.89" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.78CNW26.67" "Outputs/CompTestCaseE100-FanCoilCHW7.78CNW26.67" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.78CNW29.44" "Outputs/CompTestCaseE100-FanCoilCHW7.78CNW29.44" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.78CNW32.22" "Outputs/CompTestCaseE100-FanCoilCHW7.78CNW32.22" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.78CNW35.0" "Outputs/CompTestCaseE100-FanCoilCHW7.78CNW35.0" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW7.78CNW37.78" "Outputs/CompTestCaseE100-FanCoilCHW7.78CNW37.78" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW8.89CNW23.89" "Outputs/CompTestCaseE100-FanCoilCHW8.89CNW23.89" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW8.89CNW26.67" "Outputs/CompTestCaseE100-FanCoilCHW8.89CNW26.67" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW8.89CNW29.44" "Outputs/CompTestCaseE100-FanCoilCHW8.89CNW29.44" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW8.89CNW32.22" "Outputs/CompTestCaseE100-FanCoilCHW8.89CNW32.22" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW8.89CNW35.0" "Outputs/CompTestCaseE100-FanCoilCHW8.89CNW35.0" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW8.89CNW37.78" "Outputs/CompTestCaseE100-FanCoilCHW8.89CNW37.78" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW10.0CNW23.89" "Outputs/CompTestCaseE100-FanCoilCHW10.0CNW23.89" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW10.0CNW26.67" "Outputs/CompTestCaseE100-FanCoilCHW10.0CNW26.67" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW10.0CNW29.44" "Outputs/CompTestCaseE100-FanCoilCHW10.0CNW29.44" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW10.0CNW32.22" "Outputs/CompTestCaseE100-FanCoilCHW10.0CNW32.22" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW10.0CNW35.0" "Outputs/CompTestCaseE100-FanCoilCHW10.0CNW35.0" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW10.0CNW37.78" "Outputs/CompTestCaseE100-FanCoilCHW10.0CNW37.78" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW11.11CNW23.89" "Outputs/CompTestCaseE100-FanCoilCHW11.11CNW23.89" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW11.11CNW26.67" "Outputs/CompTestCaseE100-FanCoilCHW11.11CNW26.67" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW11.11CNW29.44" "Outputs/CompTestCaseE100-FanCoilCHW11.11CNW29.44" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW11.11CNW32.22" "Outputs/CompTestCaseE100-FanCoilCHW11.11CNW32.22" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW11.11CNW35.0" "Outputs/CompTestCaseE100-FanCoilCHW11.11CNW35.0" "CE200ATM2.epw")
AddSimulation(HVACComponent "EIRChiller-Inputs/CompTestCaseE100-FanCoilCHW11.11CNW37.78" "Outputs/CompTestCaseE100-FanCoilCHW11.11CNW37.78" "CE200ATM2.epw")









AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC100Test"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC100Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC120Test"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC120Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC200-HiFlowTest"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC200HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC200-LoFlowTest"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC200LoFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC220-HiFlowTest"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC220HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC220-LoFlowTest"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC220LoFlowTest"  "14933TM2.epw")

AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC140Test"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC140Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC160Test"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC160Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC240-HiFlowTest"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC240HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC240-LoFlowTest"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC240LoFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC260-HiFlowTest"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC260HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Simple/Inputs/CaseCC260-LoFlowTest"  "Exer2-CoolingCoilComparativeTest-Simple/Outputs/CaseCC260LoFlowTest"  "14933TM2.epw")



AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC100Test"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC100Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC120Test"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC120Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC200-HiFlowTest"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC200HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC200-LoFlowTest"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC200LoFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC220-HiFlowTest"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC220HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC220-LoFlowTest"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC220LoFlowTest"  "14933TM2.epw")

AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC140Test"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC140Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC160Test"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC160Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC240-HiFlowTest"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC240HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC240-LoFlowTest"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC240LoFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC260-HiFlowTest"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC260HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-CoolingCoilComparativeTest-Detailed/Inputs/CaseCC260-LoFlowTest"  "Exer2-CoolingCoilComparativeTest-Detailed/Outputs/CaseCC260LoFlowTest"  "14933TM2.epw")




AddSimulation(IEAMechanical "Exer2-HeatingCoilComparativeTest/Inputs/CaseHX100Test"  "Exer2-HeatingCoilComparativeTest/Outputs/CaseHX100Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoilComparativeTest/Inputs/CaseHX120Test"  "Exer2-HeatingCoilComparativeTest/Outputs/CaseHX120Test"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoilComparativeTest/Inputs/CaseHX200-HiFlowTest"  "Exer2-HeatingCoilComparativeTest/Outputs/CaseHX200HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoilComparativeTest/Inputs/CaseHX200-LoFlowTest"  "Exer2-HeatingCoilComparativeTest/Outputs/CaseHX200LoFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoilComparativeTest/Inputs/CaseHX220-HiFlowTest"  "Exer2-HeatingCoilComparativeTest/Outputs/CaseHX220HiFlowTest"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoilComparativeTest/Inputs/CaseHX220-LoFlowTest"  "Exer2-HeatingCoilComparativeTest/Outputs/CaseHX220LoFlowTest"  "14933TM2.epw")
#
#
#  AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX100Test"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX100Test"  "14933TM2.epw")
#  AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX120Test"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX120Test"  "14933TM2.epw")
#  AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX200-HiFlowTest"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX200HiFlowTest"  "14933TM2.epw")
#  AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX200-LoFlowTest"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX200LoFlowTest"  "14933TM2.epw")
#  AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX220-HiFlowTest"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX220HiFlowTest"  "14933TM2.epw")
#  AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX220-LoFlowTest"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX220LoFlowTest"  "14933TM2.epw")


AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX100Test-rEquals0.5"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX100Test-rEquals0.5"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX120Test-rEquals0.5"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX120Test-rEquals0.5"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX200-HiFlowTest-rEquals0.5"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX200HiFlowTest-rEquals0.5"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX200-LoFlowTest-rEquals0.5"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX200LoFlowTest-rEquals0.5"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX220-HiFlowTest-rEquals0.5"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX220HiFlowTest-rEquals0.5"  "14933TM2.epw")
AddSimulation(IEAMechanical "Exer2-HeatingCoil-HtgCoilNomCapMethod/Inputs/CaseHX220-LoFlowTest-rEquals0.5"  "Exer2-HeatingCoil-HtgCoilNomCapMethod/Outputs/CaseHX220LoFlowTest-rEquals0.5"  "14933TM2.epw")




AddSimulation(MultizoneBESTEST "Inputs/CaseMZ320"  "Outputs/CaseMZ320"  "MZ320TM2.epw")
AddSimulation(MultizoneBESTEST "Inputs/CaseMZ340"  "Outputs/CaseMZ340"  "MZ340TM2.epw")
AddSimulation(MultizoneBESTEST "Inputs/CaseMZ350a" "Outputs/CaseMZ350a" "MZ340TM2.epw")
AddSimulation(MultizoneBESTEST "Inputs/CaseMZ350b" "Outputs/CaseMZ350b" "MZ340TM2.epw")
AddSimulation(MultizoneBESTEST "Inputs/CaseMZ350c" "Outputs/CaseMZ350c" "MZ340TM2.epw")
AddSimulation(MultizoneBESTEST "Inputs/CaseMZ350d" "Outputs/CaseMZ350d" "MZ340TM2.epw")
AddSimulation(MultizoneBESTEST "Inputs/CaseMZ355"  "Outputs/CaseMZ355"  "MZ340TM2.epw")

AddSimulation(MultizoneBESTEST "Inputs/CaseMZ360-AlternatSurfaceInput"  "Outputs/CaseMZ360-AlternatSurfaceInput"  "MZ340TM2.epw")


AddSimulation(MultizoneBESTESTWithAirflow "Inputs/Case MA101" "Outputs/Case MA101" "")
AddSimulation(MultizoneBESTESTWithAirflow "Inputs/Case MA102" "Outputs/Case MA102" "")
AddSimulation(MultizoneBESTESTWithAirflow "Inputs/Case MA103" "Outputs/Case MA103" "")
AddSimulation(MultizoneBESTESTWithAirflow "Inputs/Case MA301" "Outputs/Case MA301" "")
AddSimulation(MultizoneBESTESTWithAirflow "Inputs/Case MA302" "Outputs/Case MA302" "")
AddSimulation(MultizoneBESTESTWithAirflow "Inputs/Case MA303" "Outputs/Case MA303" "")
AddSimulation(MultizoneBESTESTWithAirflow "Inputs/Case MA304" "Outputs/Case MA304" "")
AddSimulation(MultizoneBESTESTWithAirflow "Inputs/Case MA306_Detailed_1" "Outputs/Case MA306_Detailed_1" "")





AddSimulation(Shading "Inputs/SolRadShade-South-Horiz" "Outputs/SolRadShade-South-Horiz" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Horiz-Frame" "Outputs/SolRadShade-South-Horiz-Frame" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Horiz-Divider" "Outputs/SolRadShade-South-Horiz-Divider" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Horiz-FrameandDivider" "Outputs/SolRadShade-South-Horiz-FrameandDivider" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Horiz-Frame-SmallWin" "Outputs/SolRadShade-South-Horiz-Frame-SmallWin" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Horiz-FrameandDivider-SmallWin" "Outputs/SolRadShade-South-Horiz-FrameandDivider-SmallWin" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Horiz-NoTransSched" "Outputs/SolRadShade-South-Horiz-NoTransSched" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Horiz-Trans001" "Outputs/SolRadShade-South-Horiz-Trans001" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Horiz-Trans5" "Outputs/SolRadShade-South-Horiz-Trans5" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Horiz-Trans999" "Outputs/SolRadShade-South-Horiz-Trans999" "")

AddSimulation(Shading "Inputs/SolRadShade-South-HorVer" "Outputs/SolRadShade-South-HorVer" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Frame" "Outputs/SolRadShade-South-HorVer-Frame" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Divider" "Outputs/SolRadShade-South-HorVer-Divider" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-FrameandDivider" "Outputs/SolRadShade-South-HorVer-FrameandDivider" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Frame-SmallWin" "Outputs/SolRadShade-South-HorVer-Frame-SmallWin" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-FrameandDivider-SmallWin" "Outputs/SolRadShade-South-HorVer-FrameandDivider-SmallWin" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Frame-Win2x" "Outputs/SolRadShade-South-HorVer-Frame-Win2x" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-FrameandDivider-Win2x" "Outputs/SolRadShade-South-HorVer-FrameandDivider-Win2x" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Divider-Win2x" "Outputs/SolRadShade-South-HorVer-Divider-Win2x" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-FrameandDivider-SmallWin-Win2x" "Outputs/SolRadShade-South-HorVer-FrameandDivider-SmallWin-Win2x" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Frame-SmallWin-Win2x" "Outputs/SolRadShade-South-HorVer-Frame-SmallWin-Win2x" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-NoTransSched" "Outputs/SolRadShade-South-HorVer-NoTransSched" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Trans001" "Outputs/SolRadShade-South-HorVer-Trans001" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Trans5" "Outputs/SolRadShade-South-HorVer-Trans5" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Trans999" "Outputs/SolRadShade-South-HorVer-Trans999" "")
AddSimulation(Shading "Inputs/SolRadShade-South-HorVer-Win2x" "Outputs/SolRadShade-South-HorVer-Win2x" "")

AddSimulation(Shading "Inputs/SolRadShade-South-NoShade" "Outputs/SolRadShade-South-NoShade" "")
AddSimulation(Shading "Inputs/SolRadShade-South-NoShade-Frame" "Outputs/SolRadShade-South-NoShade-Frame" "")
AddSimulation(Shading "Inputs/SolRadShade-South-NoShade-Divider" "Outputs/SolRadShade-South-NoShade-Divider" "")
AddSimulation(Shading "Inputs/SolRadShade-South-NoShade-FrameandDivider" "Outputs/SolRadShade-South-NoShade-FrameandDivider" "")
AddSimulation(Shading "Inputs/SolRadShade-South-NoShade-Frame-SmallWin" "Outputs/SolRadShade-South-NoShade-Frame-SmallWin" "")
AddSimulation(Shading "Inputs/SolRadShade-South-NoShade-FrameandDivider-SmallWin" "Outputs/SolRadShade-South-NoShade-FrameandDivider-SmallWin" "")
AddSimulation(Shading "Inputs/SolRadShade-South-NoShade-Door" "Outputs/SolRadShade-South-NoShade-Door" "")

AddSimulation(Shading "Inputs/SolRadShade-South-Vert" "Outputs/SolRadShade-South-Vert" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Vert-Frame" "Outputs/SolRadShade-South-Vert-Frame" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Vert-Divider" "Outputs/SolRadShade-South-Vert-Divider" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Vert-FrameandDivider" "Outputs/SolRadShade-South-Vert-FrameandDivider" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Vert-Frame-SmallWin" "Outputs/SolRadShade-South-Vert-Frame-SmallWin" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Vert-FrameandDivider-SmallWin" "Outputs/SolRadShade-South-Vert-FrameandDivider-SmallWin" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Vert-NoTransSched" "Outputs/SolRadShade-South-Vert-NoTransSched" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Vert-Trans001" "Outputs/SolRadShade-South-Vert-Trans001" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Vert-Trans5" "Outputs/SolRadShade-South-Vert-Trans5" "")
AddSimulation(Shading "Inputs/SolRadShade-South-Vert-Trans999" "Outputs/SolRadShade-South-Vert-Trans999" "")
 




