from typing import Any, Mapping
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from pathlib import Path
from subprocess import run, DEVNULL
from .tempfile import UnopenedTemporaryFile

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
                path = Path(included.path)
                output = UnopenedTemporaryFile(suffix='.mo')

                run(['msgfmt', '-o', str(output), str(path)], check=True, stdin=DEVNULL)

                self.__files.append(output)
                build_data['force_include'][str(output)] = str(distribution_path.with_suffix('.mo'))
                path.unlink()
