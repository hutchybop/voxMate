import os
from contextlib import contextmanager

@contextmanager
def mute_output():
    """Temporarily silence low level C/C++ writes to stdout & stderr."""
    devnull = open(os.devnull, "w")
    # Save the original file‑descriptors so we can restore them later
    saved_stdout = os.dup(1)   # fd 1 = stdout
    saved_stderr = os.dup(2)   # fd 2 = stderr
    # Point both descriptors at /dev/null
    os.dup2(devnull.fileno(), 1)
    os.dup2(devnull.fileno(), 2)
    try:
        yield
    finally:
        # Restore the original descriptors
        os.dup2(saved_stdout, 1)
        os.dup2(saved_stderr, 2)
        # Clean up
        os.close(saved_stdout)
        os.close(saved_stderr)
        devnull.close()