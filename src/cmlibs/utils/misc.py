import hashlib


# Source - https://stackoverflow.com/a/44873382
# Posted by maxschlepzig, modified by community. See post 'Timeline' for change history
# Retrieved 2026-07-30, License - CC BY-SA 4.0
def sha256sum_old(filename):
    h = hashlib.sha256()
    b = bytearray(1024 * 1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()
import hashlib

def sha256sum(filename, normalize=True):
    """
    An efficient file hashing utility that avoids line-ending issues.

    :param filename: The name of the files content to hash.
    :param normalize: Normalize line endings in the file.
    :return: The hash of the file contents.
    """
    h = hashlib.sha256()

    with open(filename, 'rb', buffering=0) as f:
        last_was_cr = False

        while chunk := f.read(1024 * 1024):
            if normalize:
                chunk = chunk.replace(b"\r\n", b"\n")

                if last_was_cr and chunk.startswith(b"\n"):
                    chunk = chunk[1:]

                last_was_cr = chunk.endswith(b"\r")
                chunk = chunk.replace(b"\r", b"\n")

            h.update(chunk)

    return h.hexdigest()