from __future__ import print_function
import json
from typedef import *

# used definition from 010editor template: https://www.sweetscape.com/010editor/repository/files/EXE.bt
with pragma.pack(1):
    IMAGE_DOS_HEADER = struct([
        (WORD, 'MZSignature'),
        (WORD, 'UsedBytesInTheLastPage'),
        (WORD, 'FileSizeInPages'),
        (WORD, 'NumberOfRelocationItems'),
        (WORD, 'HeaderSizeInParagraphs'),
        (WORD, 'MinimumExtraParagraphs'),
        (WORD, 'MaximumExtraParagraphs'),
        (WORD, 'InitialRelativeSS'),
        (WORD, 'InitialSP'),
        (WORD, 'Checksum'),
        (WORD, 'InitialIP'),
        (WORD, 'InitialRelativeCS'),
        (WORD, 'AddressOfRelocationTable'),
        (WORD, 'OverlayNumber'),
        (WORD[4], 'Reserved'),
        (WORD, 'OEMid'),
        (WORD, 'OEMinfo'),
        (WORD[10], 'Reserved2'),
        (DWORD, 'AddressOfNewExeHeader')
    ])

f = open(r'C:\windows\system32\cmd.exe', 'rb')
dos_hdr = IMAGE_DOS_HEADER(f)
print(json.dumps(dos_hdr, cls=TypeEncoder, indent=2))
