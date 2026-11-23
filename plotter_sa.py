####
#
# CASAsim
# Plot Module for Sensitivity Analysis Results
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
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FormatStrFormatter



def plot_sa_data(export_sa_path, set_years, PLOTTER_START_YEAR, PLOTTER_END_YEAR, material_demand, material_supply, material_use, closedloop, steel_production, aluminum_production, TARGET_YEARS, sa_closedloop_plus, sa_closedloop_minus, sa_materialuse_plus, sa_materialuse_minus, sa_titles, sa_tmp_plus, sa_tmp_minus, SENSITIVITY, color, n_sa_iterations, sa_closedloop_max, sa_closedloop_min, sa_material_use_max, sa_material_use_min):

    set_years = range(PLOTTER_START_YEAR, PLOTTER_END_YEAR + 1)

    plots_df = pd.DataFrame()



    ###
    ###  (1.1) MATERIAL-SPECIFIC RECYCLED CONTENT CLOSED LOOP RATES
    ###

    name = 'sa_recycled-content-rates.pdf'

    plt.figure(figsize=(8, 6))


    # PLOT CLOSED-LOOP RATES BASED ON INPUT DATA

    flatsteel = [closedloop.loc[j, 'flatsteel_recycledcontent'] for j in set_years]
    longsteel = [closedloop.loc[j, 'longsteel_recycledcontent'] for j in set_years]
    wroughtaluminum = [closedloop.loc[j, 'wroughtaluminum_recycledcontent'] for j in set_years]
    castaluminum_lowCu = [closedloop.loc[j, 'castaluminum_lowCu_recycledcontent'] for j in set_years]
    castaluminum_highCu = [closedloop.loc[j, 'castaluminum_highCu_recycledcontent'] for j in set_years]
    
    maximum = max(max(flatsteel), max(longsteel), max(wroughtaluminum), max(castaluminum_lowCu), max(castaluminum_highCu))

    plt.plot(set_years, flatsteel, color=tuple(color['flatsteel']), label='Flat steel')
    plt.plot(set_years, longsteel, color=tuple(color['longsteel']), label='Long steel')
    plt.plot(set_years, castaluminum_lowCu, color=tuple(color['castaluminum_lowCu']), label='Low-Cu cast aluminum')
    plt.plot(set_years, castaluminum_highCu, color=tuple(color['castaluminum_highCu']), label='High-Cu cast aluminum')
    plt.plot(set_years, wroughtaluminum, color=tuple(color['wroughtaluminum']), label='Wrought aluminum')
    

    # PLOT CLOSED-LOOP RATE AREAS BASED ON SENSITIVITY ANALYSIS RESULTS

    parameter = ['flatsteel_recycledcontent', 'longsteel_recycledcontent', 'castaluminum_lowCu_recycledcontent', 'castaluminum_highCu_recycledcontent', 'wroughtaluminum_recycledcontent']
    parameter_color = ['flatsteel', 'longsteel', 'castaluminum_lowCu', 'castaluminum_highCu', 'wroughtaluminum']
    parameter_label = ['Flat steel', 'Long steel', 'Low-Cu cast aluminum', 'High-Cu cast aluminum', 'Wrought aluminum']

    p_idx = 0
    maximum = 0

    for p in parameter:
    
        _max = sa_closedloop_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, p].tolist()
        _min = sa_closedloop_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, p].tolist()
        maximum = max(maximum, max(_max), max(_min))

        plt.fill_between(set_years, _max, _min, alpha=0.2, color=color[parameter_color[p_idx]])

        p_idx += 1


    # PLOT SETTINGS

    plt.title('Closed-loop recycled content rates [%]')
    plt.gca().set_ylim(0, maximum + 2)
    plt.gca().set_xlim(set_years[0], set_years[-1])
    plt.legend()

    plt.savefig(f'{export_sa_path}{name}', bbox_inches='tight')

    #plt.show()
    plt.close()

    print(f'   {name} exported.')



    ###
    ###  (1.2) TOTAL RECYCLED CONTENT CLOSED LOOP RATES
    ###

    name = 'sa_recycled-content-rates-total.pdf'

    plt.figure(figsize=(8, 6))


    # PLOT CLOSED-LOOP RATES BASED ON INPUT DATA

    total_steel = [closedloop.loc[j, 'steel_recycledcontent'] for j in set_years]
    total_aluminum = [closedloop.loc[j, 'aluminum_recycledcontent'] for j in set_years]
    #total = [closedloop.loc[j, 'total_recycledcontent'] for j in set_years]

    maximum = max(max(total_steel), max(total_aluminum))

    plt.plot(set_years, total_steel, color=tuple(color['steel']), linestyle='-', label='Steel')
    plt.plot(set_years, total_aluminum, color=tuple(color['aluminum']), linestyle='-', label='Aluminum')
    #plt.plot(set_years, total, color=tuple(color['total']), linestyle='-', label='Total')

    # Save plot data:

    plots_df['steel_recycledcontent'] = total_steel
    plots_df['aluminum_recycledcontent'] = total_aluminum


    # PLOT CLOSED-LOOP RATE AREAS BASED ON SENSITIVITY ANALYSIS RESULTS

    parameter = ['steel_recycledcontent', 'aluminum_recycledcontent']
    parameter_color = ['steel', 'aluminum']
    parameter_label = ['Steel', 'Aluminum']

    p_idx = 0
    maximum = 0

    for p in parameter:
    
        _max = sa_closedloop_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, p].tolist()
        _min = sa_closedloop_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, p].tolist()
        maximum = max(maximum, max(_max), max(_min))

        plt.fill_between(set_years, _max, _min, alpha=0.2, color=color[parameter_color[p_idx]])

        p_idx += 1

        # Save plot data:

        plots_df[f'{p}_min'] = _min
        plots_df[f'{p}_max'] = _max


    # PLOT SETTINGS

    plt.title('Closed-loop recycled content rates [%]')
    plt.gca().set_ylim(0, maximum + 2)
    plt.gca().set_xlim(set_years[0], set_years[-1])
    plt.legend()

    plt.savefig(f'{export_sa_path}{name}', bbox_inches='tight')

    #plt.show()
    plt.close()

    print(f'   {name} exported.')



    ###
    ###  (2.1) MATERIAL-SPECIFIC POST-CONSUMER CLOSED LOOP RATES
    ###

    name = 'sa_recycled-content-PoC-rates.pdf'

    plt.figure(figsize=(8, 6))


    # PLOT CLOSED-LOOP RATES BASED ON INPUT DATA

    flatsteel = [closedloop.loc[j, 'flatsteel_postconsumer'] for j in set_years]
    longsteel = [closedloop.loc[j, 'longsteel_postconsumer'] for j in set_years]
    wroughtaluminum = [closedloop.loc[j, 'wroughtaluminum_postconsumer'] for j in set_years]
    castaluminum_lowCu = [closedloop.loc[j, 'castaluminum_lowCu_postconsumer'] for j in set_years]
    castaluminum_highCu = [closedloop.loc[j, 'castaluminum_highCu_postconsumer'] for j in set_years]
   
    maximum = max(max(flatsteel), max(longsteel), max(wroughtaluminum), max(castaluminum_lowCu), max(castaluminum_highCu))

    plt.plot(set_years, flatsteel, color=tuple(color['flatsteel']), label='Flat steel')
    plt.plot(set_years, longsteel, color=tuple(color['longsteel']), label='Long steel')
    plt.plot(set_years, castaluminum_lowCu, color=tuple(color['castaluminum_lowCu']), label='Low-Cu cast aluminum')
    plt.plot(set_years, castaluminum_highCu, color=tuple(color['castaluminum_highCu']), label='High-Cu cast aluminum')
    plt.plot(set_years, wroughtaluminum, color=tuple(color['wroughtaluminum']), label='Wrought aluminum')
   
    
    # PLOT CLOSED-LOOP RATE AREAS BASED ON SENSITIVITY ANALYSIS RESULTS

    parameter = ['flatsteel_postconsumer', 'longsteel_postconsumer', 'castaluminum_lowCu_postconsumer', 'castaluminum_highCu_postconsumer', 'wroughtaluminum_postconsumer']
    parameter_color = ['flatsteel', 'longsteel', 'castaluminum_lowCu', 'castaluminum_highCu','wroughtaluminum']
    parameter_label = ['Flat steel', 'Long steel', 'Low-Cu cast aluminum', 'High-Cu cast aluminum', 'Wrought aluminum']

    p_idx = 0
    maximum = 0

    for p in parameter:
    
        _max = sa_closedloop_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, p].tolist()
        _min = sa_closedloop_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, p].tolist()
        maximum = max(maximum, max(_max), max(_min))

        plt.fill_between(set_years, _max, _min, alpha=0.2, color=color[parameter_color[p_idx]])

        p_idx += 1


    # PLOT SETTINGS

    plt.title('Post-consumer closed-loop recycled content rates [%]')
    plt.gca().set_ylim(0, maximum + 2)
    plt.gca().set_xlim(set_years[0], set_years[-1])
    plt.legend()

    plt.savefig(f'{export_sa_path}{name}', bbox_inches='tight')

    #plt.show()
    plt.close()

    print(f'   {name} exported.')



    ###
    ###  (2.2) TOTAL POST-CONSUMER CLOSED LOOP RATES
    ###

    name = 'sa_recycled-content-PoC-rates-total.pdf'

    plt.figure(figsize=(8, 6))


    # PLOT CLOSED-LOOP RATES BASED ON INPUT DATA

    total_steel = [closedloop.loc[j, 'steel_postconsumer'] for j in set_years]
    total_aluminum = [closedloop.loc[j, 'aluminum_postconsumer'] for j in set_years]
    #total = [closedloop.loc[j, 'total_recycledcontent'] for j in set_years]

    maximum = max(max(total_steel), max(total_aluminum))

    plt.plot(set_years, total_steel, color=tuple(color['steel']), linestyle='-', label='Steel')
    plt.plot(set_years, total_aluminum, color=tuple(color['aluminum']), linestyle='-', label='Aluminum')
    #plt.plot(set_years, total, color=tuple(color['total']), linestyle='-', label='Total')

    # Save plot data:

    plots_df['steel_postconsumer_recycledcontent'] = total_steel
    plots_df['aluminum_postconsumer_recycledcontent'] = total_aluminum

    # PLOT CLOSED-LOOP RATE AREAS BASED ON SENSITIVITY ANALYSIS RESULTS

    parameter = ['steel_postconsumer', 'aluminum_postconsumer']
    parameter_color = ['steel', 'aluminum']
    parameter_label = ['Steel', 'Aluminum']

    p_idx = 0
    maximum = 0

    for p in parameter:
    
        _max = sa_closedloop_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, p].tolist()
        _min = sa_closedloop_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, p].tolist()
        maximum = max(maximum, max(_max), max(_min))

        plt.fill_between(set_years, _max, _min, alpha=0.2, color=color[parameter_color[p_idx]])

        p_idx += 1

        # Save plot data:

        plots_df[f'{p}_recycledcontent_min'] = _min
        plots_df[f'{p}_recycledcontent_max'] = _max


    # PLOT SETTINGS

    plt.title('Post-consumer closed-loop recycled content rates [%]')
    plt.gca().set_ylim(0, maximum + 2)
    plt.gca().set_xlim(set_years[0], set_years[-1])
    plt.legend()

    plt.savefig(f'{export_sa_path}{name}', bbox_inches='tight')

    #plt.show()
    plt.close()

    print(f'   {name} exported.')



    ###
    ###  (3) SCRAP ALLOCATION
    ###

    SCALE_VALUE = 1e9
    SCALE_UNIT = 'Mt'


    # (3.1) STEEL

    name = 'sa_scrap-allocation-steel.pdf'

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(24, 5))
    y_max = 0


    # TOTAL SCRAP ALLOCATION

    # Maximum feasible scrap input based on input data:

    y2 = [(
        (material_demand.loc[j, 'flatsteel_production_s1'] * steel_production.loc[j, 's1_max_scrap'] / 100) +
        (material_demand.loc[j, 'flatsteel_production_s2'] * steel_production.loc[j, 's2_max_scrap'] / 100) + 
        (material_demand.loc[j, 'flatsteel_production_s3'] * steel_production.loc[j, 's3_max_scrap'] / 100))        
        / SCALE_VALUE for j in set_years]

    ax1.plot(set_years, y2, color=tuple(color['flatsteel']), linestyle='--', label='Max. feasible scrap in flat steel production')

    y3 = [(
        (material_demand.loc[j, 'longsteel_production_s1'] * steel_production.loc[j, 's1_max_scrap'] / 100) +
        (material_demand.loc[j, 'longsteel_production_s2'] * steel_production.loc[j, 's2_max_scrap'] / 100) + 
        (material_demand.loc[j, 'longsteel_production_s3'] * steel_production.loc[j, 's3_max_scrap'] / 100))        
        / SCALE_VALUE for j in set_years]

    ax1.plot(set_years, y3, color=tuple(color['longsteel']), linestyle='--', label='Max. feasible scrap in long steel production')

    y_max = max(y_max, max(y2), max(y3))

    # Calculate min and max values for annual maximum feasible scrap input:

    parameter = ['flatsteel', 'longsteel']
    baseline = [y2, y3]
    p_idx = 0

    for p in parameter:

        _max = baseline[p_idx].copy()
        _min = baseline[p_idx].copy()

        for j in set_years:
            _idx = j - PLOTTER_START_YEAR

            for sa_data in sa_tmp_plus.values():

                # sa_tmp_plus/minus = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]
                _material_demand = sa_data[7].copy()
                _steel_production = sa_data[18].copy()

                _value = (
                    (_material_demand.loc[j, f'{p}_production_s1'] * _steel_production.loc[j, 's1_max_scrap'] / 100) +
                    (_material_demand.loc[j, f'{p}_production_s2'] * _steel_production.loc[j, 's2_max_scrap'] / 100) +
                    (_material_demand.loc[j, f'{p}_production_s3'] * _steel_production.loc[j, 's3_max_scrap'] / 100)
                ) / SCALE_VALUE

                _max[_idx] = max(_max[_idx], _value)
                _min[_idx] = min(_min[_idx], _value)

            for sa_data in sa_tmp_minus.values():

                _material_demand = sa_data[7].copy()
                _steel_production = sa_data[18].copy()

                _value = (
                    (_material_demand.loc[j, f'{p}_production_s1'] * _steel_production.loc[j, 's1_max_scrap'] / 100) +
                    (_material_demand.loc[j, f'{p}_production_s2'] * _steel_production.loc[j, 's2_max_scrap'] / 100) +
                    (_material_demand.loc[j, f'{p}_production_s3'] * _steel_production.loc[j, 's3_max_scrap'] / 100)
                ) / SCALE_VALUE

                _max[_idx] = max(_max[_idx], _value)
                _min[_idx] = min(_min[_idx], _value)

        ax1.fill_between(set_years, _max, _min, alpha=0.2, color=color[f'{p}'])

        y_max = max(y_max, max(_max))

        p_idx += 1

        # Save plot data:

        plots_df[f'{p}_max_scrap_min'] = _min
        plots_df[f'{p}_max_scrap_max'] = _max

    # Material use based on input data:

    y4 = [(material_use.loc[j, 'flatsteel_internal'] + material_use.loc[j, 'flatsteel_preconsumer'] + material_use.loc[j, 'flatsteel_postconsumer']) / SCALE_VALUE for j in set_years]
    ax1.plot(set_years, y4, color=tuple(color['flatsteel']), label='Scrap input in flat steel production')

    y5 = [(material_use.loc[j, 'longsteel_internal'] + material_use.loc[j, 'longsteel_preconsumer'] + material_use.loc[j, 'longsteel_postconsumer']) / SCALE_VALUE for j in set_years]
    ax1.plot(set_years, y5, color=tuple(color['longsteel']), label='Scrap input in long steel production')

    y_max = max(y_max, max(y4), max(y5))

    # Calculate min and max values for annual material use:

    parameter = ['flatsteel', 'longsteel']
    p_idx = 0

    for p in parameter:
    
        _max = (
            sa_material_use_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_internal'] +
            sa_material_use_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_preconsumer'] +
            sa_material_use_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_postconsumer']
        ) / SCALE_VALUE
        _max = _max.tolist()

        _min = (
            sa_material_use_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_internal'] +
            sa_material_use_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_preconsumer'] +
            sa_material_use_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_postconsumer']
        ) / SCALE_VALUE
        _min = _min.tolist()

        ax1.fill_between(set_years, _max, _min, alpha=0.2, color=color[f'{p}'])

        y_max = max(y_max, max(_max))

        p_idx += 1

        # Save plot data:

        plots_df[f'{p}_scrap_input_min'] = _min
        plots_df[f'{p}_scrap_input_max'] = _max

    # Plot settings:

    ax1.legend(loc='upper left')
    ax1.set_title(f'Total steel scrap [{SCALE_UNIT}]')
    ax1.set_xlim(set_years[0], set_years[-1])
    ax1.set_ylim(0, y_max)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Save plot data:

    plots_df['flatsteel_max_scrap'] = y2
    plots_df['longsteel_max_scrap'] = y3
    plots_df['flatsteel_scrap_input'] = y4
    plots_df['longsteel_scrap_input'] = y5


    # INTERNAL, PRE-CONSUMER, AND POST-CONSUMER SCRAP

    scrap = ['internal', 'preconsumer', 'postconsumer']
    scrap_label = ['Internal', 'Pre-consumer', 'Post-consumer']
    scrap_ax = [ax2, ax3, ax4]

    s_idx = 0
    y_max = 0

    for s in scrap:

        # Scrap use based on input data:

        y2 = [material_use.loc[j, f'longsteel_{s}'] / SCALE_VALUE for j in set_years]
        y3 = [material_use.loc[j, f'flatsteel_{s}'] / SCALE_VALUE for j in set_years]

        scrap_ax[s_idx].plot(set_years, y2, color=tuple(color['longsteel']), label='Scrap to long steel production')
        scrap_ax[s_idx].plot(set_years, y3, color=tuple(color['flatsteel']), label='Scrap to flat steel production')

        # Calculate min and max values for annual scrap use:

        parameter = ['longsteel', 'flatsteel']
        p_idx = 0

        for p in parameter:

            _max = sa_material_use_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_{s}'] / SCALE_VALUE
            _max = _max.tolist()

            _min = sa_material_use_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_{s}'] / SCALE_VALUE
            _min = _min.tolist()

            scrap_ax[s_idx].fill_between(set_years, _max, _min, alpha=0.2, color=color[f'{p}'])

            y_max = max(y_max, max(_max))

            p_idx += 1

        # Scrap supply based on input data:

        if s == 'postconsumer':
            y4 = [material_supply.loc[j, f'steel_{s}'] / SCALE_VALUE for j in set_years]

            scrap_ax[s_idx].plot(set_years, y4, color=tuple(color['steel']), linestyle='--', label='Steel scrap supply')

            y_max = max(y_max,max(y4))

            # Calculate min and max values for annual scrap use:

            parameter = ['steel']
            baseline = [y4]
            p_idx = 0

            for p in parameter:

                _max = baseline[p_idx].copy()
                _min = baseline[p_idx].copy()

                for j in set_years:
                    _idx = j - PLOTTER_START_YEAR

                    for sa_data in sa_tmp_plus.values():

                        # sa_tmp_plus/minus = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]
                        _material_supply = sa_data[8].copy()

                        _value = _material_supply.loc[j, f'{p}_{s}'] / SCALE_VALUE

                        _max[_idx] = max(_max[_idx], _value)
                        _min[_idx] = min(_min[_idx], _value)

                    for sa_data in sa_tmp_minus.values():

                        _material_supply = sa_data[8].copy()

                        _value = _material_supply.loc[j, f'{p}_{s}'] / SCALE_VALUE

                        _max[_idx] = max(_max[_idx], _value)
                        _min[_idx] = min(_min[_idx], _value)

                scrap_ax[s_idx].fill_between(set_years, _max, _min, alpha=0.2, color=color[f'{p}'])

                y_max = max(y_max, max(_max))

                p_idx += 1

            y_max = max(y_max, max(y2), max(y3), max(y4))

        else:
            y4 = [material_supply.loc[j, f'flatsteel_{s}'] / SCALE_VALUE for j in set_years]
            y5 = [material_supply.loc[j, f'longsteel_{s}'] / SCALE_VALUE for j in set_years]

            scrap_ax[s_idx].plot(set_years, y4, color=tuple(color['flatsteel']), linestyle='--', label='Flat steel scrap supply')
            scrap_ax[s_idx].plot(set_years, y5, color=tuple(color['longsteel']), linestyle='--', label='Long steel scrap supply')

            # Calculate min and max values for annual scrap use:

            parameter = ['flatsteel', 'longsteel']
            baseline = [y4, y5]
            p_idx = 0

            for p in parameter:

                _max = baseline[p_idx].copy()
                _min = baseline[p_idx].copy()

                for j in set_years:
                    _idx = j - PLOTTER_START_YEAR

                    for sa_data in sa_tmp_plus.values():

                        # sa_tmp_plus/minus = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]
                        _material_supply = sa_data[8].copy()

                        _value = _material_supply.loc[j, f'{p}_{s}'] / SCALE_VALUE

                        _max[_idx] = max(_max[_idx], _value)
                        _min[_idx] = min(_min[_idx], _value)

                    for sa_data in sa_tmp_minus.values():

                        _material_supply = sa_data[8].copy()

                        _value = _material_supply.loc[j, f'{p}_{s}'] / SCALE_VALUE

                        _max[_idx] = max(_max[_idx], _value)
                        _min[_idx] = min(_min[_idx], _value)

                scrap_ax[s_idx].fill_between(set_years, _max, _min, alpha=0.2, color=color[f'{p}'])

                y_max = max(y_max, max(_max))

                p_idx += 1

            y_max = max(y_max, max(y2), max(y3), max(y4), max(y5))

        # Plot settings:

        scrap_ax[s_idx].legend(loc='upper left')
        scrap_ax[s_idx].set_title(f'{scrap_label[s_idx]} steel scrap [{SCALE_UNIT}]')
        scrap_ax[s_idx].set_xlim(set_years[0], set_years[-1])

        s_idx += 1

    # Set y-limits:

    ax2.set_ylim(0, y_max)
    ax3.set_ylim(0, y_max)
    ax4.set_ylim(0, y_max)
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax3.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax4.yaxis.set_major_locator(MaxNLocator(integer=True))


    plt.savefig(f'{export_sa_path}{name}', bbox_inches='tight')
    plt.close()
    print(f'   {name} exported.')


    # (3.2) ALUMINUM

    name = 'sa_scrap-allocation-aluminum.pdf'

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(24, 5))
    y_max = 0


    # TOTAL SCRAP ALLOCATION

    # Maximum feasible scrap input based on input data:

    y2 = [(material_demand.loc[j, 'wroughtaluminum_production'] * aluminum_production.loc[j, 'wroughtaluminum_max_scrap'] / 100) / SCALE_VALUE for j in set_years]
    ax1.plot(set_years, y2, color=tuple(color['wroughtaluminum']), linestyle='--', label='Max. feasible scrap in wrought Al production')

    y3 = [(material_demand.loc[j, 'castaluminum_lowCu_production'] * aluminum_production.loc[j, 'castaluminum_lowCu_max_scrap'] / 100) / SCALE_VALUE for j in set_years]
    ax1.plot(set_years, y3, color=tuple(color['castaluminum_lowCu']), linestyle='--', label='Max. feasible scrap in low-Cu cast Al production')

    y4 = [(material_demand.loc[j, 'castaluminum_highCu_production'] * aluminum_production.loc[j, 'castaluminum_highCu_max_scrap'] / 100) / SCALE_VALUE for j in set_years]
    ax1.plot(set_years, y4, color=tuple(color['castaluminum_highCu']), linestyle='--', label='Max. feasible scrap in high-Cu cast Al production')

    y_max = max(y_max, max(y2), max(y3), max(y4))

    # Calculate min and max values for annual maximum feasible scrap input:

    parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
    baseline = [y2, y3, y4]
    p_idx = 0

    for p in parameter:

        _max = baseline[p_idx].copy()
        _min = baseline[p_idx].copy()

        for j in set_years:
            _idx = j - PLOTTER_START_YEAR

            for sa_data in sa_tmp_plus.values():

                # sa_tmp_plus/minus = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]
                _material_demand = sa_data[7].copy()
                _aluminum_production = sa_data[19].copy()

                _value = (_material_demand.loc[j, f'{p}_production'] * _aluminum_production.loc[j, f'{p}_max_scrap'] / 100) / SCALE_VALUE

                _max[_idx] = max(_max[_idx], _value)
                _min[_idx] = min(_min[_idx], _value)

            for sa_data in sa_tmp_minus.values():

                _material_demand = sa_data[7].copy()
                _aluminum_production = sa_data[19].copy()

                _value = (_material_demand.loc[j, f'{p}_production'] * _aluminum_production.loc[j, f'{p}_max_scrap'] / 100) / SCALE_VALUE

                _max[_idx] = max(_max[_idx], _value)
                _min[_idx] = min(_min[_idx], _value)

        ax1.fill_between(set_years, _max, _min, alpha=0.2, color=color[f'{p}'])

        y_max = max(y_max, max(_max))

        p_idx += 1

        # Save plot data:

        plots_df[f'{p}_max_scrap_min'] = _min
        plots_df[f'{p}_max_scrap_max'] = _max

    # Material use based on input data:

    y5 = [(material_use.loc[j, 'wroughtaluminum_internal'] + material_use.loc[j, 'wroughtaluminum_preconsumer'] + material_use.loc[j, 'wroughtaluminum_postconsumer']) / SCALE_VALUE for j in set_years]
    ax1.plot(set_years, y5, color=tuple(color['wroughtaluminum']), label='Scrap input in wrought Al production')

    y6 = [(material_use.loc[j, 'castaluminum_lowCu_internal'] + material_use.loc[j, 'castaluminum_lowCu_preconsumer'] + material_use.loc[j, 'castaluminum_lowCu_postconsumer']) / SCALE_VALUE for j in set_years]
    ax1.plot(set_years, y6, color=tuple(color['castaluminum_lowCu']), label='Scrap input in low-Cu cast Al production')
    
    y7 = [(material_use.loc[j, 'castaluminum_highCu_internal'] + material_use.loc[j, 'castaluminum_highCu_preconsumer'] + material_use.loc[j, 'castaluminum_highCu_postconsumer']) / SCALE_VALUE for j in set_years]
    ax1.plot(set_years, y7, color=tuple(color['castaluminum_highCu']), label='Scrap input in high-Cu cast Al production')
    
    y_max = max(y_max, max(y5), max(y6), max(y7))

    # Calculate min and max values for annual material use:

    parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
    p_idx = 0

    for p in parameter:
    
        _max = (
            sa_material_use_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_internal'] +
            sa_material_use_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_preconsumer'] +
            sa_material_use_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_postconsumer']
        ) / SCALE_VALUE
        _max = _max.tolist()

        _min = (
            sa_material_use_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_internal'] +
            sa_material_use_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_preconsumer'] +
            sa_material_use_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_postconsumer']
        ) / SCALE_VALUE
        _min = _min.tolist()

        ax1.fill_between(set_years, _max, _min, alpha=0.2, color=color[f'{p}'])

        y_max = max(y_max, max(_max))

        p_idx += 1

        # Save plot data:

        plots_df[f'{p}_scrap_input_min'] = _min
        plots_df[f'{p}_scrap_input_max'] = _max

    # Plot settings:

    ax1.legend(loc='upper left')
    ax1.set_title(f'Total aluminum (Al) scrap [{SCALE_UNIT}]')
    ax1.set_xlim(set_years[0], set_years[-1])
    ax1.set_ylim(0, y_max)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Save plot data:

    plots_df['wroughtaluminum_max_scrap'] = y2
    plots_df['castaluminum_lowCu_max_scrap'] = y3
    plots_df['castaluminum_highCu_max_scrap'] = y4
    plots_df['wroughtaluminum_scrap_input'] = y5
    plots_df['castaluminum_lowCu_scrap_input'] = y6
    plots_df['castaluminum_highCu_scrap_input'] = y7


    # INTERNAL, PRE-CONSUMER, AND POST-CONSUMER SCRAP

    scrap = ['internal', 'preconsumer', 'postconsumer']
    scrap_label = ['Internal', 'Pre-consumer', 'Post-consumer']
    scrap_ax = [ax2, ax3, ax4]

    s_idx = 0
    y_max = 0

    for s in scrap:

        # Scrap use based on input data:
        
        y2 = [material_use.loc[j, f'wroughtaluminum_{s}'] / SCALE_VALUE for j in set_years]
        y3 = [material_use.loc[j, f'castaluminum_lowCu_{s}'] / SCALE_VALUE for j in set_years]
        y4 = [material_use.loc[j, f'castaluminum_highCu_{s}'] / SCALE_VALUE for j in set_years]

        scrap_ax[s_idx].plot(set_years, y2, color=tuple(color['wroughtaluminum']), label='Scrap to wrought aluminum production')
        scrap_ax[s_idx].plot(set_years, y3, color=tuple(color['castaluminum_lowCu']), label='Scrap to low-Cu cast aluminum production')
        scrap_ax[s_idx].plot(set_years, y4, color=tuple(color['castaluminum_highCu']), label='Scrap to high-Cu cast aluminum production')

        # Calculate min and max values for annual scrap use:

        parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
        p_idx = 0

        for p in parameter:

            _max = sa_material_use_max.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_{s}'] / SCALE_VALUE
            _max = _max.tolist()

            _min = sa_material_use_min.loc[PLOTTER_START_YEAR:PLOTTER_END_YEAR, f'{p}_{s}'] / SCALE_VALUE
            _min = _min.tolist()

            scrap_ax[s_idx].fill_between(set_years, _max, _min, alpha=0.2, color=color[f'{p}'])

            y_max = max(y_max, max(_max))

            p_idx += 1

        # Scrap supply based on input data:

        y5 = [material_supply.loc[j, f'wroughtaluminum_{s}'] / SCALE_VALUE for j in set_years]
        y6 = [material_supply.loc[j, f'castaluminum_lowCu_{s}'] / SCALE_VALUE for j in set_years]
        y7 = [material_supply.loc[j, f'castaluminum_highCu_{s}'] / SCALE_VALUE for j in set_years]

        scrap_ax[s_idx].plot(set_years, y5, color=tuple(color['wroughtaluminum']), linestyle='--', label='Wrought Al scrap supply')
        scrap_ax[s_idx].plot(set_years, y6, color=tuple(color['castaluminum_lowCu']), linestyle='--', label='Low-Cu cast Al scrap supply')
        scrap_ax[s_idx].plot(set_years, y7, color=tuple(color['castaluminum_highCu']), linestyle='--', label='High-Cu cast Al scrap supply')

        if s == 'postconsumer':
            y8 = [material_supply.loc[j, f'mixedaluminum_{s}'] / SCALE_VALUE for j in set_years]
            scrap_ax[s_idx].plot(set_years, y8, color=tuple(color['mixedaluminum']), linestyle='--', label='Mixed Al scrap supply')
            y_max = max(y_max, max(y8))

        # Calculate min and max values for annual scrap use:

        if s == 'postconsumer':
            parameter = ['mixedaluminum', 'wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
            baseline = [y8, y5, y6, y7]

        else:
            parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
            baseline = [y5, y6, y7]

        p_idx = 0

        for p in parameter:

            _max = baseline[p_idx].copy()
            _min = baseline[p_idx].copy()

            for j in set_years:
                _idx = j - PLOTTER_START_YEAR

                for sa_data in sa_tmp_plus.values():

                    # sa_tmp_plus/minus = [_vehicles_data, cagr, _registrations, _fleet_detail, _fleet, _eol_veh, _eol, _material_demand, _material_supply, _material_use, _material_quality, _objective, _closedloop, eol_loss, eol_dismantling, eol_dismantling_recycling, eol_pst, component_production, steel_production, aluminum_production]
                    _material_supply = sa_data[8].copy()

                    _value = _material_supply.loc[j, f'{p}_{s}'] / SCALE_VALUE

                    _max[_idx] = max(_max[_idx], _value)
                    _min[_idx] = min(_min[_idx], _value)

                for sa_data in sa_tmp_minus.values():

                    _material_supply = sa_data[8].copy()

                    _value = _material_supply.loc[j, f'{p}_{s}'] / SCALE_VALUE

                    _max[_idx] = max(_max[_idx], _value)
                    _min[_idx] = min(_min[_idx], _value)

            scrap_ax[s_idx].fill_between(set_years, _max, _min, alpha=0.2, color=color[f'{p}'])

            y_max = max(y_max, max(_max))

            p_idx += 1

        # Plot settings:

        scrap_ax[s_idx].legend(loc='upper left')
        scrap_ax[s_idx].set_title(f'{scrap_label[s_idx]} aluminum (Al) scrap [{SCALE_UNIT}]')
        scrap_ax[s_idx].set_xlim(set_years[0], set_years[-1])

        y_max = max(y_max, max(y2), max(y3), max(y4), max(y5), max(y6), max(y7))

        s_idx += 1

    # Set y-limits:

    ax2.set_ylim(0, y_max)
    ax3.set_ylim(0, y_max)
    ax4.set_ylim(0, y_max)
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax3.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax4.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))


    plt.savefig(f'{export_sa_path}{name}', bbox_inches='tight')
    plt.close()
    print(f'   {name} exported.')



    ###
    ###  (4) TORNADO PLOTS FOR CLOSED-LOOP RATES
    ###

    # a) infeasible solutions:
    _sa_keys = list(sa_tmp_plus.keys())
    _infeasible_plus_flags  = [sa_tmp_plus[name][11] < 0 for name in _sa_keys]
    _infeasible_minus_flags = [sa_tmp_minus[name][11] < 0 for name in _sa_keys]

    # b) contamination parameters with base value 0:
    _dismantling_contamination_params = {
        'flatsteel_contamination', 'longsteel_contamination',
        'wroughtaluminum_contamination', 'castaluminum_lowCu_contamination',
        'castaluminum_highCu_contamination'
    }
    _pst_contamination_params = {
        'steel_contamination', 'mixedaluminum_contamination',
        'wroughtaluminum_contamination', 'castaluminum_lowCu_contamination',
        'castaluminum_highCu_contamination'
    }

    # (for minus runs: modified = value * (1 - sensitivity), so if base = 0 the stored value is also 0)
    _zero_base_flags = []
    for name in _sa_keys:
        is_zero_base = False
        if name.startswith('dismantling_recycling_') and 'contamination' in name:
            remainder = name[len('dismantling_recycling_'):]
            parts = remainder.rsplit('_', 1)
            if len(parts) == 2 and parts[0] in _dismantling_contamination_params and parts[1].isdigit():
                p, i = parts[0], int(parts[1]) - 1
                minus_data = sa_tmp_minus[name][15]  # _eol_dismantling_recycling
                if all(minus_data.loc[t, p][i] == 0 for t in set_years):
                    is_zero_base = True
        elif name.startswith('pst_recycling_') and 'contamination' in name:
            remainder = name[len('pst_recycling_'):]
            parts = remainder.rsplit('_', 1)
            if len(parts) == 2 and parts[0] in _pst_contamination_params and parts[1].isdigit():
                p, i = parts[0], int(parts[1]) - 1
                minus_data = sa_tmp_minus[name][16]  # _eol_pst
                if all(minus_data.loc[t, p][i] == 0 for t in set_years):
                    is_zero_base = True
        _zero_base_flags.append(is_zero_base)

    parameter = ['flatsteel_recycledcontent', 'longsteel_recycledcontent', 'castaluminum_lowCu_recycledcontent', 'castaluminum_highCu_recycledcontent', 'wroughtaluminum_recycledcontent', 'steel_recycledcontent', 'aluminum_recycledcontent']
    parameter_short = ['flatsteel', 'longsteel', 'castaluminum_lowCu', 'castaluminum_highCu', 'wroughtaluminum', 'steel', 'aluminum']
    parameter_label = ['flat steel', 'long steel', 'low-Cu cast aluminum', 'high-Cu cast aluminum', 'wrought aluminum', 'total steel', 'total aluminum']

    for year in TARGET_YEARS:

        n_labels = len(sa_titles)
        idx = 0

        for p in parameter:

            name = f'sa_tornado_{year}_{parameter_short[idx]}.pdf'

            # Get total values:

            base_value = closedloop.loc[year, p]
            plus_values = [sa_closedloop_plus[l].loc[year, p] for l in range(n_labels)]
            minus_values = [sa_closedloop_minus[l].loc[year, p] for l in range(n_labels)]

            # Calculate absolute differences to base values:

            if base_value != 0:
                plus_differences  = [0 if _infeasible_plus_flags[l]  else (plus_values[l]  - base_value) for l in range(n_labels)]
                minus_differences = [0 if _infeasible_minus_flags[l] else (minus_values[l] - base_value) for l in range(n_labels)]

            else:
                plus_differences = [0 for l in range(n_labels)]
                minus_differences = [0 for l in range(n_labels)]

            # Calculate relative differences to base values:

            # if base_value != 0:
            #     plus_differences  = [0 if _infeasible_plus_flags[l]  else (plus_values[l]  - base_value) / base_value * 100 for l in range(n_labels)]
            #     minus_differences = [0 if _infeasible_minus_flags[l] else (minus_values[l] - base_value) / base_value * 100 for l in range(n_labels)]

            # else:
            #     plus_differences = [0 for l in range(n_labels)]
            #     minus_differences = [0 for l in range(n_labels)]

            spectrum = [abs(dl) + abs(dh) for dl, dh in zip(minus_differences, plus_differences)]

            # Filter out entries where spectrum is zero (no sensitivity effect):

            filtered_values = [(label, minus_diff, plus_diff, spec, _infeasible_plus_flags[l] or _infeasible_minus_flags[l], _zero_base_flags[l]) for l, (label, minus_diff, plus_diff, spec) in enumerate(zip(sa_titles, minus_differences, plus_differences, spectrum)) if spec > 0.1]

            # Sort by spectrum (impact):

            sorted_values = sorted(filtered_values, key=lambda x: x[3], reverse=False)

            labels_sorted            = [x[0] + (' $^{b)}$' if x[5] else '') + (' $^{a)}$' if x[4] else '') for x in sorted_values]
            minus_differences_sorted = [x[1] for x in sorted_values]
            plus_differences_sorted  = [x[2] for x in sorted_values]

            # Plot:

            row_height = 0.5
            fig_height = max(4, len(labels_sorted) * row_height)

            fig, ax = plt.subplots(figsize=(10, fig_height))
            y_pos = range(len(labels_sorted))

            ax.barh(y_pos, minus_differences_sorted, color="#AA2B2B", label=f'parameter values -{SENSITIVITY * 100:.0f}%')

            ax.barh(y_pos, plus_differences_sorted, color="#4F6640", label=f'parameter values +{SENSITIVITY * 100:.0f}%')

            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels_sorted)

            ax.set_xlabel(f'(Absolute) deviation of the closed-loop recycled content rate for {parameter_label[idx]} in {year:.0f} [pp]')
            #ax.set_xlabel(f'(Relative) deviation of the closed-loop recycled content rate for {parameter_label[idx]} in {year:.0f} [%]')
            
            ax.axvline(0, color='black', linewidth=1)
            ax.legend(loc='lower left')
            ax.grid(axis='x', alpha=0.2)
            
            plt.savefig(f'{export_sa_path}{name}', bbox_inches='tight')
            plt.close()

            print(f'   {name} exported.')

            idx += 1


    return plots_df