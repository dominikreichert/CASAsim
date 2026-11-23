####
#
# CASAsim
# Calculate model parameters: (1) vehicle contents, (2) future vehicle registrations,
#   (3) vehicle fleet, (4) ELVs, (5) recycling outputs, (6) material supply and demand,
#   (7) material use, and (8) closed-loop rates
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
import math

from optimizer import run_optimization



###
###  (1) CALCULATE VEHICLE CONTENTS
###

# Model vehicle contents in kg based on the vehicle content data in percentage in vehicles_data

def calc_vehicles(start_year, end_year, n_vehicles, vehicles_data):

    _vehicles_data = vehicles_data.copy()

    for i in range(1, n_vehicles + 1):
        for j in range(start_year, end_year + 1):

            _vehicles_data.loc[(i, j), 'steel_mass'] = _vehicles_data.loc[(i, j), 'total_mass'] * _vehicles_data.loc[(i, j), 'steel_content'] / 100

            _vehicles_data.loc[(i, j), 'flatsteel_mass'] = _vehicles_data.loc[(i, j), 'steel_mass'] * _vehicles_data.loc[(i, j), 'flatsteel_content'] / 100

            _vehicles_data.loc[(i, j), 'longsteel_mass'] = _vehicles_data.loc[(i, j), 'steel_mass'] * _vehicles_data.loc[(i, j), 'longsteel_content'] / 100

            _vehicles_data.loc[(i, j), 'aluminum_mass'] = _vehicles_data.loc[(i, j), 'total_mass'] * _vehicles_data.loc[(i, j), 'aluminum_content'] / 100

            _vehicles_data.loc[(i, j), 'wroughtaluminum_mass'] = _vehicles_data.loc[(i, j), 'aluminum_mass'] * _vehicles_data.loc[(i, j), 'wroughtaluminum_content'] / 100

            _vehicles_data.loc[(i, j), 'castaluminum_lowCu_mass'] = _vehicles_data.loc[(i, j), 'aluminum_mass'] * _vehicles_data.loc[(i, j), 'castaluminum_lowCu_content'] / 100

            _vehicles_data.loc[(i, j), 'castaluminum_highCu_mass'] = _vehicles_data.loc[(i, j), 'aluminum_mass'] * _vehicles_data.loc[(i, j), 'castaluminum_highCu_content'] / 100

    return _vehicles_data



###
###  (2) CALCULATE FUTURE VEHICLE REGISTRATIONS
###

# Model future vehicle registrations from the last year with defined registration data in the input file based on the defined CAGR, and update the registrations matrix

# registrations[id, year] = {registrations}

def calc_registrations(start_year, end_year, set_vehicles, cagr, init_year, registrations):

    for veh in set_vehicles:
        
        init_reg = registrations.loc[(veh, init_year), 'registrations']

        # CAGR = (end value / start value)^(1 / number of years) - 1
        # => end value = start value * (1 + CAGR)^(number of years)

        for year in range(init_year + 1, end_year + 1):
            # new_row = pd.DataFrame(
            #     int(init_reg * (1 + cagr / 100) ** (year - init_year)),
            #     columns = registrations.columns, index = [(veh, year)])
            new_row = pd.DataFrame(
                {'registrations': [int(init_reg * (1 + cagr / 100) ** (year - init_year))]},
                index = pd.MultiIndex.from_tuples([(veh, year)], names=registrations.index.names)
            )
            registrations = pd.concat([registrations, new_row])

    return registrations.sort_index()



###
###  (3) CALCULATE VEHILCE FLEET
###

# Create detailed and cumulated vehicle fleet matrix per vehicle model (id), and calculate vehicle stocks (vehicle fleet). The matrices will be added by data on vehicles exiting the vehicle fleet (elvs_exit), thereof, veheicles being exported (elvs_export), vehicles with unknown whereabouts (elvs_unknown), vehicles entering recycling (elvs_recycling), and the resulting vehicle stock (stock) for each year of registration (year_reg) and each current year (year_now)

# fleet_detail[id, year_reg, year_now] = {stock, elvs_exit, elvs_export, elvs_unknown, elvs_recycling}
# fleet[id, year] = {stock, elvs_exit, elvs_export, elvs_unknown, elvs_recycling}

