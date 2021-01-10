from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os
import shutil


class SwitchOpenALSoftConan(ConanFile):
    name = "switch-openal-soft"
    description = "OpenAL Soft is a software implementation of the OpenAL 3D audio API."
    topics = ("conan", "openal", "audio", "api")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/fgsfdsfgs/openal-soft"
    license = "MIT"
    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _os_is_nintendo_switch(self):
        return str(self.settings.get_safe("os", "")) == "Nintendo Switch"

    def configure(self):
        if not self._os_is_nintendo_switch:
            raise ConanInvalidConfiguration("{} is only available for os=Nintendo Switch".format(self.name))

        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("openal-soft-*")[0], self._source_subfolder)

    @property
    def _lib_filename(self):
        return "libopenald.a" if self.settings.build_type == "Debug" else "libopenal.a"

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(os.path.join(self._source_subfolder)):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.make(target="lib/{}".format(self._lib_filename), args=["-f", "Makefile.nx"])

    def package(self):
        self.copy(self._lib_filename, src=os.path.join(self._source_subfolder, "nx", "lib"), dst="lib")
        shutil.copytree(os.path.join(self._source_subfolder, "include"),
                        os.path.join(self.package_folder, "include"))
        shutil.copytree(os.path.join(self._source_subfolder, "lib"),
                        os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "openal"
        self.cpp_info.names["cmake_find_package"] = "OpenAL"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenAL"
        self.cpp_info.libs = ["openald" if self.settings.build_type == "Debug" else "openal"]
        self.cpp_info.includedirs.append(os.path.join("include", "AL"))
        self.cpp_info.system_libs.extend(["dl", "m"])
        libcxx = tools.stdcpp_library(self)
        if libcxx:
            self.cpp_info.system_libs.append(libcxx)
        if not self.options.shared:
            self.cpp_info.defines.append("AL_LIBTYPE_STATIC")
