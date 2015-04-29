#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import shutil
import subprocess
from multiprocessing import current_process
import glob
import tempfile

path = os.path.dirname(__file__)
script_dir = os.path.abspath(path)

def execute_energyplus(input_name, footer_file, rvi_file, output_name, parametric_file, weather_file_name, eplus_install, additional_files):
    print ("Starting '"+str(input_name)+"' '"+str(footer_file)+"' '"+str(rvi_file)+"' '"+str(output_name)+"' '"+str(parametric_file)+"' '"+ str(weather_file_name)+"'")


    test_name = os.path.basename(input_name)

    # external tools also
    if os.path.isdir(os.path.join(eplus_install, 'Products')):
        basement      = os.path.join(eplus_install, 'Products', 'Basement')
        slab          = os.path.join(eplus_install, 'Products', 'Slab')
        basementidd   = os.path.join(eplus_install, 'Products', 'BasementGHT.idd')
        slabidd       = os.path.join(eplus_install, 'Products', 'SlabGHT.idd')
        expandobjects = os.path.join(eplus_install, 'Products', 'ExpandObjects')
        epmacro       = os.path.join(eplus_install, 'Products', 'EPMacro')
        readvars      = os.path.join(eplus_install, 'Products', 'ReadVarsESO')
        parametric    = os.path.join(eplus_install, 'Products', 'parametricpreprocessor')
        energyplus    = os.path.join(eplus_install, 'Products', 'EnergyPlus')
        idd           = os.path.join(eplus_install, 'Products', 'Energy+.idd')

    else:
        basement      = os.path.join(eplus_install, 'PreProcess', 'GrndTempCalc', 'Basement')
        slab          = os.path.join(eplus_install, 'PreProcess', 'GrndTempCalc', 'Slab')
        basementidd   = os.path.join(eplus_install, 'PreProcess', 'GrndTempCalc', 'BasementGHT.idd')
        slabidd       = os.path.join(eplus_install, 'PreProcess', 'GrndTempCalc', 'SlabGHT.idd')
        expandobjects = os.path.join(eplus_install, 'ExpandObjects')
        epmacro       = os.path.join(eplus_install, 'EPMacro')
        readvars      = os.path.join(eplus_install, 'PostProcess', 'ReadVarsESO')
        parametric    = os.path.join(eplus_install, 'PreProcess', 'ParametricPreProcessor', 'parametricpreprocessor')
        energyplus    = os.path.join(eplus_install, 'EnergyPlus')
        idd           = os.path.join(eplus_install, 'Energy+.idd')

    # Save the current path so we can go back here
    start_path = os.getcwd()

    try:
        simdir = tempfile.mkdtemp()

        print("Running simulation in: " + simdir)

        # Copy the idd into the simulation directory
        shutil.copy(idd, simdir)


        if footer_file == None:
            shutil.copy(input_name + ".idf", os.path.join(simdir, "in.idf"))

        else:
            with open(os.path.join(simdir, "in.idf"), 'w') as fo:
                with open(input_name, 'r') as fi:
                    fo.write(fi.read())

                with open(footer_file, 'r') as fi:
                    fo.write(fi.read())


        if weather_file_name != None:
            shutil.copy(weather_file_name, os.path.join(simdir, "in.epw"))

        if rvi_file != None:
            shutil.copy(rvi_file, os.path.join(simdir, "eplusout.inp"))
        else:
            if os.path.isfile(input_name + ".rvi"):
                shutil.copy(input_name + ".rvi", os.path.join(simdir, "eplusout.inp"))


        for f in additional_files:
            shutil.copy(f, simdir)

    #    sys.exit()

        # Switch to the simulation directory
        os.chdir(simdir)

        # Run EPMacro as necessary
        if os.path.exists('in.imf'):
            # print("IMF file exists")
            lines = []
            with open('in.imf') as f:
                lines = f.readlines()
            newlines = []
            for line in lines:
                if '##fileprefix' in line:
                    newlines.append('')
                    print ("Replaced fileprefix line with a blank")
                else:
                    newlines.append(line)
            with open('in.imf', 'w') as f:
                for line in newlines:
                    f.write(line)
            macro_run = subprocess.Popen(epmacro, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            macro_run.communicate()
            os.rename('out.idf','in.idf')

        # Run Preprocessor -- after EPMacro?
        if parametric_file:
            parametric_run = subprocess.Popen([parametric, 'in.idf'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            parametric_run.communicate()
            candidate_files = glob.glob('in-*.idf')
            if len(candidate_files) > 0:
                sorted_candidates = sorted(candidate_files)
                file_to_run_here = sorted(candidate_files)[0]
                if os.path.exists('in.idf'):
                    os.remove('in.idf')
                os.rename(file_to_run_here, 'in.idf')
            else:
                #print("in-000001.idf file doesn't exist -- parametric preprocessor failed")
                return [False, current_process().name]

        # Run ExpandObjects and process as necessary
        expand_objects_run = subprocess.Popen(expandobjects, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        expand_objects_run.communicate()
        if os.path.exists('expanded.idf'):
            if os.path.exists('in.idf'):
                os.remove('in.idf')
            os.rename('expanded.idf', 'in.idf')

            if os.path.exists('BasementGHTIn.idf'):
                shutil.copy(basementidd, simdir)
                basement_run = subprocess.Popen(basement, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                basement_run.communicate()
                appendText = ''
                with open('EPObjects.TXT') as f:
                    appendText = f.read()
                with open('in.idf', 'a') as f:
                    f.write("\n%s\n" % appendText)
#                os.remove('RunINPUT.TXT')
#                os.remove('RunDEBUGOUT.TXT')
#                os.remove('EPObjects.TXT')
#                os.remove('BasementGHTIn.idf')
#                os.remove('MonthlyResults.csv')
#                os.remove('BasementGHT.idd')

            if os.path.exists('GHTIn.idf'):
                shutil.copy(slabidd, simdir)
                slab_run = subprocess.Popen(slab, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                slab_run.communicate()
                appendText = ''
                with open('SLABSurfaceTemps.TXT') as f:
                    appendText = f.read()
                with open('in.idf', 'a') as f:
                    f.write("\n%s\n" % appendText)
#                os.remove('SLABINP.TXT')
#                os.remove('GHTIn.idf')
#                os.remove('SLABSurfaceTemps.TXT')
#                os.remove('SLABSplit Surface Temps.TXT')
#                os.remove('SlabGHT.idd')


        # Execute EnergyPlus
        eplus_run = subprocess.Popen(energyplus, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eplus_run.communicate()

        # Execute readvars
        if os.path.isfile('eplusout.inp'):
            csv_run = subprocess.Popen([readvars, 'eplusout.inp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            csv_run = subprocess.Popen([readvars], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        csv_run.communicate()

        with open('test.mvi', 'w') as f:
            f.write("eplusout.mtr\n")
            f.write("eplusmtr.csv\n")
        mtr_run = subprocess.Popen([readvars, 'test.mvi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mtr_run.communicate()

        if not os.path.isdir(os.path.dirname(output_name)):
            os.makedirs(os.path.dirname(output_name))

        shutil.copy("eplusout.csv", output_name + ".csv")

        if os.path.isfile("eplustbl.csv"):
            shutil.copy("eplustbl.csv", output_name + "Table.csv")

        if os.path.isfile("SLABSurfaceTemps.TXT"):
            shutil.copy("SLABSurfaceTemps.TXT", output_name + "-SLABSurfaceTemps.TXT")

        # os.remove('Energy+.idd')
        return [True, False, current_process().name]

    except Exception as e:
        print(e)
        return [False, False, current_process().name]

    finally:
        os.chdir(start_path)
        shutil.rmtree(simdir)


input_name = sys.argv[1]
footer_file = None
index = 2
rvi_file = None

print("Parmas: ("+str(len(sys.argv))+")" + str(sys.argv))

rvi_file = None
if len(sys.argv) == 7:
    footer_file = sys.argv[index]
    index += 1
    rvi_file = sys.argv[index]
    index += 1

if len(sys.argv) == 6:
    footer_file = sys.argv[index]
    index += 1


output_name = sys.argv[index]
index += 1

weather_file_name = None

if len(sys.argv) > 4:
    weather_file_name = sys.argv[index]
    index += 1

eplus_install = sys.argv[index]
additional_files = []

parentfolder = os.path.dirname(os.path.dirname(os.path.abspath(input_name)))

if os.path.isfile(os.path.join(parentfolder, "GHTIn.idf")):
    additional_files.append(os.path.join(parentfolder, "GHTIn.idf"))

execute_energyplus(input_name, footer_file, rvi_file, os.path.abspath(output_name), "", weather_file_name, eplus_install, additional_files)