def calc_fleet(start_year, end_year, set_years, set_vehicles, registrations, SHAPE, SCALE):


    # DETAILED VEHICLE FLEET

    fleet_detail = pd.DataFrame({
        'id': [i for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'year_reg': [j_reg for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'year_now': [j_now for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'stock': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'elvs_exit': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'elvs_export': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'elvs_unknown': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years],
        'elvs_recycling': [0 for i in set_vehicles for j_reg in set_years for j_now in set_years]})
    fleet_detail.set_index(['id', 'year_reg', 'year_now'], inplace=True)

    for veh in set_vehicles:
        for year_reg in set_years:

            veh_reg = registrations.loc[(veh, year_reg), 'registrations']

            exit_sum = 0

            for year_now in range(year_reg, end_year + 1):

                # Calculate number of vehicles exiting the fleet according to Weibull distribution including Weibull parameters shape and scale defined in lines 39-40 above
                elvs_exit = math.floor(veh_reg * weibull_min.pdf(year_now - year_reg, SHAPE, scale=SCALE))

                exit_sum += elvs_exit

                # No negative stock permitted: check if more vehicles exit the fleet than were originally registered
                if exit_sum > veh_reg:
                    if year_now == year_reg:
                        elvs_exit = veh_reg

                    elif year_now > year_reg:
                        elvs_exit = min(fleet_detail.loc[(veh, year_reg, year_now-1), 'stock'], elvs_exit)

                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] = int(elvs_exit)

                # Calculate vehicle stock
                if year_now == year_reg:
                    fleet_detail.loc[(veh, year_reg, year_now), 'stock'] = int(veh_reg - elvs_exit)

                else:
                    fleet_detail.loc[(veh, year_reg, year_now), 'stock'] = int(
                        fleet_detail.loc[(veh, year_reg, year_now-1), 'stock'] - elvs_exit)


    # CUMULATED VEHICLE FLEET

    fleet = pd.DataFrame({
        'id': [i for i in set_vehicles for j in set_years],
        'year': [j for i in set_vehicles for j in set_years],
        'stock': [0 for i in set_vehicles for j in set_years],
        'elvs_exit': [0 for i in set_vehicles for j in set_years],
        'elvs_export': [0 for i in set_vehicles for j in set_years],
        'elvs_unknown': [0 for i in set_vehicles for j in set_years],
        'elvs_recycling': [0 for i in set_vehicles for j in set_years]})
    fleet.set_index(['id', 'year'], inplace=True)

    for veh in set_vehicles:
        for year_now in set_years:
            stock_j = 0

            for year_reg in range(start_year, year_now + 1):
                stock_j += fleet_detail.loc[(veh, year_reg, year_now), 'stock']

            fleet.loc[(veh, year_now), 'stock'] = int(stock_j)

    return fleet_detail, fleet



###
###  (4) CALCULATE END-OF-LIFE (ELVS)
###

def calc_eol(start_year, set_years, set_vehicles, fleet_detail, fleet, eol_loss):

    # (4.1) FLEET EXITS

    # Calculate vehicles exiting the fleet (elvs_exit) in the detailed vehicle fleet matrix fleet_detail per vehicle model (id) for each current year (year_now) based on the change in stock, and update the cumulated vehicle fleet matrix fleet

    # adding fleet_detail[id, year_reg, year_now] = {elvs_exit}
    # adding fleet[id, year] = {elvs_exit}

    for veh in set_vehicles:
        for year_now in set_years:

            # First year:
            fleet_detail.loc[(veh, year_now, year_now), 'elvs_exit'] = 0

            # From second year on:
            _exits = 0

            for year_reg in range(start_year, year_now):
                exits = fleet_detail.loc[(veh, year_reg, year_now-1), 'stock'] - fleet_detail.loc[(veh, year_reg, year_now), 'stock']
                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] = int(exits)
                _exits += exits
                
            fleet.loc[(veh, year_now), 'elvs_exit'] = int(_exits)


    # (4.2) EXPORTS, UNKNOWN WHEREABOUTS

    # Calculate vehicles being exported (elvs_export) and vehicles with unknown whereabouts (elvs_unknown) in the detailed vehicle fleet matrix fleet_detail per vehicle model (id) for each current year (year_now) based on the vehicles exiting the fleet (elvs_exit), and update the cumulated vehicle fleet matrix fleet

    # adding fleet_detail[id, year_reg, year_now] = {elvs_export, elvs_unknown}
    # adding fleet[id, year] = {elvs_export, elvs_unknown}

    for veh in set_vehicles:
        for year_now in set_years:

            exports = eol_loss.loc[year_now, 'exports']
            unknown_whereabouts = eol_loss.loc[year_now, 'unknown_whereabouts']

            _exp = 0
            _unk = 0

            for year_reg in range(start_year, year_now):
                exp = fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] * exports / 100
                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_export'] = int(exp)
                _exp += exp

                unk = fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] * unknown_whereabouts / 100
                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_unknown'] = int(unk)
                _unk += unk
                
            fleet.loc[(veh, year_now), 'elvs_export'] = int(_exp)
            fleet.loc[(veh, year_now), 'elvs_unknown'] = int(_unk)


    # (4.3) ELVS / VEHICLES ENTERING RECYCLING

    # Calculate vehicles entering recycling (elvs_recycling) in the detailed vehicle fleet matrix fleet_detail per vehicle model (id) for each current year (year_now) based on the vehicles exiting the fleet (elvs_exit) minus vehicles being exported (elvs_export) and vehicles with unknown whereabouts (elvs_unknown), and update the cumulated vehicle fleet matrix fleet

    # adding fleet_detail[id, year_reg, year_now] = {elvs_recycling}
    # adding fleet[id, year] = {elvs_recycling}

    for veh in set_vehicles:
        for year_now in set_years:

            rec = 0

            for year_reg in range(start_year, year_now):
                _rec = fleet_detail.loc[(veh, year_reg, year_now), 'elvs_exit'] - fleet_detail.loc[(veh, year_reg, year_now), 'elvs_export'] - fleet_detail.loc[(veh, year_reg, year_now), 'elvs_unknown']
                fleet_detail.loc[(veh, year_reg, year_now), 'elvs_recycling'] = int(_rec)
                rec += _rec
                
            fleet.loc[(veh, year_now), 'elvs_recycling'] = int(rec)

    
    return fleet_detail, fleet



###
###  (5) CALCULATE RECYCLING OUTPUTS
###

# Model recycling outputs or recyclate supplies from ELVs based on the vehicles entering recycling (elvs_recycling) in the detailed vehicle fleet matrix fleet_detail per vehicle model (id) for each current year (year_now), the vehicle model data in vehicles_data, the dismantling rates in dismantling, and the recycling efficiencies in recycling

