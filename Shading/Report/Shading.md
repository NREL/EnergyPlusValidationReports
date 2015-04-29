---
title: Self-Comparison Test Suite for Shading Calculations, Energyplus version {{ engine.config["EnergyPlusVersion"] }}
---

Automatically Generated {{ engine.month_year() }}

Originally Prepared by  
R. Henninger & M. Witte, GARD Analytics, Inc.


# Introduction

**Software:** EnergyPlus Version {{ engine.config["EnergyPlusVersion"] }}  
**Authoring Organization:** Department of Energy, Energy Efficiency and Renewable Energy, Office of Building Technologies  
**Authoring Country:** USA

This test suite was developed in October 2007 in response to several issues
involving sunlit areas of surfaces, the reporting of window areas, the
reporting of window-to-wall ratios, and partially transmitting shading surfaces
when frames and/or dividers are present and when window/door multipliers are
used. This new internal test suite and spreadsheets were developed to check
that these features were working properly and giving reasonable results. This
Shading Test suite continues to be used to check new EnergyPlus releases.


# Test Suite Description

The Shading Test suite makes use of ASHRAE 1052RP test cases called SolRadShade
(Spitler et al 2001) which tests a program’s ability to model a window surface
in several modes: unshaded, shaded by horizontal overhang, shaded by vertical
fins, and shaded by overhang and fins. Nine separate test cases with
appropriate spreadsheets to compare results between test cases were developed
as follows.

- Test 1 – This basic case uses the ASHRAE 1052-RP SolRadShade test cases with
  horizontal and vertical shading for which EnergyPlus results were known to
  agree with the ASHRAE 1052-RP analytical toolkit results. This case was modeled
  as a south facing wall with window that was unshaded, horizontally shaded,
  vertically shaded, and both horizontally and vertically shaded. The tests were
  run with 1052-RP weather files.

- Test 2 – Same as Test 1 but add a substantial frame to the window that
  would cover about half the remaining wall area. Since window frames in
  EnergyPlus are supposed to subtract from the wall area, not the window
  subsurface area, results for the window should be the same as Test 1.

- Test 3 - Same as Test 2 but with a smaller window such that the window
  plus frame area is the same as in the base case (Test 1) with no frame.
  Results for the wall should be identical to Test 1.

- Test 4 - Take Test 1 files, Test 2 files and Test 3 files and add
  dividers to the window. Results for the wall should not change.

- Test 5 - Take all of the above test files (Tests 1-4) and make the wall
  twice as wide and set the window multiplier to 2. The results for the
  window should remain unchanged, because it will be in the same place
  relative to the shading surfaces and simply multiplied by 2.

- Test 6 - Same as Test 1 but add a transmittance schedule of 0.001 to the
  shading surface(s). All results should change only by a very small amount compared to Test 1.

- Test 7 - Same as Test 6 but change the transmittance schedule to 0.999. All
  results should be nearly identical to the unshaded case of Test 1.

- Test 8 - Same as Test 6 but change the transmittance schedule to 0.5. All
  shaded results should be close to halfway between the unshaded case of Test 7
  and the almost fully shaded Test 6.

- Test 9 - For the unshaded cases from Tests 1 through 5, confirm that the
  reporting of window areas, wall areas, and window-to-wall ratios in various
  EnergyPlus output reports is correctly accounting for the frames, dividers and
  multipliers.


# Initial Problems Encountered

The Shading test suite was originally developed and tested with EnergyPlus
version 2.1. Two problems were encountered with standard output reports
reporting incorrect quantities for certain output report variables:

- With a frame and divider added to the window, the window area shown
  in the Performance/Zone Summary table was not correct. The window
  area in the Envelope/Window-Wall Ratio table was correct.

- Problems were found in the Surface Shadowing Summary report, for
  example: (1) fins and overhangs were shown as being shaded by base
  surface; (2) when fins and overhang were present only the fin and
  not the overhang was being shown as shadow casters and (3) for the
  window subsurface neither the fin or overhang were shown as shadow
  casters.

These reporting problems were corrected in EnergyPlus version 2.2. See
examples of these Summary Reports on the following page where the
details of a surface with a 2m x 2m window with a 0.25m frame and 0.02m
horizontal and vertical dividers which divide the window into 9 equal
sections are summarized.


# Results

A series of spreadsheets were created to compare the sunlit areas and fractions
of the wall and window for various test cases. Example of results with
EnergyPlus {{ engine.config["EnergyPlusVersion"] }} are shown on the following pages.

![](./media/image1.svg)

![](./media/image2.svg)

![](./media/image3.svg)


{{ engine.create_table_from_excel_range('Compare Results-Areas.xlsx', 'Areas-Cases1-4', 'A1:AE33', [0,1,2], 10) }}



