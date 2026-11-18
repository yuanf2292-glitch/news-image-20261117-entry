"""news-image-20261117 entry: validated, chunked copy of the finished artwork.

The artwork (entry.png, "The World in One Page - Tuesday 17 November 2026")
is a fixed, pre-made image that lives in this same directory. The program
copies it byte-for-byte to the output directory, but only after proving the
source is a real, in-limits image, and it verifies the copy afterwards.

The artwork is JPEG bytes under the name entry.png: the competition tells
PNG and JPEG apart by their first bytes and keeps the name entry.png either
way, so this program accepts both.

Checks, in order:
  1. Source size must be at most 1 MiB (1_048_576 bytes); otherwise refuse.
  2. First bytes must be the PNG signature or the JPEG start-of-image
     marker; anything else is refused.
  3. The image header must declare a width and height, each at most
     1024 px and greater than 0; for PNG that is the IHDR chunk, for
     JPEG the first start-of-frame segment.
  4. Copy in 64 KiB chunks (the whole file is never loaded into memory).
  5. After writing, re-read the destination and compare its SHA-256 with
     the source's SHA-256; on any mismatch, delete the output and fail.

Standard library only, no network, deterministic. Nothing is written when
a check fails - a bad input produces no output file, not a silent one.
"""

import hashlib
import os
import struct

SRC_NAME = "entry.png"
MAX_BYTES = 1_048_576          # 1 MiB
MAX_DIMENSION = 1024           # px, width and height
CHUNK_SIZE = 65_536            # 64 KiB
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8\xff"


def _sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _png_dimensions(header):
    """(width, height) from the 33-byte PNG prefix, or raise ValueError."""
    length, chunk_type = struct.unpack(">I4s", header[8:16])
    if chunk_type != b"IHDR" or length != 13:
        raise ValueError("entry.png first chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def _jpeg_dimensions(f):
    """(width, height) from the first JPEG start-of-frame segment."""
    while True:
        marker = f.read(2)
        if len(marker) < 2 or marker[0] != 0xFF:
            raise ValueError("entry.png JPEG stream has no SOF segment")
        code = marker[1]
        if code in (0xD8, 0xD9) or 0xD0 <= code <= 0xD7:
            continue  # SOI, EOI, RSTn: no length field follows
        size_bytes = f.read(2)
        if len(size_bytes) < 2:
            raise ValueError("entry.png JPEG stream ends mid-segment")
        (seg_len,) = struct.unpack(">H", size_bytes)
        if seg_len < 2:
            raise ValueError("entry.png JPEG segment length is invalid")
        if 0xC0 <= code <= 0xCF and code not in (0xC4, 0xC8, 0xCC):
            body = f.read(5)
            if len(body) < 5:
                raise ValueError("entry.png JPEG SOF segment is truncated")
            height, width = struct.unpack(">xHH", body)
            return width, height
        f.seek(seg_len - 2, os.SEEK_CUR)


def _validate_image(path):
    """Raise ValueError unless the file is an acceptable entry image.

    Returns (format, size, width, height).
    """
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        raise ValueError(
            f"entry.png is {size} bytes, over the {MAX_BYTES} byte limit"
        )
    if size < 33:
        raise ValueError("entry.png is too small to hold an image header")
    with open(path, "rb") as f:
        header = f.read(33)
        if header[:8] == PNG_SIGNATURE:
            fmt = "PNG"
            width, height = _png_dimensions(header)
        elif header[:3] == JPEG_SOI:
            fmt = "JPEG"
            f.seek(0)
            width, height = _jpeg_dimensions(f)
        else:
            raise ValueError(
                "entry.png starts with neither the PNG signature nor "
                "the JPEG start-of-image marker"
            )
    if width == 0 or height == 0:
        raise ValueError("entry.png has a zero dimension")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            f"entry.png is {width}x{height}, over the "
            f"{MAX_DIMENSION}x{MAX_DIMENSION} limit"
        )
    return fmt, size, width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, SRC_NAME)
    fmt, size, width, height = _validate_image(src)
    src_hash = _sha256_of(src)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, SRC_NAME)

    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break
            fout.write(chunk)

    dst_hash = _sha256_of(dst)
    if dst_hash != src_hash:
        os.remove(dst)
        raise SystemExit(
            "copy verification failed: destination sha256 "
            f"{dst_hash} != source {src_hash}"
        )
    print(
        f"wrote {dst} ({fmt}, {size} bytes, {width}x{height}, "
        f"sha256 {dst_hash})"
    )


if __name__ == "__main__":
    main()
