class TypedefBaseException(Exception):
    """
    Base exception for package
    """


class BufferTooShort(TypedefBaseException):
    """
    Raised whenever the input buffer/file is too small to initialize the type
    """


class UnsupportedInitializationMethod(TypedefBaseException):
    """
    Raised when trying to initialize a type with unsupported input
    """


class TypeMismatch(TypedefBaseException):
    """
    Raised when an input's type does not match target type
    """


class PragmaValueMissing(TypedefBaseException):
    """
    Raised when trying to set pragma without value
    """


class UnsupportedPragmaPack(TypedefBaseException):
    """
    Raised when trying to set pragma pack with an supported value
    """


class ArchDependentType(TypedefBaseException):
    """
    Raised when trying to create instance of type that is packed differently in each architeture, without specifying the target architecture
    """


class BadAccessorName(TypedefBaseException):
    """
    Raised when trying to define type with forbidden name
    """


class BadBufferInput(TypedefBaseException):
    """
    when the string input is in unicode in py2 or not bytes in py3
    """


class MissingField(TypedefBaseException):
    """
    when member is being accessd but cannot be found
    """