# eol_veh[id, year] = {
#   INPUT:         input_flatsteel, input_longsteel, input_wroughtaluminum,
#                  input_castaluminum_lowCu, input_castaluminum_highCu, input_elvs
#   DISMANTLING:   dismantling_flatsteel, dismantling_longsteel,
#                  dismantling_wroughtaluminum, dismantling_castaluminum_lowCu,
#                  dismantling_castaluminum_highCu,
#                  bodies_flatsteel, bodies_longsteel, bodies_wroughtaluminum,
#                  bodies_castaluminum_lowCu, bodies_castaluminum_highCu, bodies_steel
#   OUTPUT D.REC.: output_dismantling_recycling_flatsteel,
#                  output_dismantling_recycling_longsteel,
#                  output_dismantling_recycling_wroughtaluminum,
#                  output_dismantling_recycling_castaluminum_lowCu,
#                  output_dismantling_recycling_castaluminum_highCu
#   OUTPUT PST:    output_pst_steel, output_pst_mixedaluminum,
#                  output_pst_wroughtaluminum,
#                  output_pst_castaluminum_lowCu, output_pst_castaluminum_highCu
# }

# eol[year] = {
#   INPUT:         input_flatsteel, input_longsteel, input_wroughtaluminum,
#                  input_castaluminum_lowCu, input_castaluminum_highCu,
#                  input_steel, input_aluminum, input_elvs
#   DISMANTLING:   dismantling_flatsteel, dismantling_longsteel,
#                  dismantling_wroughtaluminum, dismantling_castaluminum_lowCu,
#                  dismantling_castaluminum_highCu,
#                  dismantling_steel, dismantling_aluminum,
#                  bodies_flatsteel, bodies_longsteel, bodies_wroughtaluminum,
#                  bodies_castaluminum_lowCu, bodies_castaluminum_highCu,
#                  bodies_steel, bodies_aluminum
#   OUTPUT D.REC.: output_dismantling_recycling_flatsteel,
#                  output_dismantling_recycling_longsteel,
#                  output_dismantling_recycling_wroughtaluminum,
#                  output_dismantling_recycling_castaluminum_lowCu,
#                  output_dismantling_recycling_castaluminum_highCu,
#                  output_dismantling_recycling_steel,
#                  output_dismantling_recycling_aluminum,
#   OUTPUT PST:    output_pst_steel, output_pst_mixedaluminum,
#                  output_pst_wroughtaluminum,
#                  output_pst_castaluminum_lowCu, output_pst_castaluminum_highCu,
#                  output_pst_aluminum
# }

