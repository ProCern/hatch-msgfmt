import re
from typing import Any, Mapping, Optional
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
        pathsub_regex: Optional[re.Pattern] = None

        if 'pathsub_regex' in self.config:
            pathsub_regex = re.compile(self.config['pathsub_regex'])

        pathsub_replace = self.config.get('pathsub_replace')

        for po in locales.glob('**/*.po'):
            mo = po.relative_to(locales).with_suffix('.mo')

            if pathsub_regex is not None:
                if not isinstance(pathsub_replace, str):
                    raise TypeError('pathsub_replace must be a string')
                mo = Path(re.sub(pathsub_regex, pathsub_replace, str(mo)))

            dest = str(destination / mo)

            output = UnopenedTemporaryFile(suffix='.mo')

            run(['msgfmt', '-o', str(output), str(po)], check=True, stdin=DEVNULL)

            self.__files.append(output)
            build_data['force_include'][str(output)] = dest
