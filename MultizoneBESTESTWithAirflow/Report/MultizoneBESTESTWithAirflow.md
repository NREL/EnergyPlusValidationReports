---
title: IEA Bestest Multi-Zone With Air Flow Cases MA101 – MA103 and Cases MA301 - MA304, Energyplus version {{ engine.config["EnergyPlusVersion"] }}  
---

Automatically Generated {{ engine.month_year() }}

Modelers Report  
Originally Prepared by  
R. Henninger & M. Witte, GARD Analytics, Inc.  

# Introduction

**Software:** EnergyPlus Version {{ engine.config["EnergyPlusVersion"] }}  
**Authoring Organization:** Department of Energy, Energy Efficiency and Renewable Energy, Office of Building Technologies  
**Authoring Country:** USA

This report describes the modeling methodology and results for Round 2
of testing done for the IEA BESTEST Multi-Zone with Air Flow Cases:
MA101 – MA103 and Cases MA301 – MA304 which were simulated using the
EnergyPlus software. The original set of Round 2 test results were submitted in December 2008 using EnergyPlus version 3.0.0.028. This report has been updated with results for EnergyPlus version {{ engine.config["EnergyPlusVersion"] }}. The specifications for the test suite are
described in *Air Flow Tests including Multi-Zone Airflow, IEA: SHC Task 34 / ECBCS Annex 43, November 2008* (referred to as the BESTEST Multi-Zone with Air Flow User’s Manual in this report).

The current status of this IEA test suite task is that a final report
still has not been published and there are several questions raised by
GARD (see Section 6) that remain unanswered.


# Modeling Assumptions

The following comments are provided in regards to user inputs that were
used with EnergyPlus to model each of the cases described in the BESTEST
Multi-Zone with Air Flow User’s Manual. Except where discussed below,
all other requirements of the specification were met.

**Cases MA101 – MA103 and Cases MA301 – MA304**

-  The requirement for an adiabatic building shell was modeled for all
    surfaces except the external surfaces with north and south exposures
    which had openings. In order for these surfaces to see the effect of
    wind pressure they had to be modeled as true exterior surfaces in
    EnergyPlus. These surfaces were made near adiabatic by assuming they
    had a 2 m thickness of insulation with conductivity of 0.0000001
    $\frac{W}{mK}$ .

-  All exterior surfaces were locked out from seeing any solar
    radiation by specifying the NoSun option for each surface.

-  Number of timesteps per hour was set to 4.

-  Building outdoor terrain was set to the Country option.

-  In order to maintain the specified constant interior zone
    temperature over the period of simulation an ideal heating/cooling
    system was specified for each zone using the
    ZoneHVAC:IdealLoadsAirSystem object in EnergyPlus which provides
    just the amount of heating or cooling necessary to each zone in
    order to maintain the scheduled set-point temperature.


# Modeling Options

To simulate air flow through exterior openings and between zones due to
wind driven or temperature difference effects the EnergyPlus Airflow
Network model was used.

The EnergyPlus AirflowNetwork model allows a wall opening through which
air flows to be modeled as a SIMPLE OPENING, DETAILED OPENING or SURFACE
CRACK. The SURFACE CRACK approach was chosen for this suite of tests
because the formulas used by EnergyPlus for the SURFACE CRACK approach
are the same as those described in the User’s Manual for the analytical
solutions. The SIMPLE OPENING and DETAILED OPENING approaches are for
openings with much larger vertical distances where air flow can move
simultaneously in two directions depending on stack effects and wind
conditions. For Case MA101, the EnergyPlus input variables describing
the crack are shown below:

    AIRFLOWNETWORK:MULTIZONE:REFERENCE CRACK CONDITIONS,
     ReferenceCrackConditions, !- Name of Reference Crack Conditions  
     20.0, !- Reference temperature for crack data {C}  
     101300, !- Reference barometric pressure for crack data {Pa}  
     0.0; !- Reference humidity ratio for crack data {kg/kg}

    AIRFLOWNETWORK:MULTIZONE:SURFACE:CRACK,
     Crack-1, !- Name of surface crack component  
     0.10866, !- Air Mass Flow Coefficient at Reference Conditions {kg/s} 
     0.5; !- Air Mass Flow Exponent {dimensionless}

The air mass flow exponent of 0.5 in EnergyPlus inputs represents the
reciprocal of the flow exponent n = 2 and the air mass flow coefficient
was calculated as follows using the mass flow coefficient equation for
“a” on page 6 of the User’s Manual:

> $a=\frac{C_dA\sqrt{2\rho}}{l}$

where:  

> - $C_d$ = 0.7  
> - A = 0.1 $m^2$  
> - $\rho$ = 1.204 $\frac{kg}{m^3}$  
> - l = 1.0

A 24 hour design day was used for the simulation period with the
parameters for the design day weather set to those specified in Table
3-1 of the User’s Manual except that the outdoor dry-bulb temperature
and wind speed were varied in accordance with that required for each
test case.


# Modeling Difficulties

Table 3-1 summarizes the site and weather parameters for test case
MA101. These parameters were specified in EnergyPlus by using the
DESIGNDAY object as set forth below.

