from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import shlex
import shutil


class SwitchToolchainConan(ConanFile):
    name = "switch-toolchain"
    description = "Build helpers for switch (CMake toolchain + compiler options)"
    homepage = "https://github.com/madebr/conan-nxdev"
    topics = ("nintendo", "switch", "cmake", "toolchain", "cross", "building")
    exports_sources = "toolchain/*", "meson_switch.txt"
    no_copy_sources = True
    url = "https://github.com/madebr/conan-nxdev"
    settings = "os"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _os_is_nintendo_switch(self):
        return str(self.settings.get_safe("os", "")) == "Nintendo Switch"

    def configure(self):
        if self._os_is_nintendo_switch:
            raise ConanInvalidConfiguration("This recipe is supposed to be used as a build requirement")

    def requirements(self):
        self.requires("libnx/4.0.0")

    def package_id(self):
        self.info.settings.clear()

    def package(self):
        shutil.copytree(src=os.path.join(self.source_folder, "toolchain"),
                        dst=os.path.join(self.package_folder, "lib", "cmake"))
        shutil.copy(src=os.path.join(self.source_folder, "meson_switch.txt"),
                    dst=os.path.join(self.package_folder, "meson_switch.txt"))

    @property
    def _flags(self):
        arch = ["-march=armv8-a+crc+crypto", "-mtune=cortex-a57", "-mtp=soft", "-fPIC", "-ftls-model=local-exec"]
        cflags = ["-D__SWITCH__", "-ffunction-sections", "-fdata-sections"] + arch
        return {
            "ASFLAGS": list(arch),
            "CPPFLAGS": ["-D__SWITCH__"] + arch,
            "CFLAGS": cflags,
            "CXXFLAGS": cflags,
            "LDFLAGS": ["-specs={}/libnx/switch.specs".format(self.deps_cpp_info["libnx"].rootpath.replace("\\", "/"))] + arch,
        }

    def package_info(self):
        self.cpp_info.builddirs = [os.path.join("lib", "cmake")]
        self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = os.path.join(self.package_folder, "lib", "cmake", "nx-toolchain.cmake")
        self.env_info.CONAN_CMAKE_SYSTEM_NAME = "Nintendo Switch"
        self.env_info.CONAN_CMAKE_SYSTEM_PROCESSOR = "aarch64"

        self.env_info.CONAN_MESON_CROSS_FILE = os.path.join(self.package_folder, "meson_switch.txt")

        for k, v in self._flags.items():
            current = tools.get_env(k, "")
            print(k, v)
            added = " ".join(v)
            if current:
                current += " "
            new_value = current + added
            self.output.info("Adding flags to environment variable {}: {}".format(k, added))
            setattr(self.env_info, k, new_value)

        # def set_env(name, value):
        #     current = tools.get_env(name, None)
        #     if current:
        #         current += " "
        #     current += value
        #     setattr(self.env_info, name, value)

