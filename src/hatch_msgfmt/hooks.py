from typing import Any

from hatchling.plugin import hookimpl
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from .msgfmt import make
from tempfile import TemporaryDirectory
from pathlib import Path

class MsgfmtBuildHook(BuildHookInterface):
    PLUGIN_NAME = 'msgfmt'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__tempdir = None

    @property
    def __packagedir(self) -> Path:
        if self.__tempdir is None:
            self.__tempdir = TemporaryDirectory()
        return Path(self.__tempdir.name)

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        if self.target_name != 'wheel':
            return
        print('initialize')
        print(f'{version=}')
        print(f'{build_data=}')
        print(f'{self.directory=}')
        print(f'{self.build_config.directory=}')
        print(f'{self.build_config.default_include()=}')
        print(f'{self.build_config.default_exclude()=}')
        print(f'{self.build_config.default_only_include()=}')
        print(f'{self.build_config.default_packages()=}')
        print(f'{[(file.path, file.relative_path, file.distribution_path) for file in  self.build_config.builder.recurse_included_files()]=}')

    def finalize(self, version: str, build_data: dict[str, Any], artifact_path: str) -> None:
        if self.target_name != 'wheel':
            return
        print('finalize')
        print(f'{version=}')
        print(f'{build_data=}')
        print(f'{artifact_path=}')
        print(f'{self.directory=}')
        print(f'{self.build_config.directory=}')
        print(f'{self.build_config.default_include()=}')
        print(f'{self.build_config.default_exclude()=}')
        print(f'{self.build_config.default_only_include()=}')
        print(f'{self.build_config.default_packages()=}')
        print(f'{[(file.path, file.relative_path, file.distribution_path) for file in  self.build_config.builder.recurse_included_files()]=}')

@hookimpl
def hatch_register_build_hook():
    return MsgfmtBuildHook
