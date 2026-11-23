####
#
# CASAsim
# Sensitivity Analysis Module
# 
# AUTHOR: Dominik Reichert
#         Technical University of Munich
#         (dominik.reichert@tum.de)
#  
# VERSION: 1.0.0
#
# LICENSE: Copyright 2026 Dominik Reichert
#  
####


import pandas as pd
import numpy as np
from scipy.stats import weibull_min

from calculator import *


def run_sa(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, n_init_years, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE, SENSITIVITY, material_quality, s, n_scenarios):


    ############################################################################

    ###  
    ###  SENSITIVITY ANALYSIS (SA) CONFIGURATION
    ###

    # Define which parameters to be included in the sensitivity analysis per scenario.
    # The following parameters are considered for sensitivity analysis:

    # SA.1.1:   Vehicle data (total mass, material contents)
    #           (!) For changes of sub-material contents (e.g., flat steel), changes in one material share (e.g., for flat steel)
    #               are compensated by opposite changes in the other material shares (e.g., for long steel) to keep and not exceed 100%.
    # SA.1.2:   CAGR
    # SA.1.3:   Systemic loss (exports, unknwown whereabouts)
    # SA.1.4:   Dismantling contents
    # SA.1.5a:  Dismantling-recycling efficiency (yield)
    # SA.1.5b:  Dismantling-recycling contamination
    #           (!) Contamination parameters are varied by adding/subtracting a percentage (sensitivity factor) of the quality threshold
    #               in material production.
    # SA.1.6a:  PST recycling efficiency (yield)
    # SA.1.6b:  PST recycling contamination
    #           (!) Contamination parameters are varied by adding/subtracting a percentage (sensitivity factor) of the quality threshold
    #               in material production.
    # SA.1.7a:  Steel production routes setting
    #           (!) Changes in one production route are compensated by opposite changes in the other two routes to keep 100% production.
    # SA.1.7b:  Steel production route configuration (min scrap, max scrap, yield, scrap recycling rate)
    # SA.1.7c:  Steel quality thresholds
    # SA.1.7d:  Virgin steel quality
    # SA.1.8a:  Aluminum production configuration (min scrap, max scrap, yield, scrap recycling rate)
    # SA.1.8b:  Aluminum quality thresholds
    # SA.1.8c:  Virgin aluminum quality
    # SA.1.9:   Component production configuration (yield, scrap recycling rate)


    # Define the SA config matrix:
    # Rows represent parameters, columns represent scenarios (S01, S02, etc.).
    # Add or remove columns as needed based on the total number of scenarios.
    # True = include in SA, False = exclude from SA.

    sa_config = [
    #    S01,       S02,        S03,        S04
        [True,      False,      False,      False],     # SA.1.1: Vehicle data
        [False,     True,       False,      True],      # SA.1.2: CAGR
        [False,     True,       False,      True],      # SA.1.3: Systemic loss
        [False,     False,      True,       True],      # SA.1.4: Dismantling content
        [False,     False,      True,       True],      # SA.1.5a: Dismantling-recycling yield
        [False,     False,      True,       True],      # SA.1.5b: Dismantling-recycling contamination
        [False,     False,      True,       True],      # SA.1.6a: PST recycling yield
        [False,     False,      True,       True],      # SA.1.6b: PST recycling contamination
        [False,     True,       False,      True],      # SA.1.7a: Steel production routes
        [False,     True,       False,      False],     # SA.1.7b: Steel production configuration
        [False,     True,       False,      False],     # SA.1.7c: Steel quality thresholds
        [False,     False,      False,      False],     # SA.1.7d: Virgin steel quality
        [False,     True,       False,      False],     # SA.1.8a: Aluminum production configuration
        [False,     True,       False,      False],     # SA.1.8b: Aluminum quality thresholds
        [False,     False,      False,      False],     # SA.1.8c: Virgin aluminum quality
        [False,     True,       False,      False],     # SA.1.9: Component production configuration
    ]

    ############################################################################

    if len(sa_config[0]) != n_scenarios:
        raise Exception("ERROR: The number of scenarios configurated for the SA in analyzer.py must be consistent with the total number of scenarios!")
    
    sa_closedloop_plus = []
    sa_closedloop_minus = []
    sa_materialuse_plus = []
    sa_materialuse_minus = []
    sa_titles = []
    sa_tmp_plus = {}
    sa_tmp_minus = {}
    sa_tmp_elements = ['vehicles_data', 'cagr', 'registrations', 'fleet_detail', 'fleet', 'eol_veh', 'eol', 'material_demand', 'material_supply', 'material_use', 'material_quality', 'objective_value', 'closedloop', 'eol_loss', 'eol_dismantling', 'eol_dismantling_recycling', 'eol_pst', 'component_production', 'steel_production', 'aluminum_production']


    # (SA.1) INPUT DATA

    # (SA.1.1) VEHICLES_DATA

    if sa_config[0][s]:

        # (SA.1.1.1) VEHICLES_DATA: TOTAL_MASS

        for i in range(1, n_vehicles + 1):

            print(f'   (SA:) calculating +{SENSITIVITY * 100}% for total_mass, vehicle {i}...')

            _vehicles_data = vehicles_data.copy()

            for j in range(start_year, end_year + 1):
                value = vehicles_data.loc[(i, j), 'total_mass'] 
                _vehicles_data.loc[(i, j), 'total_mass'] = value * (1 + SENSITIVITY)
                
            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, _vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_plus.append(_closedloop)
            sa_materialuse_plus.append(_material_use)

            name = f'total_mass_vehicle_{i}'
            sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

            ##

            print(f'   (SA:) calculating -{SENSITIVITY * 100}% for total_mass, vehicle {i}...')

            _vehicles_data = vehicles_data.copy()

            for j in range(start_year, end_year + 1):
                value = vehicles_data.loc[(i, j), 'total_mass'] 
                _vehicles_data.loc[(i, j), 'total_mass'] = value * (1 - SENSITIVITY)
                
            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, _vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_minus.append(_closedloop)
            sa_materialuse_minus.append(_material_use)

            name = f'total_mass_vehicle_{i}'
            sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

            sa_titles.append(f'total mass of vehicle {i}')


        # (SA.1.1.2) VEHICLES_DATA: TOTAL STEEL AND ALUMINUM CONTENTS

        parameter = ['steel_content', 'aluminum_content']
        parameter_titels = ['steel content', 'aluminum content']
        compensation_parameter = ['aluminum_content', 'steel_content']

        p_idx = 0

        for p in parameter:

            for i in range(1, n_vehicles + 1):

                print(f'   (SA:) calculating +{SENSITIVITY * 100}% for {p}, vehicle {i}...')

                _vehicles_data = vehicles_data.copy()

                for j in range(start_year, end_year + 1):
                    value_old = vehicles_data.loc[(i, j), p] 
                    value_new = min(value_old * (1 + SENSITIVITY), 100) # max 100%
                    _vehicles_data.loc[(i, j), p] = value_new

                    comp_param = compensation_parameter[parameter.index(p)]
                    comp_value = vehicles_data.loc[(i, j), comp_param]

                    if value_new + comp_value > 100:
                        _vehicles_data.loc[(i, j), comp_param] = 100 - value_new

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, _vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_plus.append(_closedloop)
                sa_materialuse_plus.append(_material_use)

                name = f'{p}_vehicle_{i}'
                sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

                ##

                print(f'   (SA:) calculating -{SENSITIVITY * 100}% for {p}, vehicle {i}...')

                _vehicles_data = vehicles_data.copy()

                for j in range(start_year, end_year + 1):
                    value = vehicles_data.loc[(i, j), p] 
                    _value = max(value * (1 - SENSITIVITY), 0)
                    _vehicles_data.loc[(i, j), p] = _value
                    
                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, _vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_minus.append(_closedloop)
                sa_materialuse_minus.append(_material_use)

                name = f'{p}_vehicle_{i}'
                sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

                sa_titles.append(f'{parameter_titels[p_idx]} of vehicle {i}')
            
            p_idx += 1

        
        # (SA.1.1.3) VEHICLES_DATA: MATERIAL CONTENTS
        # Method: for steel and aluminum sub-material categories, changes in one material share are compensated by opposite changes in the other material shares
        # (to keep and not exceed 100%).

        parameter = ['flatsteel_content', 'longsteel_content', 'wroughtaluminum_content', 'castaluminum_lowCu_content', 'castaluminum_highCu_content']
        compensation_parameter = [('longsteel_content',), ('flatsteel_content',), ('castaluminum_lowCu_content', 'castaluminum_highCu_content'), ('wroughtaluminum_content', 'castaluminum_highCu_content'), ('wroughtaluminum_content', 'castaluminum_lowCu_content')]
        parameter_titels = ['flat steel content', 'long steel content', 'wrought aluminum content', 'low-Cu cast aluminum content', 'high-Cu cast aluminum content']

        p_idx = 0

        for p in parameter:

            for i in range(1, n_vehicles + 1):

                print(f'   (SA:) calculating +{SENSITIVITY * 100}% for {p}, vehicle {i}...')

                _vehicles_data = vehicles_data.copy()

                for j in range(start_year, end_year + 1):
                    value_old = vehicles_data.loc[(i, j), p] 
                    value_new = min(value_old * (1 + SENSITIVITY), 100) # max 100%
                    _vehicles_data.loc[(i, j), p] = value_new
                    value_diff = value_new - value_old

                    comp_params = compensation_parameter[p_idx]
                    comp_values = [vehicles_data.loc[(i, j), cp] for cp in comp_params]
                    comp_sum = sum(comp_values)

                    if comp_sum > 0:
                        rest = 0

                        # proportional adjustment of compensation parameters
                        for cp, cv_old in zip(comp_params, comp_values):
                            share = cv_old / comp_sum
                            cv_new = cv_old - (value_diff * share) - rest
                            _value = max(0.0, cv_new)
                            _vehicles_data.loc[(i, j), cp] = _value
                            
                            rest += abs(cv_new - _value)

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, _vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_plus.append(_closedloop)
                sa_materialuse_plus.append(_material_use)

                name = f'{p}_vehicle_{i}'
                sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

                ##

                print(f'   (SA:) calculating -{SENSITIVITY * 100}% for {p}, vehicle {i}...')

                _vehicles_data = vehicles_data.copy()

                for j in range(start_year, end_year + 1):
                    value_old = vehicles_data.loc[(i, j), p] 
                    value_new = max(value_old * (1 - SENSITIVITY), 0)
                    _vehicles_data.loc[(i, j), p] = value_new
                    value_diff = value_new - value_old

                    comp_params = compensation_parameter[p_idx]
                    comp_values = [vehicles_data.loc[(i, j), cp] for cp in comp_params]
                    comp_sum = sum(comp_values)

                    if comp_sum > 0:
                        rest = 0

                        # proportional adjustment of compensation parameters
                        for cp, cv_old in zip(comp_params, comp_values):
                            share = cv_old / comp_sum
                            cv_new = cv_old - (value_diff * share) + rest
                            _value = min(100.0, cv_new)
                            _vehicles_data.loc[(i, j), cp] = _value
                            
                            rest += abs(cv_new - _value)
                    
                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, _vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_minus.append(_closedloop)
                sa_materialuse_minus.append(_material_use)

                name = f'{p}_vehicle_{i}'
                sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

                sa_titles.append(f'{parameter_titels[p_idx]} of vehicle {i}')
            
            p_idx += 1

          
    ### (SA.1.2) CAGR

    if sa_config[1][s]:

        print(f'   (SA:) calculating +{SENSITIVITY * 100}% for CAGR...')

        _cagr = cagr * (1 + SENSITIVITY)

        _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, _cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

        sa_closedloop_plus.append(_closedloop)
        sa_materialuse_plus.append(_material_use)

        name = f'cagr'
        sa_tmp_plus[name] = [_vehicles_data, _cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

        ##

        print(f'   (SA:) calculating -{SENSITIVITY * 100}% for CAGR...')

        _cagr = cagr * (1 - SENSITIVITY)

        _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, _cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

        sa_closedloop_minus.append(_closedloop)
        sa_materialuse_minus.append(_material_use)

        name = f'cagr'
        sa_tmp_minus[name] = [_vehicles_data, _cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

        sa_titles.append(f'CAGR')


    ### (SA.1.3) LOSS

    if sa_config[2][s]:

        parameter = ['exports', 'unknown_whereabouts']

        for p in parameter:

            print(f'   (SA:) calculating +{SENSITIVITY * 100}% for {p}...')

            _eol_loss = eol_loss.copy()

            for j in range(start_year, end_year + 1):
                value = eol_loss.loc[j, p] 
                _eol_loss.loc[j, p] = min(value * (1 + SENSITIVITY), 100)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, _eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_plus.append(_closedloop)
            sa_materialuse_plus.append(_material_use)

            name = f'{p}'
            sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, _eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

            ##

            print(f'   (SA:) calculating -{SENSITIVITY * 100}% for {p}...')

            _eol_loss = eol_loss.copy()

            for j in range(start_year, end_year + 1):
                value = eol_loss.loc[j, p] 
                _eol_loss.loc[j, p] = max(value * (1 - SENSITIVITY), 0)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, _eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_minus.append(_closedloop)
            sa_materialuse_minus.append(_material_use)

            name = f'{p}'
            sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, _eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

            sa_titles.append(f'{p.replace("_", " ")}')


    ### (SA.1.4) DISMANTLING CONTENT

    if sa_config[3][s]:

        parameter = ['flatsteel_content', 'longsteel_content', 'wroughtaluminum_content', 'castaluminum_lowCu_content', 'castaluminum_highCu_content']

        for p in parameter:
            for i in range(1, n_vehicles + 1):

                print(f'   (SA:) calculating +{SENSITIVITY * 100}% for dismantling {p}, vehicle {i}...')

                _eol_dismantling = eol_dismantling.copy()
            
                for j in range(start_year, end_year + 1):
                    value = eol_dismantling.loc[(i,j), p] 
                    _eol_dismantling.loc[(i,j), p] = min(value * (1 + SENSITIVITY), 100)

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, _eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_plus.append(_closedloop)
                sa_materialuse_plus.append(_material_use)

                name = f'dismantling_{p}_vehicle_{i}'
                sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, _eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

                ##

                print(f'   (SA:) calculating -{SENSITIVITY * 100}% for dismantling {p}, vehicle {i}...')

                _eol_dismantling = eol_dismantling.copy()
            
                for j in range(start_year, end_year + 1):
                    value = eol_dismantling.loc[(i,j), p] 
                    _eol_dismantling.loc[(i,j), p] = max(value * (1 - SENSITIVITY), 0)

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, _eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_minus.append(_closedloop)
                sa_materialuse_minus.append(_material_use)

                name = f'dismantling_{p}_vehicle_{i}'
                sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, _eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

                title = p.split('_')[0]
                sa_titles.append(f'dismantled {title} of vehicle {i}')


    ### (SA.1.5) DISMANTLING-RECYCLING EFFICIENCY

    ### (a) YIELD

    if sa_config[4][s]:

        parameter = ['flatsteel_yield', 'longsteel_yield', 'wroughtaluminum_yield', 'castaluminum_lowCu_yield', 'castaluminum_highCu_yield']

        for p in parameter:

            print(f'   (SA:) calculating +{SENSITIVITY * 100}% for dismantling recycling {p}...')

            _eol_dismantling_recycling = eol_dismantling_recycling.copy()

            for j in range(start_year, end_year + 1):
                value = eol_dismantling_recycling.loc[j, p] 
                _eol_dismantling_recycling.loc[j, p] = min(value * (1 + SENSITIVITY), 100)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, _eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_plus.append(_closedloop)
            sa_materialuse_plus.append(_material_use)

            name = f'dismantling_recycling_{p}'
            sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, _eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

            ##

            print(f'   (SA:) calculating -{SENSITIVITY * 100}% for dismantling recycling {p}...')

            _eol_dismantling_recycling = eol_dismantling_recycling.copy()

            for j in range(start_year, end_year + 1):
                value = eol_dismantling_recycling.loc[j, p] 
                _eol_dismantling_recycling.loc[j, p] = max(value * (1 - SENSITIVITY), 0)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, _eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_minus.append(_closedloop)
            sa_materialuse_minus.append(_material_use)

            name = f'dismantling_recycling_{p}'
            sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, _eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

            title = f'{p.replace("_", " ")}'
            sa_titles.append(f'dismantling recycling {title}')

    
    ### (b) CONTAMINATION

    # Method: Contamination parameters are varied by adding/subtracting a percentage (sensitivity factor) of the quality threshold.

    if sa_config[5][s]:

        parameter = ['flatsteel_contamination', 'longsteel_contamination', 'wroughtaluminum_contamination', 'castaluminum_lowCu_contamination', 'castaluminum_highCu_contamination']
        quality_parameter = [steel_production['flatsteel_threshold'], steel_production['longsteel_threshold'], aluminum_production['wroughtaluminum_threshold'], aluminum_production['castaluminum_lowCu_threshold'], aluminum_production['castaluminum_highCu_threshold']]
        
        n_thresholds_steel = steel_production.loc[start_year, 'n_thresholds']
        n_thresholds_aluminum = aluminum_production.loc[start_year, 'n_thresholds']
        p_n_thresholds = [n_thresholds_steel, n_thresholds_steel, n_thresholds_aluminum, n_thresholds_aluminum, n_thresholds_aluminum]

        p_idx = 0

        for p in parameter:
            for i in range(p_n_thresholds[p_idx]):

                print(f'   (SA:) calculating +{SENSITIVITY * 100}% for dismantling recycling {p} [{i+1}]...')

                _eol_dismantling_recycling = eol_dismantling_recycling.copy()

                for j in range(start_year, end_year + 1):
                    value = eol_dismantling_recycling.loc[j, p][i]
                    new_list = list(eol_dismantling_recycling.loc[j, p])

                    threshold_quality = quality_parameter[p_idx][j][i]
                    new_list[i] = value + threshold_quality * SENSITIVITY
                    _eol_dismantling_recycling.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, _eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_plus.append(_closedloop)
                sa_materialuse_plus.append(_material_use)

                name = f'dismantling_recycling_{p}_{i+1}'
                sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, _eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

                ##

                print(f'   (SA:) calculating -{SENSITIVITY * 100}% for dismantling recycling {p} [{i+1}]...')

                _eol_dismantling_recycling = eol_dismantling_recycling.copy()

                for j in range(start_year, end_year + 1):
                    value = eol_dismantling_recycling.loc[j, p][i]
                    new_list = list(eol_dismantling_recycling.loc[j, p])
                    
                    threshold_quality = quality_parameter[p_idx][j][i]
                    new_list[i] = max(0, value - threshold_quality * SENSITIVITY)
                    _eol_dismantling_recycling.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, _eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_minus.append(_closedloop)
                sa_materialuse_minus.append(_material_use)

                name = f'dismantling_recycling_{p}_{i+1}'
                sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, _eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]

                title = f'{p.replace("_", " ")} (c{i+1})'
                sa_titles.append(f'dismantling recycling {title}')

            p_idx += 1


    ### (SA.1.6) PST-RECYCLING EFFICIENCY

    ### (a) YIELD

    if sa_config[6][s]:

        parameter = ['steel_yield', 'mixedaluminum_yield', 'wroughtaluminum_yield', 'castaluminum_lowCu_yield', 'castaluminum_highCu_yield']

        for p in parameter:

            print(f'   (SA:) calculating +{SENSITIVITY * 100}% for PST recycling {p}...')

            _eol_pst = eol_pst.copy()

            for j in range(start_year, end_year + 1):
                value = eol_pst.loc[j, p] 
                _eol_pst.loc[j, p] = min(value * (1 + SENSITIVITY), 100)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, _eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_plus.append(_closedloop)
            sa_materialuse_plus.append(_material_use)

            name = f'pst_recycling_{p}'
            sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, _eol_pst, component_production, steel_production, aluminum_production]

            ##

            print(f'   (SA:) calculating -{SENSITIVITY * 100}% for PST recycling {p}...')

            _eol_pst = eol_pst.copy()

            for j in range(start_year, end_year + 1):
                value = eol_pst.loc[j, p] 
                _eol_pst.loc[j, p] = max(value * (1 - SENSITIVITY), 0)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, _eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_minus.append(_closedloop)
            sa_materialuse_minus.append(_material_use)

            name = f'pst_recycling_{p}'
            sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, _eol_pst, component_production, steel_production, aluminum_production]

            title = f'{p.replace("_", " ")}'
            sa_titles.append(f'PST recycling {title}')

    
    ### (b) CONTAMINATION

    if sa_config[7][s]:

        # Method: Contamination parameters are varied by adding/subtracting a percentage (sensitivity factor) of the quality threshold.
        # For mixed material fractions (steel, mixed aluminum), a weighted average of the (flat/long) steel and (wrought/low-Cu cast/high-Cu cast)
        # aluminum thresholds in material production is used, based on the vehicle contents in the respective year.

        n_thresholds_steel = steel_production.loc[start_year, 'n_thresholds']
        n_thresholds_aluminum = aluminum_production.loc[start_year, 'n_thresholds']
        p_n_thresholds = [n_thresholds_steel, n_thresholds_aluminum, n_thresholds_aluminum, n_thresholds_aluminum, n_thresholds_aluminum]

        _reg_full = calc_registrations(start_year, end_year, set_vehicles, cagr, init_year, registrations.copy()) if n_init_years < (end_year - start_year + 1) else registrations.copy()

        parameter = ['steel_contamination', 'mixedaluminum_contamination', 'wroughtaluminum_contamination', 'castaluminum_lowCu_contamination', 'castaluminum_highCu_contamination']
        quality_parameter = [
            {year: [
                steel_production.loc[year, 'flatsteel_threshold'][i]
                * (_reg_full.xs(year, level=1)['registrations'] * vehicles_data.xs(year, level=1)['flatsteel_content']).sum()
                / _reg_full.xs(year, level=1)['registrations'].sum() / 100
                + steel_production.loc[year, 'longsteel_threshold'][i]
                * (_reg_full.xs(year, level=1)['registrations'] * vehicles_data.xs(year, level=1)['longsteel_content']).sum()
                / _reg_full.xs(year, level=1)['registrations'].sum() / 100
                for i in range(n_thresholds_steel)
            ] for year in set_years},  # registration-weighted average quality thresholds for steel
            {year: [
                aluminum_production.loc[year, 'wroughtaluminum_threshold'][i]
                * (_reg_full.xs(year, level=1)['registrations'] * vehicles_data.xs(year, level=1)['wroughtaluminum_content']).sum()
                / _reg_full.xs(year, level=1)['registrations'].sum() / 100
                + aluminum_production.loc[year, 'castaluminum_lowCu_threshold'][i]
                * (_reg_full.xs(year, level=1)['registrations'] * vehicles_data.xs(year, level=1)['castaluminum_lowCu_content']).sum()
                / _reg_full.xs(year, level=1)['registrations'].sum() / 100
                + aluminum_production.loc[year, 'castaluminum_highCu_threshold'][i]
                * (_reg_full.xs(year, level=1)['registrations'] * vehicles_data.xs(year, level=1)['castaluminum_highCu_content']).sum()
                / _reg_full.xs(year, level=1)['registrations'].sum() / 100
                for i in range(n_thresholds_aluminum)
            ] for year in set_years},  # registration-weighted average quality thresholds for mixed aluminum
            aluminum_production['wroughtaluminum_threshold'],
            aluminum_production['castaluminum_lowCu_threshold'],
            aluminum_production['castaluminum_highCu_threshold']
        ]
        
        p_idx = 0

        for p in parameter:
            for i in range(p_n_thresholds[p_idx]):

                print(f'   (SA:) calculating +{SENSITIVITY * 100}% for PST recycling {p} [{i+1}]...')

                _eol_pst = eol_pst.copy()

                for j in range(start_year, end_year + 1):
                    value = eol_pst.loc[j, p][i]
                    new_list = list(eol_pst.loc[j, p])

                    threshold_quality = quality_parameter[p_idx][j][i]
                    new_list[i] = value + threshold_quality * SENSITIVITY
                    _eol_pst.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, _eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_plus.append(_closedloop)
                sa_materialuse_plus.append(_material_use)

                name = f'pst_recycling_{p}_{i+1}'
                sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, _eol_pst, component_production, steel_production, aluminum_production]

                ##

                print(f'   (SA:) calculating -{SENSITIVITY * 100}% for PST recycling {p} [{i+1}]...')

                _eol_pst = eol_pst.copy()

                for j in range(start_year, end_year + 1):
                    value = eol_pst.loc[j, p][i]
                    new_list = list(eol_pst.loc[j, p])

                    threshold_quality = quality_parameter[p_idx][j][i]
                    new_list[i] = max(0, value - threshold_quality * SENSITIVITY)
                    _eol_pst.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, _eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_minus.append(_closedloop)
                sa_materialuse_minus.append(_material_use)

                name = f'pst_recycling_{p}_{i+1}'
                sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, _eol_pst, component_production, steel_production, aluminum_production]

                title = f'{p.replace("_", " ")} (c{i+1})'
                sa_titles.append(f'PST recycling {title}')

            p_idx += 1


    ### (SA.1.7) STEEL PRODUCTION EFFICIENCY

    ### (a) PRODUCTION ROUTES

    if sa_config[8][s]:

        # Method: changes in one production route are compensated by opposite changes in the other two routes (to keep 100% production).
        # If both compensation routes have a share of more than 0% each, both of them are used for compensation. If both compensation
        # routes have a share of 0% each, the following compensation method is used:
        #   s1 is compensated by s2
        #   s2 is compensated by s1
        #   s3 is compensated by s2

        parameter = ['flatsteel_s1', 'flatsteel_s2', 'flatsteel_s3', 'longsteel_s1', 'longsteel_s2', 'longsteel_s3']
        compensation_parameter = [('flatsteel_s2', 'flatsteel_s3'), ('flatsteel_s1', 'flatsteel_s3'), ('flatsteel_s1', 'flatsteel_s2'), ('longsteel_s2', 'longsteel_s3'), ('longsteel_s1', 'longsteel_s3'), ('longsteel_s1', 'longsteel_s2')]
        compensation_fallback_parameter = ['flatsteel_s2', 'flatsteel_s1', 'flatsteel_s2', 'longsteel_s2', 'longsteel_s1', 'longsteel_s2']

        p_idx = 0
        
        for p in parameter:

            print(f'   (SA:) calculating +{SENSITIVITY * 100}% for production {p}...')

            _steel_production = steel_production.copy()

            for j in range(start_year, end_year + 1):
                value_old = steel_production.loc[j, p] 
                value_new = min(value_old * (1 + SENSITIVITY), 100)
                _steel_production.loc[j, p] = value_new
                value_diff = value_new - value_old

                comp_params = compensation_parameter[p_idx]
                comp_values = [steel_production.loc[j, cp] for cp in comp_params]
                comp_sum = sum(comp_values)

                if comp_sum > 0:
                    rest = 0

                    # proportional adjustment of compensation parameters
                    for cp, cv_old in zip(comp_params, comp_values):
                        share = cv_old / comp_sum
                        cv_new = cv_old - (value_diff * share) - rest
                        _value = max(0.0, cv_new)
                        _steel_production.loc[j, cp] = _value
                        
                        rest += abs(cv_new - _value)

                else:
                    # deterministic adjustment
                    fallback_param = compensation_fallback_parameter[p_idx]                    
                    _steel_production.loc[j, fallback_param] = max(0.0, steel_production.loc[j, fallback_param] - value_diff)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_plus.append(_closedloop)
            sa_materialuse_plus.append(_material_use)

            name = f'production_{p}'
            sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production]

            ##

            print(f'   (SA:) calculating -{SENSITIVITY * 100}% for production {p}...')

            _steel_production = steel_production.copy()

            for j in range(start_year, end_year + 1):
                value_old = steel_production.loc[j, p] 
                value_new = max(value_old * (1 - SENSITIVITY), 0)
                _steel_production.loc[j, p] = value_new
                value_diff = value_new - value_old

                comp_params = compensation_parameter[p_idx]
                comp_values = [steel_production.loc[j, cp] for cp in comp_params]
                comp_sum = sum(comp_values)

                if comp_sum > 0:
                    rest = 0

                    # proportional adjustment of compensation parameters
                    for cp, cv_old in zip(comp_params, comp_values):
                        share = cv_old / comp_sum
                        cv_new = cv_old - (value_diff * share) + rest
                        _value = min(100.0, cv_new)
                        _steel_production.loc[j, cp] = _value
                        
                        rest += abs(cv_new - _value)

                else:
                    # deterministic adjustment
                    fallback_param = compensation_fallback_parameter[p_idx]                    
                    _steel_production.loc[j, fallback_param] = min(100.0, steel_production.loc[j, fallback_param] - value_diff)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_minus.append(_closedloop)
            sa_materialuse_minus.append(_material_use)

            name = f'production_{p}'
            sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production]

            title = f'{p.replace("_", " ")}'
            sa_titles.append(f'production {title}')

            p_idx += 1

    
    ### (b) PRODUCTION ROUTE CONFIGURATION

    if sa_config[9][s]:

        # all parameters: parameter = ['s1_max_scrap', 's1_min_scrap', 's1_efficiency', 's1_scrap_recycling_rate', 's2_max_scrap', 's2_min_scrap', 's2_efficiency', 's2_scrap_recycling_rate', 's3_max_scrap', 's3_min_scrap', 's3_efficiency', 's3_scrap_recycling_rate']
        parameter = ['s1_efficiency', 's1_scrap_recycling_rate', 's2_efficiency', 's2_scrap_recycling_rate', 's3_efficiency', 's3_scrap_recycling_rate']    # without max_scrap and min_scrap parameters

        for p in parameter:

            print(f'   (SA:) calculating +{SENSITIVITY * 100}% for production {p}...')

            _steel_production = steel_production.copy()

            for j in range(start_year, end_year + 1):
                value = steel_production.loc[j, p] 
                _steel_production.loc[j, p] = min(value * (1 + SENSITIVITY), 100)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_plus.append(_closedloop)
            sa_materialuse_plus.append(_material_use)

            name = f'production_{p}'
            sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production]

            ##

            print(f'   (SA:) calculating -{SENSITIVITY * 100}% for production {p}...')

            _steel_production = steel_production.copy()

            for j in range(start_year, end_year + 1):
                value = steel_production.loc[j, p] 
                _steel_production.loc[j, p] = max(value * (1 - SENSITIVITY), 0)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_minus.append(_closedloop)
            sa_materialuse_minus.append(_material_use)

            name = f'production_{p}'
            sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production]
            
            title = f'{p.replace("_", " ")}'
            sa_titles.append(f'steel production {title}')


    ### (c) QUALITY THRESHOLDS

    if sa_config[10][s]:

        parameter = ['flatsteel_threshold', 'longsteel_threshold']
        n_thresholds = steel_production.loc[start_year, 'n_thresholds']

        for p in parameter:
            for i in range(n_thresholds):

                print(f'   (SA:) calculating +{SENSITIVITY * 100}% for production {p} [{i+1}]...')

                _steel_production = steel_production.copy()

                for j in range(start_year, end_year + 1):
                    value = steel_production.loc[j, p][i]
                    new_list = list(steel_production.loc[j, p])
                    new_list[i] = value * (1 + SENSITIVITY)
                    _steel_production.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_plus.append(_closedloop)
                sa_materialuse_plus.append(_material_use)

                name = f'production_{p}_{i+1}'
                sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production]

                ##

                print(f'   (SA:) calculating -{SENSITIVITY * 100}% for production {p} [{i+1}]...')

                _steel_production = steel_production.copy()

                for j in range(start_year, end_year + 1):
                    value = steel_production.loc[j, p][i]
                    new_list = list(steel_production.loc[j, p])
                    new_list[i] = max(value * (1 - SENSITIVITY), 0)
                    _steel_production.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_minus.append(_closedloop)
                sa_materialuse_minus.append(_material_use)

                name = f'production_{p}_{i+1}'
                sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production]
        
                title = f'{p.replace("_", " ")} (c{i+1})'
                sa_titles.append(f'production {title}')


    ### (d) VIRGIN MATERIAL QUALITY

    if sa_config[11][s]:

        parameter = ['virgin_steel_quality']
        n_thresholds = steel_production.loc[start_year, 'n_thresholds']

        for p in parameter:
            for i in range(n_thresholds):

                print(f'   (SA:) calculating +{SENSITIVITY * 100}% for production {p} [{i+1}]...')

                _steel_production = steel_production.copy()

                for j in range(start_year, end_year + 1):
                    value = steel_production.loc[j, p][i]
                    new_list = list(steel_production.loc[j, p])
                    new_list[i] = value * (1 + SENSITIVITY)
                    _steel_production.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_plus.append(_closedloop)
                sa_materialuse_plus.append(_material_use)

                name = f'production_{p}_{i+1}'
                sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production]

                ##

                print(f'   (SA:) calculating -{SENSITIVITY * 100}% for production {p} [{i+1}]...')

                _steel_production = steel_production.copy()

                for j in range(start_year, end_year + 1):
                    value = steel_production.loc[j, p][i]
                    new_list = list(steel_production.loc[j, p])
                    new_list[i] = max(value * (1 - SENSITIVITY), 0)
                    _steel_production.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_minus.append(_closedloop)
                sa_materialuse_minus.append(_material_use)

                name = f'production_{p}_{i+1}'
                sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, _steel_production, aluminum_production]
        
                title = f'{p.replace("_", " ")} (c{i+1})'
                sa_titles.append(f'production {title}')


    ### (SA.1.8) ALUMINUM PRODUCTION EFFICIENCY

    ### (a) MIN/MAX SCRAP, EFFICIENCY, AND SCRAP_RECYCLING_RATE

    if sa_config[12][s]:

        # with all parameters: parameter = ['wroughtaluminum_max_scrap', 'wroughtaluminum_min_scrap', 'wroughtaluminum_efficiency', 'wroughtaluminum_scrap_recycling_rate', 'castaluminum_lowCu_max_scrap', 'castaluminum_lowCu_min_scrap', 'castaluminum_lowCu_efficiency', 'castaluminum_lowCu_scrap_recycling_rate', 'castaluminum_highCu_max_scrap', 'castaluminum_highCu_min_scrap', 'castaluminum_highCu_efficiency', 'castaluminum_highCu_scrap_recycling_rate']
        parameter = ['wroughtaluminum_efficiency', 'wroughtaluminum_scrap_recycling_rate', 'castaluminum_lowCu_efficiency', 'castaluminum_lowCu_scrap_recycling_rate', 'castaluminum_highCu_efficiency', 'castaluminum_highCu_scrap_recycling_rate']    # without max_scrap and min_scrap parameters
        
        for p in parameter:

            print(f'   (SA:) calculating +{SENSITIVITY * 100}% for production {p}...')

            _aluminum_production = aluminum_production.copy()

            for j in range(start_year, end_year + 1):
                value = aluminum_production.loc[j, p] 
                _aluminum_production.loc[j, p] = min(value * (1 + SENSITIVITY), 100)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_plus.append(_closedloop)
            sa_materialuse_plus.append(_material_use)

            name = f'production_{p}'
            sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production]

            ##

            print(f'   (SA:) calculating -{SENSITIVITY * 100}% for production {p}...')

            _aluminum_production = aluminum_production.copy()

            for j in range(start_year, end_year + 1):
                value = aluminum_production.loc[j, p] 
                _aluminum_production.loc[j, p] = max(value * (1 - SENSITIVITY), 0)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_minus.append(_closedloop)
            sa_materialuse_minus.append(_material_use)

            name = f'production_{p}'
            sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production]
            
            title = f'{p.replace("_", " ")}'
            sa_titles.append(f'production {title}')

    
    ### (b) QUALITY THRESHOLDS

    if sa_config[13][s]:

        parameter = ['wroughtaluminum_threshold', 'castaluminum_lowCu_threshold', 'castaluminum_highCu_threshold']
        n_thresholds = aluminum_production.loc[start_year, 'n_thresholds']

        for p in parameter:
            for i in range(n_thresholds):

                print(f'   (SA:) calculating +{SENSITIVITY * 100}% for production {p} [{i+1}]...')

                _aluminum_production = aluminum_production.copy()

                for j in range(start_year, end_year + 1):
                    value = aluminum_production.loc[j, p][i]
                    new_list = list(aluminum_production.loc[j, p])
                    new_list[i] = value * (1 + SENSITIVITY)
                    _aluminum_production.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_plus.append(_closedloop)
                sa_materialuse_plus.append(_material_use)

                name = f'production_{p}_{i+1}'
                sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production]

                ##

                print(f'   (SA:) calculating -{SENSITIVITY * 100}% for production {p} [{i+1}]...')

                _aluminum_production = aluminum_production.copy()

                for j in range(start_year, end_year + 1):
                    value = aluminum_production.loc[j, p][i]
                    new_list = list(aluminum_production.loc[j, p])
                    new_list[i] = max(value * (1 - SENSITIVITY), 0)
                    _aluminum_production.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_minus.append(_closedloop)
                sa_materialuse_minus.append(_material_use)

                name = f'production_{p}_{i+1}'
                sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production]
        
                title = f'{p.replace("_", " ")} (c{i+1})'
                sa_titles.append(f'production {title}')


    ### (c) VIRGIN MATERIAL QUALITY

    if sa_config[14][s]:

        parameter = ['virgin_wroughtaluminum_quality', 'virgin_castaluminum_lowCu_quality', 'virgin_castaluminum_highCu_quality']
        n_thresholds = aluminum_production.loc[start_year, 'n_thresholds']

        for p in parameter:
            for i in range(n_thresholds):

                print(f'   (SA:) calculating +{SENSITIVITY * 100}% for production {p} [{i+1}]...')

                _aluminum_production = aluminum_production.copy()

                for j in range(start_year, end_year + 1):
                    value = aluminum_production.loc[j, p][i]
                    new_list = list(aluminum_production.loc[j, p])
                    new_list[i] = value * (1 + SENSITIVITY)
                    _aluminum_production.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_plus.append(_closedloop)
                sa_materialuse_plus.append(_material_use)

                name = f'production_{p}_{i+1}'
                sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production]

                ##

                print(f'   (SA:) calculating -{SENSITIVITY * 100}% for production {p} [{i+1}]...')

                _aluminum_production = aluminum_production.copy()

                for j in range(start_year, end_year + 1):
                    value = aluminum_production.loc[j, p][i]
                    new_list = list(aluminum_production.loc[j, p])
                    new_list[i] = max(value * (1 - SENSITIVITY), 0)
                    _aluminum_production.at[j, p] = new_list

                _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

                sa_closedloop_minus.append(_closedloop)
                sa_materialuse_minus.append(_material_use)

                name = f'production_{p}_{i+1}'
                sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, _aluminum_production]
        
                title = f'{p.replace("_", " ")} (c{i+1})'
                sa_titles.append(f'production {title}')


    ### (SA.1.9) COMPONENT PRODUCTION EFFICIENCY

    if sa_config[15][s]:

        parameter = ['flatsteel_efficiency', 'longsteel_efficiency', 'wroughtaluminum_efficiency', 'castaluminum_lowCu_efficiency', 'castaluminum_highCu_efficiency', 'flatsteel_scrap_recycling_rate', 'longsteel_scrap_recycling_rate', 'wroughtaluminum_scrap_recycling_rate', 'castaluminum_lowCu_scrap_recycling_rate', 'castaluminum_highCu_scrap_recycling_rate']

        for p in parameter:

            print(f'   (SA:) calculating +{SENSITIVITY * 100}% for component production {p}...')

            _component_production = component_production.copy()

            for j in range(start_year, end_year + 1):
                value_old = component_production.loc[j, p] 
                value_new = min(value_old * (1 + SENSITIVITY), 100)
                _component_production.loc[j, p] = value_new

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, _component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_plus.append(_closedloop)
            sa_materialuse_plus.append(_material_use)

            name = f'component_production_{p}'
            sa_tmp_plus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, _component_production, steel_production, aluminum_production]

            ##

            print(f'   (SA:) calculating -{SENSITIVITY * 100}% for component production {p}...')

            _component_production = component_production.copy()

            for j in range(start_year, end_year + 1):
                value = component_production.loc[j, p] 
                _component_production.loc[j, p] = max(value * (1 - SENSITIVITY), 0)

            _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective = calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, _component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE)

            sa_closedloop_minus.append(_closedloop)
            sa_materialuse_minus.append(_material_use)

            name = f'component_production_{p}'
            sa_tmp_minus[name] = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, _component_production, steel_production, aluminum_production]

            title = f'{p.replace("_", " ")}'
            sa_titles.append(f'component production {title}')


    return sa_closedloop_plus, sa_closedloop_minus, sa_materialuse_plus, sa_materialuse_minus, sa_titles, sa_tmp_plus, sa_tmp_minus, sa_tmp_elements



