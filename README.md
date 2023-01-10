# hatch-msgfmt
A hatch msgfmt plugin, simply replacing all po files with mo files, using msgfmt in `PATH`.

At a future point, a pure-python version could be implemented, by implementing
a pure-Python version of msgfmt.  [The standard cpython msgfmt.py](https://
github.com/python/cpython/blob/main/Tools/i18n/msgfmt.py) could be a starting
point for this, but it's not as capable as GNU Gettext, and doesn't support
plural forms.  Even with a fresh implementation, handling the file encoding
from the header is challenging, especially for variable-length encodings like
EUC-JP, which could feasibly cause particular problems.

Better to just use the system one for now.  If somebody wants to submit a pure-
python implementation that functions, I'll gladly integrate it as a separate
msgfmtpy plugin in the same repository.

# Copyright

This plugin is Copyright 2023 Absolute Performance, Inc.

MIT licensed.
