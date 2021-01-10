from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class SwitchToolsConan(ConanFile):
    name = "switch-tools"
    description = "Helper tools for Switch homebrew development"
    homepage = "https://github.com/switchbrew/switch-tools"
    topics = ("nintendo", "switch", "homebrew", "tools")
    license = "ISC"
    url = "https://github.com/madebr/conan-nxdev"
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("automake/1.16.3")
        self.build_requires("pkgconf/1.7.3")

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("lz4/1.9.3")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("switch-tools-{}".format(self.version), self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", win_bash=tools.os_info.is_windows)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        autotools.configure(configure_dir=self._source_subfolder)
        autotools.make()

    def package(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.install()
