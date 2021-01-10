from conans import CMake, ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_BUILD_TYPE"] = "Release"
        cmake.definitions["CMAKE_SYSTEM_NAME"] = "Generic"
        cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            self.run("{}-gcc --version".format(self.deps_user_info["devkitA64"].triplet))
