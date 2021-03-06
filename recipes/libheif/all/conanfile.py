import os
from conans import ConanFile, tools, CMake


class Libheif(ConanFile):
    name = "libheif"
    description = "libheif is an HEIF and AVIF file format decoder and encoder."
    topics = ("conan", "libheif", "heif", "codec", "video")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/strukturag/libheif"
    license = ("LGPL-3.0-only", "GPL-3.0-or-later", "MIT")
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False],
               "with_x265": [True, False]}
    default_options = {"shared": False, "fPIC": True,
                       "with_x265": False}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = '{}-{}'.format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def requirements(self):
        self.requires("libde265/1.0.8")
        if self.options.with_x265:
            self.requires("libx265/3.4")

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_EXAMPLES"] = False
        self._cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_X265'] = not self.options.with_x265
        self._cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_LibAOM'] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "libheif"
        self.cpp_info.names["cmake_find_package_multi"] = "libheif"
        self.cpp_info.names["pkg_config"] = "libheif"

        self.cpp_info.components["heif"].names["cmake_find_package"] = "heif"
        self.cpp_info.components["heif"].names["cmake_find_package_multi"] = "heif"
        self.cpp_info.components["heif"].names["pkg_config"] = "libheif"
        self.cpp_info.components["heif"].requires = ["libde265::libde265"]
        if self.options.with_x265:
            self.cpp_info.components["heif"].requires.append("libx265::libx265")

        self.cpp_info.components["heif"].libs = ["heif"]

        if not self.options.shared:
            self.cpp_info.components["heif"].defines = ["LIBHEIF_STATIC_BUILD"]
        if self.settings.os == "Linux":
            self.cpp_info.components["heif"].system_libs = ["m", "pthread"]
        if not self.options.shared and tools.stdcpp_library(self):
            self.cpp_info.components["heif"].system_libs.append(tools.stdcpp_library(self))
