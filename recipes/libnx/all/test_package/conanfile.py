from conans import CMake, ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    @property
    def _os_is_nintendo_switch(self):
        return str(self.settings.get_safe("os", "")) == "Nintendo Switch"

    def build_requirements(self):
        if self._os_is_nintendo_switch:
            self.build_requires("switch-toolchain/master")

    # @property
    # def _flags(self):
    #     arch = ["-march=armv8-a+crc+crypto", "-mtune=cortex-a57", "-mtp=soft", "-fPIE", "-ftls-model=local-exec"]
    #     flags = {
    #         "ASFLAGS": list(arch),
    #         "CPPFLAGS": ["-D__SWITCH"] + arch,
    #         "CFLAGS": ["-D__SWITCH", "-ffunction-sections"] + arch,
    #         "CXXFLAGS": ["-D__SWITCH__", "-ffunction-sections"] + arch,
    #         "LDFLAGS": ["-specs={}/libnx/switch.specs".format(self.deps_cpp_info["libnx"].rootpath.replace("\\", "/"))] + arch,
    #     }
    #     return {k: " ".join(v) for k, v in flags.items()}

    def build(self):
        if self._os_is_nintendo_switch:
            # with tools.environment_append({"LIBNX": self.deps_cpp_info["libnx"].rootpath}):
            cmake = CMake(self)
            cmake.verbose = True
            cmake.definitions["CMAKE_SYSTEM_NAME"] = "Generic"
            cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
            cmake.configure()
            cmake.build()

    def test(self):
        pass
