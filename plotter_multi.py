####
#
# CASAsim
# Plot multi-scenario results
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
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import FormatStrFormatter
import math


def plot_multi_data(export_path, results, scenario_names, n_scenarios, set_years, material_use, closedloop, color, PLOTTER_START_YEAR, PLOTTER_END_YEAR, plots, PERFORM_SA):

    set_years = range(PLOTTER_START_YEAR, PLOTTER_END_YEAR + 1)
    scenarios = range(1, n_scenarios + 1)
    
    style = ['-', '--', ':', '-.']

    title = ['a)', 'b)', 'c)', 'd)', 'e)', 'f)',
             'g)', 'h)', 'i)', 'j)', 'k)', 'l)',
             'm)', 'n)', 'o)', 'p)', 'q)', 'r)',
             's)', 't)', 'u)', 'v)', 'w)', 'x)',
             'y)', 'z)'
    ]

    scenario_colors = [
        "#333333",  # Schwarz
        "#E6A926",  # Orange
        "#48ABE4",  # Hellblau
        "#02946D",  # Grün
        "#DFD43C",  # Gelb
        "#0C6BA1",  # Dunkelblau
        "#D54E00",  # Rot
        "#B96794"   # Pink
    ]

    title_loc = 'left'  # or 'center'

    

    ###
    ###  (1) RECYCLED-CONTENT (POC) RATES
    ###

    plt.figure(figsize=(8, 6))

    rates = ['recycledcontent', 'postconsumer']
    rates_name = ['recycled-content', 'recycled-content-PoC']
    rates_title = ['recycled content', 'post-consumer recycled content']
    r_idx = 0

    for r in rates:


        # TOTAL STEEL AND ALUMINUM RATES

        name = f'{rates_name[r_idx]}-rates.pdf'

        maximum = 0

        for s in scenarios:

            closedloop = results[s-1][1]

            total_steel = [closedloop.loc[j, f'steel_{r}'] for j in set_years]
            total_aluminum = [closedloop.loc[j, f'aluminum_{r}'] for j in set_years]

            maximum = max(maximum, max(total_steel), max(total_aluminum))

            plt.plot(set_years, total_steel, color=scenario_colors[s-1], linestyle=style[0], label=f'Steel, {scenario_names[s-1]}')
            plt.plot(set_years, total_aluminum, color=scenario_colors[s-1], linestyle=style[1], label=f'Aluminum, {scenario_names[s-1]}')
            #plt.plot(set_years, total_steel, color=tuple(color['steel']), linestyle=style[s-1], label=f'Steel, {scenario_names[s-1]}')
            #plt.plot(set_years, total_aluminum, color=tuple(color['aluminum']), linestyle=style[s-1], label=f'Aluminum, {scenario_names[s-1]}')
            

        plt.ylabel(f'Closed-loop {rates_title[r_idx]} [%]')
        plt.gca().set_ylim(0, maximum)
        plt.gca().set_xlim(set_years[0], set_years[-1])
        plt.legend()

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()

        print(f'   {name} exported.')


        # MATERIAL-SPECIFIC STEEL RATES

        name = f'{rates_name[r_idx]}-rates-steel.pdf'

        maximum = 0

        for s in scenarios:

            closedloop = results[s-1][1]

            flatsteel = [closedloop.loc[j, f'flatsteel_{r}'] for j in set_years]
            longsteel = [closedloop.loc[j, f'longsteel_{r}'] for j in set_years]

            maximum = max(maximum, max(flatsteel), max(longsteel))

            plt.plot(set_years, flatsteel, color=scenario_colors[s-1], linestyle=style[0], label=f'Flat steel, {scenario_names[s-1]}')
            plt.plot(set_years, longsteel, color=scenario_colors[s-1], linestyle=style[1], label=f'Long steel, {scenario_names[s-1]}')
            #plt.plot(set_years, flatsteel, color=tuple(color['flatsteel']), linestyle=style[s-1], label=f'Flat steel, {scenario_names[s-1]}')
            #plt.plot(set_years, longsteel, color=tuple(color['longsteel']), linestyle=style[s-1], label=f'Long steel, {scenario_names[s-1]}')
            

        plt.ylabel(f'Closed-loop {rates_title[r_idx]} [%]')
        plt.gca().set_ylim(0, maximum)
        plt.gca().set_xlim(set_years[0], set_years[-1])
        plt.legend()

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()

        print(f'   {name} exported.')


        # MATERIAL-SPECIFIC ALUMINUM RATES

        name = f'{rates_name[r_idx]}-rates-aluminum.pdf'

        maximum = 0

        for s in scenarios:

            closedloop = results[s-1][1]

            wroughtaluminum = [closedloop.loc[j, f'wroughtaluminum_{r}'] for j in set_years]
            castaluminum_lowCu = [closedloop.loc[j, f'castaluminum_lowCu_{r}'] for j in set_years]
            castaluminum_highCu = [closedloop.loc[j, f'castaluminum_highCu_{r}'] for j in set_years]
        
            maximum = max(maximum, max(wroughtaluminum), max(castaluminum_lowCu), max(castaluminum_highCu))

            plt.plot(set_years, wroughtaluminum, color=scenario_colors[s-1], linestyle=style[0], label=f'Wrought aluminum, {scenario_names[s-1]}')
            plt.plot(set_years, castaluminum_lowCu, color=scenario_colors[s-1], linestyle=style[1], label=f'Low-Cu cast aluminum, {scenario_names[s-1]}')
            plt.plot(set_years, castaluminum_highCu, color=scenario_colors[s-1], linestyle=style[2], label=f'High-Cu cast aluminum, {scenario_names[s-1]}')
            #plt.plot(set_years, wroughtaluminum, color=tuple(color['wroughtaluminum']), linestyle=style[s-1], label=f'Wrought aluminum, {scenario_names[s-1]}')
            #plt.plot(set_years, castaluminum_lowCu, color=tuple(color['castaluminum_lowCu']), linestyle=style[s-1], label=f'Low-Cu cast aluminum, {scenario_names[s-1]}')
            #plt.plot(set_years, castaluminum_highCu, color=tuple(color['castaluminum_highCu']), linestyle=style[s-1], label=f'High-Cu cast aluminum, {scenario_names[s-1]}')
            

        plt.ylabel(f'Closed-loop {rates_title[r_idx]} [%]')
        plt.gca().set_ylim(0, maximum)
        plt.gca().set_xlim(set_years[0], set_years[-1])
        plt.legend()

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()

        print(f'   {name} exported.')


        r_idx += 1


    
    ###
    ###  (2) SCRAP ALLOCATION / USE
    ###

    SCALE_VALUE = 1e9
    SCALE_UNIT = 'Mt'


    # (2.1) STEEL

    name = 'scrap-allocation-steel.pdf'

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(24, 5))
    y_max = 0


    # (a) TOTAL SCRAP ALLOCATION

    for s in scenarios:

        material_use = results[s-1][0]

        y4 = [(material_use.loc[j, 'flatsteel_internal'] + material_use.loc[j, 'flatsteel_preconsumer'] + material_use.loc[j, 'flatsteel_postconsumer']) / SCALE_VALUE for j in set_years]
        y5 = [(material_use.loc[j, 'longsteel_internal'] + material_use.loc[j, 'longsteel_preconsumer'] + material_use.loc[j, 'longsteel_postconsumer']) / SCALE_VALUE for j in set_years]

        ax1.plot(set_years, y4, color=scenario_colors[s-1], linestyle=style[0], label=f'Flat steel production, {scenario_names[s-1]}')
        ax1.plot(set_years, y5, color=scenario_colors[s-1], linestyle=style[1], label=f'Long steel production, {scenario_names[s-1]}')
        #ax1.plot(set_years, y4, color=tuple(color['flatsteel']), linestyle=style[s-1], label=f'Flat steel production, {scenario_names[s-1]}')
        #ax1.plot(set_years, y5, color=tuple(color['longsteel']), linestyle=style[s-1], label=f'Long steel production, {scenario_names[s-1]}')

        y_max = max(y_max, max(y4), max(y5))

    ax1.legend(loc='upper left')
    ax1.set_title(f'{title[0]} Total steel scrap input', loc=title_loc)
    ax1.set_ylabel(f'Steel scrap [{SCALE_UNIT}]')
    ax1.set_xlim(set_years[0], set_years[-1])
    ax1.set_ylim(0, y_max)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))


    # (b) INTERNAL, PRE-CONSUMER, AND POST-CONSUMER SCRAP

    scrap = ['internal', 'preconsumer', 'postconsumer']
    s_label = ['Internal', 'Pre-consumer', 'Post-consumer']
    s_ax = [ax2, ax3, ax4]

    s_idx = 0
    y_max = 0

    for s in scrap:

        for scen in scenarios:

            material_use = results[scen-1][0]

            y2 = [material_use.loc[j, f'longsteel_{s}'] / SCALE_VALUE for j in set_years]
            y3 = [material_use.loc[j, f'flatsteel_{s}'] / SCALE_VALUE for j in set_years]

            s_ax[s_idx].plot(set_years, y2, color=scenario_colors[scen-1], linestyle=style[0], label=f'To long steel production, {scenario_names[scen-1]}')
            s_ax[s_idx].plot(set_years, y3, color=scenario_colors[scen-1], linestyle=style[1], label=f'To flat steel production, {scenario_names[scen-1]}')
            #s_ax[s_idx].plot(set_years, y2, color=tuple(color['longsteel']), linestyle=style[scen-1], label=f'To long steel production, {scenario_names[scen-1]}')
            #s_ax[s_idx].plot(set_years, y3, color=tuple(color['flatsteel']), linestyle=style[scen-1], label=f'To flat steel production, {scenario_names[scen-1]}')
    
            y_max = max(y_max, max(y2), max(y3))

        s_ax[s_idx].legend(loc='upper left')
        s_ax[s_idx].set_title(f'{title[1+s_idx]} {s_label[s_idx]} steel scrap allocation', loc=title_loc)
        s_ax[s_idx].set_ylabel(f'Steel scrap [{SCALE_UNIT}]')
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


    # (2.2) ALUMINUM

    name = 'scrap-allocation-aluminum.pdf'

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(24, 5))
    y_max = 0


    # (a) TOTAL SCRAP ALLOCATION

    for s in scenarios:

        material_use = results[s-1][0]
        
        y4 = [(material_use.loc[j, 'wroughtaluminum_internal'] + material_use.loc[j, 'wroughtaluminum_preconsumer'] + material_use.loc[j, 'wroughtaluminum_postconsumer']) / SCALE_VALUE for j in set_years]
        y5 = [(material_use.loc[j, 'castaluminum_lowCu_internal'] + material_use.loc[j, 'castaluminum_lowCu_preconsumer'] + material_use.loc[j, 'castaluminum_lowCu_postconsumer']) / SCALE_VALUE for j in set_years]
        y6 = [(material_use.loc[j, 'castaluminum_highCu_internal'] + material_use.loc[j, 'castaluminum_highCu_preconsumer'] + material_use.loc[j, 'castaluminum_highCu_postconsumer']) / SCALE_VALUE for j in set_years]

        ax1.plot(set_years, y4, color=scenario_colors[s-1], linestyle=style[0], label=f'Wrought aluminum production, {scenario_names[s-1]}')
        ax1.plot(set_years, y5, color=scenario_colors[s-1], linestyle=style[1], label=f'Low-Cu cast aluminum production, {scenario_names[s-1]}')
        ax1.plot(set_years, y6, color=scenario_colors[s-1], linestyle=style[2], label=f'High-Cu cast aluminum production, {scenario_names[s-1]}')
        #ax1.plot(set_years, y4, color=tuple(color['wroughtaluminum']), linestyle=style[s-1], label=f'Wrought aluminum production, {scenario_names[s-1]}')
        #ax1.plot(set_years, y5, color=tuple(color['castaluminum_lowCu']), linestyle=style[s-1], label=f'Low-Cu cast aluminum production, {scenario_names[s-1]}')
        #ax1.plot(set_years, y6, color=tuple(color['castaluminum_highCu']), linestyle=style[s-1], label=f'High-Cu cast aluminum production, {scenario_names[s-1]}')

        y_max = max(y_max, max(y4), max(y5), max(y6))

    ax1.legend(loc='upper left')
    ax1.set_title(f'{title[0]} Total aluminum scrap input', loc=title_loc)
    ax1.set_ylabel(f'Aluminum scrap [{SCALE_UNIT}]')
    ax1.set_xlim(set_years[0], set_years[-1])
    ax1.set_ylim(0, y_max)
    ax1.yaxis.set_major_locator(MaxNLocator(integer=True))


    # (b) INTERNAL, PRE-CONSUMER, AND POST-CONSUMER SCRAP

    scrap = ['internal', 'preconsumer', 'postconsumer']
    s_label = ['Internal', 'Pre-consumer', 'Post-consumer']
    s_ax = [ax2, ax3, ax4]

    s_idx = 0
    y_max = 0

    for s in scrap:

        for scen in scenarios:

            material_use = results[scen-1][0]

            y2 = [material_use.loc[j, f'wroughtaluminum_{s}'] / SCALE_VALUE for j in set_years]
            y3 = [material_use.loc[j, f'castaluminum_lowCu_{s}'] / SCALE_VALUE for j in set_years]
            y4 = [material_use.loc[j, f'castaluminum_highCu_{s}'] / SCALE_VALUE for j in set_years]

            s_ax[s_idx].plot(set_years, y2, color=scenario_colors[scen-1], linestyle=style[0], label=f'To wrought aluminum production, {scenario_names[scen-1]}')
            s_ax[s_idx].plot(set_years, y3, color=scenario_colors[scen-1], linestyle=style[1], label=f'To low-Cu cast aluminum production, {scenario_names[scen-1]}')
            s_ax[s_idx].plot(set_years, y4, color=scenario_colors[scen-1], linestyle=style[2], label=f'To high-Cu cast aluminum production, {scenario_names[scen-1]}')
            #s_ax[s_idx].plot(set_years, y2, color=tuple(color['wroughtaluminum']), linestyle=style[scen-1], label=f'To wrought aluminum production, {scenario_names[scen-1]}')
            #s_ax[s_idx].plot(set_years, y3, color=tuple(color['castaluminum_lowCu']), linestyle=style[scen-1], label=f'To low-Cu cast aluminum production, {scenario_names[scen-1]}')
            #s_ax[s_idx].plot(set_years, y4, color=tuple(color['castaluminum_highCu']), linestyle=style[scen-1], label=f'To high-Cu cast aluminum production, {scenario_names[scen-1]}')

        s_ax[s_idx].legend(loc='upper left')
        s_ax[s_idx].set_title(f'{title[1+s_idx]} {s_label[s_idx]} aluminum scrap allocation', loc=title_loc)
        s_ax[s_idx].set_ylabel(f'Aluminum scrap [{SCALE_UNIT}]')
        s_ax[s_idx].set_xlim(set_years[0], set_years[-1])

        y_max = max(y_max, max(y2), max(y3), max(y4))

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
    ###  (3a) TOTAL MATERIAL USE FOR STEEL AND ALUMINUM
    ###

    parameter = ['steel', 'aluminum']

    for p in parameter:

        name = f'material-use-{p}.pdf'

        n_cols = math.ceil(math.sqrt(n_scenarios))
        n_rows = math.ceil(n_scenarios / n_cols)
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows), squeeze=False)
        s_ax = axes.flatten().tolist()
        
        y_max = 0

        for s in range(n_scenarios):
            y1 = plots[s][f'{p}_internal']
            y2 = plots[s][f'{p}_preconsumer']
            y3 = plots[s][f'{p}_postconsumer']
            y5 = plots[s][f'{p}_virgin']
            y6 = plots[s][f'{p}_production_max_scrap']

            s_ax[s].stackplot(set_years, y1, y2, y3, y5, labels=['Internal scrap', 'Pre-consumer scrap', 'Post-consumer scrap', 'Virgin material'], colors=[color['internal'], color['preconsumer'], color['postconsumer'], color['virgin']])
            s_ax[s].plot(set_years, y6, color='black', linestyle='--', label='Maximum feasible scrap input')

            s_ax[s].set_title(f'{title[s]} {scenario_names[s]} scenario', loc=title_loc)
            s_ax[s].set_ylabel(f'Material use in {p} production [{SCALE_UNIT}]')

            y_max = max(y_max, max(sum(values) for values in zip(y1, y2, y3, y5)))

        for s in range(n_scenarios):
            s_ax[s].set_xlim(set_years[0], set_years[-1])
            s_ax[s].set_ylim(0, y_max)
            s_ax[s].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

        s_ax[0].legend(loc='upper left')

        for idx in range(n_scenarios, n_rows * n_cols):
            s_ax[idx].set_visible(False)

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')



    ###
    ###  (3b) TOTAL MATERIAL USE IN ONE PLOT
    ###

    name = f'material-use.pdf'
    
    parameter = ['steel', 'aluminum']

    flag = True

    if n_scenarios == 2:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 12))
        ax = [ax1, ax2, ax3, ax4]
    elif n_scenarios == 3:
        fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(18, 12))
        ax = [ax1, ax2, ax3, ax4, ax5, ax6]
    elif n_scenarios == 4:
        fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)) = plt.subplots(4, 2, figsize=(12, 24))
        ax = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
    else:
        flag = False

    ax_idx = 0
    row_idx = 0

    if flag:
        for p in parameter:

            y_max = 0

            for s in range(n_scenarios):
                y1 = plots[s][f'{p}_internal']
                y2 = plots[s][f'{p}_preconsumer']
                y3 = plots[s][f'{p}_postconsumer']
                y5 = plots[s][f'{p}_virgin']
                y6 = plots[s][f'{p}_production_max_scrap']

                ax[ax_idx].stackplot(set_years, y1, y2, y3, y5, labels=['Internal scrap', 'Pre-consumer scrap', 'Post-consumer scrap', 'Virgin material'], colors=[color['internal'], color['preconsumer'], color['postconsumer'], color['virgin']])
                ax[ax_idx].plot(set_years, y6, color='black', linestyle='--', label='Maximum feasible scrap input')

                ax[ax_idx].set_title(f'{title[ax_idx]} {scenario_names[s]} scenario', loc=title_loc)
                ax[ax_idx].set_ylabel(f'Material use in {p} production [{SCALE_UNIT}]')

                y_max = max(y_max, max(sum(values) for values in zip(y1, y2, y3, y5)))

                ax_idx += 1

            for s in range(n_scenarios):
                if s == 0:
                    ax[row_idx].legend(loc='upper left')

                ax[row_idx + s].set_xlim(set_years[0], set_years[-1])
                ax[row_idx + s].set_ylim(0, y_max)
                ax[row_idx + s].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

            row_idx += n_scenarios

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')



    if PERFORM_SA:

        ###
        ###  (4a) RECYCLED CONTENT RATES FOR STEEL AND ALUMINUM
        ###

        name = f'sa_recycled-content-rates.pdf'

        n_cols = math.ceil(math.sqrt(n_scenarios))
        n_rows = math.ceil(n_scenarios / n_cols)
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows), squeeze=False)
        s_ax = axes.flatten().tolist()

        parameter = ['steel', 'aluminum']
        p_label = ['Steel', 'Aluminum']
        y_max = 0

        for s in range(n_scenarios):
            p_idx = 0

            for p in parameter:

                y1 = plots[s][f'{p}_recycledcontent']
                y2 = plots[s][f'{p}_recycledcontent_max']
                y3 = plots[s][f'{p}_recycledcontent_min']

                s_ax[s].plot(set_years, y1, color=tuple(color[f'{p}']), linestyle='-', label=f'{p_label[p_idx]}')
                s_ax[s].fill_between(set_years, y2, y3, alpha=0.2, color=color[f'{p}'])

                s_ax[s].set_title(f'{title[s]} {scenario_names[s]} scenario', loc=title_loc)
                s_ax[s].set_ylabel(f'Closed-loop recycled content [%]')

                y_max = max(y_max, max(y1), max(y2), max(y3))
                
                p_idx += 1

        for s in range(n_scenarios):
            s_ax[s].set_xlim(set_years[0], set_years[-1])
            s_ax[s].set_ylim(0, y_max)
            s_ax[s].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

        s_ax[0].legend(loc='upper left')

        for idx in range(n_scenarios, n_rows * n_cols):
            s_ax[idx].set_visible(False)

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')



        ###
        ###  (4b) RECYCLED CONTENT RATES FOR STEEL AND ALUMINUM IN ONE PLOT
        ###

        name = f'sa_recycled-content-rates-2.pdf'

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        ax = list(axes)

        parameter = ['steel', 'aluminum']

        p_idx = 0

        for p in parameter:
            y_max = 0

            for s in range(n_scenarios):

                y1 = plots[s][f'{p}_recycledcontent']
                y2 = plots[s][f'{p}_recycledcontent_max']
                y3 = plots[s][f'{p}_recycledcontent_min']

                ax[p_idx].plot(set_years, y1, color=scenario_colors[s], linestyle='-', label=f'{scenario_names[s]}')
                ax[p_idx].fill_between(set_years, y2, y3, alpha=0.2, color=scenario_colors[s])

                y_max = max(y_max, max(y1), max(y2), max(y3))

            ax[p_idx].set_title(f'{title[p_idx]} {p}', loc=title_loc)
            ax[p_idx].set_ylabel(f'Closed-loop recycled content [%]')
            
            ax[p_idx].set_xlim(set_years[0], set_years[-1])
            ax[p_idx].set_ylim(0, y_max)
            ax[p_idx].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

            p_idx += 1

        ax[0].legend(loc='upper left')

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')



        ###
        ###  (4c) (POC) RECYCLED CONTENT RATES FOR STEEL AND ALUMINUM IN ONE PLOT
        ###

        name = f'sa_(poc)_recycled-content-rates-2.pdf'

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        ax = list(axes)

        parameter = ['steel', 'aluminum']

        p_idx = 0

        for p in parameter:
            y_max = 0

            for s in range(n_scenarios):

                y1 = plots[s][f'{p}_recycledcontent']
                y2 = plots[s][f'{p}_recycledcontent_max']
                y3 = plots[s][f'{p}_recycledcontent_min']

                ax[p_idx].plot(set_years, y1, color=scenario_colors[s], linestyle='-', label=f'{scenario_names[s]}')
                ax[p_idx].fill_between(set_years, y2, y3, alpha=0.2, color=scenario_colors[s])

                y4 = plots[s][f'{p}_postconsumer_recycledcontent']
                y5 = plots[s][f'{p}_postconsumer_recycledcontent_max']
                y6 = plots[s][f'{p}_postconsumer_recycledcontent_min']

                ax[p_idx].plot(set_years, y4, color=scenario_colors[s], linestyle='--', label=f'{scenario_names[s]}, from post-consumer')
                ax[p_idx].fill_between(set_years, y5, y6, alpha=0.2, color=scenario_colors[s])


                y_max = max(y_max, max(y1), max(y2), max(y3), max(y4), max(y5), max(y6))

            ax[p_idx].set_title(f'{title[p_idx]} {p}', loc=title_loc)
            ax[p_idx].set_ylabel(f'Closed-loop recycled content [%]')

            ax[p_idx].set_xlim(set_years[0], set_years[-1])
            ax[p_idx].set_ylim(0, y_max)
            ax[p_idx].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

            p_idx += 1

        ax[0].legend(loc='upper left')

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')



        ###
        ###  (5) TOTAL SCRAP ALLOCATION FOR STEEL AND ALUMINUM
        ###

        n_cols = math.ceil(math.sqrt(n_scenarios))
        n_rows = math.ceil(n_scenarios / n_cols)

        steel_parameter = ['flatsteel', 'longsteel']
        steel_parameter_label = ['flat steel', 'long steel']
        aluminum_parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
        aluminum_parameter_label = ['wrought Al', 'low-Cu cast Al', 'high-Cu cast Al']


        # (5.1) STEEL

        name = f'sa_scrap-allocation-steel.pdf'

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows), squeeze=False)
        ax = axes.flatten().tolist()

        y_max = 0

        for s in range(n_scenarios):
            p_idx = 0

            for p in steel_parameter:

                y1 = plots[s][f'{p}_max_scrap']
                y2 = plots[s][f'{p}_max_scrap_max']
                y3 = plots[s][f'{p}_max_scrap_min']

                ax[s].plot(set_years, y1, color=tuple(color[f'{p}']), linestyle='--', label=f'{steel_parameter_label[p_idx]} production, max. feasible scrap')
                #ax[s].fill_between(set_years, y2, y3, alpha=0.2, color=color[f'{p}'])

                y4 = plots[s][f'{p}_scrap_input']
                y5 = plots[s][f'{p}_scrap_input_max']
                y6 = plots[s][f'{p}_scrap_input_min']

                ax[s].plot(set_years, y4, color=tuple(color[f'{p}']), linestyle='-', label=f'{steel_parameter_label[p_idx]} production')
                ax[s].fill_between(set_years, y5, y6, alpha=0.2, color=color[f'{p}'])
                
                ax[s].set_title(f'{title[s]} {scenario_names[s]} scenario', loc=title_loc)
                ax[s].set_ylabel(f'Scrap input in steel production [{SCALE_UNIT}]')

                y_max = max(y_max, max(y1), max(y2), max(y3), max(y4), max(y5), max(y6))

                p_idx += 1

        for s in range(n_scenarios):
            ax[s].set_xlim(set_years[0], set_years[-1])
            ax[s].set_ylim(0, y_max)
            ax[s].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

        for idx in range(n_scenarios, n_rows * n_cols):
            ax[idx].set_visible(False)

        ax[0].legend(loc='upper left')

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')

        
        # (5.2) ALUMINUM

        name = f'sa_scrap-allocation-aluminum.pdf'

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows), squeeze=False)
        ax = axes.flatten().tolist()

        y_max = 0

        for s in range(n_scenarios):
            p_idx = 0

            for p in aluminum_parameter:

                y1 = plots[s][f'{p}_max_scrap']
                y2 = plots[s][f'{p}_max_scrap_max']
                y3 = plots[s][f'{p}_max_scrap_min']

                ax[s].plot(set_years, y1, color=tuple(color[f'{p}']), linestyle='--', label=f'{aluminum_parameter_label[p_idx]} production, max. feasible scrap')
                #ax[s].fill_between(set_years, y2, y3, alpha=0.2, color=color[f'{p}'])

                y4 = plots[s][f'{p}_scrap_input']
                y5 = plots[s][f'{p}_scrap_input_max']
                y6 = plots[s][f'{p}_scrap_input_min']

                ax[s].plot(set_years, y4, color=tuple(color[f'{p}']), linestyle='-', label=f'{aluminum_parameter_label[p_idx]} production')
                ax[s].fill_between(set_years, y5, y6, alpha=0.2, color=color[f'{p}'])
                
                ax[s].set_title(f'{title[s]} {scenario_names[s]} scenario', loc=title_loc)
                ax[s].set_ylabel(f'Scrap input in aluminum production [{SCALE_UNIT}]')

                y_max = max(y_max, max(y1), max(y2), max(y3), max(y4), max(y5), max(y6))

                p_idx += 1

        for s in range(n_scenarios):
            ax[s].set_xlim(set_years[0], set_years[-1])
            ax[s].set_ylim(0, y_max)
            ax[s].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

        for idx in range(n_scenarios, n_rows * n_cols):
            ax[idx].set_visible(False)

        ax[0].legend(loc='upper left')

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')



        ###
        ###  (6) TOTAL SCRAP ALLOCATION IN ONE PLOT
        ###

        name = f'sa_scrap-allocation.pdf'

        steel_parameter = ['flatsteel', 'longsteel']
        steel_parameter_label = ['flat steel', 'long steel']
        aluminum_parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
        aluminum_parameter_label = ['wrought Al', 'low-Cu cast Al', 'high-Cu cast Al']

        if n_scenarios == 2:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 12))
            ax = [ax1, ax2, ax3, ax4]
        elif n_scenarios == 3:
            fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(18, 12))
            ax = [ax1, ax2, ax3, ax4, ax5, ax6]
        elif n_scenarios == 4:
            fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8)) = plt.subplots(4, 2, figsize=(12, 24))
            ax = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
        else:
            return
        

        # (6.1) STEEL

        y_max = 0
        ax_idx = 0

        for s in range(n_scenarios):
            p_idx = 0

            for p in steel_parameter:

                y1 = plots[s][f'{p}_max_scrap']
                y2 = plots[s][f'{p}_max_scrap_max']
                y3 = plots[s][f'{p}_max_scrap_min']

                ax[ax_idx].plot(set_years, y1, color=tuple(color[f'{p}']), linestyle='--', label=f'{steel_parameter_label[p_idx]} production, max. feasible scrap')
                #ax[ax_idx].fill_between(set_years, y2, y3, alpha=0.2, color=color[f'{p}'])

                y4 = plots[s][f'{p}_scrap_input']
                y5 = plots[s][f'{p}_scrap_input_max']
                y6 = plots[s][f'{p}_scrap_input_min']

                ax[ax_idx].plot(set_years, y4, color=tuple(color[f'{p}']), linestyle='-', label=f'{steel_parameter_label[p_idx]} production')
                ax[ax_idx].fill_between(set_years, y5, y6, alpha=0.2, color=color[f'{p}'])
                
                ax[ax_idx].set_title(f'{title[ax_idx]} {scenario_names[s]} scenario', loc=title_loc)
                ax[ax_idx].set_ylabel(f'Scrap input in steel production [{SCALE_UNIT}]')

                y_max = max(y_max, max(y1), max(y2), max(y3), max(y4), max(y5), max(y6))

                p_idx += 1

            ax_idx += 1

        for s in range(n_scenarios):
            ax[s].set_xlim(set_years[0], set_years[-1])
            ax[s].set_ylim(0, y_max)
            ax[s].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

        
        # (6.2) ALUMINUM

        y_max = 0

        for s in range(n_scenarios):
            p_idx = 0

            for p in aluminum_parameter:

                y1 = plots[s][f'{p}_max_scrap']
                y2 = plots[s][f'{p}_max_scrap_max']
                y3 = plots[s][f'{p}_max_scrap_min']

                ax[ax_idx].plot(set_years, y1, color=tuple(color[f'{p}']), linestyle='--', label=f'{aluminum_parameter_label[p_idx]} production, max. feasible scrap')
                #ax[ax_idx].fill_between(set_years, y2, y3, alpha=0.2, color=color[f'{p}'])

                y4 = plots[s][f'{p}_scrap_input']
                y5 = plots[s][f'{p}_scrap_input_max']
                y6 = plots[s][f'{p}_scrap_input_min']

                ax[ax_idx].plot(set_years, y4, color=tuple(color[f'{p}']), linestyle='-', label=f'{aluminum_parameter_label[p_idx]} production')
                ax[ax_idx].fill_between(set_years, y5, y6, alpha=0.2, color=color[f'{p}'])
                
                ax[ax_idx].set_title(f'{title[ax_idx]} {scenario_names[s]} scenario', loc=title_loc)
                ax[ax_idx].set_ylabel(f'Scrap input in aluminum production [{SCALE_UNIT}]')

                y_max = max(y_max, max(y1), max(y2), max(y3), max(y4), max(y5), max(y6))

                p_idx += 1

            ax_idx += 1

        for s in range(n_scenarios, 2 * n_scenarios):
            ax[s].set_xlim(set_years[0], set_years[-1])
            ax[s].set_ylim(0, y_max)
            ax[s].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))

        ax[0].legend(loc='upper left')
        ax[n_scenarios].legend(loc='upper left')

        plt.savefig(f'{export_path}{name}', bbox_inches='tight')
        plt.close()
        print(f'   {name} exported.')


    return