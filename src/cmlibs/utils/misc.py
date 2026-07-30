import hashlib


# Source - https://stackoverflow.com/a/44873382
# Posted by maxschlepzig, modified by community. See post 'Timeline' for change history
# Retrieved 2026-07-30, License - CC BY-SA 4.0
def sha256sum(filename):
    """
    An efficient file hashing utility that avoids line-ending issues.

    :param filename: The name of the files content to hash.
    :return: The hash of the file contents.
    """
    h = hashlib.sha256()
    b = bytearray(1024 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()
