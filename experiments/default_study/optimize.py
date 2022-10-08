import argparse
import logging
from random import Random, random
import sys
import os
import multineat

from genotype import random as random_genotype
from optimizer import Optimizer

from revolve2.core.database import open_async_database_sqlite
from revolve2.core.optimization import ProcessIdGen
from revolve2.core.config import Config


async def main() -> None:

    args = Config()._get_params()

    mainpath = os.getlogin() # current user's username

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
    )

    logging.info(f"Starting optimization")

    # prepares params for environmental conditions
    seasonal_conditions_parsed = []
    seasonal_conditions = args.seasons_conditions.split('#')
    for seasonal_condition in seasonal_conditions:
        params = seasonal_condition.split('_')
        seasonal_conditions_parsed.append([params[0], params[1], params[2]])

    # random number generator
    rng = Random()
    rng.seed(random())

    # database
    database = open_async_database_sqlite(f'/storage/{mainpath}/{args.study_name}/{args.experiment_name}/run_{args.run}')
    print(args.experiment)

    # process id generator
    process_id_gen = ProcessIdGen()

    # multineat innovation databases
    innov_db_body = multineat.InnovationDatabase()
    innov_db_brain = multineat.InnovationDatabase()

    process_id = process_id_gen.gen()

    maybe_optimizer = await Optimizer.from_database(
        database=database,
        process_id=process_id,
        innov_db_body=innov_db_body,
        innov_db_brain=innov_db_brain,
        rng=rng,
        process_id_gen=process_id_gen,
        run_simulation=args.run_simulation,
        num_generations=args.num_generations,
    )

    if maybe_optimizer is not None:
        optimizer = maybe_optimizer
    else:

        initial_population = [
            random_genotype(innov_db_body, innov_db_brain, rng, args.num_initial_mutations,
                            len(seasonal_conditions_parsed), args.plastic_body, args.plastic_brain)
            for _ in range(args.population_size)
        ]

        optimizer = await Optimizer.new(
            database=database,
            process_id=process_id,
            initial_population=initial_population,
            rng=rng,
            process_id_gen=process_id_gen,
            innov_db_body=innov_db_body,
            innov_db_brain=innov_db_brain,
            simulation_time=args.simulation_time,
            sampling_frequency=args.sampling_frequency,
            control_frequency=args.control_frequency,
            num_generations=args.num_generations,
            fitness_measure=args.fitness_measure,
            offspring_size=args.offspring_size,
            experiment_name=args.experiment_name,
            max_modules=args.max_modules,
            crossover_prob=args.crossover_prob,
            mutation_prob=args.mutation_prob,
            substrate_radius=args.substrate_radius,
            run_simulation=args.run_simulation,
            env_conditions=seasonal_conditions_parsed,
            plastic_body=args.plastic_body,
            plastic_brain=args.plastic_brain
        )
    
    logging.info("Starting optimization process..")

    await optimizer.run()

    logging.info(f"Finished optimizing.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
