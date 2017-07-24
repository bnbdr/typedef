class BufferTooShort(ValueError):
    """
    Raised whenever the input buffer/file is too small to initialize the type
    """


class UnsupportedInitializationMethod(ValueError):
    """
    Raised when trying to initialize a type with unsupported input
    """


class TypeMismatch(TypeError):
    """
    Raised when an input's type does not match target type
    """


class PragmaValueMissing(ValueError):
    """
    Raised when trying to set pragma without value
    """


class UnsupportedPragmaPack(ValueError):
    """
    Raised when trying to set pragma pack with an supported value
    """


class ArchDependentType(ValueError):
    """
    Raised when trying to create instance of type that is packed differently in each architeture, without specifying the target architecture
    """


class BadAccessorName(NameError):
    """
    Raised when trying to define type with forbidden name
    """


class BadBufferInput(TypeError):
    """
    when the string input is in unicode in py2 or not bytes in py3
    """


class MissingMember(AttributeError):
    """
    when member is being accessd but cannot be found
    """
