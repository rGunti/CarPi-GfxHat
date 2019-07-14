
def try_int(val, default: int = None) -> int:
    try:
        return int(val)
    except TypeError:
        return default
    except ValueError:
        return default