SizingPeriod:DesignDay,

    MIAMI_FL_USA, !- Name  
     7, !- Month  
     21, !- Day of Month  
     SummerDesignDay, !- Day Type  
     20.0, !- Maximum Dry-Bulb Temperature {C}  
     0.0, !- Daily Dry-Bulb Temperature Range {deltaC}  
     , !- Dry-Bulb Temperature Range Modifier Type  
     , !- Dry-Bulb Temperature Range Modifier Schedule Name  
     DewPoint, !- Humidity Condition Type  
     -56.6, !- Wetbulb or DewPoint at Maximum Dry-Bulb {C}  
     , !- Humidity Condition Day Schedule Name  
     , !- Humidity Ratio at Maximum Dry-Bulb {kgWater/kgDryAir}  
     , !- Enthalpy at Maximum Dry-Bulb {J/kg}  
     , !- Daily Wet-Bulb Temperature Range {deltaC}  
     101300., !- Barometric Pressure {Pa}  
     2.0, !- Wind Speed {m/s}  
     0.0, !- Wind Direction {deg}  
     No, !- Rain Indicator  
     No, !- Snow Indicator  
     No, !- Daylight Saving Time Indicator  
     ASHRAEClearSky, !- Solar Model Indicator

     , !- Beam Solar Day Schedule Name  
     , !- Diffuse Solar Day Schedule Name  
     , !- ASHRAE Clear Sky Optical Depth for Beam Irradiance  
     (taub) {dimensionless}  
     , !- ASHRAE Clear Sky Optical Depth for Diffuse Irradiance  
     (taud) {dimensionless}  
     1.0; !- Sky Clearness

Table 3-1 in the User’s Manual indicates that for a 20 C dry-bulb temperature and –56.6 C dew-point temperature the resulting humidity ratio is 0.000007 kg/kg and the relative humidity is 0.05%. For these conditions, EnergyPlus calculates a humidity ratio of 0.00000104 kg/kg and relative humidity of 0.72%.


# Results

Results for each test are presented in an Excel spreadsheet provided
with the BESTEST Multi-Zone with Air Flow test suite. The EnergyPlus
results are reported on a spreadsheet provided by with the BESTEST
Multi-Zone with Air Flow User’s Manual, a copy of which is reproduced at
the end of this report. Also on the last page is a comparison of the
EnergyPlus results to analytical results along with the percentage
difference between the two. Converting of air mass flow rates (kg/s) to
air volume flow rates ( $\frac{m^3}{s}$ ) requires the use of air density. The
EnergyPlus air volume flow rates are based on the outside air density
which changes depending on the test case. For Cases MA101 and MA301 the
outdoor air temperature is 20C with a corresponding air density of 1.204 $\frac{kg}{m^3}$. For all other test cases the outdoor air temperature is 0C with a corresponding air density of 1.293 $\frac{kg}{m^3}$. The BESTEST Multi-Zone with Air Flow specification does not indicate what air density conditions were assumed for the analytical results. One might expect that the percentage differences when comparing EnergyPlus results to analytical results should be the same for mass flow rates and volume flow rates on a case by case basis. Due to the inclusion of air density in the volume flow rate conversion, the smaller numbers produce different percentages


# Issues

The results reported below are not to be considered final for this second round of testing due to a couple of issues that still need to be resolved:

-   Further clarification was requested from the authors of the
    specification regarding the air density assumption that the
    analytical results are based on. An e-mail request was sent to Dr.
    Yasuo Utsumi, Institutes of National Colleges of Technology, Natori,
    on 11/9/06 requesting clarification.

-   A follow-up e-mail from Dr. Utsumi indicated that they had found a
    mistake in the analytical results and following a meeting of the
    Japanese committee they would be responding to our request. The
    result was a revised user manual dated March 2007 which eliminated
    Cases MA201, MA202, MA203 and MA204. The User Manual also changed
    some the zone interior temperatures.

It still is not clear as to what assumptions have been made to arrive at
the latest analytical results. An e-mail was sent to Dr. Utsumi on April 17, 2007 with numerous suggestions and questions compiled by Dr. Lixing Gu from FSEC which are summarized below. As of the writing of this report there has been no response from Dr. Utsumi.

- Provide detailed derivation to get analytical solution. It is needed
to help users understand how the analytical solutions are derived and
what assumptions are used to get analytical solutions.

- Need references. We don't think that the authors developed everything
related to the analytical solutions. It is a good practice to acknowledge previous work.

- Mass flow rate. We think that under steady-state conditions, mass is
conservative, while volume flow rate may not be conservative. It would
be better to use mass flow rate to compare results instead of volumetric
rate.

- Provide detailed calculation procedures as to how to get results from
analytical solutions. Detailed calculations could the be shown in an
appendix or attachment to show which values are used to obtain
analytical results. We tried to calculate the analytical results for
Cases MA101, 102, 303 and 304 and could not get the same results for
these cases.

- For Case MA101, although there is no density variation involved, we
could not get the same results as BESTEST. Please give me more direction.

- How do you handle negative values from the buoyancy calculation? Each
buoyancy term, $g\cdot$ density difference $\cdot h$  on page 11 of the User Manual may be positive and negative. The sum of the buoyancy term is negative in MA102 and MA303 from our calculations. If we use the absolute value of buoyancy term, the result is close to the BESTEST results for MA102
and MA303. Otherwise, results are way off.

- Flow coefficient calculation (a) on page 8. Based on equations used
to calculate flow coefficients, air density is an independent variable.
Which air density should be used to calculate flow coefficients:
upstream, downstream, or average? It is not clear from the document.


# References

EnergyPlus 2014. Department of Energy, Energy Efficiency and Renewable
Energy, Office of Building Technologies.
[www.energyplus.gov](http://www.energyplus.gov)

Air Flow Tests Including Multi-Zone Airflow, Draft IEA Report, IEA: SHC
Task 34 / ECBCS Annex 43, November 2008

# EnergyPlus results as reported on standard output form

{{ engine.create_table_from_excel_range('MZ-Air_Flow-Output-EPlus.xlsx', 'StandardOutput', 'D14:L42', info_rows=range(0, 4)) }}

# EnergyPlus results compared to analytical results

{{ engine.create_table_from_excel_range('Multi-Zone with Airflow Results-Round 2.xlsx', 'Sheet1', 'A22:J36', info_rows=[0,13,14]) }}


