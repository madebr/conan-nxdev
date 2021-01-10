from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException, ConanInvalidConfiguration
import os
import shutil


class SwitchLibdrmNouveauConan(ConanFile):
    name = "switch-libdrm_nouveau"
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
            raise ConanInvalidConfiguration("libnx is only available for os=Nintendo Switch")

    _libnx_package = "libnx/4.0.0"

    def requirements(self):
        self.requires(self._libnx_package)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libdrm_nouveau-{}".format(self.version), self._source_subfolder)

    @property
    def _lib_filename(self):
        return "libdrm_nouveaud.a" if self.settings.build_type == "Debug" else "libdrm_nouveau.a"

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        autotools = AutoToolsBuildEnvironment(self)
        with tools.environment_append(autotools.vars):
            with tools.chdir(os.path.join(self._source_subfolder)):
                autotools.make(target="lib/{}".format(self._lib_filename))

    def package(self):
        shutil.copytree(os.path.join(self._source_subfolder, "include"),
                        os.path.join(self.package_folder, "include"))
        shutil.copytree(os.path.join(self._source_subfolder, "lib"),
                        os.path.join(self.package_folder, "lib"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: this version is only for the pkg_config generator
        self.cpp_info.version = "9.9.99"
        self.cpp_info.names["pkg_config"] = "libdrm_nouveau"
        self.cpp_info.libs = ["drm_nouveaud" if self.settings.build_type == "Debug" else "drm_nouveau"]

        libnx_root = self.package_folder.replace("\\", "/")
        self.output.info("Set LIBNX environment variable: {}".format(libnx_root))
        self.env_info.LIBNX = libnx_root