def calc_recycling(start_year, set_years, set_vehicles, vehicles_data, fleet_detail, eol_dismantling, eol_dismantling_recycling, eol_pst):

    eol_veh = pd.DataFrame({
        'id': [i for i in set_vehicles for j in set_years],
        'year': [j for i in set_vehicles for j in set_years]
    })
    eol_veh.set_index(['id', 'year'], inplace=True)

    eol = pd.DataFrame({
        'year': [j for j in set_years],
    })
    eol.set_index('year', inplace=True)


    for year_now in set_years:

        for veh in set_vehicles:

            parameter = ['flatsteel', 'longsteel', 'wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']

            for p in parameter:

                # RECYCLING INPUTS
    
                # Calculate material-specific recycling inputs and number of ELVs entering recycling (input_elvs) per vehicle model (id) for each current year (year_now) based on the vehicles entering recycling (elvs_recycling) in the detailed vehicle fleet matrix fleet_detail and the vehicle model data in vehicles_data

                mass = 0
                n_veh = 0

                for year_reg in range(start_year, year_now + 1):

                    _n_veh = fleet_detail.loc[(veh, year_reg, year_now), 'elvs_recycling']
                    _mass = vehicles_data.loc[(veh, year_reg), f'{p}_mass']

                    mass += _n_veh * _mass
                    n_veh += _n_veh

                eol_veh.loc[(veh, year_now), f'input_{p}'] = mass

                if p == parameter[0]:
                    eol_veh.loc[(veh, year_now), 'input_elvs'] = n_veh


                # DISMANTLING OUTPUTS
        
                # Calculate material-specific dismantling outputs per vehicle model (id) for each current year (year_now) based on the number of ELVs entering recycling (input_elvs) in eol and the dismantling rates in dismantling

                dismantling_content_recycling = eol_dismantling.loc[(veh, year_now), f'{p}_content'] / 100
           
                dismantling_recycling_mass = mass * dismantling_content_recycling

                eol_veh.loc[(veh, year_now), f'dismantling_{p}'] = dismantling_recycling_mass
           
                eol_veh.loc[(veh, year_now), f'bodies_{p}'] = mass * (1 - dismantling_content_recycling)

            # Total steel in bodies:

            eol_veh.loc[(veh, year_now), 'bodies_steel'] = (
                eol_veh.loc[(veh, year_now), 'bodies_flatsteel'] + 
                eol_veh.loc[(veh, year_now), 'bodies_longsteel']
            )


        # TOTAL RECYCLING INPUTS AND DISMANTLING OUTPUTS PER YEAR

        eol.loc[year_now, 'input_elvs'] = eol_veh.loc[(slice(None), year_now), 'input_elvs'].sum()

        category = ['input', 'dismantling', 'bodies']

        for c in category:
            
            for p in parameter:

                eol.loc[year_now, f'{c}_{p}'] = eol_veh.loc[(slice(None), year_now), f'{c}_{p}'].sum()

            # Total steel and aluminum:

            eol.loc[year_now, f'{c}_steel'] = (
                eol.loc[year_now, f'{c}_flatsteel'] + 
                eol.loc[year_now, f'{c}_longsteel']
            )
            eol.loc[year_now, f'{c}_aluminum'] = (
                eol.loc[year_now, f'{c}_wroughtaluminum'] + 
                eol.loc[year_now, f'{c}_castaluminum_lowCu'] + 
                eol.loc[year_now, f'{c}_castaluminum_highCu']
            )


        # RECYCLING OUTPUTS FROM RECYCLING OF DISMANTLED COMPONENTS
        # AND PST RECYCLING
        
        # Calculate material-specific recycling outputs and the total recycling output per vehicle model (id) for each current year (year_now) for the dismantling content and bodies entering recycling based on the recycling yields


        # RECYCLING OF DISMANTLED COMPONENTS

        parameter = ['flatsteel', 'longsteel', 'wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']

        for p in parameter:

            output = 0

            for veh in set_vehicles:

                _mass = eol_veh.loc[(veh, year_now), f'dismantling_{p}']
                _yield = eol_dismantling_recycling.loc[year_now, f'{p}_yield'] / 100

                _output = _mass * _yield
                
                eol_veh.loc[(veh, year_now), f'output_dismantling_recycling_{p}'] = _output
                
                output += _output

            eol.loc[year_now, f'output_dismantling_recycling_{p}'] = output

        # Total steel and aluminum:

        eol.loc[year_now, 'output_dismantling_recycling_steel'] = (
            eol.loc[year_now, 'output_dismantling_recycling_flatsteel'] +
            eol.loc[year_now, 'output_dismantling_recycling_longsteel']
        )
        eol.loc[year_now, 'output_dismantling_recycling_aluminum'] = (
            eol.loc[year_now, 'output_dismantling_recycling_wroughtaluminum'] +
            eol.loc[year_now, 'output_dismantling_recycling_castaluminum_lowCu'] + 
            eol.loc[year_now, 'output_dismantling_recycling_castaluminum_highCu']
        )


        # PST RECYCLING

        # (!) In PST, there are no seperate flat steel and long steel outputs; thus, there is only one total steel output.
        # There are two possible aluminum output options: (1) mixedaluminum, or (2) wroughtaluminum, castaluminum_lowCu, and castaluminum_highCu. 
        parameter = ['steel', 'mixedaluminum', 'wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']

        for p in parameter:

            output = 0

            for veh in set_vehicles:  

                if p == 'mixedaluminum':
                    _mass = eol_veh.loc[(veh, year_now), f'bodies_wroughtaluminum'] + eol_veh.loc[(veh, year_now), f'bodies_castaluminum_lowCu'] + eol_veh.loc[(veh, year_now), f'bodies_castaluminum_highCu']

                else:
                    _mass = eol_veh.loc[(veh, year_now), f'bodies_{p}']

                _yield = eol_pst.loc[year_now, f'{p}_yield'] / 100

                _output = _mass * _yield

                eol_veh.loc[(veh, year_now), f'output_pst_{p}'] = _output

                output += _output

            eol.loc[year_now, f'output_pst_{p}'] = output

        # Total aluminum:

        if eol.loc[year_now, 'output_pst_mixedaluminum'] > 0:
            eol.loc[year_now, 'output_pst_aluminum'] = eol.loc[year_now, 'output_pst_mixedaluminum']

        else:
            eol.loc[year_now, 'output_pst_aluminum'] = (
                eol.loc[year_now, 'output_pst_wroughtaluminum'] +
                eol.loc[year_now, 'output_pst_castaluminum_lowCu'] + 
                eol.loc[year_now, 'output_pst_castaluminum_highCu']
            )


    return eol_veh, eol



###
###  (6) CALCULATE MATERIAL DEMAND AND SUPPLY
###

