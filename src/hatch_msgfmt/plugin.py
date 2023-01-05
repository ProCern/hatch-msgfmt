from typing import Any, Union, Mapping
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from typing import BinaryIO
from tempfile import mkstemp
from pathlib import Path
import os
from subprocess import run, DEVNULL

class UnopenedTemporaryFile:
    '''Like NamedTemporaryFile, but not open by default and only with functionality that we need.
    '''
    def __init__(self, *args, **kwargs):
        handle, pathname = mkstemp(*args, **kwargs)
        os.close(handle)
        self.name: Union[str, bytes] = pathname

    def __str__(self) -> str:
        if isinstance(self.name, str):
            return self.name
        else:
            return os.fsdecode(self.name)

    def __bytes__(self) -> bytes:
        if isinstance(self.name, bytes):
            return self.name
        else:
            return os.fsencode(self.name)

    def __del__(self):
        os.remove(self.name)


class MsgfmtBuildHook(BuildHookInterface):
    PLUGIN_NAME = 'msgfmt'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__files = []

    def initialize(self, version: str, build_data: Mapping[str, Any]) -> None:
        if self.target_name != 'wheel':
            return

        for included in self.build_config.builder.recurse_included_files():
            distribution_path = Path(included.distribution_path)
            if distribution_path.suffix == '.po':
                output = UnopenedTemporaryFile(suffix='.mo')

                run(['msgfmt', '-o', str(output.name), included.path], check=True, stdin=DEVNULL)

                self.__files.append(output)
                build_data['force_include'][output.name] = str(distribution_path.with_suffix('.mo'))
                os.remove(included.path)
