#!/usr/bin/env python

#
# (C) 2022 Alex "Lexi" Mayfield
#

import platform

from buildlib import *
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CMAKE_PREFIX_PATH = SCRIPT_DIR / "local"


def build_zlib():
    git_submodule("libraries/zlib")
    cmake_build("zlib")


def build_libpng():
    git_submodule("libraries/libpng")
    cmake_build("libpng", defines={"PNG_SHARED": "OFF", "PNG_TESTS": "OFF"})


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

    git_submodule("libraries/curl")
    cmake_build("curl", defines=defines)


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

    git_submodule("libraries/fltk")
    cmake_build("fltk", lang="cxx", defines=defines)


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

    git_submodule("libraries/jsoncpp")
    cmake_build("jsoncpp", lang="cxx", defines=defines)


def build_miniupnpc():
    defines = {
        "UPNPC_BUILD_SHARED": "OFF",
        "UPNPC_BUILD_TESTS": "OFF",
        "UPNPC_BUILD_SAMPLE": "OFF",
    }

    git_submodule("libraries/miniupnp")
    cmake_build(
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

    git_submodule("libraries/protobuf")
    cmake_build(
        "protobuf",
        lang="cxx",
        defines=defines,
        cxxflags=cxxflags,
        srcdir=SCRIPT_DIR / "libraries" / "protobuf" / "cmake",
    )


def build_sdl():
    git_submodule("libraries/SDL")
    cmake_build("SDL")


def build_sdl_mixer():
    git_submodule("libraries/SDL_mixer")
    git_submodule("external/flac", "libraries/SDL_mixer")
    git_submodule("external/libmodplug", "libraries/SDL_mixer")
    git_submodule("external/ogg", "libraries/SDL_mixer")
    git_submodule("external/opus", "libraries/SDL_mixer")
    git_submodule("external/opusfile", "libraries/SDL_mixer")
    cmake_build("SDL_mixer", defines={"SDL2MIXER_SAMPLES": "OFF"})


def build_wxwidgets():
    git_submodule("libraries/wxWidgets")
    cmake_build(
        "wxWidgets",
        lang="cxx",
        config="Release",
        defines={
            "wxBUILD_COMPATIBILITY": "3.0",
            "wxUSE_REGEX": "OFF",
            "wxUSE_ZLIB": "OFF",
            "wxUSE_EXPAT": "OFF",
            "wxUSE_LIBJPEG": "OFF",
            "wxUSE_LIBPNG": "OFF",
            "wxUSE_LIBTIFF": "OFF",
            "wxUSE_NANOSVG": "OFF",
        },
    )


build_zlib()
build_libpng()
build_curl()
build_fltk()
build_jsoncpp()
build_miniupnpc()
build_protobuf()
build_sdl()
build_sdl_mixer()
build_wxwidgets()
