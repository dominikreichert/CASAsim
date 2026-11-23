####
#
# CASAsim
# Circular Automotive Steel and Aluminum simulation model for assessing the
# closed-loop recycled content of steel and aluminum in new passenger cars
# 
# AUTHOR: Dominik Reichert
#         Technical University of Munich
#         (dominik.reichert@tum.de)
#  
# VERSION: 1.0.0
# 
# PUBLISHED: 23/11/2026
#
# LICENSE: Copyright 2026 Dominik Reichert
#     Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0.
#     Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
####


import pandas as pd
from scipy.stats import weibull_min
import matplotlib.pyplot as plt
from datetime import datetime
import os
import re
import shutil

from reader import import_data
from calculator import *
from analyzer import run_sa, interpret_sa
from plotter import plot_data
from plotter_sa import plot_sa_data
from plotter_multi import plot_multi_data
from writer import export
from writer_sa import export_sa_data



############################################################################

###  
###  SETTINGS
###

# Set Weibull parameters:
SHAPE = 3.2     # k
SCALE = 16.75   # lambda

# Set time span for plotting results:
# (!) Years must be consistant with the input data.
PLOTTER_START_YEAR = 2025
PLOTTER_END_YEAR = 2050

# Perform sensitivity analysis?
# (!) This function can lead to a significant increase in computing time.
PERFORM_SA = True  # [True/False]
SENSITIVITY = 0.2
TARGET_YEARS = [2030, 2050]

############################################################################



###
###  START
###

print('\n##### CASAsim - Closed-Loop Circularity Assessment for Automotive Steel and Aluminum #####')
print('Copyright 2026 Dominik Reichert')

plots = []
results = []



###
###  SEARCH FOR INPUT FILES
###

print('\n>  Looking for input files...')

files = sorted([
    file for file in os.listdir('data/')
    if file.lower().startswith('data') and file.lower().endswith(('.xls', '.xlsx'))
])

if not files:
    raise FileNotFoundError(f"(!) The expected input file 'data.xlsx' was not found in 'data/'.")
    
n_scenarios = len(files)

print(f'   number of input files (scenarios) found: {n_scenarios}')



###
###  IMPORT DATA
###

scenario_names = list()

