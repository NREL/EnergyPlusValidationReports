---
title: EnergyPlus Testing with BEpac/Bland Conduction Tests, Energyplus Version {{ engine.config["EnergyPlusVersion"] }}
---

Automatically Generated {{ engine.month_year() }}

Originally Prepared by  
R. Henninger & M. Witte, GARD Analytics, Inc.  


# Introduction

**Software:** EnergyPlus Version {{ engine.config["EnergyPlusVersion"] }}  
**Authoring Organization:** Department of Energy, Energy Efficiency and Renewable Energy, Office of Building Technologies  
**Authoring Country:** USA

This report describes progress for using EnergyPlus to model tests which
are part of a test suite published by BEPAC (Building Energy Performance
Analysis Club in the UK) which contains a collection of conduction tests
for validating building simulation software (BEPAC 1993). The BEPAC
tests are based entirely on a paper by B. H. Bland titled *Conduction in Dynamic Thermal Models: Analytical Tests for Validation* (Bland 1992).


# Description of BEPAC/Bland Tests

The BEPAC validation package includes FORTRAN routines for calculating
the results of the analytical solutions. The abstract from B.H. Bland’s
original paper provides an excellent overview of the purpose and
applicability of these tests:

> Analytical tests are based on physically simple cases for which the
> exact solution is known. A set of recommended analytical tests is
> described for the validation of conduction calculations in dynamic
> thermal models of buildings. They are one product of a collaborative
> research project on model validation. The principal advance is the
> explicit recognition of the need to design tests differently for (a)
> verification and bugging, in which not more than one source of error
> should contribute to the difference observed between model predictions
> and exact solution, and (b) tests to estimate the likely accuracy in
> use, in which ultimately all sources of error should be active in the
> way that they would be in a normal building simulation. The chief
> obstacles to creating such clear-cut tests are the discretion errors
> arising from input sampling and reconstruction, and other deliberate
> approximations used in the modeling. It is shown that it is possible
> to construct tests that have all the necessary properties, without
> having recourse to tests of isolated sub-models. It is strongly
> recommended that analytical tests be made available as a software
> facility accessible to users, and be applied: (i) to programs by their
> authors, both when new, and as part of routine software maintenance,
> (ii) to established programs by independent validators. (Bland 1992)

Further discussion of the merits of analytical tests is offered in the
BEPAC report:

> Thermal models may be tested against measurements in real structures,
> or against predictions from other models. Analytical tests belong to
> this second class, and are based on physically simple cases for which
> the exact solution is known. The predictions of the model under test
> are compared with the predictions of the truth model, in this case the
> exact solution. It is called an analytical test because the exact
> solution is normally an analytical result. Truth models are never true
> in any absolute sense, they are all necessarily based on particular
> simplifications and idealizations of the real world. For example, the
> analytical tests of conduction described here are all based on three
> simplifications:
>
>-   conduction is one dimensional   
>-   the conductivity is independent of temperature   
>-   the surface conductivity is constant
>
> Real walls experience three dimensional conduction, the conductivity
> varies with temperature, and the surface conductivity varies with
> temperature and air speed, and may also be used to approximate long
> wave heat exchange, which also varies with temperature. (BEPAC 1993)

The BEPAC/Bland suite includes a variety of tests with the recommendation that a selection of the tests be performed as needed. Only one series of tests were conducted with EnergyPlus: Dynamic
Free-Floating Temperature Prediction. There are three types of Excitations that are presented in the paper: step change in outdoor temp, ramp change in outdoor temp, and sinusoidal change in outdoor temp. We did only the step change in temp.

# Dynamic Free-Floating Temperature Prediction Tests

