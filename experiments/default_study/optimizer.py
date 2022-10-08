import math
import pickle
from random import Random
from typing import List, Tuple

import multineat
import sqlalchemy
from genotype import Genotype, GenotypeSerializer, crossover, develop, mutate
from pyrr import Quaternion, Vector3
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select

import revolve2.core.optimization.ea.generic_ea.population_management as population_management
import revolve2.core.optimization.ea.generic_ea.selection as selection
from revolve2.actor_controller import ActorController
from revolve2.core.database import IncompatibleError
from revolve2.core.database.serializers import FloatSerializer, StatesSerializer
from revolve2.core.optimization import ProcessIdGen
from revolve2.core.modular_robot import Measure

from revolve2.core.optimization.ea.generic_ea import EAOptimizer
import numpy as np
import pprint


from revolve2.core.physics.running import (
    ActorControl,
    ActorState,
    Batch,
    Environment,
    PosedActor,
    Runner,
)
from revolve2.runners.isaacgym import LocalRunner


class Optimizer(EAOptimizer[Genotype, float]):
    _process_id: int

    _runner: Runner

    _controllers: List[ActorController]

    _innov_db_body: multineat.InnovationDatabase
    _innov_db_brain: multineat.InnovationDatabase

    _rng: Random

    _simulation_time: int
    _sampling_frequency: float
    _control_frequency: float

    _num_generations: int
    _offspring_size: int
    _fitness_measure: str
    _experiment_name: str
    _max_modules: int
    _crossover_prob: float
    _mutation_prob: float
    _substrate_radius: str
    _run_simulation: bool
    _env_conditions: List
    _plastic_body = int
    _plastic_brain = int

    async def ainit_new(  # type: ignore # TODO for now ignoring mypy complaint about LSP problem, override parent's ainit
        self,
        database: AsyncEngine,
        session: AsyncSession,
        process_id: int,
        process_id_gen: ProcessIdGen,
        initial_population: List[Genotype],
        rng: Random,
        innov_db_body: multineat.InnovationDatabase,
        innov_db_brain: multineat.InnovationDatabase,
        simulation_time: int,
        sampling_frequency: float,
        control_frequency: float,
        num_generations: int,
        offspring_size: int,
        fitness_measure: str,
        experiment_name: str,
        max_modules: int,
        crossover_prob: float,
        mutation_prob: float,
        substrate_radius: str,
        run_simulation: bool,
        env_conditions: List,
        plastic_body: int,
        plastic_brain: int
    ) -> None:
        await super().ainit_new(
            database=database,
            session=session,
            process_id=process_id,
            process_id_gen=process_id_gen,
            genotype_type=Genotype,
            genotype_serializer=GenotypeSerializer,
            states_serializer=StatesSerializer,
            measures_type=float,
            measures_serializer=FloatSerializer,
            initial_population=initial_population,
            fitness_measure=fitness_measure,
            offspring_size=offspring_size,
            experiment_name=experiment_name,
            max_modules=max_modules,
            crossover_prob=crossover_prob,
            mutation_prob=mutation_prob,
            substrate_radius=substrate_radius,
            run_simulation=run_simulation,
            env_conditions=env_conditions,
            plastic_body=plastic_body,
            plastic_brain=plastic_brain
        )

        self._process_id = process_id
        self._env_conditions = env_conditions
        self._init_runner()
        self._innov_db_body = innov_db_body
        self._innov_db_brain = innov_db_brain
        self._rng = rng
        self._simulation_time = simulation_time
        self._sampling_frequency = sampling_frequency
        self._control_frequency = control_frequency
        self._num_generations = num_generations
        self._fitness_measure = fitness_measure
        self._offspring_size = offspring_size
        self._experiment_name = experiment_name
        self._max_modules = max_modules
        self._crossover_prob = crossover_prob
        self._mutation_prob = mutation_prob
        self._substrate_radius = substrate_radius
        self._plastic_body = plastic_body,
        self._plastic_brain = plastic_brain
        self._run_simulation = run_simulation

        # create database structure if not exists
        # TODO this works but there is probably a better way
        await (await session.connection()).run_sync(DbBase.metadata.create_all)

        # save to database
        self._on_generation_checkpoint(session)

    async def ainit_from_database(  # type: ignore # see comment at ainit_new
        self,
        database: AsyncEngine,
        session: AsyncSession,
        process_id: int,
        process_id_gen: ProcessIdGen,
        rng: Random,
        innov_db_body: multineat.InnovationDatabase,
        innov_db_brain: multineat.InnovationDatabase,
        run_simulation: int,
        num_generations: int
    ) -> bool:
        if not await super().ainit_from_database(
            database=database,
            session=session,
            process_id=process_id,
            process_id_gen=process_id_gen,
            genotype_type=Genotype,
            genotype_serializer=GenotypeSerializer,
            states_serializer=StatesSerializer,
            measures_type=float,
            measures_serializer=FloatSerializer,
            run_simulation=run_simulation,
        ):
            return False

        self._process_id = process_id
        self._init_runner()

        opt_row = (
            (
                await session.execute(
                    select(DbOptimizerState)
                    .filter(DbOptimizerState.process_id == process_id)
                    .order_by(DbOptimizerState.generation_index.desc())
                )
            )
            .scalars()
            .first()
        )

        # if this happens something is wrong with the database
        if opt_row is None:
            raise IncompatibleError
            raise IncompatibleError

        self._simulation_time = opt_row.simulation_time
        self._sampling_frequency = opt_row.sampling_frequency
        self._control_frequency = opt_row.control_frequency
        self._num_generations = num_generations

        self._rng = rng
        self._rng.setstate(pickle.loads(opt_row.rng))

        self._innov_db_body = innov_db_body
        self._innov_db_body.Deserialize(opt_row.innov_db_body)
        self._innov_db_brain = innov_db_brain
        self._innov_db_brain.Deserialize(opt_row.innov_db_brain)
        self._run_simulation = run_simulation

        return True

    def _init_runner(self) -> None:
        self._runner = {}
        for env in self.env_conditions:
            # TODO: can we make the headless var automatically update depending on whether we are running on a Ripper
            #  or remote?
            self._runner[env] = (LocalRunner(LocalRunner.SimParams(), headless=True, env_conditions=self.env_conditions[env]))

    def _select_parents(
        self,
        population: List[Genotype],
        fitnesses: List[float],
        num_parent_groups: int,
    ) -> List[List[int]]:

        # TODO: allow variable number
        #  and adapt the to_database to take the crossover probabilistic choice into consideration
        if self.crossover_prob == 0:
            number_of_parents = 1
        else:
            number_of_parents = 2

        return [
            selection.multiple_unique(
                population,
                fitnesses,
                number_of_parents,
                lambda _, fitnesses: selection.tournament(self._rng, fitnesses, k=2),
            )
            for _ in range(num_parent_groups)
        ]

    def _select_survivors(
        self,
        old_individuals: List[Genotype],
        old_fitnesses: List[float],
        new_individuals: List[Genotype],
        new_fitnesses: List[float],
        num_survivors: int,
    ) -> Tuple[List[int], List[int]]:

        assert len(old_individuals) == num_survivors

        return population_management.steady_state(
            old_individuals,
            old_fitnesses,
            new_individuals,
            new_fitnesses,
            lambda _, fitnesses: selection.tournament(self._rng, fitnesses, k=2),
        )

    def _must_do_next_gen(self) -> bool:
        return self.generation_index != self._num_generations

    def _crossover(self, parents: List[Genotype]) -> Genotype:
        if self._rng.uniform(0, 1) > self.crossover_prob:
            return parents[0]
        else:
            return crossover(parents[0], parents[1], self._rng)

    def _mutate(self, genotype: Genotype) -> Genotype:
        if self._rng.uniform(0, 1) > self.mutation_prob:
            return genotype
        else:
            return mutate(genotype, self._innov_db_body, self._innov_db_brain, self._rng)

    async def _evaluate_generation(
            self,
            genotypes: List[Genotype],
            database: AsyncEngine,
            process_id: int,
            process_id_gen: ProcessIdGen,
    ) -> List[float]:

        envs_measures_genotypes = {}
        envs_states_genotypes = {}
        envs_queried_substrates = {}

        for cond in self.env_conditions:

            batch = Batch(
                simulation_time=self._simulation_time,
                sampling_frequency=self._sampling_frequency,
                control_frequency=self._control_frequency,
                control=self._control,
            )

            self._controllers = []
            phenotypes = []
            queried_substrates = []

            for genotype in genotypes:
                phenotype, queried_substrate = develop(genotype, genotype.mapping_seed, self.max_modules,
                                                       self.substrate_radius,
                                                       self.env_conditions[cond], len(self.env_conditions),
                                                       self.plastic_body, self.plastic_brain)
                phenotypes.append(phenotype)
                queried_substrates.append(queried_substrate)

                actor, controller = phenotype.make_actor_and_controller()
                bounding_box = actor.calc_aabb()
                self._controllers.append(controller)
                env = Environment()

                x_rotation_degrees = float(self.env_conditions[cond][2])
                robot_rotation = x_rotation_degrees * np.pi / 180
                env.actors.append(
                    PosedActor(
                        actor,
                        Vector3(
                            [
                                0.0,
                                0.0,
                                (bounding_box.size.z / 2.0 - bounding_box.offset.z),
                            ]
                        ),
                        Quaternion.from_eulers([robot_rotation, 0, 0]),
                        [0.0 for _ in controller.get_dof_targets()],
                    )
                )
                batch.environments.append(env)

            envs_queried_substrates[cond] = queried_substrates

            if self._run_simulation:
                states = await self._runner[cond].run_batch(batch)
            else:
                states = None

            measures_genotypes = []
            for i, phenotype in enumerate(phenotypes):
                m = Measure(states=states, genotype_idx=i, phenotype=phenotype, \
                            generation=self.generation_index, simulation_time=self._simulation_time)
                measures_genotypes.append(m.measure_all_non_relative())
            envs_measures_genotypes[cond] = measures_genotypes

            states_genotypes = []
            if states is not None:
                for idx_genotype in range(0, len(states.environment_results)):
                    states_genotypes.append({})
                    for idx_state in range(0, len(states.environment_results[idx_genotype].environment_states)):
                        states_genotypes[-1][idx_state] = \
                            states.environment_results[idx_genotype].environment_states[idx_state].actor_states[
                                0].serialize()
            envs_states_genotypes[cond] = states_genotypes

        envs_measures_genotypes = self.measure_plasticity(envs_queried_substrates, envs_measures_genotypes)

        return envs_measures_genotypes, envs_states_genotypes

    def measure_plasticity(self, envs_queried_substrates, envs_measures_genotypes):

        if len(self.env_conditions) > 1:
            # TODO: this works only for two seasons
            first_cond = list(self.env_conditions.keys())[0]
            second_cond = list(self.env_conditions.keys())[1]
            for idg in range(0, len(envs_queried_substrates[first_cond])):

                keys_first = set(envs_queried_substrates[first_cond][idg].keys())
                keys_second = set(envs_queried_substrates[second_cond][idg].keys())
                intersection = keys_first & keys_second
                disjunct_first = [a for a in keys_first if a not in intersection]
                disjunct_second = [b for b in keys_second if b not in intersection]
                body_changes = len(disjunct_first) + len(disjunct_second)

                for i in intersection:
                    if type(envs_queried_substrates[first_cond][idg][i]) != type(envs_queried_substrates[second_cond][idg][i]):
                        body_changes += 1

                envs_measures_genotypes[first_cond][idg]['body_changes'] = body_changes
                envs_measures_genotypes[second_cond][idg]['body_changes'] = body_changes
        else:
            any_cond = list(self.env_conditions.keys())[0]
            for idg in range(0, len(envs_queried_substrates[any_cond])):
                envs_measures_genotypes[any_cond][idg]['body_changes'] = 0

        return envs_measures_genotypes

    def _control(self, dt: float, control: ActorControl) -> None:
        for control_i, controller in enumerate(self._controllers):
            controller.step(dt)
            control.set_dof_targets(control_i, 0, controller.get_dof_targets())
            
    def _on_generation_checkpoint(self, session: AsyncSession) -> None:
        session.add(
            DbOptimizerState(
                process_id=self._process_id,
                generation_index=self.generation_index,
                rng=pickle.dumps(self._rng.getstate()),
                innov_db_body=self._innov_db_body.Serialize(),
                innov_db_brain=self._innov_db_brain.Serialize(),
                simulation_time=self._simulation_time,
                sampling_frequency=self._sampling_frequency,
                control_frequency=self._control_frequency,
            )
        )


DbBase = declarative_base()


class DbOptimizerState(DbBase):
    __tablename__ = "optimizer"

    process_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        primary_key=True,
    )
    generation_index = sqlalchemy.Column(
        sqlalchemy.Integer, nullable=False, primary_key=True
    )
    rng = sqlalchemy.Column(sqlalchemy.PickleType, nullable=False)
    innov_db_body = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    innov_db_brain = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    simulation_time = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    sampling_frequency = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    control_frequency = sqlalchemy.Column(sqlalchemy.Float, nullable=False)

