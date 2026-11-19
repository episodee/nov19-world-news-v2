"""Publish the adjacent PNG locally with an atomic, verified copy (Python 3.13)."""
import os
from pathlib import Path
import sys

# Fixed staging name deliberately avoids clocks and random temporary names.
PNG_MAGIC = b'\x89PNG\r\n\x1a\n'


def main():
    data = Path(__file__).resolve().with_name('entry.png').read_bytes()
    if not data.startswith(PNG_MAGIC):
        raise ValueError('entry.png has an invalid PNG signature')
    directory = Path(os.environ.get('MAKEFUN_OUTPUT_DIR') or 'output')
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / 'entry.png'
    temporary = directory / '.entry.png.tmp'
    try:
        with temporary.open('wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(target)
        if target.read_bytes() != data:
            raise OSError('output read-back differs from source')
    finally:
        temporary.unlink(missing_ok=True)
    print(f'Verified {target}: {len(data)} bytes')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        sys.exit(1)
