"""Prepare stable assets from the exact tested ZIP; no rebuilding or uploading.

python release_maintenance/promote_package.py PATH_TO_TEST_ZIP OUTPUT_DIRECTORY
The caller publishes them on the SAME numeric release after explicit approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


def promote(source, destination):
    source, destination = Path(source), Path(destination)
    if source.name != 'FineDiaryMessenger-test-windows-x64.zip':
        raise ValueError('Expected the tested channel ZIP')
    checksum = source.with_suffix('.zip.sha256').read_text(encoding='ascii').split()[0]
    with source.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if checksum != digest:
        raise ValueError('Tested ZIP checksum mismatch')
    with zipfile.ZipFile(source) as zf:
        if zf.testzip() is not None:
            raise ValueError('Corrupt ZIP')
        meta = json.loads(zf.read('FineDiaryMessenger/_internal/channel-runtime.json'))
        if meta.get('channel_protocol') != 1 or meta.get('app') != 'FineDiaryMessenger':
            raise ValueError('Unsupported package')
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / 'FineDiaryMessenger-windows-x64.zip'
    checksum_target = target.with_suffix('.zip.sha256')
    if target.exists() or checksum_target.exists():
        raise FileExistsError('Do not overwrite published assets')
    with source.open('rb') as original, target.open('xb') as copy:
        shutil.copyfileobj(original, copy)
    with target.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
            raise ValueError('Copied ZIP differs from tested package')
    checksum_target.write_text(f'{digest}  {target.name}\n', encoding='ascii')
    return target, checksum_target


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    for result in promote(args.source, args.destination):
        print(result)
