"""
Test cases for .../utils/func.py file
"""
import configparser
import math
import os
import random
import sys
import tempfile


from typing import List


import pytest

src2_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "src", "New Mobility",
    )
)

assert os.path.exists(src2_path), (
    f"unable to find {src2_path}\n"
    f"current folder = {os.path.abspath(os.curdir)}"
)

utils_path = os.path.abspath(
    os.path.join(src2_path, "utils"
    )
)

assert os.path.exists(utils_path), (
    f"unable to find {utils_path}\n"
    f"current folder = {os.path.abspath(os.curdir)}"
)

sys.path.insert(0, src2_path,)
sys.path.insert(0, utils_path,)

import func

random.seed()

@pytest.fixture
def r1() -> List[int]
    return [random.randint(100, 199) for k in range(3)]


@pytest.fixture
def r2() -> List[int]
    return [random.randint(200, 255) for k in range(3)]


@pytest.fixture
def g1() -> List[int]
    return [random.randint(10, 49) for k in range(3)]


@pytest.fixture
def g2() -> List[int]
    return [random.randint(50, 99) for k in range(3)]


@pytest.fixture
def b1() -> List[int]
    return [random.randint(1, 4) for k in range(3)]


@pytest.fixture
def b2() -> List[int]
    return [random.randint(5, 9) for k in range(3)]


@pytest.fixture
def rgb_range_file_normal(r1, r2, g1, g2, b1, b2):
    txt = (
        "[range]"
        f"r1 = {r1}\n"
        f"r2= {r2}     \n"
        f"g1 = {g1}     \n"
        f"g2 = {g2}    \n"
        f"b1 = {b1}\n"
        f"b2 = {b2}\n"
    )

    with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
        name = f.name
        f.write(txt)

    assert os.path.exists(name)

    # run test
    yield name

    # remove config file after test
    os.remove(name)


def test_read_rgb_range__normal(rgb_range_file_normal, r1, r2, g1, g2, b1, b2):
    result = func.read_rgb_range(rgb_range_file_normal)

    for k, v in enumerate(result):
        assert isinstance(v, int), f"result[{k}] = {result[k]}"

    assert math.isclose(result[0], r1)
    assert math.isclose(result[1], r2)
    assert math.isclose(result[2], g1)
    assert math.isclose(result[3], g2)
    assert math.isclose(result[4], b1)
    assert math.isclose(result[5], b2)
