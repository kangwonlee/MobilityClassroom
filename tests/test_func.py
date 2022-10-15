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
    txt = (
        f"lateral distance gain: {ky}\n"
        f"angle gain: {ka}     \n"
        f"lane curvature gain: {kcv}     \n"
        f"clearance gain for stop: {kcl}    \n"
        f"vehicle velocity max(lower than 1.5): {Vmax}\n"
        f"velocity lateral acceleration max: {Aymax}\n"
        "\n"
        "\n"
        "##########################################\n"
        "For memo \n"
        "##########################################\n"
        "lateral distance gain: 0\n"
        "angle gain: 0     \n"
        "lane curvature gain: 0     \n"
        "clearance gain for stop: 0    \n"
        "vehicle velocity max(lower than 1.5): 0\n"
        "velocity lateral acceleration max: 0\n"
        "##########################################\n"
        "\n"
    )
    with tempfile.NamedTemporaryFile(mode="wt", delete=False) as f:
        name = f.name
        f.write(txt)
    assert os.path.exists(name)
    yield name
    # remove config file after test
    os.remove(name)


def test_read_cfg__normal(cfg_file_normal, ky, ka, kcv, kcl, Vmax, Aymax):
    result = func.read_cfg(cfg_file_normal)

    for k, v in enumerate(result):
        assert isinstance(v, float), f"result[{k}] = {result[k]}"

    assert math.isclose(result[0], ky)
    assert math.isclose(result[1], ka)
    assert math.isclose(result[2], kcv)
    assert math.isclose(result[3], kcl)
    assert math.isclose(result[4], Vmax)
    assert math.isclose(result[5], Aymax)
