import logging

from exec.cmd import run_cmd, CompletedProcess
from typing import Optional


def fastboot_erase_dtbo():
    logging.info("Fastboot: Erasing DTBO")
    run_cmd(
        [
            'fastboot',
            'erase',
            'dtbo',
        ],
        capture_output=True,
    )


def fastboot_flash(partition: str, file: str, sparse_size: Optional[str] = None):
    logging.info(f"Fastboot: Flashing {file} to {partition}")
    result = run_cmd([
        'fastboot',
        *(['-S', sparse_size] if sparse_size is not None else []),
        'flash',
        partition,
        file,
    ])
    assert isinstance(result, CompletedProcess)
    if result.returncode != 0:
        raise Exception(f'Failed to flash {file}')


def fastboot_boot(file):
    logging.info(f"Fastboot: booting {file}")
    result = run_cmd([
        'fastboot',
        'boot',
        file,
    ])
    assert isinstance(result, CompletedProcess)
    if result.returncode != 0:
        raise Exception(f'Failed to boot {file} using fastboot')