def interpret_sa(start_year, set_years, closedloop, material_use, sa_closedloop_plus, sa_closedloop_minus, sa_materialuse_plus, sa_materialuse_minus, sa_tmp_plus, sa_tmp_minus):

    n_sa_iterations = len(sa_closedloop_plus)
    sa_tmp_plus_values = list(sa_tmp_plus.values())
    sa_tmp_minus_values = list(sa_tmp_minus.values())

    # check for infeasible sa runs:

    infeasible_sa_runs = []

    for name, data_list in sa_tmp_plus.items():
        obj = data_list[11]

        if obj < 0:
            infeasible_sa_runs.append(f'{name}_plus')

    for name, data_list in sa_tmp_minus.items():
        obj = data_list[11]

        if obj < 0:
            infeasible_sa_runs.append(f'{name}_minus')

    _infeasible_plus  = [data[11] < 0 for data in sa_tmp_plus_values]
    _infeasible_minus = [data[11] < 0 for data in sa_tmp_minus_values]

    # closedloop:

    _sa_closedloop_min = closedloop.copy()
    _sa_closedloop_max = closedloop.copy()

    parameter = closedloop.columns.tolist()

    for p in parameter:
        _max = [closedloop.loc[j, p] for j in set_years]
        _min = [closedloop.loc[j, p] for j in set_years]

        for j in set_years:
            _idx = j - start_year

            for sa_iterat in range(n_sa_iterations):
                plus_val  = closedloop.loc[j, p] if _infeasible_plus[sa_iterat]  else sa_closedloop_plus[sa_iterat].loc[j, p]
                minus_val = closedloop.loc[j, p] if _infeasible_minus[sa_iterat] else sa_closedloop_minus[sa_iterat].loc[j, p]
                _max[_idx] = max(_max[_idx], plus_val, minus_val)
                _min[_idx] = min(_min[_idx], plus_val, minus_val)

        _sa_closedloop_max[p] = _max
        _sa_closedloop_min[p] = _min

    sa_closedloop_min = _sa_closedloop_min
    sa_closedloop_max = _sa_closedloop_max
    
    # material_use:

    _sa_material_use_min = material_use.copy()
    _sa_material_use_max = material_use.copy()

    parameter = material_use.columns.tolist() 

    for p in parameter:
        _max = [material_use.loc[j, p] for j in set_years]
        _min = [material_use.loc[j, p] for j in set_years]

        for j in set_years:
            _idx = j - start_year

            for sa_iterat in range(n_sa_iterations):
                plus_val  = material_use.loc[j, p] if _infeasible_plus[sa_iterat]  else sa_materialuse_plus[sa_iterat].loc[j, p]
                minus_val = material_use.loc[j, p] if _infeasible_minus[sa_iterat] else sa_materialuse_minus[sa_iterat].loc[j, p]
                _max[_idx] = max(_max[_idx], plus_val, minus_val)
                _min[_idx] = min(_min[_idx], plus_val, minus_val)

        _sa_material_use_max[p] = _max
        _sa_material_use_min[p] = _min

    sa_material_use_min = _sa_material_use_min
    sa_material_use_max = _sa_material_use_max


    return sa_closedloop_max, sa_closedloop_min, sa_material_use_max, sa_material_use_min, infeasible_sa_runs