This series of tests was applied to a test structure which was a cube
with four walls, a ceiling, and a floor all made of the same thickness
of the same material with the same surface boundary conditions. The test
zone has no fenestration. The test zone was modified to prevent interaction with the capacitance of the zone air by setting the dimensions of the cell to be 2 m by 2 m by 0.001 m to minimize the ratio of air mass to wall mass. Fifteen different types of materials were
tested including the following:

 - 0.1 mm aluminum (Test 1-1)  
 - 1 cm concrete (Test 3-1)  
 - 5 cm concrete (Test 3-2)  
 - 10 cm concrete Test 3-3)  
 - 20 cm concrete (Test 3-4)  
 - 1 cm insulation (Test 5-1)  
 - 5 cm insulation (Test 5-2)  
 - 10 cm insulation (Test 5-3)  
 - 20 cm insulation (Test 5-4)  
 - 1 cm wood (Test 7-1)  
 - 5 cm wood (Test 7-2)  
 - 10 cm wood (Test 7-3)  
 - 20 cm wood (Test 7-4)  
 - 2 mm glass (Test 9-1)  
 - 5 cm aluminum (Test 10-1)

The properties for the these materials are as follows:

<table>
<tr>
  <th>Material</th>
  <th>Conductivity $\frac{W}{mK}$</th>
  <th>Density $\frac{kg}{m^3}$</th>
  <th>Specific Heat $\frac{J}{kgK}$</th>
</tr>
<tr>
  <td>Concrete</td>
  <td>1.4</td>
  <td>2100</td>
  <td>650</td>
</tr>
<tr>
  <td>Insulation</td>
  <td>0.03</td>
  <td>30</td>
  <td>1300</td>
</tr>
<tr>
  <td>Wood</td>
  <td>0.14</td>
  <td>500</td>
  <td>2500</td>
</tr>
<tr>
  <td>Glass</td>
  <td>1.8</td>
  <td>2200</td>
  <td>560</td>
</tr>
<tr>
  <td>Aluminum</td>
  <td>160.0</td>
  <td>2800</td>
  <td>900</td>
</tr>
</table>


Each of the 15 tests consist of four independent , optional parts which
test for:

1. Steady-state heat loss. In January (see figure below), the external
   air temperature is 0C, and the heating set-point is fixed at 20C.

2. Steady-state heat gain. In April, the external air temperature id
   70C, and the cooling set-point is fixed at 50C.

3. Upward temperature step. Between February and March there is a step
   change in external air temperature from 20C to 70C.

4. Downward temperature step. The same as for the upward step, but
   using the step down from 50C to 0C from May to June.

The effects of sun and wind on the exterior surfaces were locked out.
The space temperature was allowed to float in response to outdoor temperature and heat gain/loss through the space envelope. The interior and exterior surface convection coefficient for both the analytical and EnergyPlus simulations were set as follows:

<table>
<tr>
  <th>Test</th>
  <th>Interior Convection Coefficient ( $\frac{W}{m^2K}$ )</th>
  <th>Exterior Convection Coefficient ( $\frac{W}{m^2K}$ )</th>
</tr>
<tr>
  <td>1-1</td>
  <td>0.1</td>
  <td>10.22</td>
</tr>
<tr>
  <td>3-1</td>
  <td>0.1</td>
  <td>12.49</td>
</tr>
<tr>
  <td>3-2</td>
  <td>0.1</td>
  <td>12.49</td>
</tr>
<tr>
  <td>3-3</td>
  <td>0.1</td>
  <td>12.49</td>
</tr>
<tr>
  <td>3-4</td>
  <td>0.1</td>
  <td>12.49</td>
</tr>
<tr>
  <td>5-1</td>
  <td>0.1</td>
  <td>11.58</td>
</tr>
<tr>
  <td>5-2</td>
  <td>0.1</td>
  <td>11.58</td>
</tr>
<tr>
  <td>5-3</td>
  <td>0.1</td>
  <td>11.58</td>
</tr>
<tr>
  <td>5-4</td>
  <td>0.1</td>
  <td>11.58</td>
</tr>
<tr>
  <td>7-1</td>
  <td>0.1</td>
  <td>10.79</td>
</tr>
<tr>
  <td>7-2</td>
  <td>0.1</td>
  <td>10.79</td>
</tr>
<tr>
  <td>7-3</td>
  <td>0.1</td>
  <td>10.79</td>
</tr>
<tr>
  <td>7-4</td>
  <td>0.1</td>
  <td>10.79</td>
</tr>
<tr>
  <td>9-1</td>
  <td>0.1</td>
  <td>8.23</td>
</tr>
<tr>
  <td>10-1</td>
  <td>0.1</td>
  <td>10.22</td>
</td>
</table>


# Weather data


