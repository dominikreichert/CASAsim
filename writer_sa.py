####
#
# CASAsim
# Export Module for Sensitivity Analysis Results
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
from openpyxl import load_workbook



def export_sa_data(export_sa_tmp_path, set_years, sa_tmp_plus, sa_tmp_minus, sa_tmp_elements, infeasible_sa_runs):

    if not sa_tmp_plus:
        pd.DataFrame(infeasible_sa_runs, columns=['infeasible_runs']).to_excel(
            f'{export_sa_tmp_path}_infeasible_sa_runs.xlsx', index=False
        )
        return


    # EXPORT INFEASIBLE SA RUNS DATA

    pd.DataFrame(infeasible_sa_runs, columns=['infeasible_runs']).to_excel(
        f'{export_sa_tmp_path}_infeasible_sa_runs.xlsx', index=False
    )


    # EXPORT SA DATA

    _sa_priority = [9, 12, 11]  # material_use, closedloop, objective_value
    _sa_order = _sa_priority + [i for i in range(len(sa_tmp_elements)) if i not in _sa_priority]

    for param_name in sa_tmp_plus:
        for prefix, sa_tmp in [('plus', sa_tmp_plus), ('minus', sa_tmp_minus)]:
            with pd.ExcelWriter(f'{export_sa_tmp_path}{param_name}_{prefix}.xlsx', engine='openpyxl') as writer:
                data_list = sa_tmp[param_name]
                for i in _sa_order:
                    item = data_list[i]
                    sheet_name = sa_tmp_elements[i]
                    if isinstance(item, pd.DataFrame):
                        item.to_excel(writer, sheet_name=sheet_name)
                    else:
                        pd.DataFrame({'value': [item]}).to_excel(writer, sheet_name=sheet_name)


    # CALCULATE MIN AND MAX VALUES FROM ALL SA ITERATIONS AND EXPORT RESULTS

    for p in ['steel', 'aluminum']:

        # Sheet "plus"
        _plus_rows = {}
        for name, data_list in sa_tmp_plus.items():
            _plus_rows[name] = data_list[12][f'{p}_recycledcontent']  # closedloop at index 12

        df_plus = pd.DataFrame(_plus_rows).T  # rows = parameter names, columns = years
        df_plus.columns = set_years

        # Sheet "minus"
        _minus_rows = {}
        for name, data_list in sa_tmp_minus.items():
            _minus_rows[name] = data_list[12][f'{p}_recycledcontent']

        df_minus = pd.DataFrame(_minus_rows).T
        df_minus.columns = set_years

        # Sheet "total"
        df_combined = pd.concat([df_plus, df_minus])

        _min_val, _max_val, _min_par, _max_par = {}, {}, {}, {}
        for year in set_years:
            col = df_combined[year]
            _min_val[year] = col.min()
            _max_val[year] = col.max()
            _min_par[year] = ', '.join(col[col == col.min()].index.tolist())
            _max_par[year] = ', '.join(col[col == col.max()].index.tolist())

        df_total = pd.DataFrame(
            [_min_val, _max_val, _min_par, _max_par],
            index=['min_value', 'max_value', 'min_parameter', 'max_parameter']
        )

        with pd.ExcelWriter(f'{export_sa_tmp_path}_total_recycledcontent_{p}.xlsx', engine='openpyxl') as writer:
            df_total.to_excel(writer, sheet_name='total')
            df_plus.to_excel(writer, sheet_name='plus')
            df_minus.to_excel(writer, sheet_name='minus')


    return