for s in range(n_scenarios):

    if n_scenarios > 1:
        match = re.match(r"data_(\d{1,2})_(.+)\.xlsx?", files[s])

        if match:
            scenario_id = match.group(1)
            scenario_id_int = int(match.group(1))
            scenario_name = match.group(2).replace("_", " ")
            scenario_names.append(scenario_name)

        else:
            print(f"(!) input file name '{files[s]}' does not match the required pattern.")

        #scenario_id = re.search(r'data_(\d+)\.xlsx$', files[s]).group(1)

        print(f'\n>  Importing data of scenario {scenario_id}...')

    else:
        print('\n>  Importing data...')

    import_file = f"data/{files[s]}"

    start_year, end_year, n_years, n_vehicles, vehicles_names, vehicles_data, cagr, n_init_years, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, steel_production, aluminum_production, component_production, tmp_import = import_data(import_file)



    ###
    ###  MODELING
    ###

    print(f'\n>  Start modeling...')

    set_years = range(start_year, end_year + 1)
    set_vehicles = range(1, n_vehicles + 1)

    tmp = {}


    # (1) MODEL VEHICLES

    print('\n>  Modeling vehicles...')

    vehicles_data = calc_vehicles(start_year, end_year, n_vehicles, vehicles_data)

    tmp['vehicles_data'] = vehicles_data

    print('   modeling vehicles done.')


    # (2) MODEL VEHICLE REGISTRATIONS

    registrations_origin = registrations.copy()

    init_year = start_year + n_init_years - 1  # last year for which registration data is defined in the input file

    if n_init_years == 0:
        raise ValueError("(!) Registrations cannot be predicted because no registration data is defined in the input file. Please add registration data for at least one year.")

    if init_year >= end_year:
        print('\n>  Vehicle registrations already defined.')

    elif init_year < end_year:
        print('\n>  Modeling future vehicle registrations...')

        registrations = calc_registrations(start_year, end_year, set_vehicles, cagr, init_year, registrations)

    tmp['registrations'] = registrations

    print('   modeling future vehicle registrations done.')


    # (3) MODEL VEHICLE FLEET

    print('\n>  Modeling vehicle fleet...')

    fleet_detail, fleet = calc_fleet(start_year, end_year, set_years, set_vehicles, registrations, SHAPE, SCALE)

    tmp['fleet_detail'] = fleet_detail
    tmp['fleet'] = fleet

    print('   modeling vehicle fleet done.')


    # (4) MODEL END-OF-LIFE VEHICLES
    #
    # (4.1) MODEL FLEET EXITS
    # (4.2) MODEL EXPORTS AND UNKNOWN WHEREABOUTS
    # (4.3) MODEL VEHICLES ENTERING RECYCLING

    print('\n>  Modeling ELVs...')

    fleet_detail, fleet = calc_eol(start_year, set_years, set_vehicles, fleet_detail, fleet, eol_loss)

    tmp['fleet_detail'] = fleet_detail
    tmp['fleet'] = fleet

    print('   modeling ELVs done.')


    # (5) MODEL RECYCLING

    print('\n>  Modeling recycling...')

    eol_veh, eol = calc_recycling(start_year, set_years, set_vehicles, vehicles_data, fleet_detail, eol_dismantling, eol_dismantling_recycling, eol_pst)

    tmp['eol_veh'] = eol_veh
    tmp['eol'] = eol

    print('   modeling recycling done.')


    # (6) MODEL MATERIAL DEMANDS AND SUPPLIES
    #
    # (6.1) MODEL MATERIAL DEMAND IN NEW VEHILCES
    #       AND MATERIAL PRODUCTION
    # (6.2) CALCULATE MATERIAL SUPPLY FROM INTERNAL,
    #       PRE-CONSUMER, AND POST-CONSUMER SCRAP

    print('\n>  Modeling material demands and supplies...')

    material_demand, material_supply = calc_demandSupply(start_year, end_year, set_years, set_vehicles, registrations, vehicles_data, eol, component_production, steel_production, aluminum_production, eol_dismantling_recycling, eol_pst)

    tmp['material_demand'] = material_demand
    tmp['material_supply'] = material_supply

    print('   modeling material demands and supplies done.')


    # (7) MODEL MATERIAL USE BY ALLOCATNG (SCRAP) MATERIAL SUPPLY
    #     TO MEET MATERIAL DEMAND

    print('\n>  Modeling material use...')

    material_use, material_quality, objective, eol_pst = calc_use(start_year, end_year, set_years, eol, material_demand, material_supply, steel_production, aluminum_production, eol_dismantling_recycling, eol_pst)

    tmp['material_use'] = material_use
    tmp['material_quality'] = material_quality
    tmp['objective'] = objective
    tmp['eol_pst'] = eol_pst

    print('   modeling material use done.')


    # (8) MODEL CLOSED-LOOP RATES

    print('\n>  Modeling closed-loop rates...')

    closedloop = calc_closedloop(set_years, material_demand, material_use)

    tmp['closedloop'] = closedloop

    results.append((material_use, closedloop))

    print('   modeling closed-loop rates done.')



    ###
    ###  SENSITIVITY ANALYSIS
    ###

    if PERFORM_SA:

        print('\n>  Performing sensitivity analysis...')

        sa_closedloop_plus, sa_closedloop_minus, sa_materialuse_plus, sa_materialuse_minus, sa_titles, sa_tmp_plus, sa_tmp_minus, sa_tmp_elements = run_sa(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, n_init_years, registrations_origin, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE, SENSITIVITY, material_quality, s, n_scenarios)

        n_sa_iterations = len(sa_closedloop_plus)

        sa_closedloop_max, sa_closedloop_min, sa_material_use_max, sa_material_use_min, infeasible_sa_runs = interpret_sa(start_year, set_years, closedloop, material_use, sa_closedloop_plus, sa_closedloop_minus, sa_materialuse_plus, sa_materialuse_minus, sa_tmp_plus, sa_tmp_minus)

        print('   sensitivity analysis done.')



    ###
    ###  EXPORT RESULTS
    ###

    color = pd.DataFrame({
            'steel': (0/255, 81/255, 117/255, 1),
            'flatsteel': (44/255, 159/255, 212/255, 1),
            'flatsteel_t': (44/255, 159/255, 212/255, 0.5),
            'longsteel': (151/255, 173/255, 189/255, 1),
            'longsteel_t': (151/255, 173/255, 189/255, 0.5),
            'aluminum': (0/255, 102/255, 47/255, 1),
            'mixedaluminum': (186/255, 99/255, 32/255, 1),
            'castaluminum_lowCu': (106/255, 204/255, 146/255, 1),
            'castaluminum_lowCu_t': (106/255, 204/255, 146/255, 0.5),
            'castaluminum_highCu': (185/255, 185/255, 55/255, 1),
            'castaluminum_highCu_t': (185/255, 185/255, 55/255, 0.5),
            'wroughtaluminum': (30/255, 90/255, 60/255, 1),
            'wroughtaluminum_t': (30/255, 90/255, 60/255, 0.5),
            'total': (140/255, 25/255, 25/255, 1),
            'ICEV': (48/255, 66/255, 141/255, 1),
            'BEV': (64/255, 139/255, 102/255, 1),
            'internal': (205/255, 197/255, 191/255, 1),
            'preconsumer': (122/255, 197/255, 205/255, 1),
            'postconsumer': (124/255, 205/255, 124/255, 1),
            'virgin': (201/255, 73/255, 73/255, 1),
            'openloop': (238/255, 220/255, 130/255, 1)
        })

    print('\n>  Export scenario results...')


    # (a) EXPORT RESULTS IF THERE IS ONLY ONE SCENARIO

    if n_scenarios == 1:


        # CREATE RESULTS FOLDER

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        _export_path = 'results/' + timestamp
        os.makedirs(_export_path, exist_ok=True)

        export_path = _export_path + '/'

        dst = export_path
        shutil.copy(import_file, dst)

        print('   results folder created.')


        # SAVE TMP FILES

        with pd.ExcelWriter(f'{export_path}tmp_import.xlsx', engine='openpyxl') as writer:
            for sheet_name, df in tmp_import.items():
                df.to_excel(writer, sheet_name=str(sheet_name))

        with pd.ExcelWriter(f'{export_path}tmp_calc.xlsx', engine='openpyxl') as writer:
            for sheet_name, df in tmp.items():
                if isinstance(df, pd.DataFrame):
                    df.to_excel(writer, sheet_name=str(sheet_name))
                else:
                    pd.DataFrame({'value': [df]}).to_excel(writer, sheet_name=str(sheet_name))

        print('   tmp files exported.')


        # PLOT SIMULATION RESULTS

        plots_df = plot_data(export_path, set_years, set_vehicles, vehicles_names, registrations, cagr, fleet, material_demand, material_supply, material_use, closedloop, material_quality, steel_production, aluminum_production, color, PLOTTER_START_YEAR, PLOTTER_END_YEAR)

        print(f'   plots created.')

        # Plot sensitivity analysis results:

        if PERFORM_SA:
            _path = export_path + 'sensitivity_analysis'
            os.makedirs(_path, exist_ok=True)
            export_sa_path = _path + '/'

            _path = export_sa_path + 'tmp'
            os.makedirs(_path, exist_ok=True)
            export_sa_tmp_path = _path + '/'

            sa_plots_df = plot_sa_data(export_sa_path, set_years, PLOTTER_START_YEAR, PLOTTER_END_YEAR, material_demand, material_supply, material_use, closedloop, steel_production, aluminum_production, TARGET_YEARS, sa_closedloop_plus, sa_closedloop_minus, sa_materialuse_plus, sa_materialuse_minus, sa_titles, sa_tmp_plus, sa_tmp_minus, SENSITIVITY, color, n_sa_iterations, sa_closedloop_max, sa_closedloop_min, sa_material_use_max, sa_material_use_min)

            plots.append(pd.concat([plots_df, sa_plots_df], axis=1))

            print('   sensitivity analysis plots created.')


            export_sa_data(export_sa_tmp_path, set_years, sa_tmp_plus, sa_tmp_minus, sa_tmp_elements, infeasible_sa_runs)

            print('   sensitivity analysis data exported.')

        else:
            plots.append(plots_df)

        print('   plots created.')

    
    # (b) EXPORT MULTI-SCENARIO RESULTS

    else:

        # CREATE RESULTS FOLDER

        if s == 0:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            _export_path = 'results/' + timestamp

        export_path_origin = f'{_export_path}/'
        export_path = f'{_export_path}/scenario_{scenario_id}/'
        os.makedirs(export_path, exist_ok=True)

        dst = export_path + files[s]
        shutil.copy(import_file, dst)

        print('   results folder created.')


        # SAVE TMP FILES

        with pd.ExcelWriter(f'{export_path}tmp_import.xlsx', engine='openpyxl') as writer:
            for sheet_name, df in tmp_import.items():
                df.to_excel(writer, sheet_name=str(sheet_name))

        with pd.ExcelWriter(f'{export_path}tmp_calc.xlsx', engine='openpyxl') as writer:
            for sheet_name, df in tmp.items():
                if isinstance(df, pd.DataFrame):
                    df.to_excel(writer, sheet_name=str(sheet_name))
                else:
                    pd.DataFrame({'value': [df]}).to_excel(writer, sheet_name=str(sheet_name))

        print('   tmp files exported.')


        # PLOT SIMULATION RESULTS

        plots_df = plot_data(export_path, set_years, set_vehicles, vehicles_names, registrations, cagr, fleet, material_demand, material_supply, material_use, closedloop, material_quality, steel_production, aluminum_production, color, PLOTTER_START_YEAR, PLOTTER_END_YEAR)

        print(f'   plots created.')
        

        # Plot sensitivity analysis results:

        if PERFORM_SA:
            _path = export_path + 'sensitivity_analysis'
            os.makedirs(_path, exist_ok=True)
            export_sa_path = _path + '/'

            _path = export_sa_path + 'tmp'
            os.makedirs(_path, exist_ok=True)
            export_sa_tmp_path = _path + '/'

            sa_plots_df = plot_sa_data(export_sa_path, set_years, PLOTTER_START_YEAR, PLOTTER_END_YEAR, material_demand, material_supply, material_use, closedloop, steel_production, aluminum_production, TARGET_YEARS, sa_closedloop_plus, sa_closedloop_minus, sa_materialuse_plus, sa_materialuse_minus, sa_titles, sa_tmp_plus, sa_tmp_minus, SENSITIVITY, color, n_sa_iterations, sa_closedloop_max, sa_closedloop_min, sa_material_use_max, sa_material_use_min)

            plots.append(pd.concat([plots_df, sa_plots_df], axis=1))

            print('   sensitivity analysis plots created.')


            export_sa_data(export_sa_tmp_path, set_years, sa_tmp_plus, sa_tmp_minus, sa_tmp_elements, infeasible_sa_runs)
            
            print('   sensitivity analysis data exported.')

        else:
            plots.append(plots_df)

        print('   plots created.')


# EXPORT SCENARIO-COMPARISON RESULTS

if n_scenarios > 1:

    print('\n>  Export scenario-comparison results...')

    plot_multi_data(export_path_origin, results, scenario_names, n_scenarios, set_years, material_use, closedloop, color, PLOTTER_START_YEAR, PLOTTER_END_YEAR, plots, PERFORM_SA)

    print(f'   scenario-comparison results exported.')


print('\n>  End')
