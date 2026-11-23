####
#
# CASAsim
# Read model input data from excel file
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


def import_data(file_path):


    ###
    ###  (1) IMPORT 'Vehicles' DATA
    ###

    # Import vehicle model data from sheet 'Vehicles' and basic model settings (start year, end year, number of vehicle models, vehicle model names)
    
    # vehicles_names[id] = {name}
    # vehicles_data[id, year] = {total_mass, steel_content, flatsteel_content, longsteel_content, aluminum_content, wroughtaluminum_content, castaluminum_content}
    
    try:
        df = pd.read_excel(file_path, sheet_name='Vehicles')

        start_year = int(df.iat[3, 3])
        end_year = int(df.iat[4, 3])
        n_years = int(end_year - start_year + 1)
        n_vehicles = int(df.iat[6, 3])

        print(f'   start year: {start_year}')
        print(f'   end year: {end_year}')
        print(f'   number of vehicles: {n_vehicles}')

        vehicles_names = pd.DataFrame({
            'id': range(1, n_vehicles + 1)})
        vehicles_names.set_index('id', inplace=True)


        vehicles_data = pd.DataFrame({
            'id': [i for i in range(1, n_vehicles + 1) for j in range(start_year, end_year + 1)],
            'year': [j for i in range(1, n_vehicles + 1) for j in range(start_year, end_year + 1)]})
        vehicles_data.set_index(['id', 'year'], inplace=True)

        row = 13

        for i in range(1, n_vehicles + 1):
            for j in range(start_year, end_year + 1):
                vehicles_names.loc[i, 'name'] = df.iat[9, 2+i]

                vehicles_data.loc[(i, j), 'total_mass'] = df.iat[row, j-start_year+3]
                vehicles_data.loc[(i, j), 'steel_content'] = df.iat[row+1, j-start_year+3]
                vehicles_data.loc[(i, j), 'flatsteel_content'] = df.iat[row+2, j-start_year+3]
                vehicles_data.loc[(i, j), 'longsteel_content'] = df.iat[row+3, j-start_year+3]
                vehicles_data.loc[(i, j), 'aluminum_content'] = df.iat[row+4, j-start_year+3]
                vehicles_data.loc[(i, j), 'wroughtaluminum_content'] = df.iat[row+5, j-start_year+3]
                vehicles_data.loc[(i, j), 'castaluminum_lowCu_content'] = df.iat[row+6, j-start_year+3]
                vehicles_data.loc[(i, j), 'castaluminum_highCu_content'] = df.iat[row+7, j-start_year+3]

            row += 10

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")
    
    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'Vehicles': {e}")
        return None
    


    ###
    ###  (2) IMPORT 'Registrations' DATA
    ###

    # Import vehicle registration data from sheet 'Registrations' and the CAGR for forcasting future registrations
    
    # registrations[id, year] = {registrations}

    try:
        df = pd.read_excel(file_path, sheet_name='Registrations')

        cagr = float(df.iat[3, 3])
        n_init_years = df.loc[5].count()
        
        print(f'   CAGR [%]: {cagr}')
        print(f'   number of model initialization years: {n_init_years}')

        registrations = pd.DataFrame({
            'id': [i for i in range(1, n_vehicles + 1) for j in range(start_year, start_year + n_init_years)],
            'year': [j for i in range(1, n_vehicles + 1) for j in range(start_year, start_year + n_init_years)]})
        registrations.set_index(['id', 'year'], inplace=True)

        for i in range(1, n_vehicles + 1):
            for j in range(start_year, start_year + n_init_years):
                registrations.loc[(i, j), 'registrations'] = int(df.iat[6+i, j-start_year+3])

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")
    
    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'Registrations': {e}")
        return None
    


    ###
    ###  (3) IMPORT 'Steel-Production' DATA
    ###

    # Import production data from sheet 'Steel-Production' including configurations of different steel production routes, their production efficiencies and maximum recycled input capacities

    # steel_production[year] = {...}

    try:
        df = pd.read_excel(file_path, sheet_name='Steel-Production')

        # Flat steel thresholds:

        flatsteel_threshold = df.iloc[15, 3:3+n_years].values

        if isinstance(flatsteel_threshold[0], (int, float, np.number)):
            flatsteel_n_thresholds = 1
            flatsteel_threshold = [[flatsteel_threshold[i]] for i in range(len(flatsteel_threshold))]

        elif isinstance(flatsteel_threshold[0], str):
            for i in range(len(flatsteel_threshold)):
                value = flatsteel_threshold[i]
                flatsteel_threshold[i] = [float(x.strip()) for x in value.split(";")]
            
            flatsteel_n_thresholds = len(flatsteel_threshold[0])

        # Long steel thresholds:

        longsteel_threshold = df.iloc[16, 3:3+n_years].values

        if isinstance(longsteel_threshold[0], (int, float, np.number)):
            longsteel_n_thresholds = 1
            longsteel_threshold = [[longsteel_threshold[i]] for i in range(len(longsteel_threshold))]

        elif isinstance(longsteel_threshold[0], str):
            for i in range(len(longsteel_threshold)):
                value = longsteel_threshold[i]
                longsteel_threshold[i] = [float(x.strip()) for x in value.split(";")]
            
            longsteel_n_thresholds = len(longsteel_threshold[0])

        # Virgin steel quality:

        virgin_steel_quality = df.iloc[18, 3:3+n_years].values

        if isinstance(virgin_steel_quality[0], (int, float, np.number)):
            virgin_n_thresholds = 1
            virgin_steel_quality = [[virgin_steel_quality[i]] for i in range(len(virgin_steel_quality))]

        elif isinstance(virgin_steel_quality[0], str):
            for i in range(len(virgin_steel_quality)):
                value = virgin_steel_quality[i]
                virgin_steel_quality[i] = [float(x.strip()) for x in value.split(";")]
            
            virgin_n_thresholds = len(virgin_steel_quality[0])

        if not (flatsteel_n_thresholds == longsteel_n_thresholds == virgin_n_thresholds):
            raise Exception("ERROR: The number of thresholds for flat steel, long steel and virgin steel quality must be the same!")


        steel_production = pd.DataFrame({
            'year': range(start_year, end_year + 1),

            # Production routes:

            'flatsteel_s1': df.iloc[7, 3:3+n_years].values,
            'flatsteel_s2': df.iloc[8, 3:3+n_years].values,
            'flatsteel_s3': df.iloc[9, 3:3+n_years].values,
            'longsteel_s1': df.iloc[11, 3:3+n_years].values,
            'longsteel_s2': df.iloc[12, 3:3+n_years].values,
            'longsteel_s3': df.iloc[13, 3:3+n_years].values,

            'n_thresholds': [flatsteel_n_thresholds for i in range(n_years)],

            'flatsteel_threshold': flatsteel_threshold,
            'longsteel_threshold': longsteel_threshold,

            'virgin_steel_quality': virgin_steel_quality,

            # Route configurations:

            's1_min_scrap': df.iloc[22, 3:3+n_years].values,
            's1_max_scrap': df.iloc[23, 3:3+n_years].values,
            's1_efficiency': df.iloc[24, 3:3+n_years].values,
            's1_scrap_recycling_rate': df.iloc[25, 3:3+n_years].values,
            
            's2_min_scrap': df.iloc[29, 3:3+n_years].values,
            's2_max_scrap': df.iloc[30, 3:3+n_years].values,
            's2_efficiency': df.iloc[31, 3:3+n_years].values,
            's2_scrap_recycling_rate': df.iloc[32, 3:3+n_years].values,

            's3_min_scrap': df.iloc[36, 3:3+n_years].values,
            's3_max_scrap': df.iloc[37, 3:3+n_years].values,
            's3_efficiency': df.iloc[38, 3:3+n_years].values,
            's3_scrap_recycling_rate': df.iloc[39, 3:3+n_years].values
        })
         
        steel_production.set_index('year', inplace=True)

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")

    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'Steel-Production': {e}")
        return None
    


    ###
    ###  (4) IMPORT 'Aluminum-Production' DATA
    ###

    # Import production data from sheet 'Aluminum-Production' including production efficiencies and maximum recycled input capacities
    
    # aluminum_production[year] = {...}

    try:
        df = pd.read_excel(file_path, sheet_name='Aluminum-Production')

        # Wrought aluminum thresholds:

        wroughtaluminum_threshold = df.iloc[12, 3:3+n_years].values

        if isinstance(wroughtaluminum_threshold[0], (int, float, np.number)):
            wroughtaluminum_n_thresholds = 1
            wroughtaluminum_threshold = [[wroughtaluminum_threshold[i]] for i in range(len(wroughtaluminum_threshold))]

        elif isinstance(wroughtaluminum_threshold[0], str):
            for i in range(len(wroughtaluminum_threshold)):
                value = wroughtaluminum_threshold[i]
                wroughtaluminum_threshold[i] = [float(x.strip()) for x in value.split(";")]
            
            wroughtaluminum_n_thresholds = len(wroughtaluminum_threshold[0])

        # Virgin wrought aluminum quality:

        virgin_wroughtaluminum_quality = df.iloc[13, 3:3+n_years].values

        if isinstance(virgin_wroughtaluminum_quality[0], (int, float, np.number)):
            virgin_wroughtaluminum_n_thresholds = 1
            virgin_wroughtaluminum_quality = [[virgin_wroughtaluminum_quality[i]] for i in range(len(virgin_wroughtaluminum_quality))]

        elif isinstance(virgin_wroughtaluminum_quality[0], str):
            for i in range(len(virgin_wroughtaluminum_quality)):
                value = virgin_wroughtaluminum_quality[i]
                virgin_wroughtaluminum_quality[i] = [float(x.strip()) for x in value.split(";")]
            
            virgin_wroughtaluminum_n_thresholds = len(virgin_wroughtaluminum_quality[0])

        # Low-Cu cast aluminum thresholds:

        castaluminum_lowCu_threshold = df.iloc[22, 3:3+n_years].values

        if isinstance(castaluminum_lowCu_threshold[0], (int, float, np.number)):
            castaluminum_lowCu_n_thresholds = 1
            castaluminum_lowCu_threshold = [[castaluminum_lowCu_threshold[i]] for i in range(len(castaluminum_lowCu_threshold))]

        elif isinstance(castaluminum_lowCu_threshold[0], str):
            for i in range(len(castaluminum_lowCu_threshold)):
                value = castaluminum_lowCu_threshold[i]
                castaluminum_lowCu_threshold[i] = [float(x.strip()) for x in value.split(";")]
            
            castaluminum_lowCu_n_thresholds = len(castaluminum_lowCu_threshold[0])

        # Virgin low-Cu cast aluminum quality:

        virgin_castaluminum_lowCu_quality = df.iloc[23, 3:3+n_years].values

        if isinstance(virgin_castaluminum_lowCu_quality[0], (int, float, np.number)):
            virgin_castaluminum_lowCu_n_thresholds = 1
            virgin_castaluminum_lowCu_quality = [[virgin_castaluminum_lowCu_quality[i]] for i in range(len(virgin_castaluminum_lowCu_quality))]

        elif isinstance(virgin_castaluminum_lowCu_quality[0], str):
            for i in range(len(virgin_castaluminum_lowCu_quality)):
                value = virgin_castaluminum_lowCu_quality[i]
                virgin_castaluminum_lowCu_quality[i] = [float(x.strip()) for x in value.split(";")]
            
            virgin_castaluminum_lowCu_n_thresholds = len(virgin_castaluminum_lowCu_quality[0])

        # High-Cu cast aluminum thresholds:

        castaluminum_highCu_threshold = df.iloc[32, 3:3+n_years].values

        if isinstance(castaluminum_highCu_threshold[0], (int, float, np.number)):
            castaluminum_highCu_n_thresholds = 1
            castaluminum_highCu_threshold = [[castaluminum_highCu_threshold[i]] for i in range(len(castaluminum_highCu_threshold))]

        elif isinstance(castaluminum_highCu_threshold[0], str):
            for i in range(len(castaluminum_highCu_threshold)):
                value = castaluminum_highCu_threshold[i]
                castaluminum_highCu_threshold[i] = [float(x.strip()) for x in value.split(";")]
            
            castaluminum_highCu_n_thresholds = len(castaluminum_highCu_threshold[0])

        # Virgin high-Cu cast aluminum quality:

        virgin_castaluminum_highCu_quality = df.iloc[33, 3:3+n_years].values

        if isinstance(virgin_castaluminum_highCu_quality[0], (int, float, np.number)):
            virgin_castaluminum_highCu_n_thresholds = 1
            virgin_castaluminum_highCu_quality = [[virgin_castaluminum_highCu_quality[i]] for i in range(len(virgin_castaluminum_highCu_quality))]

        elif isinstance(virgin_castaluminum_highCu_quality[0], str):
            for i in range(len(virgin_castaluminum_highCu_quality)):
                value = virgin_castaluminum_highCu_quality[i]
                virgin_castaluminum_highCu_quality[i] = [float(x.strip()) for x in value.split(";")]
            
            virgin_castaluminum_highCu_n_thresholds = len(virgin_castaluminum_highCu_quality[0])

        if not (wroughtaluminum_n_thresholds == virgin_wroughtaluminum_n_thresholds == castaluminum_lowCu_n_thresholds == virgin_castaluminum_lowCu_n_thresholds == castaluminum_highCu_n_thresholds == virgin_castaluminum_highCu_n_thresholds):
            raise Exception("ERROR: The number of thresholds for low-Cu cast aluminum, high-Cu cast aluminum, and virgin aluminum quality must be the same!")

        aluminum_production = pd.DataFrame({
            'year': range(start_year, end_year + 1),

            'n_thresholds': [wroughtaluminum_n_thresholds for i in range(n_years)],

            'wroughtaluminum_min_scrap': df.iloc[7, 3:3+n_years].values,
            'wroughtaluminum_max_scrap': df.iloc[8, 3:3+n_years].values,
            'wroughtaluminum_efficiency': df.iloc[9, 3:3+n_years].values,
            'wroughtaluminum_scrap_recycling_rate': df.iloc[10, 3:3+n_years].values,
            'wroughtaluminum_threshold': wroughtaluminum_threshold,
            'virgin_wroughtaluminum_quality': virgin_wroughtaluminum_quality,
            
            'castaluminum_lowCu_min_scrap': df.iloc[17, 3:3+n_years].values,
            'castaluminum_lowCu_max_scrap': df.iloc[18, 3:3+n_years].values,
            'castaluminum_lowCu_efficiency': df.iloc[19, 3:3+n_years].values,
            'castaluminum_lowCu_scrap_recycling_rate': df.iloc[20, 3:3+n_years].values,
            'castaluminum_lowCu_threshold': castaluminum_lowCu_threshold,
            'virgin_castaluminum_lowCu_quality': virgin_castaluminum_lowCu_quality,

            'castaluminum_highCu_min_scrap': df.iloc[27, 3:3+n_years].values,
            'castaluminum_highCu_max_scrap': df.iloc[28, 3:3+n_years].values,
            'castaluminum_highCu_efficiency': df.iloc[29, 3:3+n_years].values,
            'castaluminum_highCu_scrap_recycling_rate': df.iloc[30, 3:3+n_years].values,
            'castaluminum_highCu_threshold': castaluminum_highCu_threshold,
            'virgin_castaluminum_highCu_quality': virgin_castaluminum_highCu_quality
        })
         
        aluminum_production.set_index('year', inplace=True)

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")

    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'Aluminum-Production': {e}")
        return None
    


    ###
    ###  (5) IMPORT 'Component-Production' DATA
    
    # Import production data from sheet 'Component-Production' including component production efficiencies and scrap production rates

    # component_production[year] = {...}

    try:
        df = pd.read_excel(file_path, sheet_name='Component-Production')

        component_production = pd.DataFrame({
            'year': range(start_year, end_year + 1),

            'flatsteel_efficiency': df.iloc[7, 3:3+n_years].values,
            'flatsteel_scrap_recycling_rate': df.iloc[8, 3:3+n_years].values,

            'longsteel_efficiency': df.iloc[10, 3:3+n_years].values,
            'longsteel_scrap_recycling_rate': df.iloc[11, 3:3+n_years].values,

            'wroughtaluminum_efficiency': df.iloc[13, 3:3+n_years].values,
            'wroughtaluminum_scrap_recycling_rate': df.iloc[14, 3:3+n_years].values,

            'castaluminum_lowCu_efficiency': df.iloc[16, 3:3+n_years].values,
            'castaluminum_lowCu_scrap_recycling_rate': df.iloc[17, 3:3+n_years].values,

            'castaluminum_highCu_efficiency': df.iloc[19, 3:3+n_years].values,
            'castaluminum_highCu_scrap_recycling_rate': df.iloc[20, 3:3+n_years].values
        })

        component_production.set_index('year', inplace=True)

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")

    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'Component-Production': {e}")
        return None



    ###
    ###  (6) IMPORT 'EoL' DATA
    ###

    # Import end-of-life vehicle data from sheet 'EoL' including systemic material loss rates (exports, unknown whereabouts), dismantling contents for material fractions, and PST recycling yields
    
    # eol_loss[year] = {...},
    # eol_dismantling[id, year] = {...},
    # eol_dismantling_recycling[year] = {...},
    # eol_pst[year] = {...}

    try:
        df = pd.read_excel(file_path, sheet_name='EoL')

        # Systemic losses:

        eol_loss = pd.DataFrame({
            'year': range(start_year, end_year + 1),

            'exports': df.iloc[7, 3:3+n_years].values,
            'unknown_whereabouts': df.iloc[8, 3:3+n_years].values
        })
        eol_loss.set_index('year', inplace=True)

        # PST recycling yields:

        steel_n_thresholds = steel_production['n_thresholds'].iloc[0]
        aluminum_n_thresholds = aluminum_production['n_thresholds'].iloc[0]
       
        steel_quality = df.iloc[13, 3:3+n_years].values
        mixedaluminum_quality = df.iloc[16, 3:3+n_years].values
        wroughtaluminum_quality = df.iloc[19, 3:3+n_years].values
        castaluminum_lowCu_quality = df.iloc[22, 3:3+n_years].values
        castaluminum_highCu_quality = df.iloc[25, 3:3+n_years].values

        if steel_n_thresholds == 1:
            steel_quality = [[steel_quality[i]] for i in range(len(steel_quality))]
        elif steel_n_thresholds > 1:
            for i in range(len(steel_quality)):
                value = steel_quality[i]
                steel_quality[i] = [float(x.strip()) for x in value.split(";")]

        if aluminum_n_thresholds == 1:
            mixedaluminum_quality = [[mixedaluminum_quality[i]] for i in range(len(mixedaluminum_quality))]
            wroughtaluminum_quality = [[wroughtaluminum_quality[i]] for i in range(len(wroughtaluminum_quality))]
            castaluminum_lowCu_quality = [[castaluminum_lowCu_quality[i]] for i in range(len(castaluminum_lowCu_quality))]
            castaluminum_highCu_quality = [[castaluminum_highCu_quality[i]] for i in range(len(castaluminum_highCu_quality))]
        elif aluminum_n_thresholds > 1:
            for i in range(len(wroughtaluminum_quality)):
                value = mixedaluminum_quality[i]
                mixedaluminum_quality[i] = [float(x.strip()) for x in value.split(";")]
                
                value = wroughtaluminum_quality[i]
                wroughtaluminum_quality[i] = [float(x.strip()) for x in value.split(";")]

                value = castaluminum_lowCu_quality[i]
                castaluminum_lowCu_quality[i] = [float(x.strip()) for x in value.split(";")]

                value = castaluminum_highCu_quality[i]
                castaluminum_highCu_quality[i] = [float(x.strip()) for x in value.split(";")]
                
        eol_pst = pd.DataFrame({
            'year': range(start_year, end_year + 1),

            'steel_yield': df.iloc[12, 3:3+n_years].values,
            'steel_contamination': steel_quality,

            'mixedaluminum_yield': df.iloc[15, 3:3+n_years].values,
            'mixedaluminum_contamination': mixedaluminum_quality,

            'wroughtaluminum_yield': df.iloc[18, 3:3+n_years].values,
            'wroughtaluminum_contamination': wroughtaluminum_quality,

            'castaluminum_lowCu_yield': df.iloc[21, 3:3+n_years].values,
            'castaluminum_lowCu_contamination': castaluminum_lowCu_quality,

            'castaluminum_highCu_yield': df.iloc[24, 3:3+n_years].values,
            'castaluminum_highCu_contamination': castaluminum_highCu_quality
        })
        eol_pst.set_index('year', inplace=True)

        mixed_positive = eol_pst['mixedaluminum_yield'] > 0
        specific_positive = (
            eol_pst['wroughtaluminum_yield'] +
            eol_pst['castaluminum_lowCu_yield'] +
            eol_pst['castaluminum_highCu_yield']
        ) > 0
        conflict = mixed_positive & specific_positive
        if conflict.any():
            raise Exception("ERROR: In PST recycling, mixed aluminum yield AND alloy-specific yields are set. Only mixed aluminum output OR alloy-specific outputs are allowed!")

        # Recycling yields of dismantled contents:

        flatsteel_quality = df.iloc[30, 3:3+n_years].values
        longsteel_quality = df.iloc[33, 3:3+n_years].values
        wroughtaluminum_quality = df.iloc[36, 3:3+n_years].values
        castaluminum_lowCu_quality = df.iloc[39, 3:3+n_years].values
        castaluminum_highCu_quality = df.iloc[42, 3:3+n_years].values

        if steel_n_thresholds == 1:
            flatsteel_quality = [[flatsteel_quality[i]] for i in range(len(flatsteel_quality))]
            longsteel_quality = [[longsteel_quality[i]] for i in range(len(longsteel_quality))]
        elif steel_n_thresholds > 1:
            for i in range(len(flatsteel_quality)):
                value = flatsteel_quality[i]
                flatsteel_quality[i] = [float(x.strip()) for x in value.split(";")]

                value = longsteel_quality[i]
                longsteel_quality[i] = [float(x.strip()) for x in value.split(";")]

        if aluminum_n_thresholds == 1:
            wroughtaluminum_quality = [[wroughtaluminum_quality[i]] for i in range(len(wroughtaluminum_quality))]
            castaluminum_lowCu_quality = [[castaluminum_lowCu_quality[i]] for i in range(len(castaluminum_lowCu_quality))]
            castaluminum_highCu_quality = [[castaluminum_highCu_quality[i]] for i in range(len(castaluminum_highCu_quality))]

        elif aluminum_n_thresholds > 1:
            for i in range(len(wroughtaluminum_quality)):
                value = wroughtaluminum_quality[i]
                wroughtaluminum_quality[i] = [float(x.strip()) for x in value.split(";")]
                castaluminum_lowCu_quality[i] = [float(x.strip()) for x in value.split(";")]
                castaluminum_highCu_quality[i] = [float(x.strip()) for x in value.split(";")]

        eol_dismantling_recycling = pd.DataFrame({
            'year': range(start_year, end_year + 1),

            'flatsteel_yield': df.iloc[29, 3:3+n_years].values,
            'flatsteel_contamination': flatsteel_quality,

            'longsteel_yield': df.iloc[32, 3:3+n_years].values,
            'longsteel_contamination': longsteel_quality,

            'wroughtaluminum_yield': df.iloc[35, 3:3+n_years].values,
            'wroughtaluminum_contamination': wroughtaluminum_quality,

            'castaluminum_lowCu_yield': df.iloc[38, 3:3+n_years].values,
            'castaluminum_lowCu_contamination': castaluminum_lowCu_quality,

            'castaluminum_highCu_yield': df.iloc[41, 3:3+n_years].values,
            'castaluminum_highCu_contamination': castaluminum_highCu_quality
        })
        eol_dismantling_recycling.set_index('year', inplace=True)

        # Dismantling contents:

        eol_dismantling = pd.DataFrame({
            'id': [i for i in range(1, n_vehicles + 1) for j in range(start_year, end_year + 1)],
            'year': [j for i in range(1, n_vehicles + 1) for j in range(start_year, end_year + 1)]
        })
        eol_dismantling.set_index(['id', 'year'], inplace=True)

        row = 47

        for i in range(1, n_vehicles + 1):
            for j in range(start_year, end_year + 1):
                eol_dismantling.loc[(i, j), 'flatsteel_content'] = df.iat[row, j-start_year+3]
                eol_dismantling.loc[(i, j), 'longsteel_content'] = df.iat[row+1, j-start_year+3]
                eol_dismantling.loc[(i, j), 'wroughtaluminum_content'] = df.iat[row+2, j-start_year+3]
                eol_dismantling.loc[(i, j), 'castaluminum_lowCu_content'] = df.iat[row+3, j-start_year+3]
                eol_dismantling.loc[(i, j), 'castaluminum_highCu_content'] = df.iat[row+4, j-start_year+3]

            row += 7

    except FileNotFoundError:
        raise Exception(f"ERROR: The input file '{file_path}' was not found.")

    except Exception as e:
        print(f"(!) An error occurred while importing data from sheet 'EoL': {e}")
        return None



    ###
    ###  (7) SAVE TMP FILE
    ###
    
    # Save all imported data in a tmp file for quick checks of the imported data

    tmp = {
        'vehicles_names': vehicles_names,
        'vehicles_data': vehicles_data,
        'registrations': registrations,
        'steel_production': steel_production,
        'aluminum_production': aluminum_production,
        'component_production': component_production,
        'eol_loss': eol_loss,
        'eol_dismantling': eol_dismantling,
        'eol_dismantling_recycling': eol_dismantling_recycling,
        'eol_pst': eol_pst
    }



    print('   import done.')

    return start_year, end_year, n_years, n_vehicles, vehicles_names, vehicles_data, cagr, n_init_years, registrations, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, steel_production, aluminum_production, component_production, tmp