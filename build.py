#!/usr/bin/env python

#
# (C) 2022 Alex "Lexi" Mayfield
#

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional
import os
import platform
import shutil
import subprocess

SCRIPT_DIR = Path(__file__).parent
CMAKE_PREFIX_PATH = SCRIPT_DIR / "local"


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


def build(
    libname: str,
    defines: dict[str, str] = {},
    cxxflags: Optional[list[str]] = None,
    srcdir: Optional[Path] = None,
):
    if srcdir is None:
        srcdir = SCRIPT_DIR / "libraries" / libname
    builddir = SCRIPT_DIR / "build" / libname

    lib_buildgen(srcdir=srcdir, builddir=builddir, defines=defines, cxxflags=cxxflags)
    lib_build(builddir=builddir, config="Debug", target="install")
    lib_build(builddir=builddir, config="RelWithDebInfo", target="install")


def build_zlib():
    build("zlib")


def build_libpng():
    build("libpng", defines={"PNG_SHARED": "OFF", "PNG_TESTS": "OFF"})


def build_curl():
    defines = {
        "BUILD_CURL_EXE": "OFF",
        "BUILD_SHARED_LIBS": "OFF",
        "CMAKE_USE_LIBSSH2": "OFF",
        "CURL_ZLIB": "OFF",
        "HTTP_ONLY": "ON",
    }
    if platform.system() == "Windows":
        defines["CMAKE_USE_WINSSL"] = "ON"
    build("curl", defines=defines)


def build_fltk():
    defines = {
        "OPTION_USE_SYSTEM_LIBJPEG": "OFF",
        "OPTION_PRINT_SUPPORT": "OFF",
        "OPTION_USE_GL": "OFF",
        "FLTK_BUILD_TEST": "OFF",
    }

    if True:  # Internal zlib
        defines["ZLIB_LIBRARY_RELEASE"] = (
            CMAKE_PREFIX_PATH / "lib" / libname_static("zlibstatic")
        )

    if True:  # Internal libpng
        defines["PNG_PNG_INCLUDE_DIR"] = CMAKE_PREFIX_PATH / "include" / "libpng16"
        defines["HAVE_PNG_H"] = "ON"

    build("fltk", defines=defines)


def build_jsoncpp():
    defines = {
        "JSONCPP_WITH_TESTS": "OFF",
        "JSONCPP_WITH_POST_BUILD_UNITTEST": "OFF",
        "JSONCPP_WITH_WARNING_AS_ERROR": "OFF",
        "JSONCPP_WITH_PKGCONFIG_SUPPORT": "OFF",
        "JSONCPP_WITH_CMAKE_PACKAGE": "ON",
        "CMAKE_DEBUG_POSTFIX": "d",
        "CCACHE_EXECUTABLE": "CCACHE_EXECUTABLE-NOTFOUND",
    }

    build("jsoncpp", defines=defines)


def build_miniupnpc():
    defines = {
        "UPNPC_BUILD_SHARED": "OFF",
        "UPNPC_BUILD_TESTS": "OFF",
        "UPNPC_BUILD_SAMPLE": "OFF",
    }

    build(
        "miniupnpc",
        defines=defines,
        srcdir=SCRIPT_DIR / "libraries" / "miniupnp" / "miniupnpc",
    )


def build_protobuf():
    defines = {
        "protobuf_BUILD_SHARED_LIBS": "OFF",
        "protobuf_BUILD_TESTS": "OFF",
        "protobuf_MSVC_STATIC_RUNTIME": "OFF",
    }

    cxxflags = None
    if CompileFlag.MSVC in environment().flags:
        # https://developercommunity.visualstudio.com/t/Visual-Studio-1740-no-longer-compiles-/10193665
        cxxflags = ["/D_SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS"]

    build(
        "protobuf",
        defines=defines,
        cxxflags=cxxflags,
        srcdir=SCRIPT_DIR / "libraries" / "protobuf" / "cmake",
    )


build_zlib()
build_libpng()
build_curl()
build_fltk()
build_jsoncpp()
build_miniupnpc()
build_protobuf()