def calc_demandSupply(start_year, end_year, set_years, set_vehicles, registrations, vehicles_data, eol, component_production, steel_production, aluminum_production, eol_dismantling_recycling, eol_pst):


    # (6.1) CALCULATE MATERIAL DEMAND IN NEW VEHILCES
    # AND MATERIAL PRODUCTION

    # material_demand[year] = {
    #   FLAT STEEL:    flatsteel_vehicles, flatsteel_production,
    #                  flatsteel_production_s1, flatsteel_production_s2,
    #                  flatsteel_production_s3,
    #                  flatsteel_production_max_scrap,
    #                  flatsteel_production_s1_max_scrap,
    #                  flatsteel_production_s2_max_scrap,
    #                  flatsteel_production_s3_max_scrap,
    #                  flatsteel_production_min_scrap,
    #                  flatsteel_production_s1_min_scrap,
    #                  flatsteel_production_s2_min_scrap,
    #                  flatsteel_production_s3_min_scrap,
    #   LONG STEEL:    longsteel_vehicles, longsteel_production,
    #                  longsteel_production_s1, longsteel_production_s2,
    #                  longsteel_production_s3,
    #                  longsteel_production_max_scrap,
    #                  longsteel_production_s1_max_scrap,
    #                  longsteel_production_s2_max_scrap,
    #                  longsteel_production_s3_max_scrap,
    #                  longsteel_production_min_scrap,
    #                  longsteel_production_s1_min_scrap,
    #                  longsteel_production_s2_min_scrap,
    #                  longsteel_production_s3_min_scrap,
    #   WROUGHT AL:    wroughtaluminum_vehicles, wroughtaluminum_production,
    #                  wroughtaluminum_production_max_scrap,
    #                  wroughtaluminum_production_min_scrap,
    #   CAST AL:       castaluminum_lowCu_vehicles, castaluminum_lowCu_production,
    #                  castaluminum_lowCu_production_max_scrap,
    #                  castaluminum_lowCu_production_min_scrap,
    #                  castaluminum_highCu_vehicles, castaluminum_highCu_production,
    #                  castaluminum_highCu_production_max_scrap,
    #                  castaluminum_highCu_production_min_scrap,
    #   TOTALS:        steel_vehicles, steel_production,
    #                  steel_production_max_scrap, steel_production_min_scrap,
    #                  aluminum_vehicles, aluminum_production,
    #                  aluminum_production_max_scrap, aluminum_production_min_scrap,
    # }

    material_demand = pd.DataFrame({
        'year': range(start_year, end_year + 1)
    })
    material_demand.set_index('year', inplace=True)

    for year_now in set_years:

        # (6.1.1) FLAT STEEL AND LONG STEEL DEMAND

        parameter = ['flatsteel', 'longsteel']

        for p in parameter:

            # Material demand in vehicles:

            veh_demand = 0

            for veh in set_vehicles:
                n_veh = registrations.loc[(veh, year_now), 'registrations']
                mass = vehicles_data.loc[(veh, year_now), f'{p}_mass']

                veh_demand += n_veh * mass

            material_demand.loc[year_now, f'{p}_vehicles'] = veh_demand

            # Material demand in component production:
            comp_efficiency = component_production.loc[year_now, f'{p}_efficiency'] / 100

            if comp_efficiency != 0:
                comp_demand = veh_demand / comp_efficiency

            else:
                comp_demand = 0
                print(f'!) DIVISION BY ZERO: Component production efficiency for {p} is zero. Update input data!')

            # Material demand per steel production route:

            prod_demand = 0
            prod_demand_max_scrap = 0
            prod_demand_min_scrap = 0

            for s in range(1, 4):

                prod_efficiency = steel_production.loc[year_now, f's{s}_efficiency'] / 100

                if prod_efficiency != 0:
                    _prod_demand = (steel_production.loc[year_now, f'{p}_s{s}'] / 100) * comp_demand / prod_efficiency

                else:
                    _prod_demand = 0
                    print(f'!) DIVISION BY ZERO: Production efficiency for {p}_s{s} is zero. Update input data!')

                material_demand.loc[year_now, f'{p}_production_s{s}'] = _prod_demand

                prod_demand += _prod_demand

                # Maximum feasible scrap input:

                _prod_demand_max_scrap = _prod_demand * (steel_production.loc[year_now, f's{s}_max_scrap'] / 100)
                _prod_demand_min_scrap = _prod_demand * (steel_production.loc[year_now, f's{s}_min_scrap'] / 100)

                material_demand.loc[year_now, f'{p}_production_s{s}_max_scrap'] = _prod_demand_max_scrap
                material_demand.loc[year_now, f'{p}_production_s{s}_min_scrap'] = _prod_demand_min_scrap

                prod_demand_max_scrap += _prod_demand_max_scrap
                prod_demand_min_scrap += _prod_demand_min_scrap

            material_demand.loc[year_now, f'{p}_production'] = prod_demand
            material_demand.loc[year_now, f'{p}_production_max_scrap'] = prod_demand_max_scrap
            material_demand.loc[year_now, f'{p}_production_min_scrap'] = prod_demand_min_scrap


        # (6.1.2) WROUGHT ALUMINUM AND CAST ALUMINUM DEMAND

        parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']

        for p in parameter:

            # Material demand in vehicles:

            veh_demand = 0

            for veh in set_vehicles:
                n_veh = registrations.loc[(veh, year_now), 'registrations']
                mass = vehicles_data.loc[(veh, year_now), f'{p}_mass']

                veh_demand += n_veh * mass

            material_demand.loc[year_now, f'{p}_vehicles'] = veh_demand

            # Material demand in component production:

            comp_efficiency = component_production.loc[year_now, f'{p}_efficiency'] / 100

            if comp_efficiency != 0:
                comp_demand = veh_demand / comp_efficiency

            else:
                comp_demand = 0
                print(f'!) DIVISION BY ZERO: Component production efficiency for {p} is zero. Update input data!')

            # Material demand in material production:

            prod_efficiency = aluminum_production.loc[year_now, f'{p}_efficiency'] / 100

            if prod_efficiency != 0:
                prod_demand = comp_demand / prod_efficiency

            else:
                prod_demand = 0
                print(f'!) DIVISION BY ZERO: Production efficiency for {p} is zero. Update input data!')

            material_demand.loc[year_now, f'{p}_production'] = prod_demand

            # Maximum feasible scrap input:

            prod_demand_max_scrap = prod_demand * (aluminum_production.loc[year_now, f'{p}_max_scrap'] / 100)
            prod_demand_min_scrap = prod_demand * (aluminum_production.loc[year_now, f'{p}_min_scrap'] / 100)

            material_demand.loc[year_now, f'{p}_production_max_scrap'] = prod_demand_max_scrap
            material_demand.loc[year_now, f'{p}_production_min_scrap'] = prod_demand_min_scrap


        # (6.1.3) TOTAL STEEL AND ALUMINUM DEMAND

        category = ['vehicles', 'production', 'production_max_scrap', 'production_min_scrap']

        for c in category:

            material_demand.loc[year_now, f'steel_{c}'] = (
                material_demand.loc[year_now, f'flatsteel_{c}'] + 
                material_demand.loc[year_now, f'longsteel_{c}']
            )
            material_demand.loc[year_now, f'aluminum_{c}'] = (
                material_demand.loc[year_now, f'wroughtaluminum_{c}'] + 
                material_demand.loc[year_now, f'castaluminum_lowCu_{c}'] + 
                material_demand.loc[year_now, f'castaluminum_highCu_{c}']
            )


    # (6.2) CALCULATE MATERIAL SUPPLY FROM INTERNAL,
    # PRE-CONSUMER, AND POST-CONSUMER SCRAP

    # material_supply[year] = {
    #   FLAT STEEL:    flatsteel_internal, flatsteel_internal_s1,
    #                  flatsteel_internal_s2, flatsteel_internal_s3,
    #                  flatsteel_preconsumer,
    #                  flatsteel_postconsumer_dismantling,
    #   LONG STEEL:    longsteel_internal, longsteel_internal_s1,
    #                  longsteel_internal_s2, longsteel_internal_s3,
    #                  longsteel_preconsumer,
    #                  longsteel_postconsumer_dismantling,
    #   STEEL TOTAL:   steel_internal, steel_preconsumer,
    #                  steel_postconsumer_dismantling,
    #                  steel_postconsumer_pst,
    #                  steel_postconsumer,
    #   WROUGHT AL:    wroughtaluminum_internal,
    #                  wroughtaluminum_preconsumer,
    #                  wroughtaluminum_postconsumer_dismantling,
    #                  wroughtaluminum_postconsumer_pst,
    #                  wroughtaluminum_postconsumer,
    #   CAST AL:       castaluminum_lowCu_internal,
    #                  castaluminum_lowCu_preconsumer,
    #                  castaluminum_lowCu_postconsumer_dismantling,
    #                  castaluminum_lowCu_postconsumer_pst,
    #                  castaluminum_lowCu_postconsumer,
    #                  castaluminum_highCu_internal,
    #                  castaluminum_highCu_preconsumer,
    #                  castaluminum_highCu_postconsumer_dismantling,
    #                  castaluminum_highCu_postconsumer_pst,
    #                  castaluminum_highCu_postconsumer,
    #   MIXED AL:      mixedaluminum_postconsumer_pst,
    #                  mixedaluminum_postconsumer,
    #   AL TOTAL:      aluminum_internal,
    #                  aluminum_preconsumer,
    #                  aluminum_postconsumer_dismantling,
    #                  aluminum_postconsumer_pst,
    #                  aluminum_postconsumer
    # }

    material_supply = pd.DataFrame({
        'year': range(start_year, end_year + 1)
    })
    material_supply.set_index('year', inplace=True)

    for year_now in set_years:


        # (6.2.1) STEEL SCRAP SUPPLY

        parameter = ['flatsteel', 'longsteel']

        for p in parameter:

            # Internal flat steel and longs steel scrap from material production:

            supply_internal = 0

            for s in range (1,4):

                _supply_internal = material_demand.loc[year_now, f'{p}_production_s{s}'] * (1 - steel_production.loc[year_now, f's{s}_efficiency'] / 100) * (steel_production.loc[year_now, f's{s}_scrap_recycling_rate'] / 100)

                material_supply.loc[year_now, f'{p}_internal_s{s}'] = _supply_internal
                
                supply_internal += _supply_internal
                
            material_supply.loc[year_now, f'{p}_internal'] = supply_internal

            # Pre-consumer flat steel and long steel scrap from component production:

            comp_efficiency = component_production.loc[year_now, f'{p}_efficiency'] / 100

            if comp_efficiency != 0:
                supply_preconsumer = material_demand.loc[year_now, f'{p}_vehicles'] * (1 / comp_efficiency - 1) * (component_production.loc[year_now, f'{p}_scrap_recycling_rate'] / 100)

            else:
                supply_preconsumer = 0
                print(f'!) DIVISION BY ZERO: Component production efficiency for {p} is zero. Update input data!')

            material_supply.loc[year_now,  f'{p}_preconsumer'] = supply_preconsumer

            # Post-consumer flat steel and long steel scrap from dismantling recycling:

            supply_postconsumer = eol.loc[year_now, f'output_dismantling_recycling_{p}']

            material_supply.loc[year_now, f'{p}_postconsumer_dismantling'] = supply_postconsumer

        # Post-consumer steel scrap from PST recycling:

        p = 'steel'

        supply_postconsumer = eol.loc[year_now, 'output_pst_steel']

        material_supply.loc[year_now, 'steel_postconsumer_pst'] = supply_postconsumer


        # TOTAL STEEL

        category = ['internal', 'preconsumer', 'postconsumer_dismantling']

        for c in category:

            material_supply.loc[year_now, f'steel_{c}'] = (
                material_supply.loc[year_now, f'flatsteel_{c}'] + 
                material_supply.loc[year_now, f'longsteel_{c}']
            )

        material_supply.loc[year_now, 'steel_postconsumer'] = (
            material_supply.loc[year_now, 'steel_postconsumer_dismantling'] + 
            material_supply.loc[year_now, 'steel_postconsumer_pst']
        )


        # (6.2.2) ALUMINUM SCRAP SUPPLY

        parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']

        for p in parameter:

            # Internal scrap from material production:

            supply_internal = material_demand.loc[year_now, f'{p}_production'] * (1 - aluminum_production.loc[year_now, f'{p}_efficiency'] / 100) * (aluminum_production.loc[year_now, f'{p}_scrap_recycling_rate'] / 100)

            material_supply.loc[year_now, f'{p}_internal'] = supply_internal

            # Pre-consumer scrap from component production:

            comp_efficiency = component_production.loc[year_now, f'{p}_efficiency'] / 100

            if comp_efficiency != 0:
                supply_preconsumer = material_demand.loc[year_now, f'{p}_vehicles'] * (1 / comp_efficiency - 1) * (component_production.loc[year_now, f'{p}_scrap_recycling_rate'] / 100)

            else:
                supply_preconsumer = 0
                print(f'!) DIVISION BY ZERO: Component production efficiency for {p} is zero. Update input data!')

            material_supply.loc[year_now,  f'{p}_preconsumer'] = supply_preconsumer

            # Post-consumer scrap from dismantling recycling:

            supply_postconsumer = eol.loc[year_now, f'output_dismantling_recycling_{p}']

            material_supply.loc[year_now, f'{p}_postconsumer_dismantling'] = supply_postconsumer

            # Post-consumer scrap from PST recycling:

            supply_postconsumer = eol.loc[year_now, f'output_pst_{p}']

            material_supply.loc[year_now, f'{p}_postconsumer_pst'] = supply_postconsumer

            # Total post-consumer:

            material_supply.loc[year_now, f'{p}_postconsumer'] = (
                material_supply.loc[year_now, f'{p}_postconsumer_dismantling'] + 
                material_supply.loc[year_now, f'{p}_postconsumer_pst']
            )

        # Post-consumer mixedaluminum from PST recycling:

        p = 'mixedaluminum'
        supply_postconsumer = eol.loc[year_now, f'output_pst_{p}']
        material_supply.loc[year_now, f'{p}_postconsumer_pst'] = supply_postconsumer
        material_supply.loc[year_now, f'{p}_postconsumer'] = supply_postconsumer


        # TOTAL ALUMINUM

        category = ['internal', 'preconsumer', 'postconsumer_dismantling', 'postconsumer_pst', 'postconsumer']

        for c in category:

            if c == 'postconsumer_pst' or c == 'postconsumer':
                material_supply.loc[year_now, f'aluminum_{c}'] = (
                    material_supply.loc[year_now, f'wroughtaluminum_{c}'] + 
                    material_supply.loc[year_now, f'castaluminum_lowCu_{c}'] + 
                    material_supply.loc[year_now, f'castaluminum_highCu_{c}'] + 
                    material_supply.loc[year_now, f'mixedaluminum_{c}']
                )

            else:
                material_supply.loc[year_now, f'aluminum_{c}'] = (
                    material_supply.loc[year_now, f'wroughtaluminum_{c}'] + 
                    material_supply.loc[year_now, f'castaluminum_lowCu_{c}'] + 
                    material_supply.loc[year_now, f'castaluminum_highCu_{c}']
                )


    return material_demand, material_supply