The weather file used for the R.H. Bland analytical tests is a steady-state excitation with an upward step change in outdoor temperature, from 0°C to 20°C at the beginning of February and from 20°C
to 70°C at the beginning of March, and downward step changes in outdoor
temperature from 70°C to 50°C at the beginning of May and from 50°C to
0°C at the beginning of June. A twelve month weather file with one hour
time steps was developed with these characteristics, however, only the
first seven months are relevant to the tests.


# Results

EnergyPlus Simulations were done for an entire year using three different timesteps: 15 minute (Timestep=4), 10 minute (Timestep=6) and 3 minute (Timestep=20). The results comparing the EnergyPlus surface outside and inside temperatures to the analytical results for each of the 15 tests are shown in Appendix A. Since steady state conditions after each step change in outdoor temperature are usually reached within several days after the step change, the results shown on the charts are only for a 7 day period at the time of each step change, i.e. the day
before the step change and 6 days after the step change. EnergyPlus showed excellent agreement with the analytical results with the Timestep=20 simulations giving better agreement. Minor differences occurred with Tests 5-4 where the inside surface temperatures slightly lagged the analytical inside temperature.


# References

BEPAC 1993, B.H. Bland, *Conduction tests for the validation of dynamic thermal models of buildings*, Technical Note 93/1, August 1993.

Bland, B.H. 1992, “Conduction in dynamic thermal models: Analytical
tests for validation”, *Building Services Engineering Research and Technology*, 13(4), pp 197-208.

# Appendix A

**Charts Showing Results of Bland Tests with EnergyPlus Version {{ engine.config["EnergyPlusVersion"] }}**


