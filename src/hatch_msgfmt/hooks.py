from hatchling.plugin import hookimpl
from .plugin import MsgfmtBuildHook

@hookimpl
def hatch_register_build_hook():
    return MsgfmtBuildHook
