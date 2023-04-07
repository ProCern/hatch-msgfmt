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
`msgfmtpy` plugin in the same repository.

# Config parameters

* `locales`: The location of the source `.po` files.

* `destination`: The location of the destination `.mo` files.  They will be put
  into this location in the same structure as the source tree relative to the
  `locales` path.

* `pathsub_regex` (optional): An input regex to match against source files for
  name changes.

* `pathsub_replace` (required if `pathsub_regex` is present): An replacement
  pattern to use for name changes.

# Copyright

This plugin is Copyright 2023 Absolute Performance, Inc. with contributions by
[Adrián Chaves](https://github.com/Gallaecio).

MIT licensed.
