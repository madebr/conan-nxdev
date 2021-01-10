from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class SwitchSDL2Conan(ConanFile):
    name = "switch-sdl2"
    description = "Access to audio, keyboard, mouse, joystick, and graphics hardware via OpenGL, Direct3D and Vulkan"
    topics = ("conan", "openal", "audio", "api")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/devkitPro/SDL"
    license = "Zlib"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _os_is_nintendo_switch(self):
        return str(self.settings.get_safe("os", "")) == "Nintendo Switch"

    def configure(self):
        if not self._os_is_nintendo_switch:
            raise ConanInvalidConfiguration("{} is only available for os=Nintendo Switch".format(self.name))

        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("libnx/4.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0])
        os.rename(glob.glob("SDL2-*")[0], self._source_subfolder)
        for src in self.conan_data["sources"][self.version][1:]:
            tools.download(**src, filename=os.path.basename(src["url"]))

    def _get_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.flags.append("-std=c99")
        return autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        os.chmod(os.path.join(self._source_subfolder, "configure"), 0o755)
        autotools = self._get_autotools()
        args = [
            "--disable-shared", "--enable-static",
            "--enable-audio",
            "--enable-joystick",
            "--disable-power",
            "--disable-filesystem",
            "--enable-cpuinfo",
            "--enable-threads",
            "--enable-timers",
            "--enable-video",
        ]
        autotools.configure(args=args, configure_dir=self._source_subfolder, host="aarch64-none-elf")
        tools.replace_in_file("Makefile", "-Wdeclaration-after-statement", "", strict=False)
        tools.replace_in_file("Makefile", "-Werror=declaration-after-statement", "", strict=False)
        autotools.make()

    def package(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.install()

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "sdl2"
        self.cpp_info.names["cmake_find_package"] = "SDL2"
        self.cpp_info.names["cmake_find_package_multi"] = "SDL2"
        self.cpp_info.libs = ["SDL2"]
        self.cpp_info.includedirs.append(os.path.join("include", "SDL2"))
