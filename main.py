"""coolest-art-01 entry: copy the bundled artwork to the output location.

The artwork lives in the repository as entry.png, beside this file. This
program copies it byte for byte to the output directory, so both grader
runs write exactly the same bytes. Standard library only, no network,
no randomness, no dependence on the working directory or the clock.
"""

import hashlib
import os
import shutil
import sys

# The artwork file, sitting beside this program in the repository.
SOURCE_NAME = "entry.png"

# The output file name is fixed by the competition rules, whatever the
# image format inside (a PNG or a JPEG is told apart by its first bytes).
OUTPUT_NAME = "entry.png"

# The competition cap: an image over 1 MiB takes no prize, so refuse to
# emit one rather than silently submitting an invalid entry.
MAX_BYTES = 1_048_576


def source_path() -> str:
    """Absolute path of the bundled artwork, resolved from this file."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, SOURCE_NAME)


def output_path() -> str:
    """Where the artwork must be written.

    The grader sets MAKEFUN_OUTPUT_DIR (standing in for /output). The
    legacy spelling MAKEFUN_OUTPUT names the output file itself. With
    neither set, fall back to /output/entry.png.
    """
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if out_dir:
        return os.path.join(out_dir, OUTPUT_NAME)
    legacy = os.environ.get("MAKEFUN_OUTPUT", "").strip()
    if legacy:
        # A legacy value naming a directory means "put entry.png in it".
        if os.path.isdir(legacy):
            return os.path.join(legacy, OUTPUT_NAME)
        return legacy
    return os.path.join(os.sep, "output", OUTPUT_NAME)


def main() -> int:
    src = source_path()
    if not os.path.isfile(src):
        print(f"error: artwork not found: {src}", file=sys.stderr)
        return 1
    if os.path.getsize(src) > MAX_BYTES:
        print(
            f"error: artwork is {os.path.getsize(src)} bytes, over the "
            f"{MAX_BYTES}-byte cap: {src}",
            file=sys.stderr,
        )
        return 1

    dst = output_path()
    parent = os.path.dirname(dst)
    if parent:
        os.makedirs(parent, exist_ok=True)

    # Copy the bytes unchanged: the judge sees exactly this file.
    shutil.copyfile(src, dst)

    # Verify the copy before reporting success, so a partial or
    # truncated write is never left standing as a valid-looking entry.
    if _sha256(dst) != _sha256(src):
        print(f"error: copy verification failed: {dst}", file=sys.stderr)
        return 1
    return 0


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


if __name__ == "__main__":
    sys.exit(main())
