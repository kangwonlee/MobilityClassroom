"""
Test cases for .../utils/func.py file
"""
import configparser
import math
import os
import sys
import tempfile

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


@pytest.fixture
def ky() -> float:
    return 1.0


@pytest.fixture
def ka() -> float:
    return 2.0


@pytest.fixture
def kcv() -> float:
    return 3.0


@pytest.fixture
def kcl() -> float:
    return 4.0


@pytest.fixture
def Vmax() -> float:
    return 5.0


@pytest.fixture
def Aymax() -> float:
    return 6.0


@pytest.fixture
def cfg_file_normal(ky, ka, kcv, kcl, Vmax, Aymax):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        name = f.name
        f.write(f"{ky}\n")
        f.write(f"{ka}\n")
        f.write(f"{kcv}\n")
        f.write(f"{kcl}\n")
        f.write(f"{Vmax}\n")
        f.write(f"{Aymax}\n")
    assert os.path.exists(name)
    yield name
    # remove config file after test
    os.remove(name)


def test_read_gain__normal(cfg_file_normal, ky, ka, kcv, kcl, Vmax, Aymax):
    result = func.read_gain(cfg_file_normal)

    assert math.isclose(result[0], ky)
    assert math.isclose(result[1], ka)
    assert math.isclose(result[2], kcv)
    assert math.isclose(result[3], kcl)
    assert math.isclose(result[4], Vmax)
    assert math.isclose(result[5], Aymax)
