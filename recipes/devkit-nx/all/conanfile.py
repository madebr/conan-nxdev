from conans import ConanFile
from conans.errors import ConanException
import os


class DevkitNXConan(ConanFile):
    name = "devkit-nx"
    homepage = "https://github.com/devkitPro/buildscripts"
    topics = ("nintendo", "switch", "toolchain", "gcc", "binutils", "newlib")
    license = "GPLv3-or-later", "ISC"
    url = "https://github.com/madebr/conan-nxdev"
    settings = "os", "arch"

    @property
    def _os_is_nintendo_switch(self):
        try:
            return self.settings.os == "Nintendo Switch"
        except ConanException:
            return False

    def requirements(self):
        self.requires("libnx/4.0.0")

    def build_requirements(self):
        self.build_requires("devkitA64/38")

    def package_info(self):
        archflags = ["-march=armv8-a+crc+crypto", "-mtune=cortex-a57", "-mtp=soft", "-fPIC"]
        self.cpp_info.defines = ["__SWITCH__"]
        self.cpp_info.cflags =  ["-ffunction-sections"] + archflags
        self.cpp_info.cxxflags =  ["-fno-rtti", "-fno-exceptions"] + archflags
        self.cpp_info.exelinkflags =  ["-specs={}/libnx/switch.specs".format(self.deps_cpp_info["libnx"].rootpath.replace("\\", "/"))] + archflags
        self.cpp_info.sharedlinkflags =  ["-specs={}/libnx/switch.specs".format(self.deps_cpp_info["libnx"].rootpath.replace("\\", "/"))] + archflags
