# typedef

A somewhat convenient package for packing and unpacking structs, unions, and arrays using C-like syntax

## Installation
```sh
pip install typedef
```
## Usage*
```python
from typedef import *
```

## Features
### Defining structs, unions and arrays similarly to C
```python
SIZE_LIST = struct([
    (DWORD, 'alignment'),
    (WORD[4], 'sizes')              # array of 4 words
])

VERSION = struct([
    (DWORD, 'build_version'),
    (WORD, 'major'),
    (WORD, 'minor')
])
```
```python
FLAGS = union([
    (BYTE[4], 'bytes'),             
    (DWORD, 'dw')
])
```
```python
HEADER = struct([ 
    (VERSION, 'file_version'),      # using existing definitions
    (FLAGS, 'flags'),
    struct([                    
        (WORD, 'size'),
        (WORD, 'offset')
    ], 'inner_struct'),             # define nested definitions
    struct([ 
        (DWORD, 'checksum'),
        (DWORD, 'machine')
    ])                              # define anonymous nested definitions
])
```

### Implicit alignment or explicit pragma pack support
```python
with pragma.pack(1):            # using context manager 
    # define structs here...
...
```
```python
pragma.pack.push(4)             # explicitly pushing and popping
# define structs here...
...
pragma.pack.pop()               
```

### Convenient initialization
```python
ver = VERSION()  # using default values for each type
```
```python
buffer = '\xbb\x01\x02\x03'    # using string buffer (`bytes` on py3)
ver = VERSION(buffer) 
```
```python
iobuffer = StringIO('\xbb\x01\x02\x03')    # using `StringIO` (`BytesIO` on py3)
ver = VERSION(iobuffer) 
```
```python
in_file = open('{some_path}','rb')    # using files
ver = VERSION(in_file) 
```
```python
data_dict = { 'build_version': 9600, 'major': 8, 'minor':1 }   # using dictionary for structs
ver = VERSION(data_dict) 
```
```python
data_list = ['\x01\x02', 3, 5]   # using list for arrays
size_list = SIZE_LIST({'sizes':data_list}) 
```

### Class-like access to attributes
```python
if ver.major > 3:
    ...
```
```python
for name, value in ver:       # iterating over struct/union instance
    ...
```
```python
for index, value in size_list.sizes:       # iterating over array instance
    ...
```
```python
wanted_sizes = size_list.sizes[2:3]       # getting slice of array instance
...
```
### Conveniently update values
```python
>>> ver.minor = 3
>>> ver
00 00 00 00 00 00 03 00
...
```
```python
>>> ver.major = '\x01\xFF'
>>> ver
00 00 00 00 01 ff 03 00
...
```
```python
size_list.sizes = [1,2]
...
```

### Initialize types using file and sync it on every change
```python
# file must have read/write access, and contain enough buffer to initialize the type
in_file = open('{some_path}','r+b')    
ver = VERSION(in_file,mode=F_SYNC) 
```

### Easily get the updated byte-string of a type:
```python
>>> bytes(ver)
b'\x00\x00\x00\x00\x01\xff\x03\x00'
```
### Allow types that rely on machine architecture
```python
ARCH_DEP = struct([
    (SIZE_T, 'size'),
    (PVOID, 'pointer')
])

>>> s_32bit = ARCH_DEP('\x00\x00\x00\x00\xFF\xFF\xFF\xFF', target=Arch.x86)
>>> s_64bit = ARCH_DEP('\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF', target=Arch.x64)
>>> s_32bit.size              
0                             
>>> hex(s_32bit.pointer)      
'0xffffffff'                  
>>> s_64bit.size              
0                             
>>> hex(s_64bit.pointer)      
'0xffffffffffffffff'          
```
### Endian, signed 
```python
 U = union([
    (DWORD, 'unsignedLittle'),
    (~DWORD, 'signedLittle'),
    (+DWORD, 'unsignedBig'),
    (+~DWORD, 'signedBig')
])
```
### Get size of instance:
```python
>>> sizeof(ver)
8
```
## Examples
1. dump instance as json [using TypeEncoder](examples/dump_json.py)
1. parse the [pe-file header](examples/parse_pe_header.py)

## Limitations
1. union initialization is limited to buffers or files
1. no flexible arrays
1. no nested arrays
1. no forward declation

## External dependencies
none

## Compatability**
- Python 2.7.8 
- Python 3.5.2 

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Remarks
[]()|[]()
--|--
\* |  Be mindful of name collision with the stdlib `struct`
\*\* |  Tested using the specified versions; probably will work on any 2.7.x version and any 3.x
