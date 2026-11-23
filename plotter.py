####
#
# CASAsim
# Plot model results
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
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter
import operator


def plot_data(export_path, set_years, set_vehicles, vehicles_names, registrations, cagr, fleet, material_demand, material_supply, material_use, closedloop, material_quality, steel_production, aluminum_production, color, PLOTTER_START_YEAR, PLOTTER_END_YEAR):

    plots_df = pd.DataFrame()



    ###
    ###  (1) REGISTRATIONS
    ###

    name = 'registrations.pdf'

    plt.figure(figsize=(8, 6))

    reg_total = [0 for j in set_years]

    for veh in set_vehicles:

        reg = [registrations.loc[(veh, j), 'registrations'] / 1e6 for j in set_years]
        veh_name = vehicles_names.loc[veh, 'name']

        reg_total = list(map(operator.add, reg_total, reg))

        plt.plot(set_years, reg, color=tuple(color[veh_name]), label=veh_name)

    plt.plot(set_years, reg_total, color=tuple(color['total']), linestyle='--', label='total')

    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    plt.title(f'Vehicle registrations [M] with CAGR = {cagr:.2f}%')
    plt.legend()

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()

    print(f'   {name} exported.')



    ###
    ###  (2) FLEET
    ###

    name = 'fleet.pdf'

    stock_total = [0 for j in set_years]

    for veh in set_vehicles:

        stock = [fleet.loc[(veh, j), 'stock'] / 1e6 for j in set_years]
        veh_name = vehicles_names.loc[veh, 'name']

        stock_total = list(map(operator.add, stock_total, stock))

        plt.plot(set_years, stock, color=tuple(color[veh_name]), label=veh_name)

    plt.plot(set_years, stock_total, color=tuple(color['total']), linestyle='--', label='total')

    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    plt.title('Vehicle fleet [M]')
    plt.legend()

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()

    print(f'   {name} exported.')



    ###
    ###  (3) END-OF-LIFE
    ###

    for veh in set_vehicles:
        veh_name = vehicles_names.loc[veh, 'name']
        name = f'eol_veh_{veh_name}.pdf'

        exit = [fleet.loc[(veh, j), 'elvs_exit'] / 1e6 for j in set_years]
        export = [fleet.loc[(veh, j), 'elvs_export'] / 1e6 for j in set_years]
        unknown = [fleet.loc[(veh, j), 'elvs_unknown'] / 1e6 for j in set_years]
        recycling = [fleet.loc[(veh, j), 'elvs_recycling'] / 1e6 for j in set_years]

        plt.plot(set_years, exit, label='exiting fleet')
        plt.plot(set_years, export, label='exports')
        plt.plot(set_years, unknown, label='unknown whereabouts')
        plt.plot(set_years, recycling, label='entering ELV recycling')

        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))

        plt.title(f'End-of-life vehicle {veh}: {veh_name} [M]')
        plt.legend()

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()

        print(f'   {name} exported.')



    ###
    ###  (4) RECYCLED-CONTENT (POC) RATES
    ###

    #target_year = 2035
    #idx = target_year - set_years[0]

    set_years = range(PLOTTER_START_YEAR, PLOTTER_END_YEAR + 1)


    # (4.1) RECYCLED CONTENT RATES

    name = 'recycled-content-rates.pdf'

    flatsteel = [closedloop.loc[j, 'flatsteel_recycledcontent'] for j in set_years]
    longsteel = [closedloop.loc[j, 'longsteel_recycledcontent'] for j in set_years]
    wroughtaluminum = [closedloop.loc[j, 'wroughtaluminum_recycledcontent'] for j in set_years]
    castaluminum_lowCu = [closedloop.loc[j, 'castaluminum_lowCu_recycledcontent'] for j in set_years]
    castaluminum_highCu = [closedloop.loc[j, 'castaluminum_highCu_recycledcontent'] for j in set_years]
    total_steel = [closedloop.loc[j, 'steel_recycledcontent'] for j in set_years]
    total_aluminum = [closedloop.loc[j, 'aluminum_recycledcontent'] for j in set_years]

    maximum = max(max(flatsteel), max(longsteel), max(wroughtaluminum), max(castaluminum_lowCu), max(castaluminum_highCu), max(total_steel), max(total_aluminum))

    plt.plot(set_years, flatsteel, color=tuple(color['flatsteel']), label='Flat steel')
    plt.plot(set_years, longsteel, color=tuple(color['longsteel']), label='Long steel')
    plt.plot(set_years, castaluminum_lowCu, color=tuple(color['castaluminum_lowCu']), label='Low-Cu cast aluminum')
    plt.plot(set_years, castaluminum_highCu, color=tuple(color['castaluminum_highCu']), label='High-Cu cast aluminum')
    plt.plot(set_years, wroughtaluminum, color=tuple(color['wroughtaluminum']), label='Wrought aluminum')
    plt.plot(set_years, total_steel, color=tuple(color['total']), linestyle='--', label='Steel total')
    plt.plot(set_years, total_aluminum, color=tuple(color['total']), linestyle=':', label='Aluminum total')

    plt.title('Closed-loop recycled content rates [%]')
    plt.gca().set_ylim(0, maximum)
    plt.gca().set_xlim(set_years[0], set_years[-1])
    plt.legend()

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()

    print(f'   {name} exported.')


    # (4.2) POST-CONSUMER RECYCLED-CONTENT RATES

    name = 'recycled-content-PoC-rates.pdf'

    flatsteel = [closedloop.loc[j, 'flatsteel_postconsumer'] for j in set_years]
    longsteel = [closedloop.loc[j, 'longsteel_postconsumer'] for j in set_years]
    wroughtaluminum = [closedloop.loc[j, 'wroughtaluminum_postconsumer'] for j in set_years]
    castaluminum_lowCu = [closedloop.loc[j, 'castaluminum_lowCu_postconsumer'] for j in set_years]
    castaluminum_highCu = [closedloop.loc[j, 'castaluminum_highCu_postconsumer'] for j in set_years]
    total_steel = [closedloop.loc[j, 'steel_postconsumer'] for j in set_years]
    total_aluminum = [closedloop.loc[j, 'aluminum_postconsumer'] for j in set_years]

    maximum = max(max(flatsteel), max(longsteel), max(wroughtaluminum), max(castaluminum_lowCu), max(castaluminum_highCu), max(total_steel), max(total_aluminum))

    plt.plot(set_years, flatsteel, color=tuple(color['flatsteel']), label='Flat steel')
    plt.plot(set_years, longsteel, color=tuple(color['longsteel']), label='Long steel')
    plt.plot(set_years, castaluminum_lowCu, color=tuple(color['castaluminum_lowCu']), label='Low-Cu cast aluminum')
    plt.plot(set_years, castaluminum_highCu, color=tuple(color['castaluminum_highCu']), label='High-Cu cast aluminum')
    plt.plot(set_years, wroughtaluminum, color=tuple(color['wroughtaluminum']), label='Wrought aluminum')
    plt.plot(set_years, total_steel, color=tuple(color['total']), linestyle='--', label='Steel total')
    plt.plot(set_years, total_aluminum, color=tuple(color['total']), linestyle=':', label='Aluminum total')

    plt.title('Post-consumer closed-loop recycled content rates [%]')
    plt.gca().set_ylim(0, maximum)
    plt.gca().set_xlim(set_years[0], set_years[-1])
    plt.legend()

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()

    print(f'   {name} exported.')



    ###
    ###  (5) MATERIAL USE
    ###

    SCALE_VALUE = 1e9
    SCALE_UNIT = 'Mt'


    # (5.1) STEEL

    name = 'material-use-steel.pdf'

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    parameter = ['steel', 'flatsteel', 'longsteel']
    p_label = ['total steel', 'flat steel', 'long steel']
    p_ax = [ax1, ax2, ax3]

    p_idx = 0
    y_max = 0

    for p in parameter:

        y1 = [material_use.loc[j, f'{p}_internal'] / SCALE_VALUE for j in set_years]
        y2 = [material_use.loc[j, f'{p}_preconsumer'] / SCALE_VALUE for j in set_years]
        y3 = [material_use.loc[j, f'{p}_postconsumer'] / SCALE_VALUE for j in set_years]
        #y4 = [material_use.loc[j, f'{p}_openloop'] / SCALE_VALUE for j in set_years]
        y5 = [material_use.loc[j, f'{p}_virgin'] / SCALE_VALUE for j in set_years]
        y6 = [material_demand.loc[j, f'{p}_production_max_scrap'] / SCALE_VALUE for j in set_years]

        p_ax[p_idx].stackplot(set_years, y1, y2, y3, y5, labels=['Internal scrap', 'Pre-consumer scrap', 'Post-consumer scrap', 'Virgin material'], colors=[color['internal'], color['preconsumer'], color['postconsumer'], color['virgin']])

        p_ax[p_idx].plot(set_years, y6, color='black', linestyle='--', label='Maximum feasible scrap input')

        p_ax[p_idx].set_title(f'Material use in {p_label[p_idx]} production [{SCALE_UNIT}]')

        y_max = max(y_max, max(sum(values) for values in zip(y1, y2, y3, y5)))

        p_idx += 1

        # Save plot data:

        plots_df[f'{p}_internal'] = y1
        plots_df[f'{p}_preconsumer'] = y2
        plots_df[f'{p}_postconsumer'] = y3
        plots_df[f'{p}_virgin'] = y5
        plots_df[f'{p}_production_max_scrap'] = y6

    ax1.legend(loc='upper left')
    ax1.set_xlim(set_years[0], set_years[-1])
    ax2.set_xlim(set_years[0], set_years[-1])
    ax3.set_xlim(set_years[0], set_years[-1])
    ax1.set_ylim(0, y_max)
    ax2.set_ylim(0, y_max)
    ax3.set_ylim(0, y_max)
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax3.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()
    print(f'   {name} exported.')


    # (5.2) ALUMINUM

    name = 'material-use-aluminum.pdf'

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(24, 5))

    parameter = ['aluminum', 'wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
    p_label = ['total aluminum', 'wrought aluminum', 'low-Cu cast aluminum', 'high-Cu cast aluminum']
    p_ax = [ax1, ax2, ax3, ax4]

    p_idx = 0
    y_max = 0

    for p in parameter:

        y1 = [material_use.loc[j, f'{p}_internal'] / SCALE_VALUE for j in set_years]
        y2 = [material_use.loc[j, f'{p}_preconsumer'] / SCALE_VALUE for j in set_years]
        y3 = [material_use.loc[j, f'{p}_postconsumer'] / SCALE_VALUE for j in set_years]
        #y4 = [material_use.loc[j, f'{p}_openloop'] / SCALE_VALUE for j in set_years]
        y5 = [material_use.loc[j, f'{p}_virgin'] / SCALE_VALUE for j in set_years]
        y6 = [material_demand.loc[j, f'{p}_production_max_scrap'] / SCALE_VALUE for j in set_years]

        p_ax[p_idx].stackplot(set_years, y1, y2, y3, y5, labels=['Internal scrap', 'Pre-consumer scrap', 'Post-consumer scrap', 'Virgin material'], colors=[color['internal'], color['preconsumer'], color['postconsumer'], color['virgin']])

        p_ax[p_idx].plot(set_years, y6, color='black', linestyle='--', label='Maximum feasible scrap input')

        p_ax[p_idx].set_title(f'Material use in {p_label[p_idx]} production [{SCALE_UNIT}]')

        y_max = max(y_max, max(sum(values) for values in zip(y1, y2, y3, y5)))

        p_idx += 1

        # Save plot data:

        plots_df[f'{p}_internal'] = y1
        plots_df[f'{p}_preconsumer'] = y2
        plots_df[f'{p}_postconsumer'] = y3
        plots_df[f'{p}_virgin'] = y5
        plots_df[f'{p}_production_max_scrap'] = y6

    ax1.legend(loc='upper left')
    ax1.set_xlim(set_years[0], set_years[-1])
    ax2.set_xlim(set_years[0], set_years[-1])
    ax3.set_xlim(set_years[0], set_years[-1])
    ax4.set_xlim(set_years[0], set_years[-1])
    ax1.set_ylim(0, y_max)
    ax2.set_ylim(0, y_max)
    ax3.set_ylim(0, y_max)
    ax4.set_ylim(0, y_max)
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax3.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax4.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()
    print(f'   {name} exported.')


    # (5.3) TOTAL MATERIAL

    name = 'material-use-total.pdf'

    plt.figure(figsize=(5, 5))

    y1 = [material_use.loc[j, 'total_internal'] / SCALE_VALUE for j in set_years]
    y2 = [material_use.loc[j, 'total_preconsumer'] / SCALE_VALUE for j in set_years]
    y3 = [material_use.loc[j, 'total_postconsumer'] / SCALE_VALUE for j in set_years]
    #y4 = [material_use.loc[j, 'total_openloop'] / SCALE_VALUE for j in set_years]
    y5 = [material_use.loc[j, 'total_virgin'] / SCALE_VALUE for j in set_years]

    plt.stackplot(set_years, y1, y2, y3, y5, labels=['Internal scrap', 'Pre-consumer scrap', 'Post-consumer scrap', 'Virgin material'], colors=[color['internal'], color['preconsumer'], color['postconsumer'], color['virgin']])

    plt.legend(loc='upper left')
    plt.title(f'Total material use in production [{SCALE_UNIT}]')
    plt.xlim(set_years[0], set_years[-1])
    plt.ylim(0, max(sum(values) for values in zip(y1, y2, y3, y5)))
    plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()
    print(f'   {name} exported.')


    # (5.4) FLAT STEEL AND LONG STEEL PRODUCTION ROUTES

    name = 'material-use-steel-routes.pdf'

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    ax1, ax2, ax3, ax4, ax5, ax6 = axes.flatten()

    parameter = ['flatsteel', 'flatsteel', 'flatsteel', 'longsteel', 'longsteel', 'longsteel']
    p_route = ['s1', 's2', 's3', 's1', 's2', 's3']
    p_label = ['flat steel production route S1', 'flat steel production route S2', 'flat steel production route S3', 'long steel production route S1', 'long steel production route S2', 'long steel production route S3']
    p_ax = [ax1, ax2, ax3, ax4, ax5, ax6]

    p_idx = 0
    y_max_flatsteel = 0
    y_max_longsteel = 0

    for p in parameter:

        y1 = [material_use.loc[j, f'{p}_internal_{p_route[p_idx]}'] / SCALE_VALUE for j in set_years]
        y2 = [material_use.loc[j, f'{p}_preconsumer_{p_route[p_idx]}'] / SCALE_VALUE for j in set_years]
        y3 = [material_use.loc[j, f'{p}_postconsumer_{p_route[p_idx]}'] / SCALE_VALUE for j in set_years]
        #y4 = [material_use.loc[j, f'{p}_openloop_{p_route[p_idx]}'] / SCALE_VALUE for j in set_years]
        y5 = [material_use.loc[j, f'{p}_virgin_{p_route[p_idx]}'] / SCALE_VALUE for j in set_years]
        y6 = [material_demand.loc[j, f'{p}_production_{p_route[p_idx]}_max_scrap'] / SCALE_VALUE for j in set_years]

        p_ax[p_idx].stackplot(set_years, y1, y2, y3, y5, labels=['Internal scrap', 'Pre-consumer scrap', 'Post-consumer scrap', 'Virgin material'], colors=[color['internal'], color['preconsumer'], color['postconsumer'], color['virgin']])

        p_ax[p_idx].plot(set_years, y6, color='black', linestyle='--', label='Maximum feasible scrap input')

        p_ax[p_idx].set_title(f'Material use in {p_label[p_idx]} [{SCALE_UNIT}]')

        if p_idx < 3:
            y_max_flatsteel = max(y_max_flatsteel, max(sum(values) for values in zip(y1, y2, y3, y5)))
        else:
            y_max_longsteel = max(y_max_longsteel, max(sum(values) for values in zip(y1, y2, y3, y5)))

        p_idx += 1

    ax1.set_xlim(set_years[0], set_years[-1])
    ax2.set_xlim(set_years[0], set_years[-1])
    ax3.set_xlim(set_years[0], set_years[-1])
    ax4.set_xlim(set_years[0], set_years[-1])
    ax5.set_xlim(set_years[0], set_years[-1])
    ax6.set_xlim(set_years[0], set_years[-1])
    ax1.set_ylim(0, y_max_flatsteel)
    ax2.set_ylim(0, y_max_flatsteel)
    ax3.set_ylim(0, y_max_flatsteel)
    ax4.set_ylim(0, y_max_longsteel)
    ax5.set_ylim(0, y_max_longsteel)
    ax6.set_ylim(0, y_max_longsteel)
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax3.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    ax4.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax5.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax6.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax1.legend(loc='upper left')
    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()
    print(f'   {name} exported.')



    ###
    ###  (6) SCRAP ALLOCATION / USE
    ###

    SCALE_VALUE = 1e9
    SCALE_UNIT = 'Mt'


    # (6.1) STEEL

    name = 'scrap-allocation-steel.pdf'

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(24, 5))


    # (a) TOTAL SCRAP ALLOCATION

    #y1 = [(material_supply.loc[j, 'steel_internal'] + material_supply.loc[j, 'steel_preconsumer'] + material_supply.loc[j, 'steel_postconsumer']) / scale_value for j in set_years]
    #ax1.fill_between(set_years, y1, 0, label='Total closed-loop scrap supply', color=color['total'])

    y2 = [(
        (material_demand.loc[j, 'flatsteel_production_s1'] * steel_production.loc[j, 's1_max_scrap'] / 100) +
        (material_demand.loc[j, 'flatsteel_production_s2'] * steel_production.loc[j, 's2_max_scrap'] / 100) + 
        (material_demand.loc[j, 'flatsteel_production_s3'] * steel_production.loc[j, 's3_max_scrap'] / 100))        
        / SCALE_VALUE for j in set_years]
    y3 = [(
        (material_demand.loc[j, 'longsteel_production_s1'] * steel_production.loc[j, 's1_max_scrap'] / 100) +
        (material_demand.loc[j, 'longsteel_production_s2'] * steel_production.loc[j, 's2_max_scrap'] / 100) + 
        (material_demand.loc[j, 'longsteel_production_s3'] * steel_production.loc[j, 's3_max_scrap'] / 100))        
        / SCALE_VALUE for j in set_years]
    y4 = [(material_use.loc[j, 'flatsteel_internal'] + material_use.loc[j, 'flatsteel_preconsumer'] + material_use.loc[j, 'flatsteel_postconsumer']) / SCALE_VALUE for j in set_years]
    y5 = [(material_use.loc[j, 'longsteel_internal'] + material_use.loc[j, 'longsteel_preconsumer'] + material_use.loc[j, 'longsteel_postconsumer']) / SCALE_VALUE for j in set_years]

    ax1.plot(set_years, y2, color=tuple(color['flatsteel']), linestyle='--', label='Max. feasible scrap in flat steel production')
    ax1.plot(set_years, y3, color=tuple(color['longsteel']), linestyle='--', label='Max. feasible scrap in long steel production')
    ax1.plot(set_years, y4, color=tuple(color['flatsteel']), label='Scrap input in flat steel production')
    ax1.plot(set_years, y5, color=tuple(color['longsteel']), label='Scrap input in long steel production')

    ax1.legend(loc='upper left')
    ax1.set_title(f'Total steel scrap [{SCALE_UNIT}]')
    ax1.set_xlim(set_years[0], set_years[-1])
    ax1.set_ylim(0, max(max(y2), max(y3), max(y4), max(y5)))
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))


    # (b) INTERNAL, PRE-CONSUMER, AND POST-CONSUMER SCRAP

    scrap = ['internal', 'preconsumer', 'postconsumer']
    s_label = ['Internal', 'Pre-consumer', 'Post-consumer']
    s_ax = [ax2, ax3, ax4]

    s_idx = 0
    y_max = 0

    for s in scrap:

        y2 = [material_use.loc[j, f'longsteel_{s}'] / SCALE_VALUE for j in set_years]
        y3 = [material_use.loc[j, f'flatsteel_{s}'] / SCALE_VALUE for j in set_years]

        s_ax[s_idx].plot(set_years, y2, color=tuple(color['longsteel']), label='Scrap to long steel production')
        s_ax[s_idx].plot(set_years, y3, color=tuple(color['flatsteel']), label='Scrap to flat steel production')

        if s == 'postconsumer':
            y4 = [material_supply.loc[j, f'steel_{s}'] / SCALE_VALUE for j in set_years]

            s_ax[s_idx].plot(set_years, y4, color=tuple(color['steel']), linestyle='--', label='Steel scrap supply')

            y_max = max(y_max, max(y2), max(y3), max(y4))
        
        else:
            y4 = [material_supply.loc[j, f'flatsteel_{s}'] / SCALE_VALUE for j in set_years]
            y5 = [material_supply.loc[j, f'longsteel_{s}'] / SCALE_VALUE for j in set_years]

            s_ax[s_idx].plot(set_years, y4, color=tuple(color['flatsteel']), linestyle='--', label='Flat steel scrap supply')
            s_ax[s_idx].plot(set_years, y5, color=tuple(color['longsteel']), linestyle='--', label='Long steel scrap supply')

            y_max = max(y_max, max(y2), max(y3), max(y4), max(y5))

        s_ax[s_idx].legend(loc='upper left')
        s_ax[s_idx].set_title(f'{s_label[s_idx]} steel scrap [{SCALE_UNIT}]')
        s_ax[s_idx].set_xlim(set_years[0], set_years[-1])

        s_idx += 1

    ax2.set_ylim(0, y_max)
    ax3.set_ylim(0, y_max)
    ax4.set_ylim(0, y_max)
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax3.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax4.yaxis.set_major_locator(MaxNLocator(integer=True))

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()
    print(f'   {name} exported.')


    # (6.2) ALUMINUM

    name = 'scrap-allocation-aluminum.pdf'

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(24, 5))


    # (a) TOTAL SCRAP ALLOCATION

    #y1 = [(material_supply.loc[j, 'aluminum_internal'] + material_supply.loc[j, 'aluminum_preconsumer'] + material_supply.loc[j, 'aluminum_postconsumer']) / scale_value for j in set_years]
    #ax1.fill_between(set_years, y1, 0, label='Total closed-loop scrap supply', color=color['total'])

    y2 = [(material_demand.loc[j, 'wroughtaluminum_production'] * aluminum_production.loc[j, 'wroughtaluminum_max_scrap'] / 100) / SCALE_VALUE for j in set_years]
    y3 = [(material_demand.loc[j, 'castaluminum_lowCu_production'] * aluminum_production.loc[j, 'castaluminum_lowCu_max_scrap'] / 100) / SCALE_VALUE for j in set_years]
    y4 = [(material_demand.loc[j, 'castaluminum_highCu_production'] * aluminum_production.loc[j, 'castaluminum_highCu_max_scrap'] / 100) / SCALE_VALUE for j in set_years]
    y5 = [(material_use.loc[j, 'wroughtaluminum_internal'] + material_use.loc[j, 'wroughtaluminum_preconsumer'] + material_use.loc[j, 'wroughtaluminum_postconsumer']) / SCALE_VALUE for j in set_years]
    y6 = [(material_use.loc[j, 'castaluminum_lowCu_internal'] + material_use.loc[j, 'castaluminum_lowCu_preconsumer'] + material_use.loc[j, 'castaluminum_lowCu_postconsumer']) / SCALE_VALUE for j in set_years]
    y7 = [(material_use.loc[j, 'castaluminum_highCu_internal'] + material_use.loc[j, 'castaluminum_highCu_preconsumer'] + material_use.loc[j, 'castaluminum_highCu_postconsumer']) / SCALE_VALUE for j in set_years]

    ax1.plot(set_years, y2, color=tuple(color['wroughtaluminum']), linestyle='--', label='Max. feasible scrap in wrought Al production')
    ax1.plot(set_years, y3, color=tuple(color['castaluminum_lowCu']), linestyle='--', label='Max. feasible scrap in low-Cu cast Al production')
    ax1.plot(set_years, y4, color=tuple(color['castaluminum_highCu']), linestyle='--', label='Max. feasible scrap in high-Cu cast Al production')
    ax1.plot(set_years, y5, color=tuple(color['wroughtaluminum']), label='Scrap input in wrought Al production')
    ax1.plot(set_years, y6, color=tuple(color['castaluminum_lowCu']), label='Scrap input in low-Cu cast Al production')
    ax1.plot(set_years, y7, color=tuple(color['castaluminum_highCu']), label='Scrap input in high-Cu cast Al production')

    ax1.legend(loc='upper left')
    ax1.set_title(f'Total aluminum (Al) scrap [{SCALE_UNIT}]')
    ax1.set_xlim(set_years[0], set_years[-1])
    ax1.set_ylim(0, max(max(y2), max(y3), max(y4), max(y5), max(y6), max(y7)))
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))


    # (b) INTERNAL, PRE-CONSUMER, AND POST-CONSUMER SCRAP

    scrap = ['internal', 'preconsumer', 'postconsumer']
    s_label = ['Internal', 'Pre-consumer', 'Post-consumer']
    s_ax = [ax2, ax3, ax4]

    s_idx = 0
    y_max = 0

    for s in scrap:

        y2 = [material_use.loc[j, f'wroughtaluminum_{s}'] / SCALE_VALUE for j in set_years]
        y3 = [material_use.loc[j, f'castaluminum_lowCu_{s}'] / SCALE_VALUE for j in set_years]
        y4 = [material_use.loc[j, f'castaluminum_highCu_{s}'] / SCALE_VALUE for j in set_years]

        s_ax[s_idx].plot(set_years, y2, color=tuple(color['wroughtaluminum']), label='Scrap to wrought Al production')
        s_ax[s_idx].plot(set_years, y3, color=tuple(color['castaluminum_lowCu']), label='Scrap to low-Cu cast Al production')
        s_ax[s_idx].plot(set_years, y4, color=tuple(color['castaluminum_highCu']), label='Scrap to high-Cu cast Al production')

        y5 = [material_supply.loc[j, f'wroughtaluminum_{s}'] / SCALE_VALUE for j in set_years]
        y6 = [material_supply.loc[j, f'castaluminum_lowCu_{s}'] / SCALE_VALUE for j in set_years]
        y7 = [material_supply.loc[j, f'castaluminum_highCu_{s}'] / SCALE_VALUE for j in set_years]

        s_ax[s_idx].plot(set_years, y5, color=tuple(color['wroughtaluminum']), linestyle='--', label='Wrought Al scrap supply')
        s_ax[s_idx].plot(set_years, y6, color=tuple(color['castaluminum_lowCu']), linestyle='--', label='Low-Cu cast Al scrap supply')
        s_ax[s_idx].plot(set_years, y7, color=tuple(color['castaluminum_highCu']), linestyle='--', label='High-Cu cast Al scrap supply')

        if s == 'postconsumer':
            y8 = [material_supply.loc[j, f'mixedaluminum_{s}'] / SCALE_VALUE for j in set_years]
            s_ax[s_idx].plot(set_years, y8, color=tuple(color['mixedaluminum']), linestyle='--', label='Mixed Al scrap supply')
            y_max = max(y_max, max(y8))

        s_ax[s_idx].legend(loc='upper left')
        s_ax[s_idx].set_title(f'{s_label[s_idx]} aluminum (Al) scrap [{SCALE_UNIT}]')
        s_ax[s_idx].set_xlim(set_years[0], set_years[-1])

        y_max = max(y_max, max(y2), max(y3), max(y4), max(y5), max(y6), max(y7))

        s_idx += 1

    ax2.set_ylim(0, y_max)
    ax3.set_ylim(0, y_max)
    ax4.set_ylim(0, y_max)
    ax2.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax3.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax4.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

    plt.savefig(f'{export_path}{name}', bbox_inches='tight')
    plt.close()
    print(f'   {name} exported.')



    ###
    ###  (7) MATERIAL QUALITY
    ###

    quality_colors = [
        (0.33, 0.47, 0.65),  # gedämpftes Blau
        (0.78, 0.45, 0.55),  # Altrosa
        (0.44, 0.62, 0.42),  # Salbeigrün
        (0.58, 0.40, 0.62),  # gedämpftes Lila
        (0.40, 0.55, 0.75),  # Stahlblau
        (0.60, 0.60, 0.35),  # Olive
        (0.85, 0.55, 0.30),  # gedämpftes Orange
        (0.35, 0.58, 0.58),  # Petrol
        (0.50, 0.35, 0.30),  # Braun
        (0.78, 0.36, 0.30)   # Terracotta
    ]


    # (7.1) STEEL QUALITY

    if 'flatsteel_quality_s1' in material_quality.columns:

        name = 'quality-steel.pdf'

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        ax1, ax2, ax3, ax4, ax5, ax6 = axes.flatten()

        parameter = ['flatsteel', 'flatsteel', 'flatsteel', 'longsteel', 'longsteel', 'longsteel']
        p_route = ['s1', 's2', 's3', 's1', 's2', 's3']
        p_label = ['flat steel production route S1', 'flat steel production route S2', 'flat steel production route S3', 'long steel production route S1', 'long steel production route S2', 'long steel production route S3']
        p_ax = [ax1, ax2, ax3, ax4, ax5, ax6]

        p_idx = 0
        y_max_flatsteel = 0
        y_max_longsteel = 0

        steel_n_thresholds = steel_production.loc[set_years[0], 'n_thresholds']

        for p in parameter:
            for i in range(steel_n_thresholds):

                p_qf_threshold = [[steel_production.loc[t, 'flatsteel_threshold'][i] for t in set_years],
                            [steel_production.loc[t, 'flatsteel_threshold'][i] for t in set_years],
                            [steel_production.loc[t, 'flatsteel_threshold'][i] for t in set_years],
                            [steel_production.loc[t, 'longsteel_threshold'][i] for t in set_years],
                            [steel_production.loc[t, 'longsteel_threshold'][i] for t in set_years],
                            [steel_production.loc[t, 'longsteel_threshold'][i] for t in set_years]]

                qf_values = [material_quality.loc[t, f'{p}_quality_{p_route[p_idx]}'][i] for t in set_years]
                qf_thresholds = p_qf_threshold[p_idx]

                p_ax[p_idx].plot(set_years, qf_thresholds, color=tuple(quality_colors[i]), linestyle='--', label=f'Quality threshold {i+1}')
                p_ax[p_idx].plot(set_years, qf_values, color=tuple(quality_colors[i]), linestyle='-', label=f'Process input quality {i+1}')

                if p_idx < 3:
                    y_max_flatsteel = max(y_max_flatsteel, max(sum(values) for values in zip(qf_values, qf_thresholds)))
                else:
                    y_max_longsteel = max(y_max_longsteel, max(sum(values) for values in zip(qf_values, qf_thresholds)))

            p_ax[p_idx].set_title(f'Material quality in {p_label[p_idx]}')

            p_idx += 1

        ax1.set_xlim(set_years[0], set_years[-1])
        ax2.set_xlim(set_years[0], set_years[-1])
        ax3.set_xlim(set_years[0], set_years[-1])
        ax4.set_xlim(set_years[0], set_years[-1])
        ax5.set_xlim(set_years[0], set_years[-1])
        ax6.set_xlim(set_years[0], set_years[-1])
        ax1.set_ylim(0, y_max_flatsteel)
        ax2.set_ylim(0, y_max_flatsteel)
        ax3.set_ylim(0, y_max_flatsteel)
        ax4.set_ylim(0, y_max_longsteel)
        ax5.set_ylim(0, y_max_longsteel)
        ax6.set_ylim(0, y_max_longsteel)
        ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax3.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax4.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax5.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax6.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax1.legend(loc='upper left')
        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')


    # (7.2) ALUMINUM

    if 'wroughtaluminum_quality' in material_quality.columns:

        name = 'quality-aluminum.pdf'

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

        parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
        p_label = ['wrought aluminum', 'low-Cu cast aluminum', 'high-Cu cast aluminum']
        p_ax = [ax1, ax2, ax3]

        p_idx = 0

        aluminum_n_thresholds = aluminum_production.loc[set_years[0], 'n_thresholds']

        for p in parameter:
            y_max = 0

            for i in range(aluminum_n_thresholds):           

                p_qf_threshold = [
                    [aluminum_production.loc[t, 'wroughtaluminum_threshold'][i] for t in set_years],
                    [aluminum_production.loc[t, 'castaluminum_lowCu_threshold'][i] for t in set_years],
                    [aluminum_production.loc[t, 'castaluminum_highCu_threshold'][i] for t in set_years]
                ]

                qf_values = [material_quality.loc[t, f'{p}_quality'][i] for t in set_years]
                qf_thresholds = p_qf_threshold[p_idx]

                p_ax[p_idx].plot(set_years, qf_thresholds, color=tuple(quality_colors[i]), linestyle='--', label=f'Quality threshold {i+1}')
                p_ax[p_idx].plot(set_years, qf_values, color=tuple(quality_colors[i]), linestyle='-', label=f'Process input quality {i+1}')

                y_max = max(y_max, max(sum(values) for values in zip(qf_values, qf_thresholds)))

            p_ax[p_idx].set_title(f'Material quality in {p_label[p_idx]}')
            p_ax[p_idx].set_xlim(set_years[0], set_years[-1])
            p_ax[p_idx].set_ylim(0, y_max)
            p_ax[p_idx].yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

            p_idx += 1

        ax1.legend(loc='upper left')

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')


    return plots_df