```{exec_python}

engine.write_chart('ScatterLines', 'Chart1 - Window', 'EnergyPlus Shading Test\nWindow Sunlit Areas With Various Shading Options\nAtlanta, August 21', 'Hour of Day', 'Sunlit Area (m2)', 'Compare Results-Areas.xlsx', 'Areas-Cases1-4', 'B8:F32', "(C8,B10:B32,C10:C32,1);(D8,B10:B32,D10:D32,2);(E8,B10:B32,E10:E32,3);(F8,B10:B32,F10:F32,4);", ['South wall (3m x 3m) with window (2m x 2m) with 0.6m overhang along top of wall and 1m right fin along right wall edge', 'After 1 PM (Hour 13) there is no shading of the window by the fin'])

engine.write_chart('ScatterLines', 'Chart2', 'EnergyPlus Shading Test \nWindow Sunlit Areas With Various Features Added to Window\nAtlanta, August 21', 'Hour of Day', 'Sunlit Area (m2)', 'Compare Results-Areas.xlsx', 'Areas-Cases1-4', 'B8:BA32', "('Areas-Cases1-4'!C8,B10:B32,'Areas-Cases1-4'!C10:C32,1);('Areas-Cases1-4'!M8,'Areas-Cases1-4'!B10:B32,'Areas-Cases1-4'!M10:M32,2);('Areas-Cases1-4'!W8,'Areas-Cases1-4'!B10:B32,'Areas-Cases1-4'!W10:W32,3);('Areas-Cases1-4'!AG8,'Areas-Cases1-4'!B10:B32,'Areas-Cases1-4'!AG10:AG32,4);('Areas-Cases1-4'!AQ8,'Areas-Cases1-4'!B10:B32,'Areas-Cases1-4'!AQ10:AQ32,5);('Areas-Cases1-4'!BA8,'Areas-Cases1-4'!B10:B32,'Areas-Cases1-4'!BA10:BA32,6);", ['South wall (3m x 3m) with window (2m x 2m) with 0.6m overhang along top of wall and 1m right fin along right wall edge. Small window (2m x 2m)', 'Adding frame does not change glass area. Adding divider reduces glass area'])

engine.write_chart('ScatterLines', 'Chart7 - Overhang Trans', 'EnergyPlus Shading Test\nWindow with Various Overhang Transmittances\nAtlanta, August 21', 'Hour of Day', 'Sunlit Area (m2)', 'Compare Results-Areas.xlsx', 'AreasandDeltas-Case7', 'B8:D34', "(D8,B12:B34,D12:D34,1);('AreasandDivides-Case9'!D8,'AreasandDivides-Case9'!B12:B34,'AreasandDivides-Case9'!D12:D34,2);('AreasandDeltas-Case8'!D8,'AreasandDeltas-Case8'!B12:B34,'AreasandDeltas-Case8'!D12:D34,3);", ['South wall (3 m x 3m) with window (2m x 2m) with 0.6 m overhang along top of wall', 'Increasing overhang transmittance increases sunlit area'])

engine.write_chart('ScatterLines', 'Chart1 (2)', 'EnergyPlus Shading Test\nWindow Sunlit Fractions with Various Features Added to Window\nAtlanta, August  21', 'Hour of day', 'Window Sunlit Fraction', 'Compare Results-Fractions.xlsx', 'Fractions-Cases1-4', 'A8:AS32', "(E8,A10:A32,E10:E32,1);(O8,A10:A32,O10:O32,2);(AI8,A10:A32,AI10:AI32,3);(AS8,A10:A32,AS10:AS32,4);", ['South wall (3 m x 3m) with window (2m x 2m) with 0.6 m overhang along top of wall and 1m right fin along right wall edge', 'Although the glass area changes when a divider is added, the sunlit fraction of window area remains unchanged.', 'Adding frame does not change glass area, therefore sunlit fraction does not change'])

engine.write_chart('ScatterLines', 'Chart2', 'EnergyPlus Shading Test 5\nWindow Sunlit Fractions with Wide Wall and various Window Features\nAtlanta, August 21', 'Hour of Day', 'Window Sunlit Fraction', 'Compare Results-Fractions.xlsx', 'FractionsandDeltas-Case5', 'B11:G34', "(C11,B12:B34,C12:C34,1);(D11,B12:B34,D12:D34,2);(F11,B12:B34,F12:F34,3);(G11,B12:B34,G12:G34,4);", ['South wall (6m x 3m) with window (2m x 2m)  with 0.6 m overhang along top of wall and 1m right fin along right wall edgenWindow multiplier = 2', 'Although the glass area changes when a divider is added, the sunlit fraction of window area remains unchanged.', 'Adding frame does not change glass area, therefore sunlit fraction does not change'])

```

