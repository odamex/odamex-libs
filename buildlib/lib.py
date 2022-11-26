#
# (C) 2022 Alex "Lexi" Mayfield
#

import os
import platform
import shutil
import subprocess

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal, Optional


SCRIPT_DIR = Path(__file__).parent
BASE_DIR = (SCRIPT_DIR / "..").resolve()
CMAKE_PREFIX_PATH = BASE_DIR / "local"


class CompileFlag(Enum):
    MSVC = 1


@dataclass
class CompileEnv:
    generator: str
    flags: set[CompileFlag]


ENVIRONMENT: Optional[CompileEnv] = None


def environment():
    global ENVIRONMENT

    if not ENVIRONMENT is None:
        return ENVIRONMENT

    ENVIRONMENT = CompileEnv("Visual Studio 17 2022", {CompileFlag.MSVC})
    return ENVIRONMENT


CMAKE_COMMAND: Optional[Path] = None


def cmake_command():
    global CMAKE_COMMAND

    if not CMAKE_COMMAND is None:
        return CMAKE_COMMAND

    path = shutil.which("cmake")
    if path is None:
        raise Exception("Could not find cmake installation")

    CMAKE_COMMAND = Path(path)
    return CMAKE_COMMAND


def libname_static(lib: str):
    if platform.system() == "Windows":
        return f"{lib}.lib"
    else:
        return f"lib{lib}.a"


def lib_buildgen(
    srcdir: Path,
    builddir: Path,
    defines: dict[str, str] = {},
    cxxflags: Optional[list[str]] = None,
):
    args = [
        cmake_command(),
        "-G",
        environment().generator,
        "-S",
        srcdir,
        "-B",
        builddir,
        f"-DCMAKE_PREFIX_PATH={CMAKE_PREFIX_PATH}",
        f"-DCMAKE_INSTALL_PREFIX={CMAKE_PREFIX_PATH}",
    ]
    for key, val in defines.items():
        args.append(f"-D{key}={val}")

    env = os.environ.copy()
    if not cxxflags is None:
        env["CXXFLAGS"] = " ".join(cxxflags)

    subprocess.run(args, env=env)


def lib_build(
    builddir: Path, config: Optional[str] = None, target: Optional[str] = None
):
    args = [cmake_command(), "--build", builddir]
    if not config is None:
        args.extend(["--config", config])
    if not target is None:
        args.extend(["--target", target])
    subprocess.run(args)


def cmake_build(
    libname: str,
    lang: Literal["c"] | Literal["cxx"] = "c",
    config: str = "RelWithDebInfo",
    defines: dict[str, str] = {},
    cxxflags: Optional[list[str]] = None,
    srcdir: Optional[Path] = None,
):
    if srcdir is None:
        srcdir = BASE_DIR / "libraries" / libname
    builddir = BASE_DIR / "build" / libname

    lib_buildgen(srcdir=srcdir, builddir=builddir, defines=defines, cxxflags=cxxflags)
    if lang == "cxx":
        lib_build(builddir=builddir, config="Debug", target="install")
    lib_build(builddir=builddir, config=config, target="install")


def git_submodule(path: str, repo: Optional[str] = None):
    git_cmd = ["git"]
    if not repo is None:
        git_cmd.extend(["-C", str((BASE_DIR / repo).absolute())])

    subprocess.run(git_cmd + ["submodule", "init", path])
    subprocess.run(git_cmd + ["submodule", "update", path])
