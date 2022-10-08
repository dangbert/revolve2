import argparse

import matplotlib.pyplot as plt
import pandas
from sqlalchemy.future import select
import os
import inspect
import matplotlib.pyplot as plt
import seaborn as sb
from statannot import add_stat_annotation
from itertools import combinations
import pprint
import sys
import math

from revolve2.core.database import open_database_sqlite
from revolve2.core.database.serializers import DbFloat
from revolve2.core.optimization.ea.generic_ea._database import (
    DbEAOptimizerGeneration,
    DbEAOptimizerIndividual
)


class Analysis:

    def __init__(self):

        study = os.environ['study']
        experiments_name = os.environ['experiments'].split(',')
        runs = list(range(1, int(os.environ['runs']) + 1))
        mainpath = os.environ['mainpath']

        self.study = study
        self.experiments = experiments_name
        self.inner_metrics = ['median', 'max']
        self.runs = runs
        # self.final_gen = int(args.final_gen)
        self.final_gen = int(os.environ['final_gen'])

        # self.path = f'/storage/{mainpath}/{study}'
        self.path = f'{mainpath}/{study}'

        self.measures = {
            'pop_diversity': ['Diversity', 0, 1],
            'pool_diversity': ['Pool Diversity', 0, 1],
            'dominated_quality_youth': ['Dominated individuals', 0, 1],
            'fullydominated_quality_youth': ['Fully dominated individuals', 0, 1],
            'seasonal_dominated': ['Seasonal Dominated', 0, 1],
            'age': ['Age', 0, 1],
            'speed_y': ['Speed (cm/s)', 0, 1],
            'relative_speed_y': ['Relative speed (cm/s)', 0, 1],
            'displacement': ['Total displacement (m)', 0, 1],
            'average_z': ['Z', 0, 1],
            'head_balance': ['Balance', 0, 1],
            'modules_count': ['Modules count', 0, 1],
            'hinge_count': ['Hinge count', 0, 1],
            'brick_count': ['Brick count', 0, 1],
            'hinge_prop': ['Hinge prop', 0, 1],
            'hinge_ratio': ['Hinge ratio', 0, 1],
            'brick_prop': ['Brick prop', 0, 1],
            'branching_count': ['Branching count', 0, 1],
            'branching_prop': ['Branching prop', 0, 1],
            'extremities': ['Extremities', 0, 1],
            'extensiveness': ['Extensiveness', 0, 1],
            'extremities_prop': ['Extremities prop', 0, 1],
            'extensiveness_prop': ['Extensiveness prop', 0, 1],
            'width': ['Width', 0, 1],
            'height': ['Height', 0, 1],
            'coverage': ['Coverage', 0, 1],
            'proportion': ['Proportion', 0, 1],
            'symmetry': ['Symmetry', 0, 1]}

    def consolidate(self):
        print('consolidating...')

        if not os.path.exists(self.path):
            os.makedirs(self.path)
        if not os.path.exists(f'{self.path}/analysis/basic_plots'):
            os.makedirs(f'{self.path}/analysis/basic_plots')

        all_df = None
        for experiment in self.experiments:
            for run in self.runs:
                print(experiment, run)
                db = open_database_sqlite(f'{self.path}/{experiment}/run_{run}')

                # read the optimizer data into a pandas dataframe
                df = pandas.read_sql(
                    select(
                        DbEAOptimizerIndividual,
                        DbEAOptimizerGeneration,
                        DbFloat
                    ).filter(
                        (DbEAOptimizerGeneration.individual_id == DbEAOptimizerIndividual.individual_id)
                        & (DbFloat.id == DbEAOptimizerIndividual.float_id)
                    ),
                    db,
                )
                df["experiment"] = experiment
                df["run"] = run

                if all_df is None:
                    all_df = df
                else:
                    all_df = pandas.concat([all_df, df], axis=0)

        all_df = all_df[all_df['generation_index'] <= self.final_gen]

        keys = ['experiment', 'run', 'generation_index', 'env_conditions_id']

        def renamer(col):
            if col not in keys:
                if inspect.ismethod(metric):
                    sulfix = metric.__name__
                else:
                    sulfix = metric
                return col + '_' + sulfix
            else:
                return col

        def groupby(data, measures, metric, keys):
            expr = {x: metric for x in measures}
            df_inner_group = data.groupby(keys).agg(expr).reset_index()
            df_inner_group = df_inner_group.rename(mapper=renamer, axis='columns')
            return df_inner_group

        # inner measurements (within runs)

        df_inner = {}
        for metric in self.inner_metrics:
            df_inner[metric] = groupby(all_df, self.measures.keys(), metric, keys)

        df_inner = pandas.merge(df_inner[self.inner_metrics[0]], df_inner[self.inner_metrics[1]], on=keys)

        # outer measurements (among runs)

        measures_inner = []
        for measure in self.measures.keys():
            for metric in self.inner_metrics:
                measures_inner.append(f'{measure}_{metric}')

        keys = ['experiment', 'generation_index', 'env_conditions_id']
        metric = 'median'
        df_outer_median = groupby(df_inner, measures_inner, metric, keys)

        metric = self.q25
        df_outer_q25 = groupby(df_inner, measures_inner, metric, keys)

        metric = self.q75
        df_outer_q75 = groupby(df_inner, measures_inner, metric, keys)

        df_outer = pandas.merge(df_outer_median, df_outer_q25, on=keys)
        df_outer = pandas.merge(df_outer, df_outer_q75, on=keys)

        all_df.to_csv(f'{self.path}/analysis/all_df.csv', index=True)
        df_inner.to_csv(f'{self.path}/analysis/df_inner.csv', index=True)
        df_outer.to_csv(f'{self.path}/analysis/df_outer.csv', index=True)

        print('consolidated!')

    def q25(self, x):
        return x.quantile(0.25)

    def q75(self, x):
        return x.quantile(0.75)


#TODO: either separate by run or allow resuming

parser = argparse.ArgumentParser()
# parser.add_argument("study")
# parser.add_argument("experiments")
# parser.add_argument("runs")
# parser.add_argument("final_gen")
# parser.add_argument("mainpath")
# args = parser.parse_args()

# TODO: break by environment
analysis = Analysis()
analysis.consolidate()



