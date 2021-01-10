from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os


class SwitchGeneralToolsConan(ConanFile):
    name = "switch-general-tools"
    description = "General devkitPro tools"
    homepage = "https://github.com/devkitPro/general-tools"
    topics = ("nintendo", "switch", "homebrew", "tools")
    license = "GPLv3-or-later"
    url = "https://github.com/madebr/conan-nxdev"
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("automake/1.16.3")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("general-tools-{}".format(self.version), self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", win_bash=tools.os_info.is_windows)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        autotools.configure(configure_dir=self._source_subfolder)
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.install()

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
