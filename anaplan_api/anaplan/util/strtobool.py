# ===============================================================================
# Created:        19 Feb 2024
# @author:        Jesse Wilson
# Description:    Re-implementing strtobool from deprecated distutils package.
# Input:          Authorization header string, workspace ID string, and model ID string
# Output:         None
# ===============================================================================


def strtobool(value: str) -> bool:
    """Convert a string representation of truth to boolean equivalent.
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.

    :param value: String representation of a boolean value.
    :type value: str
    :rtype: bool
    :raises: ValueError
    """

    val = value.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid truth value {val}")
