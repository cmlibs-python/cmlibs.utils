

def _parse_vector(text, value_count=None):
    try:
        values = [float(value) for value in text.split(",")]
        if value_count is None or len(values) == value_count:
            return values
    except ValueError:
        pass

    return None


def parse_vector_3(lineedit):
    """
    Return 3 component real vector as list from comma separated text in QLineEdit widget
    or None if invalid.
    """
    return _parse_vector(lineedit.text(), 3)


def parse_vector(lineedit):
    """
    Return one or more component real vector as list from comma separated text in QLineEdit widget
    or None if invalid.
    """
    return _parse_vector(lineedit.text())


def _parse_real(text, fail_value, non_negative=False):
    try:
        value = float(text)
        return fail_value if non_negative and value < 0.0 else value
    except ValueError:
        pass

    return fail_value


def parse_real(lineedit):
    """
    Return real value from line edit text, or 0.0 if not a float.
    """
    return _parse_real(lineedit.text(), 0.0)


def parse_real_non_negative(lineedit):
    """
    Return non-negative real value from line edit text, or -1.0 if negative or not a float.
    """
    return _parse_real(lineedit.text(), -1.0, True)
