from typedef.api import define

BYTE = define('BYTE', 1)
WORD = define('WORD', 2)
DWORD = define('DWORD', 4)
QWORD = define('QWORD', 8)
PVOID = define('PVOID', (4, 8))
SIZE_T = PVOID
SSIZE_T = define('SSIZE_T', (4, 8), signed=True)
HALF_PTR = define('HALF_PTR', (2, 4))