###
###  (7) CALCULATE MATERIAL USE BY ALLOCATNG (SCRAP)
###      MATERIAL SUPPLY TO MEET MATERIAL DEMAND
###

def calc_use(start_year, end_year, set_years, eol, material_demand, material_supply, steel_production, aluminum_production, eol_dismantling_recycling, eol_pst):

    # material_use[year] = {
    #   FLAT STEEL:    flatsteel_internal, flatsteel_internal_s1/s2/s3,
    #                  flatsteel_preconsumer, flatsteel_preconsumer_s1/s2/s3,
    #                  flatsteel_postconsumer, flatsteel_postconsumer_s1/s2/s3,
    #                  flatsteel_postconsumer_dismantling, 
    #                  flatsteel_postconsumer_dismantling_s1/s2/s3,
    #                  flatsteel_postconsumer_pst, 
    #                  flatsteel_postconsumer_pst_s1/s2/s3,
    #                  flatsteel_virgin, flatsteel_virgin_s1/s2/s3,
    #                  flatsteel_to_closedloop, flatsteel_to_openloop
    #   LONG STEEL:    longsteel_internal, longsteel_internal_s1/s2/s3,
    #                  longsteel_preconsumer, longsteel_preconsumer_s1/s2/s3,
    #                  longsteel_postconsumer, longsteel_postconsumer_s1/s2/s3,
    #                  longsteel_postconsumer_dismantling,             
    #                  longsteel_postconsumer_dismantling_s1/s2/s3,
    #                  longsteel_postconsumer_pst, 
    #                  longsteel_postconsumer_pst_s1/s2/s3,
    #                  longsteel_virgin, longsteel_virgin_s1/s2/s3,
    #                  longsteel_to_closedloop, longsteel_to_openloop
    #   WROUGHT AL:    wroughtaluminum_internal, wroughtaluminum_preconsumer,
    #                  wroughtaluminum_postconsumer, 
    #                  wroughtaluminum_postconsumer_dismantling, 
    #                  wroughtaluminum_postconsumer_pst,
    #                  wroughtaluminum_virgin, wroughtaluminum_to_closedloop, 
    #                  wroughtaluminum_to_openloop
    #   CAST AL:       castaluminum_internal, castaluminum_preconsumer,
    #                  castaluminum_postconsumer, 
    #                  castaluminum_postconsumer_dismantling, 
    #                  castaluminum_postconsumer_pst,
    #                  castaluminum_virgin, castaluminum_to_closedloop, 
    #                  castaluminum_to_openloop
    #   STEEL TOTAL:   steel_internal, steel_preconsumer, steel_postconsumer, 
    #                  steel_postconsumer_dismantling, steel_postconsumer_pst,
    #                  steel_openloop, steel_virgin, steel_to_closedloop, 
    #                  steel_to_openloop
    #   AL TOTAL:      aluminum_internal, aluminum_preconsumer, 
    #                  aluminum_postconsumer, 
    #                  aluminum_postconsumer_dismantling, 
    #                  aluminum_postconsumer_pst,
    #                  aluminum_openloop, aluminum_virgin, 
    #                  aluminum_to_closedloop, aluminum_to_openloop
    #   TOTAL:         total_internal, total_preconsumer, total_postconsumer, 
    #                  total_postconsumer_dismantling, total_postconsumer_pst,
    #                  total_openloop, total_virgin, total_to_closedloop, 
    #                  total_to_openloop
    # }

    material_use = pd.DataFrame({
        'year': range(start_year, end_year + 1)
    })
    material_use.set_index('year', inplace=True)


    material_use, material_quality, objective, eol_pst = run_optimization(material_use, set_years, material_demand, material_supply, steel_production, aluminum_production, eol, eol_dismantling_recycling, eol_pst)


    return material_use, material_quality, objective, eol_pst



