import click
from json import dumps as json_dump
import logging

from config.state import config

from .device import get_devices, get_profile_device


@click.command(name='devices')
@click.option('--json', is_flag=True, help='output machine-parsable JSON format')
def cmd_devices(json: bool = False):
    'list the available devices and descriptions'
    devices = get_devices()
    if not devices:
        raise Exception("No devices found!")
    profile_device = None
    try:
        dev = get_profile_device()
        assert dev
        profile_device = dev
    except Exception as ex:
        logging.debug(f"Failed to get profile device for visual highlighting, not a problem: {ex}")
    output = ['']
    json_output = {}
    for name in sorted(devices.keys()):
        prefix = ''
        suffix = ''
        device = devices[name]
        assert device
        try:
            device.parse_deviceinfo(try_download=False)
        except Exception as ex:
            logging.debug(f"Failed to parse deviceinfo for extended description, not a problem: {ex}")
        if json:
            json_output[name] = device.get_summary().toDict()
            continue
        if profile_device and profile_device.name == device.name:
            prefix = '>>> '
            suffix = f'\n\nCurrently selected by profile "{config.file.profiles.current}"'
        snippet = f'{device}{suffix}'
        # prefix each line in the snippet
        snippet = '\n'.join([f'{prefix}{line}' for line in snippet.split('\n')])
        output.append(f"{snippet}\n")
    if json:
        output = ['\n' + json_dump(json_output, indent=4)]
    for line in output:
        print(line)