```{exec_python}

engine.write_chart('ScatterLinesNoMarkers', '1-1 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n1-1: 0.1 mm Aluminum - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '1-1 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('1-1 Data TS-6'!D7,'1-1 Data TS-6'!B8:B3314,'1-1 Data TS-6'!D8:D3314,3);('1-1 Data TS-20'!D7,'1-1 Data TS-20'!B8:B11028,'1-1 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '1-1 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n1-1: 0.1 mm Aluminum - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '1-1 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('1-1 Data TS-6'!E7,'1-1 Data TS-6'!B8:B3314,'1-1 Data TS-6'!E8:E3314,3);('1-1 Data TS-20'!E7,'1-1 Data TS-20'!B8:B11028,'1-1 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '3-1 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n3-1: 1 cm Concrete - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '3-1 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('3-1 Data TS-6'!D7,'3-1 Data TS-6'!B8:B3314,'3-1 Data TS-6'!D8:D3314,3);('3-1 Data TS-20'!D7,'3-1 Data TS-20'!B8:B11028,'3-1 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '3-1 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n3-1: 1 cm Concrete - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '3-1 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('3-1 Data TS-6'!E7,'3-1 Data TS-6'!B8:B3314,'3-1 Data TS-6'!E8:E3314,3);('3-1 Data TS-20'!E7,'3-1 Data TS-20'!B8:B11028,'3-1 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '3-2 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n3-2: 5 cm Concrete - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '3-2 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('3-2 Data TS-6'!D7,'3-2 Data TS-6'!B8:B3314,'3-2 Data TS-6'!D8:D3314,3);('3-2 Data TS-20'!D7,'3-2 Data TS-20'!B8:B11028,'3-2 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '3-2 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n3-2: 5 cm Concrete - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '3-2 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('3-2 Data TS-6'!E7,'3-2 Data TS-6'!B8:B3314,'3-2 Data TS-6'!E8:E3314,3);('3-2 Data TS-20'!E7,'3-2 Data TS-20'!B8:B11028,'3-2 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '3-3 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n3-3: 10 cm Concrete - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '3-3 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('3-3 Data TS-6'!D7,'3-3 Data TS-6'!B8:B3314,'3-3 Data TS-6'!D8:D3314,3);('3-3 Data TS-20'!D7,'3-3 Data TS-20'!B8:B11028,'3-3 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '3-3 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n3-3: 10 cm Concrete - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '3-3 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('3-3 Data TS-6'!E7,'3-3 Data TS-6'!B8:B3314,'3-3 Data TS-6'!E8:E3314,3);('3-3 Data TS-20'!E7,'3-3 Data TS-20'!B8:B11028,'3-3 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '3-4 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n3-4: 20 cm Concrete - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '3-4 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('3-4 Data TS-6'!D7,'3-4 Data TS-6'!B8:B3314,'3-4 Data TS-6'!D8:D3314,3);('3-4 Data TS-20'!D7,'3-4 Data TS-20'!B8:B11028,'3-4 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '3-4 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n3-4: 20 cm Concrete - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '3-4 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('3-4 Data TS-6'!E7,'3-4 Data TS-6'!B8:B3314,'3-4 Data TS-6'!E8:E3314,3);('3-4 Data TS-20'!E7,'3-4 Data TS-20'!B8:B11028,'3-4 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '5-1 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n5-1: 1 cm Insulation - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '5-1 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('5-1 Data TS-6'!D7,'5-1 Data TS-6'!B8:B3314,'5-1 Data TS-6'!D8:D3314,3);('5-1 Data TS-20'!D7,'5-1 Data TS-20'!B8:B11028,'5-1 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '5-1 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n5-1: 1 cm Insulation - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '5-1 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('5-1 Data TS-6'!E7,'5-1 Data TS-6'!B8:B3314,'5-1 Data TS-6'!E8:E3314,3);('5-1 Data TS-20'!E7,'5-1 Data TS-20'!B8:B11028,'5-1 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '5-2 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n5-2: 5 cm Insulation - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '5-2 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('5-2 Data TS-6'!D7,'5-2 Data TS-6'!B8:B3314,'5-2 Data TS-6'!D8:D3314,3);('5-2 Data TS-20'!D7,'5-2 Data TS-20'!B8:B11028,'5-2 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '5-2 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n5-2: 5 cm Insulation - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '5-2 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('5-2 Data TS-6'!E7,'5-2 Data TS-6'!B8:B3314,'5-2 Data TS-6'!E8:E3314,3);('5-2 Data TS-20'!E7,'5-2 Data TS-20'!B8:B11028,'5-2 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '5-3 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n5-3: 10 cm Insulation - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '5-3 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('5-3 Data TS-6'!D7,'5-3 Data TS-6'!B8:B3314,'5-3 Data TS-6'!D8:D3314,3);('5-3 Data TS-20'!D7,'5-3 Data TS-20'!B8:B11028,'5-3 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '5-3 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n5-3: 10 cm Insulation - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '5-3 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('5-3 Data TS-6'!E7,'5-3 Data TS-6'!B8:B3314,'5-3 Data TS-6'!E8:E3314,3);('5-3 Data TS-20'!E7,'5-3 Data TS-20'!B8:B11028,'5-3 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '5-4 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n5-4: 20 cm Insulation - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Inside Surface Temperature (C)', 'Results-Step-FF-TS20.xlsx', '5-4 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('5-4 Data TS-6'!D7,'5-4 Data TS-6'!B8:B3314,'5-4 Data TS-6'!D8:D3314,3);('5-4 Data TS-20'!D7,'5-4 Data TS-20'!B8:B11028,'5-4 Data TS-20'!D8:D11028,4);", ['Increasing timestep\nmoves inside temperature\ncloser to analytical result'], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '5-4 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n5-4: 20 cm Insulation - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Outside Surface Temperature (C)', 'Results-Step-FF-TS20.xlsx', '5-4 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('5-4 Data TS-6'!E7,'5-4 Data TS-6'!B8:B3314,'5-4 Data TS-6'!E8:E3314,3);('5-4 Data TS-20'!E7,'5-4 Data TS-20'!B8:B11028,'5-4 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '7-1 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n7-1: 1 cm Wood - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '7-1 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('7-1 Data TS-6'!D7,'7-1 Data TS-6'!B8:B3314,'7-1 Data TS-6'!D8:D3314,3);('7-1 Data TS-20'!D7,'7-1 Data TS-20'!B8:B11028,'7-1 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '7-1 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n7-1: 1 cm Wood - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '7-1 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('7-1 Data TS-6'!E7,'7-1 Data TS-6'!B8:B3314,'7-1 Data TS-6'!E8:E3314,3);('7-1 Data TS-20'!E7,'7-1 Data TS-20'!B8:B11028,'7-1 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '7-2 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n7-2: 5 cm Wood - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '7-2 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('7-2 Data TS-6'!D7,'7-2 Data TS-6'!B8:B3314,'7-2 Data TS-6'!D8:D3314,3);('7-2 Data TS-20'!D7,'7-2 Data TS-20'!B8:B11028,'7-2 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '7-2 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n7-2: 5 cm Wood - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '7-2 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('7-2 Data TS-6'!E7,'7-2 Data TS-6'!B8:B3314,'7-2 Data TS-6'!E8:E3314,3);('7-2 Data TS-20'!E7,'7-2 Data TS-20'!B8:B11028,'7-2 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '7-3 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n7-3: 10 cm Wood - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '7-3 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('7-3 Data TS-6'!D7,'7-3 Data TS-6'!B8:B3314,'7-3 Data TS-6'!D8:D3314,3);('7-3 Data TS-20'!D7,'7-3 Data TS-20'!B8:B11028,'7-3 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '7-3 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n7-3: 10 cm Wood - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '7-3 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('7-3 Data TS-6'!E7,'7-3 Data TS-6'!B8:B3314,'7-3 Data TS-6'!E8:E3314,3);('7-3 Data TS-20'!E7,'7-3 Data TS-20'!B8:B11028,'7-3 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '7-4 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n7-4: 20 cm Wood - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '7-4 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('7-4 Data TS-6'!D7,'7-4 Data TS-6'!B8:B3314,'7-4 Data TS-6'!D8:D3314,3);('7-4 Data TS-20'!D7,'7-4 Data TS-20'!B8:B11028,'7-4 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '7-4 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n7-4: 20 cm Wood - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '7-4 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('7-4 Data TS-6'!E7,'7-4 Data TS-6'!B8:B3314,'7-4 Data TS-6'!E8:E3314,3);('7-4 Data TS-20'!E7,'7-4 Data TS-20'!B8:B11028,'7-4 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)

engine.write_chart('ScatterLinesNoMarkers', '9-1 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n9-1: 2 mm Glass - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '9-1 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('9-1 Data TS-6'!D7,'9-1 Data TS-6'!B8:B3314,'9-1 Data TS-6'!D8:D3314,3);('9-1 Data TS-20'!D7,'9-1 Data TS-20'!B8:B11028,'9-1 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '9-1 Temp Profiles TS=20 Outside', 'Bland Analytical Conduction Test\n9-1: 2 mm Glass - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '9-1 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('9-1 Data TS-6'!E7,'9-1 Data TS-6'!B8:B3314,'9-1 Data TS-6'!E8:E3314,3);('9-1 Data TS-20'!E7,'9-1 Data TS-20'!B8:B11028,'9-1 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '10-1 Temp Profiles TS=20 Inside', 'Bland Analytical Conduction Test\n10-1: 5 cm Aluminum - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Inside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '10-1 Data', 'B7:F11028', "(F7,B31:B582,F31:F582,1);(D7,B31:B582,D31:D582,2);('10-1 Data TS-6'!D7,'10-1 Data TS-6'!B8:B3314,'10-1 Data TS-6'!D8:D3314,3);('10-1 Data TS-20'!D7,'10-1 Data TS-20'!B8:B11028,'10-1 Data TS-20'!D8:D11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)
engine.write_chart('ScatterLinesNoMarkers', '10-1 Temp Profiles TS=20 Outsid', 'Bland Analytical Conduction Test\n10-1: 5 cm Aluminum - Step Excitation\n2x2x0.001m cube, Floating Space Temp', 'Time (hrs)', 'Surface Outside Temperature (C)', 'Results-Step-FF-TS20.xlsx', '10-1 Data', 'B7:G11028', "(G7,B31:B582,G31:G582,1);(E7,B31:B582,E31:E582,2);('10-1 Data TS-6'!E7,'10-1 Data TS-6'!B8:B3314,'10-1 Data TS-6'!E8:E3314,3);('10-1 Data TS-20'!E7,'10-1 Data TS-20'!B8:B11028,'10-1 Data TS-20'!E8:E11028,4);", [], [], ['b-', 'g-', 'r-', 'c-', 'y-'], False)


```