###
###  (8) CALCULATE CLOSED-LOOP RATES
###

def calc_closedloop(set_years, material_demand, material_use):

    # closedloop[year] = {
    #   FLAT STEEL:    flatsteel_postconsumer, flatsteel_recycledcontent
    #   LONG STEEL:    longsteel_postconsumer, longsteel_recycledcontent
    #   WROUGHT AL:    wroughtaluminum_postconsumer, wroughtaluminum_recycledcontent
    #   CAST AL:       castaluminum_lowCu_postconsumer,
    #                  castaluminum_lowCu_recycledcontent,
    #                  castaluminum_highCu_postconsumer,
    #                  castaluminum_highCu_recycledcontent
    #   STEEL TOTAL:   steel_postconsumer, steel_recycledcontent
    #   AL TOTAL:      aluminum_postconsumer, aluminum_recycledcontent
    #   TOTAL:         total_postconsumer, total_recycledcontent
    # }

    closedloop = pd.DataFrame({
        'year': [j for j in set_years]
    })
    closedloop.set_index('year', inplace=True)

    for year_now in set_years:

        parameter = ['flatsteel', 'longsteel', 'wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu', 'steel', 'aluminum']

        for p in parameter:

            demand_production = material_demand.loc[year_now, f'{p}_production']
            #to_closedloop = material_use.loc[year_now, f'{p}_to_closedloop']
            postconsumer = material_use.loc[year_now, f'{p}_postconsumer']
            recycledcontent = material_use.loc[year_now, f'{p}_preconsumer'] + material_use.loc[year_now, f'{p}_postconsumer']

            #closedloop.loc[year_now, f'{p}_closedloop'] = to_closedloop / demand_production * 100 if demand_production > 0 else np.nan

            closedloop.loc[year_now, f'{p}_postconsumer'] = postconsumer / demand_production * 100 if demand_production > 0 else np.nan

            closedloop.loc[year_now, f'{p}_recycledcontent'] = recycledcontent / demand_production * 100 if demand_production > 0 else np.nan


        # Total:

        total_production_demand = (
            material_demand.loc[year_now, 'flatsteel_production'] +
            material_demand.loc[year_now, 'longsteel_production'] +
            material_demand.loc[year_now, 'wroughtaluminum_production'] +
            material_demand.loc[year_now, 'castaluminum_lowCu_production'] + 
            material_demand.loc[year_now, 'castaluminum_highCu_production']
        )

        category = ['postconsumer', 'recycledcontent']  # 'closedloop', 

        for c in category:
        
            closedloop.loc[year_now, f'total_{c}'] = ((  
                    closedloop.loc[year_now, f'flatsteel_{c}'] +
                    closedloop.loc[year_now, f'longsteel_{c}'] +
                    closedloop.loc[year_now, f'wroughtaluminum_{c}'] +
                    closedloop.loc[year_now, f'castaluminum_lowCu_{c}'] + 
                    closedloop.loc[year_now, f'castaluminum_highCu_{c}']
                ) / total_production_demand * 100 if total_production_demand > 0 else np.nan
            )
        

    return closedloop



