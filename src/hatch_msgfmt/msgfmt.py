#! /usr/bin/env python3
# Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>
# Edited into a hatch plugin by Taylor C. Richberger <tcr@absolute-performance.com>

"""Generate binary message catalog from textual translation description.
"""

from email.parser import HeaderParser
from io import BytesIO
from typing import BinaryIO, Optional, MutableMapping, Union
import array
import ast
import struct

def add(
    messages: MutableMapping[bytes, bytes],
    ctxt: Optional[bytes],
    id: Optional[bytes],
    str: Optional[bytes],
    fuzzy: bool) -> None:

    "Add a non-fuzzy translation to the dictionary."
    if not fuzzy and str:
        assert str is not None
        assert id is not None

        if ctxt is None:
            messages[id] = str
        else:
            messages[b"%b\x04%b" % (ctxt, id)] = str


def generate(messages: MutableMapping[bytes, bytes]) -> bytes:
    "Return the generated output."

    # the keys are sorted in the .mo file
    keys = sorted(messages.keys())
    offsets = []
    ids = strs = b''
    for id in keys:
        # For each string, we need size and file offset.  Each string is NUL
        # terminated; the NUL does not count into the size.
        offsets.append((len(ids), len(id), len(strs), len(messages[id])))
        ids += id + b'\0'
        strs += messages[id] + b'\0'
    output = ''
    # The header is 7 32-bit unsigned integers.  We don't use hash tables, so
    # the keys start right after the index tables.
    # translated string.
    keystart = 7*4+16*len(keys)
    # and the values start after the keys
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1+keystart]
        voffsets += [l2, o2+valuestart]
    offsets = koffsets + voffsets
    output = struct.pack("Iiiiiii",
                         0x950412de,       # Magic
                         0,                 # Version
                         len(keys),         # # of entries
                         7*4,               # start of key index
                         7*4+len(keys)*8,   # start of value index
                         0, 0)              # size and offset of hash table
    output += array.array("i", offsets).tobytes()
    output += ids
    output += strs
    return output


def make(input: Union[BinaryIO, bytes]) -> bytes:
    messages: MutableMapping[bytes, bytes] = {}
    ID = 1
    STR = 2
    CTXT = 3

    if isinstance(input, bytes):
        input = BytesIO(input)

    lines = input.readlines()

    section = msgctxt = None
    fuzzy = False

    # Start off assuming Latin-1, so everything decodes without failure,
    # until we know the exact encoding
    encoding = 'latin-1'
    msgid = None
    msgstr = None
    is_plural = False

    # Parse the catalog
    lno = 0
    for l in lines:
        l = l.decode(encoding)
        lno += 1
        # If we get a comment line after a msgstr, this is a new entry
        if l[0] == '#' and section == STR:
            add(messages, msgctxt, msgid, msgstr, fuzzy)
            section = msgctxt = None
            fuzzy = False
        # Record a fuzzy mark
        if l[:2] == '#,' and 'fuzzy' in l:
            fuzzy = True
        # Skip comments
        if l[0] == '#':
            continue
        # Now we are in a msgid or msgctxt section, output previous section
        if l.startswith('msgctxt'):
            if section == STR:
                add(messages, msgctxt, msgid, msgstr, fuzzy)
            section = CTXT
            l = l[7:]
            msgctxt = b''
        elif l.startswith('msgid') and not l.startswith('msgid_plural'):
            if section == STR:
                add(messages, msgctxt, msgid, msgstr, fuzzy)
                if not msgid:
                    assert msgstr
                    # See whether there is an encoding declaration
                    p = HeaderParser()
                    charset = p.parsestr(msgstr.decode(encoding)).get_content_charset()
                    if charset:
                        encoding = charset
            section = ID
            l = l[5:]
            msgid = msgstr = b''
            is_plural = False
        # This is a message with plural forms
        elif l.startswith('msgid_plural'):
            if section != ID:
                raise RuntimeError('msgid_plural not preceded by msgid')

            l = l[12:]
            assert msgid
            msgid += b'\0' # separator of singular and plural
            is_plural = True
        # Now we are in a msgstr section
        elif l.startswith('msgstr'):
            section = STR
            if l.startswith('msgstr['):
                if not is_plural:
                    raise RuntimeError('plural without msgid_plural')
                l = l.split(']', 1)[1]
                if msgstr:
                    msgstr += b'\0' # Separator of the various plural forms
            else:
                if is_plural:
                    raise RuntimeError('indexed msgstr required for plural')
                l = l[6:]
        # Skip empty lines
        l = l.strip()
        if not l:
            continue
        l = ast.literal_eval(l)
        if section == CTXT:
            msgctxt += l.encode(encoding)
        elif section == ID:
            msgid += l.encode(encoding)
        elif section == STR:
            msgstr += l.encode(encoding)
        else:
            raise RuntimeError('Syntax error')

    # Add last entry
    if section == STR:
        add(messages, msgctxt, msgid, msgstr, fuzzy)

    # Compute output
    return generate(messages)
