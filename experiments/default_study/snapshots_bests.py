from sqlalchemy.ext.asyncio.session import AsyncSession
from revolve2.core.database import open_async_database_sqlite
from sqlalchemy.future import select
from revolve2.core.optimization.ea.generic_ea import DbEAOptimizerGeneration, DbEAOptimizerIndividual, DbEAOptimizer, DbEnvconditions
from revolve2.core.modular_robot.render.render import Render
from genotype import GenotypeSerializer, develop
from revolve2.core.database.serializers import DbFloat

import os
import sys
import argparse
from ast import literal_eval


async def main(parser) -> None:
    study = os.environ['study']
    print('study: ', study)
    runs = int(os.environ['runs'])
    generations = int(os.environ['generations'])
    experiments_name = os.environ['experiments'].split(',')
    runs = list(range(1, runs+1))
    generations = list(map(int, os.environ['generations'].split(',')))
    studypath = os.environ['studypath']

    for experiment_name in experiments_name:
        print(experiment_name)
        for run in runs:
            print(' run: ', run)
            analysis_path = os.path.join(studypath, f'analysis', f'snapshots', experiment_name, f'run_{run}')
            if not os.path.exists(analysis_path):
                os.makedirs(analysis_path)

            db_path = os.path.join(studypath, experiment_name, f'run_{run}')
            db = open_async_database_sqlite(db_path)
            print(f"opening db at '{db_path}'")

            for gen in generations:
                print('  gen: ', gen)
                path_gen = f'{analysis_path}/gen_{gen}'
                if os.path.exists(path_gen):
                    print(f'{path_gen} already exists!')
                else:
                    os.makedirs(path_gen)

                async with AsyncSession(db) as session:

                    rows = ((await session.execute(select(DbEnvconditions).order_by(DbEnvconditions.id))).all())
                    env_conditions = {}
                    for c_row in rows:
                        env_conditions[c_row[0].id] = literal_eval(c_row[0].conditions)
                        os.makedirs(f'{analysis_path}/gen_{gen}/{"_".join(literal_eval(c_row[0].conditions))}')

                    rows = (
                        (await session.execute(select(DbEAOptimizer))).all()
                    )
                    max_modules = rows[0].DbEAOptimizer.max_modules
                    substrate_radius = rows[0].DbEAOptimizer.substrate_radius
                    plastic_body = rows[0].DbEAOptimizer.plastic_body
                    plastic_brain = rows[0].DbEAOptimizer.plastic_brain

                    query = select(DbEAOptimizerGeneration, DbEAOptimizerIndividual, DbFloat)\
                        .filter(DbEAOptimizerGeneration.generation_index.in_([gen])) \
                                                .filter((DbEAOptimizerGeneration.individual_id == DbEAOptimizerIndividual.individual_id)
                                                        & (DbEAOptimizerGeneration.env_conditions_id == DbEAOptimizerIndividual.env_conditions_id)
                                                        & (DbFloat.id == DbEAOptimizerIndividual.float_id)
                                                        )
                    if len(env_conditions) > 1:
                        query = query.order_by(DbEAOptimizerGeneration.seasonal_dominated.desc(),
                                                DbEAOptimizerGeneration.individual_id.asc(),
                                                DbEAOptimizerGeneration.env_conditions_id.asc())
                    else:
                        query = query.order_by(DbFloat.speed_y.desc())

                    rows = ((await session.execute(query)).all())

                    for idx, r in enumerate(rows):
                        #print('geno',r.DbEAOptimizerIndividual.genotype_id)
                        genotype = (
                            await GenotypeSerializer.from_database(
                                session, [r.DbEAOptimizerIndividual.genotype_id]
                            )
                        )[0]

                        phenotype, queried_substrate = develop(genotype, genotype.mapping_seed, max_modules, substrate_radius,
                                            env_conditions[r.DbEAOptimizerGeneration.env_conditions_id],
                                                                len(env_conditions), plastic_body, plastic_brain)
                        render = Render()
                        img_path = f'{path_gen}/{"_".join(env_conditions[r.DbEAOptimizerGeneration.env_conditions_id])}/' \
                                    f'{idx}_{r.DbEAOptimizerIndividual.individual_id}.png'
                        render.render_robot(phenotype.body.core, img_path)

if __name__ == "__main__":
    import asyncio

    parser = argparse.ArgumentParser()
    #parser.add_argument("study")
    #parser.add_argument("experiments")
    #parser.add_argument("runs")
    #parser.add_argument("generations")
    #parser.add_argument("mainpath")

    asyncio.run(main(parser))

# can be run from root