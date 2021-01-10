from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class SwitchDeko3dConan(ConanFile):
    name = "switch-deko3d"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _os_is_nintendo_switch(self):
        return str(self.settings.get_safe("os", "")) == "Nintendo Switch"

    def configure(self):
        if not self._os_is_nintendo_switch:
            raise ConanInvalidConfiguration("{} is only available for os=Nintendo Switch".format(self.name))

    _libnx_package = "libnx/4.0.0"

    def requirements(self):
        self.requires(self._libnx_package)
        self.requires("switch-libdrm_nouveau/1.0.1")

    def build_requirements(self):
        self.build_requires(self._libnx_package)
        self.build_requires("dekotools/git.20190825@")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("deko3d-{}".format(self.version), self._source_subfolder)

    @property
    def _lib_filename(self):
        return "libdeko3dd.a" if self.settings.build_type == "Debug" else "libdeko3d.a"

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make(target="lib/{}".format(self._lib_filename))

    def package(self):
        shutil.copytree(os.path.join(self._source_subfolder, "include"),
                        os.path.join(self.package_folder, "include"))
        shutil.copytree(os.path.join(self._source_subfolder, "lib"),
                        os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["deko3dd" if self.settings.build_type == "Debug" else "deko3d"]
