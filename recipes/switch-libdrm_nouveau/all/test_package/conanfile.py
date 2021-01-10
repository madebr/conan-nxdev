from conans import CMake, ConanFile, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    def build_requirements(self):
        self.build_requires("switch-toolchain/master")

    def build(self):
        with tools.environment_append({"LIBNX": self.deps_cpp_info["libnx"].rootpath}):
            cmake = CMake(self)
            cmake.verbose = True
            cmake.definitions["CMAKE_SYSTEM_NAME"] = "Generic"
            cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
            cmake.configure()
            cmake.build()

    def test(self):
        pass
