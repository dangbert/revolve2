import math
from dataclasses import dataclass
from queue import Queue
from typing import Any, List, Optional, Set, Tuple

import multineat

from revolve2.core.modular_robot import ActiveHinge, Body, Brick, Core, Module

from .._genotype import Genotype
from .._random_v1 import random_v1 as base_random_v1


def random_v1(
    innov_db: multineat.InnovationDatabase,
    rng: multineat.RNG,
    multineat_params: multineat.Parameters,
    output_activation_func: multineat.ActivationFunction,
    num_initial_mutations: int,
) -> Genotype:
    return base_random_v1(
        innov_db,
        rng,
        multineat_params,
        output_activation_func,
        5,  # bias(always 1), pos_x, pos_y, pos_z, chain_length
        5,  # empty, brick, activehinge, rot0, rot90
        num_initial_mutations,
    )


@dataclass
class __Module:
    position: Tuple[int, int, int]
    forward: Tuple[int, int, int]
    up: Tuple[int, int, int]
    chain_length: int
    module_reference: Module


def develop_v1(
    genotype: Genotype,
    max_modules: int,
    body_substrate_dimensions: str
) -> Body:

    body_net = multineat.NeuralNetwork()
    genotype.genotype.BuildPhenotype(body_net)

    to_explore: Queue[__Module] = Queue()
    grid: Set[Tuple[int, int, int]] = set()

    body = Body()
    to_explore.put(__Module((0, 0, 0), (0, -1, 0), (0, 0, 1), 0, body.core))
    grid.add((0, 0, 0))
    part_count = 1
    while not to_explore.empty():
        module = to_explore.get()

        children: List[Tuple[int, int]] = []  # child index, rotation in increments of 90 degrees
        if isinstance(module.module_reference, Core):
            children.append((Core.FRONT, 0))
            children.append((Core.LEFT, 1))
            children.append((Core.BACK, 2))
            children.append((Core.RIGHT, 3))
        elif isinstance(module.module_reference, Brick):
            children.append((Brick.FRONT, 0))
            children.append((Brick.LEFT, 1))
            children.append((Brick.RIGHT, 3))
        elif isinstance(module.module_reference, ActiveHinge):
            children.append((ActiveHinge.ATTACHMENT, 0))
        else:  # Should actually never arrive here but just checking module type to be sure
            raise RuntimeError()

        for (index, rotation) in children:
            if part_count < max_modules:
                child = ___add_child(body_net, module, index, rotation, grid, body_substrate_dimensions)
                if child is not None:
                    to_explore.put(child)
                    part_count += 1

    body.finalize()
    return body


def __evaluate_cppn(
    body_net: multineat.NeuralNetwork,
    position: Tuple[int, int, int],
    chain_length: int,
    body_substrate_dimensions: str
) -> Tuple[Any, int]:
    """
    get module type, orientation
    """
    body_net.Input(
        [1.0, position[0], position[1], position[2], chain_length]
    )  # 1.0 is the bias input
    body_net.ActivateAllLayers()
    outputs = body_net.Output()

    # get module type from output probabilities
    type_probs = [outputs[0], outputs[1], outputs[2]]
    types = [None, Brick, ActiveHinge]
    module_type = types[type_probs.index(min(type_probs))]

    # get rotation from output probabilities
    rotation_probs = [outputs[3], outputs[4]]

    if body_substrate_dimensions == '2d':
        rotation = 0
    else:
        rotation = rotation_probs.index(min(rotation_probs))

    return (module_type, rotation)


def ___add_child(
    body_net: multineat.NeuralNetwork,
    module: __Module,
    child_index: int,
    rotation: int,
    grid: Set[Tuple[int, int, int]],
    body_substrate_dimensions: str
) -> Optional[__Module]:
    forward = __rotate(module.forward, module.up, rotation)
    position = __add(module.position, forward)
    chain_length = module.chain_length + 1

    # if grid cell is occupied, don't make a child
    # else, set cell as occupied
    if position in grid:
        return None
    else:
        grid.add(position)

    child_type, orientation = __evaluate_cppn(body_net, position, chain_length, body_substrate_dimensions)
    if child_type is None:
        return None
    up = __rotate(module.up, forward, orientation)
    print(orientation, orientation * (math.pi / 2.0))
    child = child_type(orientation * (math.pi / 2.0))
    module.module_reference.children[child_index] = child

    return __Module(
        position,
        forward,
        up,
        chain_length,
        child,
    )


def __add(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def __timesscalar(a: Tuple[int, int, int], scalar: int) -> Tuple[int, int, int]:
    return (a[0] * scalar, a[1] * scalar, a[2] * scalar)


def __cross(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> Tuple[int, int, int]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def __dot(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def __rotate(
    a: Tuple[int, int, int], b: Tuple[int, int, int], angle: int
) -> Tuple[int, int, int]:
    """
    rotates a around b. angle from [0,1,2,3]. 90 degrees each
    """
    cosangle: int
    sinangle: int
    if angle == 0:
        cosangle = 1
        sinangle = 0
    elif angle == 1:
        cosangle = 0
        sinangle = 1
    elif angle == 2:
        cosangle = -1
        sinangle = 0
    else:
        cosangle = 0
        sinangle = -1

    return __add(
        __add(
            __timesscalar(a, cosangle),
            __timesscalar(__cross(b, a), sinangle),
        ),
        __timesscalar(b, __dot(b, a) * (1 - cosangle)),
    )
