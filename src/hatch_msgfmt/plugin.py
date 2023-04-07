import re
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

        root = Path(self.root)
        locales = root / Path(self.config['locales'])
        destination = Path(self.config['destination'])
        input_re = self.config['input_re']
        output_sub = self.config['output_sub']

        for po in locales.glob('**/*.po'):
            mo = po.relative_to(locales)
            if input_re:
                mo = Path(re.sub(input_re, output_sub, str(mo)))
            dest = str(destination / mo)

            output = UnopenedTemporaryFile(suffix='.mo')

            run(['msgfmt', '-o', str(output), str(po)], check=True, stdin=DEVNULL)

            self.__files.append(output)
            build_data['force_include'][str(output)] = dest
