from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class LibnxConan(ConanFile):
    name = "libnx"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "toolchain/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _os_is_nintendo_switch(self):
        return str(self.settings.get_safe("os", "")) == "Nintendo Switch"

    @property
    def _context(self):
        if hasattr(self, "settings_target") and self.settings_target:
            return "build"
        else:
            return "host"

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if not self._os_is_nintendo_switch:
            del self.settings.arch
            del self.settings.compiler
            del self.settings.build_type

    def build_requirements(self):
        if self._os_is_nintendo_switch:
            self.build_requires("make/4.2.1")
            self.build_requires("general-tools/1.0.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libnx-{}".format(self.version), self._source_subfolder)

    @property
    def _lib_filename(self):
        return "libnxd.a" if self.settings.build_type == "Debug" else "libnx.a"

    def build(self):
        if self._os_is_nintendo_switch:
            with tools.chdir(os.path.join(self._source_subfolder, "nx")):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.make(target="lib/{}".format(self._lib_filename))

    def package(self):
        if self._os_is_nintendo_switch:
            self.copy(self._lib_filename, src=os.path.join(self._source_subfolder, "nx", "lib"), dst="lib")
        self.copy("*", src=os.path.join(self._source_subfolder, "nx", "include"), dst=os.path.join(self.package_folder, "include"))
        self.copy("*", src=os.path.join(self._source_subfolder, "nx", "external", "bsd", "include"), dst=os.path.join(self.package_folder, "include"))
            # shutil.copytree(,
            #                 os.path.join(self.package_folder, "include"), dirs_exist_ok=True)
        self.copy("switch.ld", src=os.path.join(self._source_subfolder, "nx"), dst="libnx")
        self.copy("switch.specs", src=os.path.join(self._source_subfolder, "nx"), dst="libnx")
        self.copy("switch_rules", src=os.path.join(self._source_subfolder, "nx"), dst="libnx")
        tools.replace_in_file(os.path.join(self.package_folder, "libnx", "switch.specs"),
                              "getenv(DEVKITPRO /libnx/switch.ld)",
                              "getenv(LIBNX /libnx/switch.ld)")

        shutil.copytree(src=os.path.join(self.source_folder, "toolchain"),
                        dst=os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self._os_is_nintendo_switch:
            self.cpp_info.libs = ["nxd" if self.settings.build_type == "Debug" else "nx"]
            self.cpp_info.defines = ["__SWITCH__"]
        # if self._context == "build":
        #     for k, v in flags.items():
        #         current = tools.get_env(k, "")
        #         added = " ".join(v)
        #         if current:
        #             current += " "
        #         new_value = current + added
        #         self.output.info("Adding flags to environment variable {}: {}".format(k, added))
        #         setattr(self.env_info, k, new_value)

        libnx_root = self.package_folder.replace("\\", "/")
        self.env_info.LIBNX = libnx_root

        # self.env_info.CONAN_CMAKE_TOOLCHAIN_FILE = os.path.join(self.package_folder, "lib", "cmake", "nx-toolchain.cmake")
        # self.env_info.CONAN_CMAKE_SYSTEM_NAME = "Nintendo Switch"
        # self.env_info.CONAN_CMAKE_SYSTEM_PROCESSOR = "aarch64"

        self.cpp_info.builddirs = [os.path.join("lib", "cmake")]
