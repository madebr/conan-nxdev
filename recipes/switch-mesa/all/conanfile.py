from conans import ConanFile, Meson, tools
# FIXME: import Meson from `conan.tools.meson`
from conan.tools.meson import MesonToolchain
from conans.errors import ConanInvalidConfiguration
import glob
import os


class SwitchMesaConan(ConanFile):
    name = "switch-mesa"
    description = "The Mesa 3D Graphics Library"
    topics = ("conan", "mesa", "switch", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://mesa.freedesktop.org"
    license = "Zlib"
    generators = "cmake"
    options = {
        "shared": [False,],
    }
    default_options = {
        "shared": False,
    }
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config"

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

    def requirements(self):
        self.requires("switch-libdrm_nouveau/1.0.1")

    def build_requirements(self):
        self.build_requires("meson/0.56.0")
        self.build_requires("pkgconf/1.7.3")
        self.build_requires("switch-toolchain/master")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0])
        os.rename(glob.glob("mesa-*")[0], self._source_subfolder)
        for src in self.conan_data["sources"][self.version][1:]:
            tools.download(**src, filename=os.path.basename(src["url"]))

    def toolchain(self):
        tc = MesonToolchain(self)
        tc.generate()

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        meson = Meson(self)
        args = [
            # FIXME: should not be necessary in the future
            "--cross-file", os.path.join(self.install_folder, "conan_meson_cross.ini"),
            # "--cross-file", os.environ["CONAN_MESON_CROSS_FILE"],
        ]
        meson.options["b_ndebug"] = str(not self.settings.build_type == "Debug").lower()
        # meson.options["platforms"] = "switch"
        # meson.options["dri-drivers"] = "nouveau"
        meson.configure(args=args, source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.build_folder = self._build_subfolder
        meson.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "sdl2"
        self.cpp_info.names["cmake_find_package"] = "SDL2"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2"
        self.cpp_info.libs = ["SDL2"]
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))