###
###  CALCULATE ALL
###

def calc_all(start_year, end_year, n_vehicles, vehicles_data, cagr, init_year, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production, set_years, set_vehicles, SHAPE, SCALE):


    # (1) VEHICLES

    _vehicles_data = calc_vehicles(start_year, end_year, n_vehicles, vehicles_data)


    # (2) REGISTRATIONS

    if init_year < end_year:
        _registrations = calc_registrations(start_year, end_year, set_vehicles, cagr, init_year, registrations)

    else:
        _registrations = registrations


    # (3) VEHICLE FLEET

    _fleet_detail, _fleet = calc_fleet(start_year, end_year, set_years, set_vehicles, _registrations, SHAPE, SCALE)


    # (4) END-OF-LIFE (ELVS)

    _fleet_detail, _fleet = calc_eol(start_year, set_years, set_vehicles, _fleet_detail, _fleet, eol_loss)


    # (5) RECYCLING OUTPUTS

    _eol_veh, _eol = calc_recycling(start_year, set_years, set_vehicles, _vehicles_data, _fleet_detail, eol_dismantling, eol_dismantling_recycling, eol_pst)


    # (6) MATERIAL DEMAND AND SUPPLY

    _material_demand, _material_supply = calc_demandSupply(start_year, end_year, set_years, set_vehicles, _registrations, _vehicles_data, _eol, component_production, steel_production, aluminum_production, eol_dismantling_recycling, eol_pst)


    # (7) MATERIAL USE

    _material_use, _material_quality, _objective, _eol_pst = calc_use(start_year, end_year, set_years, _eol, _material_demand, _material_supply, steel_production, aluminum_production, eol_dismantling_recycling, eol_pst)
    
    # (8) CLOSED-LOOP RATES

    _closedloop = calc_closedloop(set_years, _material_demand, _material_use)


    return _vehicles_data, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _closedloop, _material_quality, _objective