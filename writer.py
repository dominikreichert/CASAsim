####
#
# CASAsim
# Export results excel file
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
import os


def export(export_path, **dataframes):

    file_path = os.path.join(export_path, 'results.xlsx')

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:

        for sheet_name, df in dataframes.items():

            if df is not None and isinstance(df, pd.DataFrame):

                # reset index to include it in the export:
                df_export = df.reset_index()

                df_export.to_excel(writer, sheet_name=sheet_name, index=False)

            else:
                print(f'   (!) {sheet_name} is not a valid dataframe and could not be exported.')

    print(f'   Excel file exported.')

    return file_path