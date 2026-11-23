####
#
# CASAsim
# Calculate material_use based on optimization problem
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
import gurobipy as gp
from gurobipy import GRB
import warnings


def run_optimization(material_use, set_years, material_demand, material_supply, steel_production, aluminum_production, eol, eol_dismantling_recycling, eol_pst):


    ############################################################################

    ###
    ###  SETTINGS
    ###

    # Penalty factor for post-consumer material:
    EPSILON = 1e-7

    # Penalty factor for steel scrap allocation between production processes:
    DELTA_STEEL = 1e-7

    # Penalty factor for aluminum scrap allocation between production processes:
    DELTA_ALUMINUM = 1e-5


    ############################################################################

    
    material_use = material_use.copy()
    eol_pst = eol_pst.copy()

    material_quality = pd.DataFrame({
        'year': set_years
    })
    material_quality.set_index('year', inplace=True)

    #warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)



    ###
    ###  MODEL PARAMETERS
    ###

    # Processes:

    steel_processes = [
        'flatsteel_production_s1',
        'flatsteel_production_s2',
        'flatsteel_production_s3',
        'longsteel_production_s1',
        'longsteel_production_s2',
        'longsteel_production_s3'
    ]

    aluminum_processes = [
        'wroughtaluminum_production',
        'castaluminum_lowCu_production',
        'castaluminum_highCu_production'
    ]



    ###
    ###  MODEL INITIALIZATION
    ###

    model = gp.Model('material-use-optimization')
    model.setParam('OutputFlag', 0)  # Suppress solver output
    model.setParam('NumericFocus', 1)  # Improve numerical stability
    model.setParam('DualReductions', 0)  # Required for correct IIS computation



    ###
    ###  MODEL VARIABLES
    ###

    # Variables for steel:

    virgin_steel = model.addVars(
        set_years, steel_processes, lb=0, vtype=GRB.CONTINUOUS, name="virgin_steel")

    internal_flatsteel_s1 = model.addVars(
        set_years, lb=0, vtype=GRB.CONTINUOUS, name="internal_flatsteel_s1")
    internal_flatsteel_s2 = model.addVars(
        set_years, lb=0, vtype=GRB.CONTINUOUS, name="internal_flatsteel_s2")
    internal_flatsteel_s3 = model.addVars(
        set_years, lb=0, vtype=GRB.CONTINUOUS, name="internal_flatsteel_s3")
    internal_longsteel_s1 = model.addVars(
        set_years, lb=0, vtype=GRB.CONTINUOUS, name="internal_longsteel_s1")
    internal_longsteel_s2 = model.addVars(
        set_years, lb=0, vtype=GRB.CONTINUOUS, name="internal_longsteel_s2")
    internal_longsteel_s3 = model.addVars(
        set_years, lb=0, vtype=GRB.CONTINUOUS, name="internal_longsteel_s3")

    internal_steel = [
        internal_flatsteel_s1,
        internal_flatsteel_s2,
        internal_flatsteel_s3,
        internal_longsteel_s1,
        internal_longsteel_s2,
        internal_longsteel_s3
    ]

    internal_labels_steel = [
        'flatsteel_internal_s1',
        'flatsteel_internal_s2',
        'flatsteel_internal_s3',
        'longsteel_internal_s1',
        'longsteel_internal_s2',
        'longsteel_internal_s3'
    ]

    preconsumer_flatsteel = model.addVars(
        set_years, steel_processes, lb=0, vtype=GRB.CONTINUOUS, name="preconsumer_flatsteel")
    preconsumer_longsteel = model.addVars(
        set_years, steel_processes, lb=0, vtype=GRB.CONTINUOUS, name="preconsumer_longsteel")

    postconsumer_dismantling_flatsteel = model.addVars(
        set_years, steel_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_dismantling_flatsteel")
    postconsumer_dismantling_longsteel = model.addVars(
        set_years, steel_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_dismantling_longsteel")

    postconsumer_pst_steel = model.addVars(
        set_years, steel_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_pst_steel")

    # Variables for aluminum:

    virgin_aluminum = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="virgin_aluminum")

    internal_wroughtaluminum = model.addVars(
        set_years, lb=0, vtype=GRB.CONTINUOUS, name="internal_wroughtaluminum")
    internal_castaluminum_lowCu = model.addVars(
        set_years, lb=0, vtype=GRB.CONTINUOUS, name="internal_castaluminum_lowCu")
    internal_castaluminum_highCu = model.addVars(
        set_years, lb=0, vtype=GRB.CONTINUOUS, name="internal_castaluminum_highCu")

    internal_aluminum = [
        internal_wroughtaluminum,
        internal_castaluminum_lowCu,
        internal_castaluminum_highCu
    ]

    internal_labels_aluminum = [
        'wroughtaluminum_internal',
        'castaluminum_lowCu_internal',
        'castaluminum_highCu_internal'
    ]

    preconsumer_wroughtaluminum = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="preconsumer_wroughtaluminum")
    preconsumer_castaluminum_lowCu = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="preconsumer_castaluminum_lowCu")
    preconsumer_castaluminum_highCu = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="preconsumer_castaluminum_highCu")

    postconsumer_dismantling_wroughtaluminum = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_dismantling_wroughtaluminum")
    postconsumer_dismantling_castaluminum_lowCu = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_dismantling_castaluminum_lowCu")
    postconsumer_dismantling_castaluminum_highCu = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_dismantling_castaluminum_highCu")

    postconsumer_pst_mixedaluminum = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_pst_mixedaluminum")
    postconsumer_pst_wroughtaluminum = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_pst_wroughtaluminum")
    postconsumer_pst_castaluminum_lowCu = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_pst_castaluminum_lowCu")
    postconsumer_pst_castaluminum_highCu = model.addVars(
        set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="postconsumer_pst_castaluminum_highCu")



    ###
    ###  MODEL CONSTRAINTS
    ###

    ### (C1) DEMAND constraint

    for t in set_years:

        ### (C1.1) STEEL DEMAND constraint

        p_idx = 0

        for p in steel_processes:

            model.addConstr(
                virgin_steel[t,p] + 
                internal_steel[p_idx][t] + 
                preconsumer_flatsteel[t,p] + 
                preconsumer_longsteel[t,p] + 
                postconsumer_dismantling_flatsteel[t,p] + 
                postconsumer_dismantling_longsteel[t,p] + 
                postconsumer_pst_steel[t,p]
                == material_demand.loc[t, p],
                name=f'c1_{p}_{t}'
            )

            p_idx += 1


        ### (C1.2) ALUMINUM DEMAND constraint

        p_idx = 0
        
        for p in aluminum_processes:

            model.addConstr(
                virgin_aluminum[t,p] + 
                internal_aluminum[p_idx][t] + 
                preconsumer_wroughtaluminum[t,p] + 
                preconsumer_castaluminum_lowCu[t,p] + 
                preconsumer_castaluminum_highCu[t,p] +
                postconsumer_dismantling_wroughtaluminum[t,p] + 
                postconsumer_dismantling_castaluminum_lowCu[t,p] + 
                postconsumer_dismantling_castaluminum_highCu[t,p] + 
                postconsumer_pst_mixedaluminum[t,p] + 
                postconsumer_pst_wroughtaluminum[t,p] + 
                postconsumer_pst_castaluminum_lowCu[t,p] + 
                postconsumer_pst_castaluminum_highCu[t,p]
                == material_demand.loc[t, p],
                name=f'c1_{p}_{t}'
            )

            p_idx += 1


    ### (C2) MAXIMUM SCRAP constraint

    for t in set_years:

        ### (C2.1) STEEL MAXIMUM SCRAP constraint

        p_idx = 0

        for p in steel_processes:

            model.addConstr(
                internal_steel[p_idx][t] +
                preconsumer_flatsteel[t,p] + 
                preconsumer_longsteel[t,p] + 
                postconsumer_dismantling_flatsteel[t,p] + 
                postconsumer_dismantling_longsteel[t,p] + 
                postconsumer_pst_steel[t,p]
                <= material_demand.loc[t, f'{p}_max_scrap'],
                name=f'c2_{p}_{t}'
            )

            p_idx += 1


        ### (C2.2) ALUMINUM MAXIMUM SCRAP constraint

        p_idx = 0

        for p in aluminum_processes:

            model.addConstr(
                internal_aluminum[p_idx][t] + 
                preconsumer_wroughtaluminum[t,p] + 
                preconsumer_castaluminum_lowCu[t,p] + 
                preconsumer_castaluminum_highCu[t,p] + 
                postconsumer_dismantling_wroughtaluminum[t,p] + 
                postconsumer_dismantling_castaluminum_lowCu[t,p] + 
                postconsumer_dismantling_castaluminum_highCu[t,p] + 
                postconsumer_pst_mixedaluminum[t,p] + 
                postconsumer_pst_wroughtaluminum[t,p] + 
                postconsumer_pst_castaluminum_lowCu[t,p] + 
                postconsumer_pst_castaluminum_highCu[t,p]
                <= material_demand.loc[t, f'{p}_max_scrap'],
                name=f'c2_{p}_{t}'
            )

            p_idx += 1


    ### (C3) MINIMUM SCRAP constraint

    for t in set_years:

        # To prevent infeasible model states during the model build-up, the minimum scrap input
        # constraint is considering a ramp-up of scrap in the model. 
        offset = t - set_years[0]
        ramp_value   = min(1.0, offset / 15)   # 0.0 → 1.0 over 15 years


        ### (C3.1) STEEL MINIMUM SCRAP constraint

        p_idx = 0

        for p in steel_processes:

            model.addConstr(
                material_demand.loc[t, f'{p}_min_scrap'] * ramp_value <=
                internal_steel[p_idx][t] +
                preconsumer_flatsteel[t,p] + 
                preconsumer_longsteel[t,p] + 
                postconsumer_dismantling_flatsteel[t,p] + 
                postconsumer_dismantling_longsteel[t,p] + 
                postconsumer_pst_steel[t,p],
                name=f'c3_{p}_{t}'
            )

            p_idx += 1


        ### (C3.2) ALUMINUM MINIMUM SCRAP constraint

        p_idx = 0

        for p in aluminum_processes:

            model.addConstr(
                material_demand.loc[t, f'{p}_min_scrap'] * ramp_value <=
                internal_aluminum[p_idx][t] + 
                preconsumer_wroughtaluminum[t,p] + 
                preconsumer_castaluminum_lowCu[t,p] + 
                preconsumer_castaluminum_highCu[t,p] + 
                postconsumer_dismantling_wroughtaluminum[t,p] + 
                postconsumer_dismantling_castaluminum_lowCu[t,p] + 
                postconsumer_dismantling_castaluminum_highCu[t,p] + 
                postconsumer_pst_mixedaluminum[t,p] + 
                postconsumer_pst_wroughtaluminum[t,p] + 
                postconsumer_pst_castaluminum_lowCu[t,p] + 
                postconsumer_pst_castaluminum_highCu[t,p],
                name=f'c3_{p}_{t}'
            )

            p_idx += 1


    ### (C4) SUPPLY constraints

    for t in set_years:

        ### (C4.1) STEEL SUPPLY constraints

        # Internal scrap:

        p_idx = 0

        for p in steel_processes:

            model.addConstr(
                internal_steel[p_idx][t]
                <= material_supply.loc[t, internal_labels_steel[p_idx]],
                name=f'c4_internal_{p}_{t}'
            )

            p_idx += 1

        # Pre-consumer scrap:

        model.addConstr(
            gp.quicksum(
                preconsumer_flatsteel[t,p] for p in steel_processes
            )
            <= material_supply.loc[t, 'flatsteel_preconsumer'],
            name=f'c4_preconsumer_flatsteel_{t}'
        )

        model.addConstr(
            gp.quicksum(
                preconsumer_longsteel[t,p] for p in steel_processes
            )
            <= material_supply.loc[t, 'longsteel_preconsumer'],
            name=f'c4_preconsumer_longsteel_{t}'
        )

        # Post-consumer scrap from dismantling recycling:

        model.addConstr(
            gp.quicksum(
                postconsumer_dismantling_flatsteel[t,p] for p in steel_processes
            )
            <= material_supply.loc[t, 'flatsteel_postconsumer_dismantling'],
            name=f'c4_postconsumer_dismantling_flatsteel_{t}'
        )

        model.addConstr(
            gp.quicksum(
                postconsumer_dismantling_longsteel[t,p] for p in steel_processes
            )
            <= material_supply.loc[t, 'longsteel_postconsumer_dismantling'],
            name=f'c4_postconsumer_dismantling_longsteel_{t}'
        )

        # Post-consumer scrap from PST recycling:

        model.addConstr(
            gp.quicksum(
                postconsumer_pst_steel[t,p] for p in steel_processes
            )
            <= material_supply.loc[t, 'steel_postconsumer_pst'],
            name=f'c4_postconsumer_pst_steel_{t}'
        )


        ### (C4.2) ALUMINUM SUPPLY constraints

        # Internal scrap:

        p_idx = 0

        for p in aluminum_processes:

            model.addConstr(
                internal_aluminum[p_idx][t]
                <= material_supply.loc[t, internal_labels_aluminum[p_idx]],
                name=f'c4_internal_{p}_{t}'
            )

            p_idx += 1

        # Pre-consumer scrap:

        model.addConstr(
            gp.quicksum(
                preconsumer_wroughtaluminum[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'wroughtaluminum_preconsumer'],
            name=f'c4_preconsumer_wroughtaluminum_{t}'
        )

        model.addConstr(
            gp.quicksum(
                preconsumer_castaluminum_lowCu[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'castaluminum_lowCu_preconsumer'],
            name=f'c4_preconsumer_castaluminum_lowCu_{t}'
        )

        model.addConstr(
            gp.quicksum(
                preconsumer_castaluminum_highCu[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'castaluminum_highCu_preconsumer'],
            name=f'c4_preconsumer_castaluminum_highCu_{t}'
        )

        # Post-consumer scrap from dismantling recycling:

        model.addConstr(
            gp.quicksum(
                postconsumer_dismantling_wroughtaluminum[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'wroughtaluminum_postconsumer_dismantling'],
            name=f'c4_postconsumer_dismantling_wroughtaluminum_{t}'
        )

        model.addConstr(
            gp.quicksum(
                postconsumer_dismantling_castaluminum_lowCu[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'castaluminum_lowCu_postconsumer_dismantling'],
            name=f'c4_postconsumer_dismantling_castaluminum_lowCu_{t}'
        )

        model.addConstr(
            gp.quicksum(
                postconsumer_dismantling_castaluminum_highCu[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'castaluminum_highCu_postconsumer_dismantling'],
            name=f'c4_postconsumer_dismantling_castaluminum_highCu_{t}'
        )

        # Post-consumer scrap from PST recycling:

        model.addConstr(
            gp.quicksum(
                postconsumer_pst_mixedaluminum[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'mixedaluminum_postconsumer_pst'],
            name=f'c4_postconsumer_pst_mixedaluminum_{t}'
        )

        model.addConstr(
            gp.quicksum(
                postconsumer_pst_wroughtaluminum[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'wroughtaluminum_postconsumer_pst'],
            name=f'c4_postconsumer_pst_wroughtaluminum_{t}'
        )

        model.addConstr(
            gp.quicksum(
                postconsumer_pst_castaluminum_lowCu[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'castaluminum_lowCu_postconsumer_pst'],
            name=f'c4_postconsumer_pst_castaluminum_lowCu_{t}'
        )

        model.addConstr(
            gp.quicksum(
                postconsumer_pst_castaluminum_highCu[t,p] for p in aluminum_processes
            )
            <= material_supply.loc[t, 'castaluminum_highCu_postconsumer_pst'],
            name=f'c4_postconsumer_pst_castaluminum_highCu_{t}'
        )


    ### (C5) QUALITY constraint

    steel_n_thresholds = steel_production.loc[set_years[0], 'n_thresholds']
    aluminum_n_thresholds = aluminum_production.loc[set_years[0], 'n_thresholds']

    # Because flat steel and long steel is mixed in PST recycling, we need to
    # pre-calculate the steel quality from PST:

    eol_pst['steel_quality'] = [[0.0] * steel_n_thresholds for _ in set_years]

    for t in set_years:
        input_flatsteel = eol.loc[t, 'bodies_flatsteel']
        input_longsteel = eol.loc[t, 'bodies_longsteel']
        input_steel = input_flatsteel + input_longsteel

        for i in range(steel_n_thresholds):
            qf_flatsteel = steel_production.loc[t, 'flatsteel_threshold'][i]
            qf_longsteel = steel_production.loc[t, 'longsteel_threshold'][i]

            eol_pst.at[t, 'steel_quality'][i] = (qf_flatsteel * input_flatsteel + qf_longsteel * input_longsteel) / input_steel if input_steel > 0.0 else 0.0

    # Because a mixed aluminum output is allowed in PST recycling, we need to
    # pre-calculate the mixed aluminum quality from PST:

    eol_pst['mixedaluminum_quality'] = [[0.0] * aluminum_n_thresholds for _ in set_years]

    for t in set_years:
        input_wroughtaluminum = eol.loc[t, 'bodies_wroughtaluminum']
        input_castaluminum_lowCu = eol.loc[t, 'bodies_castaluminum_lowCu']
        input_castaluminum_highCu = eol.loc[t, 'bodies_castaluminum_highCu']
        input_mixedaluminum = input_wroughtaluminum + input_castaluminum_lowCu + input_castaluminum_highCu

        for i in range(aluminum_n_thresholds):
            qf_wroughtaluminum = aluminum_production.loc[t, 'wroughtaluminum_threshold'][i]
            qf_castaluminum_lowCu = aluminum_production.loc[t, 'castaluminum_lowCu_threshold'][i]
            qf_castaluminum_highCu = aluminum_production.loc[t, 'castaluminum_highCu_threshold'][i]

            eol_pst.at[t, 'mixedaluminum_quality'][i] = (qf_wroughtaluminum * input_wroughtaluminum + qf_castaluminum_lowCu * input_castaluminum_lowCu + qf_castaluminum_highCu * input_castaluminum_highCu) / input_mixedaluminum if input_mixedaluminum > 0.0 else 0.0

        
        
    for t in set_years:

        ### (C5.1) STEEL QUALITY constraint

        flatsteel_qf = steel_production.loc[t, 'flatsteel_threshold']
        longsteel_qf = steel_production.loc[t, 'longsteel_threshold']

        qf = [
            flatsteel_qf,
            flatsteel_qf,
            flatsteel_qf,
            longsteel_qf,
            longsteel_qf,
            longsteel_qf
        ]

        flatsteel_contamination_dismantling = eol_dismantling_recycling.loc[t, 'flatsteel_contamination']
        longsteel_contamination_dismantling = eol_dismantling_recycling.loc[t, 'longsteel_contamination']
        
        steel_contamination_pst = eol_pst.loc[t, 'steel_contamination']
        steel_qf_pst = eol_pst.loc[t, 'steel_quality']

        steel_qf_virgin = steel_production.loc[t, 'virgin_steel_quality']

        p_idx = 0

        for p in steel_processes:

            demand = material_demand.loc[t, p]

            for i in range(steel_n_thresholds):

                model.addConstr(
                    internal_steel[p_idx][t] * qf[p_idx][i] +
                    preconsumer_flatsteel[t,p] * flatsteel_qf[i] +
                    preconsumer_longsteel[t,p] * longsteel_qf[i] +
                    postconsumer_dismantling_flatsteel[t,p] * (flatsteel_qf[i] + flatsteel_contamination_dismantling[i]) +
                    postconsumer_dismantling_longsteel[t,p] * (longsteel_qf[i] + longsteel_contamination_dismantling[i]) +
                    postconsumer_pst_steel[t,p] * (steel_qf_pst[i] + steel_contamination_pst[i]) +
                    virgin_steel[t,p] * steel_qf_virgin[i]
                    <= qf[p_idx][i] * demand,
                    name=f'c5_{p}_{t}_{i}'
                )

            p_idx += 1


        ### (C5.2) ALUMINUM QUALITY constraint

        wroughtaluminum_qf = aluminum_production.loc[t, 'wroughtaluminum_threshold']
        castaluminum_lowCu_qf = aluminum_production.loc[t, 'castaluminum_lowCu_threshold']
        castaluminum_highCu_qf = aluminum_production.loc[t, 'castaluminum_highCu_threshold']
        mixedaluminum_qf = eol_pst.at[t, 'mixedaluminum_quality']

        qf = [
            wroughtaluminum_qf,
            castaluminum_lowCu_qf,
            castaluminum_highCu_qf
        ]

        wroughtaluminum_contamination_dismantling = eol_dismantling_recycling.loc[t, 'wroughtaluminum_contamination']
        castaluminum_lowCu_contamination_dismantling = eol_dismantling_recycling.loc[t, 'castaluminum_lowCu_contamination']
        castaluminum_highCu_contamination_dismantling = eol_dismantling_recycling.loc[t, 'castaluminum_highCu_contamination']

        mixedaluminum_contamination_pst = eol_pst.loc[t, 'mixedaluminum_contamination']
        wroughtaluminum_contamination_pst = eol_pst.loc[t, 'wroughtaluminum_contamination']
        castaluminum_lowCu_contamination_pst = eol_pst.loc[t, 'castaluminum_lowCu_contamination']
        castaluminum_highCu_contamination_pst = eol_pst.loc[t, 'castaluminum_highCu_contamination']

        qf_virgin = [
            aluminum_production.loc[t, 'virgin_wroughtaluminum_quality'],
            aluminum_production.loc[t, 'virgin_castaluminum_lowCu_quality'],
            aluminum_production.loc[t, 'virgin_castaluminum_highCu_quality']
        ]

        p_idx = 0

        for p in aluminum_processes:

            demand = material_demand.loc[t, p]

            for i in range(aluminum_n_thresholds):

                model.addConstr(
                    internal_aluminum[p_idx][t] * qf[p_idx][i] +
                    preconsumer_wroughtaluminum[t,p] * wroughtaluminum_qf[i] +
                    preconsumer_castaluminum_lowCu[t,p] * castaluminum_lowCu_qf[i] +
                    preconsumer_castaluminum_highCu[t,p] * castaluminum_highCu_qf[i] +
                    postconsumer_dismantling_wroughtaluminum[t,p] * (wroughtaluminum_qf[i] + wroughtaluminum_contamination_dismantling[i]) +
                    postconsumer_dismantling_castaluminum_lowCu[t,p] * (castaluminum_lowCu_qf[i] + castaluminum_lowCu_contamination_dismantling[i]) +
                    postconsumer_dismantling_castaluminum_highCu[t,p] * (castaluminum_highCu_qf[i] + castaluminum_highCu_contamination_dismantling[i]) +
                    postconsumer_pst_mixedaluminum[t,p] * (mixedaluminum_qf[i] + mixedaluminum_contamination_pst[i]) +
                    postconsumer_pst_wroughtaluminum[t,p] * (wroughtaluminum_qf[i] + wroughtaluminum_contamination_pst[i]) +
                    postconsumer_pst_castaluminum_lowCu[t,p] * (castaluminum_lowCu_qf[i] + castaluminum_lowCu_contamination_pst[i]) +
                    postconsumer_pst_castaluminum_highCu[t,p] * (castaluminum_highCu_qf[i] + castaluminum_highCu_contamination_pst[i]) +
                    virgin_aluminum[t,p] * qf_virgin[p_idx][i]
                    <= qf[p_idx][i] * demand,
                    name=f'c5_{p}_{t}_{i}'
                )

            p_idx += 1


    ### (C6) INTERNAL SCRAP PRIORITY constraint
    ### Internal scrap must be fully used before other scrap sources.

    for t in set_years:
        for p_idx, p in enumerate(steel_processes):

            internal_scrap = material_supply.loc[t, internal_labels_steel[p_idx]]

            max_scrap_limit = material_demand.loc[t, f'{p}_max_scrap']
            demand = material_demand.loc[t, p]

            model.addConstr(
                internal_steel[p_idx][t] >= min(internal_scrap, max_scrap_limit, demand),
                name=f'c6_internal_priority_{p}_{t}'
            )

    for t in set_years:
        for p_idx, p in enumerate(aluminum_processes):

            internal_scrap = material_supply.loc[t, internal_labels_aluminum[p_idx]]

            max_scrap_limit = material_demand.loc[t, f'{p}_max_scrap']
            demand = material_demand.loc[t, p]

            model.addConstr(
                internal_aluminum[p_idx][t] >= min(internal_scrap, max_scrap_limit, demand),
                name=f'c6_internal_priority_{p}_{t}'
            )



    ###
    ###  OBJECTIVE FUNCTION
    ###


    # MINIMIZE VIRGIN MATERIAL USE

    # Penalty function:

    steel_variables = [preconsumer_flatsteel, preconsumer_longsteel, postconsumer_dismantling_flatsteel, postconsumer_dismantling_longsteel, postconsumer_pst_steel]
    steel_labels = ['flatsteel_preconsumer', 'longsteel_preconsumer', 'flatsteel_postconsumer_dismantling', 'longsteel_postconsumer_dismantling', 'steel_postconsumer_pst']
    
    aluminum_variables = [preconsumer_wroughtaluminum, preconsumer_castaluminum_lowCu, preconsumer_castaluminum_highCu, postconsumer_dismantling_wroughtaluminum, postconsumer_dismantling_castaluminum_lowCu, postconsumer_dismantling_castaluminum_highCu, postconsumer_pst_mixedaluminum, postconsumer_pst_wroughtaluminum, postconsumer_pst_castaluminum_lowCu, postconsumer_pst_castaluminum_highCu]
    aluminum_labels = ['wroughtaluminum_preconsumer', 'castaluminum_lowCu_preconsumer', 'castaluminum_highCu_preconsumer', 'wroughtaluminum_postconsumer_dismantling', 'castaluminum_lowCu_postconsumer_dismantling', 'castaluminum_highCu_postconsumer_dismantling', 'mixedaluminum_postconsumer_pst', 'wroughtaluminum_postconsumer_pst', 'castaluminum_lowCu_postconsumer_pst', 'castaluminum_highCu_postconsumer_pst']

    n_delta_steel = len(steel_variables)
    delta_steel = model.addVars(
        n_delta_steel, set_years, steel_processes, lb=0, vtype=GRB.CONTINUOUS, name="delta_steel")
    
    n_delta_aluminum = len(aluminum_variables)
    delta_aluminum = model.addVars(
        n_delta_aluminum, set_years, aluminum_processes, lb=0, vtype=GRB.CONTINUOUS, name="delta_aluminum")

    for t in range(set_years[1], set_years[-1] + 1):
        t_prev = t - 1

        # Steel:

        for p_idx in range(n_delta_steel):
            for p in steel_processes:
            
                model.addConstr(
                    steel_variables[p_idx][t,p] - steel_variables[p_idx][t_prev,p]
                    <= delta_steel[p_idx,t,p],
                    name=f'obj_penalty_{steel_labels[p_idx]}_pos_{p}_{t}'
                )

                model.addConstr(
                    steel_variables[p_idx][t_prev,p] - steel_variables[p_idx][t,p]
                    <= delta_steel[p_idx,t,p],
                    name=f'obj_penalty_{steel_labels[p_idx]}_neg_{p}_{t}'
                )

        # Aluminum:

        for p_idx in range(n_delta_aluminum):
            for p in aluminum_processes:
            
                model.addConstr(
                    aluminum_variables[p_idx][t,p] - aluminum_variables[p_idx][t_prev,p]
                    <= delta_aluminum[p_idx,t,p],
                    name=f'obj_penalty_{aluminum_labels[p_idx]}_pos_{p}_{t}'
                )

                model.addConstr(
                    aluminum_variables[p_idx][t_prev,p] - aluminum_variables[p_idx][t,p]
                    <= delta_aluminum[p_idx,t,p],
                    name=f'obj_penalty_{aluminum_labels[p_idx]}_neg_{p}_{t}'
                )


    model.setObjective(
        gp.quicksum(virgin_steel[t,p] for t in set_years for p in steel_processes)
        + EPSILON * gp.quicksum(
            postconsumer_dismantling_flatsteel[t,p] +
            postconsumer_dismantling_longsteel[t,p] +
            postconsumer_pst_steel[t,p]
            for t in set_years for p in steel_processes
        )
        + gp.quicksum(virgin_aluminum[t,p] for t in set_years for p in aluminum_processes)
        + EPSILON * gp.quicksum(
            postconsumer_dismantling_wroughtaluminum[t,p] +
            postconsumer_dismantling_castaluminum_lowCu[t,p] +
            postconsumer_dismantling_castaluminum_highCu[t,p] +
            postconsumer_pst_mixedaluminum[t,p] +
            postconsumer_pst_wroughtaluminum[t,p] +
            postconsumer_pst_castaluminum_lowCu[t,p] +
            postconsumer_pst_castaluminum_highCu[t,p]
            for t in set_years for p in aluminum_processes
        )
        + DELTA_STEEL * gp.quicksum(delta_steel[p_idx,t,p] for p_idx in range(n_delta_steel) for t in set_years for p in steel_processes)
        + DELTA_ALUMINUM * gp.quicksum(delta_aluminum[p_idx,t,p] for p_idx in range(n_delta_aluminum) for t in set_years for p in aluminum_processes),
        GRB.MINIMIZE
    )



    ###
    ###  START OPTIMIZATION
    ###

    model.optimize()



    ###
    ###  GENERTALE MATERIAL_USE DATAFRAME
    ###

    # Initialization of material_use with zeros:

    steel_types = ['flatsteel', 'longsteel']
    aluminum_types = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
    suffixes = ['_s1', '_s2', '_s3', '']
    categories = ['internal', 'preconsumer', 'postconsumer', 'postconsumer_dismantling', 'postconsumer_pst', 'virgin']  # ,'to_closedloop', 'to_openloop'

    columns = []

    for steel in steel_types:
        for cat in categories:
            # if cat in ['to_closedloop', 'to_openloop']:
            #     columns.append(f'{steel}_{cat}')
            # else:
            for suf in suffixes:
                columns.append(f'{steel}_{cat}{suf}')

    for alu in aluminum_types:
        for cat in categories:
            columns.append(f'{alu}_{cat}')

    for cat in categories:
        columns.extend([f'steel_{cat}', f'aluminum_{cat}', f'total_{cat}'])

    for col in columns:
        material_use.loc[set_years, col] = 0


    # Write optimization results into material_use:

    if model.status == GRB.OPTIMAL:
        obj_value = model.objVal
        print(f'   optimal solution found: {obj_value}')

        steel_parameter = ['flatsteel', 'longsteel']
        aluminum_parameter = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']

        for t in set_years:


            # (a) FLAT STEEL AND LONG STEEL USE

            p_idx = 0

            for p in steel_parameter:

                # Internal scrap (per production route):
                # internal scrap may only be allocated to the same production process (s1 -> s1, s2 -> s2, s3 -> s3)

                material_use.loc[t, f'{p}_internal_s1'] = internal_steel[p_idx][t].X
                material_use.loc[t, f'{p}_internal_s2'] = internal_steel[p_idx + 1][t].X
                material_use.loc[t, f'{p}_internal_s3'] = internal_steel[p_idx + 2][t].X
                material_use.loc[t, f'{p}_internal'] = (
                    material_use.loc[t, f'{p}_internal_s1'] +
                    material_use.loc[t, f'{p}_internal_s2'] +
                    material_use.loc[t, f'{p}_internal_s3']
                )

                # Pre-consumer scrap (per production route):

                material_use.loc[t, f'{p}_preconsumer_s1'] = (
                    preconsumer_flatsteel[t, steel_processes[p_idx]].X + 
                    preconsumer_longsteel[t, steel_processes[p_idx]].X
                )
                material_use.loc[t, f'{p}_preconsumer_s2'] = (
                    preconsumer_flatsteel[t, steel_processes[p_idx + 1]].X + 
                    preconsumer_longsteel[t, steel_processes[p_idx + 1]].X
                )
                material_use.loc[t, f'{p}_preconsumer_s3'] = (
                    preconsumer_flatsteel[t, steel_processes[p_idx + 2]].X + 
                    preconsumer_longsteel[t, steel_processes[p_idx + 2]].X
                )
                material_use.loc[t, f'{p}_preconsumer'] = (
                    material_use.loc[t, f'{p}_preconsumer_s1'] +
                    material_use.loc[t, f'{p}_preconsumer_s2'] +
                    material_use.loc[t, f'{p}_preconsumer_s3']
                )

                # Post-consumer scrap from dismantling (per production route):

                material_use.loc[t, f'{p}_postconsumer_dismantling_s1'] = (
                    postconsumer_dismantling_flatsteel[t, steel_processes[p_idx]].X +
                    postconsumer_dismantling_longsteel[t, steel_processes[p_idx]].X
                )
                material_use.loc[t, f'{p}_postconsumer_dismantling_s2'] = (
                    postconsumer_dismantling_flatsteel[t, steel_processes[p_idx + 1]].X +
                    postconsumer_dismantling_longsteel[t, steel_processes[p_idx + 1]].X
                )
                material_use.loc[t, f'{p}_postconsumer_dismantling_s3'] = (
                    postconsumer_dismantling_flatsteel[t, steel_processes[p_idx + 2]].X +
                    postconsumer_dismantling_longsteel[t, steel_processes[p_idx + 2]].X
                )
                material_use.loc[t, f'{p}_postconsumer_dismantling'] = (
                    material_use.loc[t, f'{p}_postconsumer_dismantling_s1'] +
                    material_use.loc[t, f'{p}_postconsumer_dismantling_s2'] +
                    material_use.loc[t, f'{p}_postconsumer_dismantling_s3']
                )

                # Post-consumer scrap from PST (per production route):

                material_use.loc[t, f'{p}_postconsumer_pst_s1'] = postconsumer_pst_steel[t, steel_processes[p_idx]].X
                material_use.loc[t, f'{p}_postconsumer_pst_s2'] = postconsumer_pst_steel[t, steel_processes[p_idx + 1]].X
                material_use.loc[t, f'{p}_postconsumer_pst_s3'] = postconsumer_pst_steel[t, steel_processes[p_idx + 2]].X
                material_use.loc[t, f'{p}_postconsumer_pst'] = (
                    material_use.loc[t, f'{p}_postconsumer_pst_s1'] +
                    material_use.loc[t, f'{p}_postconsumer_pst_s2'] +
                    material_use.loc[t, f'{p}_postconsumer_pst_s3']
                )

                # Total post-consumer scrap (per production route):

                material_use.loc[t, f'{p}_postconsumer_s1'] = (
                    material_use.loc[t, f'{p}_postconsumer_dismantling_s1'] +
                    material_use.loc[t, f'{p}_postconsumer_pst_s1']
                )
                material_use.loc[t, f'{p}_postconsumer_s2'] = (
                    material_use.loc[t, f'{p}_postconsumer_dismantling_s2'] +
                    material_use.loc[t, f'{p}_postconsumer_pst_s2']
                )
                material_use.loc[t, f'{p}_postconsumer_s3'] = (
                    material_use.loc[t, f'{p}_postconsumer_dismantling_s3'] +
                    material_use.loc[t, f'{p}_postconsumer_pst_s3']
                )
                material_use.loc[t, f'{p}_postconsumer'] = (
                    material_use.loc[t, f'{p}_postconsumer_dismantling'] +
                    material_use.loc[t, f'{p}_postconsumer_pst']
                )

                # Virgin material (per production route):

                material_use.loc[t, f'{p}_virgin_s1'] = virgin_steel[t, steel_processes[p_idx]].X
                material_use.loc[t, f'{p}_virgin_s2'] = virgin_steel[t, steel_processes[p_idx + 1]].X
                material_use.loc[t, f'{p}_virgin_s3'] = virgin_steel[t, steel_processes[p_idx + 2]].X
                material_use.loc[t, f'{p}_virgin'] = (
                    material_use.loc[t, f'{p}_virgin_s1'] +
                    material_use.loc[t, f'{p}_virgin_s2'] +
                    material_use.loc[t, f'{p}_virgin_s3']
                )

                # Scrap to closed-loop and open-loop:

                # supply_internal = (
                #     material_supply.loc[t, f'{p}_internal_s1'] +
                #     material_supply.loc[t, f'{p}_internal_s2'] +
                #     material_supply.loc[t, f'{p}_internal_s3']
                # )
                # supply_pre = material_supply.loc[t, f'{p}_preconsumer']
                # supply_post_dismantling = material_supply.loc[t, f'{p}_postconsumer_dismantling']

                # # PST share based on flatsteel proportion of total steel bodies
                # bodies = eol.loc[t, 'bodies_steel']
                # if bodies != 0:
                #     share = eol.loc[t, f'bodies_{p}'] / bodies
                # else:
                #     share = 0
                # supply_post_pst = material_supply.loc[t, 'steel_postconsumer_pst'] * share

                # to_closedloop = (
                #     material_use.loc[t, f'{p}_internal'] +
                #     material_use.loc[t, f'{p}_preconsumer'] + 
                #     material_use.loc[t, f'{p}_postconsumer']
                # )
                # material_use.loc[t, f'{p}_to_closedloop'] = to_closedloop

                # supply_total = supply_internal + supply_pre + supply_post_dismantling + supply_post_pst
                # material_use.loc[t, f'{p}_to_openloop'] = max(0, supply_total - to_closedloop)

                p_idx = 3


            # (b) WROUGHT ALUMINUM AND CAST ALUMINUM USE

            p_idx = 0

            for p in aluminum_parameter:

                # Internal scrap:
                # internal scrap may only be allocated to the same production process (wrought -> wrought, cast -> cast)

                material_use.loc[t, f'{p}_internal'] = internal_aluminum[p_idx][t].X

                # Pre-consumer scrap:

                material_use.loc[t, f'{p}_preconsumer'] = (
                    preconsumer_wroughtaluminum[t, aluminum_processes[p_idx]].X +
                    preconsumer_castaluminum_lowCu[t, aluminum_processes[p_idx]].X +
                    preconsumer_castaluminum_highCu[t, aluminum_processes[p_idx]].X
                )

                # Post-consumer scrap from dismantling:

                material_use.loc[t, f'{p}_postconsumer_dismantling'] = (
                    postconsumer_dismantling_wroughtaluminum[t, aluminum_processes[p_idx]].X +
                    postconsumer_dismantling_castaluminum_lowCu[t, aluminum_processes[p_idx]].X + 
                    postconsumer_dismantling_castaluminum_highCu[t, aluminum_processes[p_idx]].X
                )

                # Post-consumer scrap from PST:

                material_use.loc[t, f'{p}_postconsumer_pst'] = (
                    postconsumer_pst_mixedaluminum[t, aluminum_processes[p_idx]].X +
                    postconsumer_pst_wroughtaluminum[t, aluminum_processes[p_idx]].X +
                    postconsumer_pst_castaluminum_lowCu[t, aluminum_processes[p_idx]].X + 
                    postconsumer_pst_castaluminum_highCu[t, aluminum_processes[p_idx]].X
                )

                # Total post-consumer scrap:

                material_use.loc[t, f'{p}_postconsumer'] = (
                    material_use.loc[t, f'{p}_postconsumer_dismantling'] +
                    material_use.loc[t, f'{p}_postconsumer_pst']
                )

                # Virgin material:

                material_use.loc[t, f'{p}_virgin'] = virgin_aluminum[t, aluminum_processes[p_idx]].X

                # Scrap to closed-loop and open-loop:

                # supply_internal = material_supply.loc[t, f'{p}_internal']
                # supply_pre = material_supply.loc[t, f'{p}_preconsumer']
                # supply_post_dismantling = material_supply.loc[t, f'{p}_postconsumer_dismantling']
                # supply_post_pst = material_supply.loc[t, f'{p}_postconsumer_pst']

                # to_closedloop = (
                #     material_use.loc[t, f'{p}_internal'] +
                #     material_use.loc[t, f'{p}_preconsumer'] +
                #     material_use.loc[t, f'{p}_postconsumer']
                # )
                # material_use.loc[t, f'{p}_to_closedloop'] = to_closedloop

                # supply_total = supply_internal + supply_pre + supply_post_dismantling + supply_post_pst
                # material_use.loc[t, f'{p}_to_openloop'] = max(0, supply_total - to_closedloop)

                p_idx += 1


            # (c) TOTAL STEEL, ALUMINUM, AND TOTAL MATERIAL USE

            category = ['internal', 'preconsumer', 'postconsumer', 'postconsumer_dismantling', 'postconsumer_pst', 'virgin']    # , to_openloop', 'to_closedloop'

            for c in category:

                material_use.loc[t, f'steel_{c}'] = (
                    material_use.loc[t, f'flatsteel_{c}'] +
                    material_use.loc[t, f'longsteel_{c}']
                )

                material_use.loc[t, f'aluminum_{c}'] = (
                    material_use.loc[t, f'wroughtaluminum_{c}'] +
                    material_use.loc[t, f'castaluminum_lowCu_{c}'] + 
                    material_use.loc[t, f'castaluminum_highCu_{c}']
                )

                material_use.loc[t, f'total_{c}'] = (
                    material_use.loc[t, f'steel_{c}'] +
                    material_use.loc[t, f'aluminum_{c}']
                )

        # (d) MATERIAL QAULITY IN PRODUCTION

        steel_types = ['flatsteel', 'flatsteel', 'flatsteel', 'longsteel', 'longsteel', 'longsteel']
        aluminum_types = ['wroughtaluminum', 'castaluminum_lowCu', 'castaluminum_highCu']
        suffixes = ['s1', 's2', 's3', 's1', 's2', 's3']

        for t in set_years:

            # For steel:

            flatsteel_qf_threshold = steel_production.loc[t, 'flatsteel_threshold']
            longsteel_qf_threshold = steel_production.loc[t, 'longsteel_threshold']

            qf_internal = [
                flatsteel_qf_threshold,
                flatsteel_qf_threshold,
                flatsteel_qf_threshold,
                longsteel_qf_threshold,
                longsteel_qf_threshold,
                longsteel_qf_threshold
            ]

            flatsteel_qf_preconsumer = flatsteel_qf_threshold
            longsteel_qf_preconsumer = longsteel_qf_threshold

            flatsteel_qf_postconsumer_dismantling = [
                flatsteel_qf_threshold[i] + eol_dismantling_recycling.loc[t, 'flatsteel_contamination'][i]
                for i in range(steel_n_thresholds)
            ]
            longsteel_qf_postconsumer_dismantling = [
                longsteel_qf_threshold[i] + eol_dismantling_recycling.loc[t, 'longsteel_contamination'][i]
                for i in range(steel_n_thresholds)
            ]

            steel_qf_postconsumer_pst = [
                eol_pst.loc[t, 'steel_quality'][i] + eol_pst.loc[t, 'steel_contamination'][i]
                for i in range(steel_n_thresholds)
            ]

            steel_qf_virgin = steel_production.loc[t, 'virgin_steel_quality']

            p_idx = 0

            for p in steel_processes:

                denominator = (
                    internal_steel[p_idx][t].X +
                    preconsumer_flatsteel[t,p].X +
                    preconsumer_longsteel[t,p].X +
                    postconsumer_dismantling_flatsteel[t,p].X +
                    postconsumer_dismantling_longsteel[t,p].X +
                    postconsumer_pst_steel[t,p].X +
                    virgin_steel[t,p].X
                )

                col = f'{steel_types[p_idx]}_quality_{suffixes[p_idx]}'

                if col not in material_quality.columns:
                    material_quality[col] = [[0.0] * steel_n_thresholds for _ in set_years]

                if denominator > 0:
                    material_quality.at[t, col] = [
                        (
                            internal_steel[p_idx][t].X * qf_internal[p_idx][i] +
                            preconsumer_flatsteel[t,p].X * flatsteel_qf_preconsumer[i] +
                            preconsumer_longsteel[t,p].X * longsteel_qf_preconsumer[i] +
                            postconsumer_dismantling_flatsteel[t,p].X * flatsteel_qf_postconsumer_dismantling[i] +
                            postconsumer_dismantling_longsteel[t,p].X * longsteel_qf_postconsumer_dismantling[i] +
                            postconsumer_pst_steel[t,p].X * steel_qf_postconsumer_pst[i] +
                            virgin_steel[t,p].X * steel_qf_virgin[i]
                        ) / denominator
                        for i in range(steel_n_thresholds)
                    ]

                p_idx += 1

            # For aluminum:

            wroughtaluminum_qf_threshold = aluminum_production.loc[t, 'wroughtaluminum_threshold']
            castaluminum_lowCu_qf_threshold = aluminum_production.loc[t, 'castaluminum_lowCu_threshold']
            castaluminum_highCu_qf_threshold = aluminum_production.loc[t, 'castaluminum_highCu_threshold']

            qf_internal = [
                wroughtaluminum_qf_threshold,
                castaluminum_lowCu_qf_threshold,
                castaluminum_highCu_qf_threshold
            ]

            wroughtaluminum_qf_preconsumer = wroughtaluminum_qf_threshold
            castaluminum_lowCu_qf_preconsumer = castaluminum_lowCu_qf_threshold
            castaluminum_highCu_qf_preconsumer = castaluminum_highCu_qf_threshold

            wroughtaluminum_qf_postconsumer_dismantling = [
                wroughtaluminum_qf_threshold[i] + eol_dismantling_recycling.loc[t, 'wroughtaluminum_contamination'][i]
                for i in range(aluminum_n_thresholds)
            ]
            castaluminum_lowCu_qf_postconsumer_dismantling = [
                castaluminum_lowCu_qf_threshold[i] + eol_dismantling_recycling.loc[t, 'castaluminum_lowCu_contamination'][i]
                for i in range(aluminum_n_thresholds)
            ]
            castaluminum_highCu_qf_postconsumer_dismantling = [
                castaluminum_highCu_qf_threshold[i] + eol_dismantling_recycling.loc[t, 'castaluminum_highCu_contamination'][i]
                for i in range(aluminum_n_thresholds)
            ]

            mixedaluminum_qf_postconsumer_pst = [
                eol_pst.loc[t, 'mixedaluminum_quality'][i] + eol_pst.loc[t, 'mixedaluminum_contamination'][i]
                for i in range(aluminum_n_thresholds)
            ]
            wroughtaluminum_qf_postconsumer_pst = [
                wroughtaluminum_qf_threshold[i] + eol_pst.loc[t, 'wroughtaluminum_contamination'][i]
                for i in range(aluminum_n_thresholds)
            ]
            castaluminum_lowCu_qf_postconsumer_pst = [
                castaluminum_lowCu_qf_threshold[i] + eol_pst.loc[t, 'castaluminum_lowCu_contamination'][i]
                for i in range(aluminum_n_thresholds)
            ]
            castaluminum_highCu_qf_postconsumer_pst = [
                castaluminum_highCu_qf_threshold[i] + eol_pst.loc[t, 'castaluminum_highCu_contamination'][i]
                for i in range(aluminum_n_thresholds)
            ]

            qf_virgin = [
               aluminum_production.loc[t, 'virgin_wroughtaluminum_quality'],
                aluminum_production.loc[t, 'virgin_castaluminum_lowCu_quality'],
                aluminum_production.loc[t, 'virgin_castaluminum_highCu_quality']
           ]

            p_idx = 0

            for p in aluminum_processes:

                denominator = (
                    internal_aluminum[p_idx][t].X +
                    preconsumer_wroughtaluminum[t,p].X +
                    preconsumer_castaluminum_lowCu[t,p].X +
                    preconsumer_castaluminum_highCu[t,p].X +
                    postconsumer_dismantling_wroughtaluminum[t,p].X +
                    postconsumer_dismantling_castaluminum_lowCu[t,p].X +
                    postconsumer_dismantling_castaluminum_highCu[t,p].X +
                    postconsumer_pst_mixedaluminum[t,p].X +
                    postconsumer_pst_wroughtaluminum[t,p].X +
                    postconsumer_pst_castaluminum_lowCu[t,p].X +
                    postconsumer_pst_castaluminum_highCu[t,p].X +
                    virgin_aluminum[t,p].X
                )

                col = f'{aluminum_types[p_idx]}_quality'

                if col not in material_quality.columns:
                    material_quality[col] = [[0.0] * aluminum_n_thresholds for _ in set_years]

                if denominator > 0:
                    material_quality.at[t, col] = [
                        (
                            internal_aluminum[p_idx][t].X * qf_internal[p_idx][i] +
                            preconsumer_wroughtaluminum[t,p].X * wroughtaluminum_qf_preconsumer[i] +
                            preconsumer_castaluminum_lowCu[t,p].X * castaluminum_lowCu_qf_preconsumer[i] +
                            preconsumer_castaluminum_highCu[t,p].X * castaluminum_highCu_qf_preconsumer[i] +
                            postconsumer_dismantling_wroughtaluminum[t,p].X * wroughtaluminum_qf_postconsumer_dismantling[i] +
                            postconsumer_dismantling_castaluminum_lowCu[t,p].X * castaluminum_lowCu_qf_postconsumer_dismantling[i] +
                            postconsumer_dismantling_castaluminum_highCu[t,p].X * castaluminum_highCu_qf_postconsumer_dismantling[i] +
                            postconsumer_pst_mixedaluminum[t,p].X * mixedaluminum_qf_postconsumer_pst[i] +
                            postconsumer_pst_wroughtaluminum[t,p].X * wroughtaluminum_qf_postconsumer_pst[i] +
                            postconsumer_pst_castaluminum_lowCu[t,p].X * castaluminum_lowCu_qf_postconsumer_pst[i] +
                            postconsumer_pst_castaluminum_highCu[t,p].X * castaluminum_highCu_qf_postconsumer_pst[i] +
                            virgin_aluminum[t,p].X * qf_virgin[p_idx][i]
                        ) / denominator
                        for i in range(aluminum_n_thresholds)
                    ]
                
                p_idx += 1
                

        print('   modeling material use by optimization done.')

    elif model.status == GRB.INFEASIBLE:
        obj_value = -1
        print('   (!) optimization model is infeasible.')

        # Debugging:

        try:
            # Re-solve without presolve so IIS can be computed on the full model
            model.setParam('Presolve', 0)
            model.optimize()
            model.computeIIS()
            
            for c in model.getConstrs():
                if c.IISConstr:
                    print(f'        - INFEASIBLE CONSTRAINT: {c.ConstrName}')
            for v in model.getVars():
                if v.IISLB or v.IISUB:
                    print(f'        - INFEASIBLE BOUND: {v.VarName}')

        except Exception as e:
            print(f'       IIS failed: {e}')

    elif model.status == GRB.UNBOUNDED:
        obj_value = -1
        print('   (!) optimization model is unbounded.')

    else:
        obj_value = -1
        print('   no optimal solution could be found.')


    return material_use, material_quality, obj_value, eol_pst
