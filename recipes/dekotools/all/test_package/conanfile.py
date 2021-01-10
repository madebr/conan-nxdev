from conans import ConanFile, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch"

    def test(self):
        if not tools.cross_building(self):
            self.run("dekodef -h {} {}".format(os.path.join(self.build_folder, "header.h"),
                                               os.path.join(self.source_folder, "test_package.def")), run_environment=True)
