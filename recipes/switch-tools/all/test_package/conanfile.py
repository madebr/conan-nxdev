from conans import ConanFile, tools


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self):
            self.run("build_pfs0 -h", run_environment=True)
