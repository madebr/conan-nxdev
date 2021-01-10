from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os
import shutil


class DevkitA64Conan(ConanFile):
    name = "devkitA64"
    homepage = "https://github.com/devkitPro/buildscripts"
    topics = ("nintendo", "switch", "toolchain", "gcc", "binutils", "newlib")
    license = "GPLv3-or-later"
    url = "https://github.com/madebr/conan-nxdev"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _devkit_subfolder(self):
        return "devkit"

    @property
    def _binutils_subfolder(self):
        return "binutils"

    @property
    def _gcc_subfolder(self):
        return "gcc"

    @property
    def _newlib_subfolder(self):
        return "newlib"

    @property
    def _base_dir(self):
        return os.path.join(self._devkit_subfolder, "dka64")

    @property
    def _script_dir(self):
        return os.path.join(self._base_dir, "scripts")

    @property
    def _patch_dir(self):
        return os.path.join(self._base_dir, "patches")

    @property
    def _target_triplet(self):
        return "aarch64-none-elf"

    def configure(self):
        if hasattr(self, "settings_target") and self.settings_target:
            if self.settings_target.get_safe("arch") and self.settings_target.arch != "armv8":
                raise ConanInvalidConfiguration("This package is only able to build armv8 packages")

    def requirements(self):
        self.requires("gmp/6.2.1", private=True)
        self.requires("mpfr/4.1.0", private=True)
        self.requires("mpc/1.2.0", private=True)
        self.requires("zlib/1.2.11", private=True)

    def source(self):
        for source in self.conan_data["sources"][self.version]:
            tools.get(**source)
        os.rename(glob.glob("buildscripts-*")[0].format(self.version), self._devkit_subfolder)
        os.rename(glob.glob("binutils-*")[0].format(self.version), self._binutils_subfolder)
        os.rename(glob.glob("gcc-*")[0].format(self.version), self._gcc_subfolder)
        os.rename(glob.glob("newlib-*")[0].format(self.version), self._newlib_subfolder)

    def validate(self):
        if any((self.options["gmp"].shared, self.options["mpfr"].shared,
                self.options["mpc"].shared, self.options["zlib"].shared)):
            raise ConanInvalidConfiguration("gmp, mpfr, mpc, zlib must be static libraries")

    @property
    def _cflags_for_target(self):
        return "-O2 -ffunction-sections -fdata-sections"

    def _build_install_binutils(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        args = [
            "--disable-nls",
            "--disable-werror",
            "--enable-lto",
            "--enable-plugins",
            "--enable-poison-system-directories",
        ]
        tools.mkdir("binutils_build")
        with tools.chdir("binutils_build"):
            autotools.configure(args=args, configure_dir=os.path.join(self.source_folder, self._binutils_subfolder),
                                target=self._target_triplet)
            autotools.make()
            autotools.install()

    def _build_install_gcc(self, stage):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        tools.mkdir("gcc_build")
        with tools.chdir("gcc_build"):
            if stage == 1:
                args = [
                    "--enable-languages=c,c++,objc,lto",
                    "--with-gnu-as", "--with-gnu-ld", "--with-gcc",
                    "--with-march=armv8",
                    "--enable-cxx-flags=-ffunction-sections",
                    "--disable-libstdcxx-verbose",
                    "--enable-poison-system-directories",
                    "--enable-interwork",
                    "--enable-multilib",
                    "--enable-threads",
                    "--disable-win32-registry",
                    "--disable-nls",
                    "--disable-debug",
                    "--disable-libmudflap",
                    "--disable-libssp",
                    "--disable-libgomp",
                    "--disable-libstdcxx-pch",
                    "--enable-libstdcxx-time",
                    "--enable-libstdcxx-filesystem-ts",
                    "--with-newlib=yes",
                    "--with-headers={}".format(os.path.join(self.source_folder, self._newlib_subfolder, "newlib", "libc", "include").replace("\\", "/")),
                    "--enable-lto",
                    "--with-system-zlib",
                    "--disable-tm-clone-registry",
                    "--disable-__cxa_atexit",
                    "--with-bugurl='{}'".format(self.url),
                    "--with-pkgversion={} version {}, packaged by {}".format(self.name, self.version, self.url),
                    "--with-gmp={}".format(self.deps_cpp_info["gmp"].rootpath.replace("\\", "/")),
                    "--with-mpfr={}".format(self.deps_cpp_info["mpfr"].rootpath.replace("\\", "/")),
                    "--with-mpc={}".format(self.deps_cpp_info["mpc"].rootpath.replace("\\", "/")),
                ]
                with tools.environment_append({"CFLAGS_FOR_TARGET": self._cflags_for_target,
                                               "CXXFLAGS_FOR_TARGET": self._cflags_for_target,
                                               "LDFLAGS_FOR_TARGET": ""}):
                    autotools.configure(args=args, configure_dir=os.path.join(self.source_folder, self._gcc_subfolder),
                                        target=self._target_triplet)
                    autotools.make(target="all-gcc")
                    autotools.make(target="install-gcc")
            elif stage == 2:
                autotools.make(target="all")
                autotools.make(target="install", args=["-j1"])


    def _build_install_newlib(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        args = [
            "--enable-newlib-mb",
            "--disable-newlib-supplied-syscalls",
            "--enable-newlib-multithread",
            "--disable-newlib-wide-orient",
        ]
        tools.mkdir("newlib_build")
        with tools.chdir("newlib_build"):
            with tools.environment_append({"CCFLAGS_FOR_TARGET": self._cflags_for_target}):
                autotools.configure(args=args, configure_dir=os.path.join(self.source_folder, self._newlib_subfolder),
                                    target=self._target_triplet)
                autotools.make()
                autotools.install(args=["-j1"])

        # # FIXME: HACK (copy sys/mman.h from rtems's newlib)
        # for header in ("mman.h",):
        #     shutil.copy(os.path.join(self._newlib_subfolder, "newlib", "libc", "sys", "rtems", "include", "sys", header),
        #                 os.path.join(self.package_folder, self._target_triplet, "include", "sys", header))

    def build(self):
        tools.patch(patch_file=glob.glob(os.path.join(self._patch_dir, "binutils-*.patch"))[0],
                    base_path=self._binutils_subfolder)
        tools.patch(patch_file=glob.glob(os.path.join(self._patch_dir, "newlib-*.patch"))[0],
                    base_path=self._newlib_subfolder)
        tools.patch(patch_file=glob.glob(os.path.join(self._patch_dir, "gcc-*.patch"))[0],
                    base_path=self._gcc_subfolder)

        with tools.environment_append({"PATH": [os.path.join(self.package_folder, "bin")]}):
            self._build_install_binutils()
            self._build_install_gcc(stage=1)
            with tools.environment_append({"CC": None, "CXX": None}):
                self._build_install_newlib()
            self._build_install_gcc(stage=2)

        tools.rmdir(os.path.join(self.package_folder, self._target_triplet, "sys-include"))

    def package(self):
        shutil.copytree(os.path.join(self._base_dir, "rules"),
                        os.path.join(self.package_folder, "devkitA64"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        devkitpro = self.package_folder.replace("\\", "/")
        self.output.info("Setting DEVKITPRO environment variable: {}".format(devkitpro))
        self.user_info.devitpro = devkitpro
        self.env_info.DEVKITPRO = devkitpro

        self.cpp_info.bindirs = [os.path.join("devkitA64", "bin")]

        self.user_info.triplet = self._target_triplet

        def add_env(name, gcc_suffix):
            value = os.path.join(self.package_folder, "bin", "{}-{}").format(self._target_triplet, gcc_suffix)
            self.output.info("Set {}={}".format(name, value))
            setattr(self.env_info, name, value)

        add_env("AR", "ar")
        add_env("AS", "as")
        add_env("CC", "gcc")
        add_env("CC_LD", "gcc")
        add_env("CXX", "g++")
        add_env("CXX_LD", "g++")
        add_env("CPP", "cpp")
        add_env("NM", "nm")
        add_env("OBJDUMP", "objdump")
        add_env("OBJCOPY", "objcopy")
        add_env("RANLIB", "ranlib")
        add_env("READELF", "readelf")
        add_env("STRINGS", "strings")
        add_env("STRIP", "strip")
