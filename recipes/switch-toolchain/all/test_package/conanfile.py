from conans import CMake, ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def build(self):
        pass
        # cmake = CMake(self)
        # cmake.configure()
        # cmake.build()
    def test(self):
        pass


