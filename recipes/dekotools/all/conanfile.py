from conans import ConanFile, Meson, tools
import glob
import os


class DekoToolsConan(ConanFile):
    name = "dekotools"
    description = "Tools used to develop the deko3d library"
    homepage = "https://github.com/fincs/dekotools"
    topics = ("nintendo", "switch", "homebrew", "tools")
    license = "ISC"
    url = "https://github.com/madebr/conan-nxdev"
    settings = "os", "arch", "compiler", "build_type"
    # generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.build_requires("flex/2.6.4")
        self.build_requires("bison/3.7.1")
        self.build_requires("meson/0.56.0")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(glob.glob("dekotools-*")[0], self._source_subfolder)

    def _get_meson(self):
        meson = Meson(self)
        meson.build_folder = os.path.join(self.build_folder, self._build_subfolder)
        return meson

    def build(self):
        meson = self._get_meson()
        meson.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        meson.build()

    def package(self):
        meson = self._get_meson()
        meson.install()

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
