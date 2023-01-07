import click
import logging

from json import dumps

from config.state import config
from utils import colors_supported, color_str

from .flavour import get_flavours, get_profile_flavour

profile_option = click.option('-p', '--profile', help="name of the profile to use", required=False, default=None)


@click.command(name='flavours')
@click.option('-j', '--json', is_flag=True, help='output machine-parsable JSON format')
def cmd_flavours(json: bool = False):
    'list information about available flavours'
    results = []
    profile_flavour = None
    flavours = get_flavours()
    use_colors = colors_supported(config.runtime.colors)
    if not flavours:
        raise Exception("No flavours found!")
    if not json:
        try:
            profile_flavour = get_profile_flavour()
        except Exception as ex:
            logging.debug(f"Failed to get profile flavour for marking as currently selected, continuing anyway. Exception: {ex}")
    for name in sorted(flavours.keys()):
        f = flavours[name]
        try:
            f.parse_flavourinfo()
        except Exception as ex:
            logging.debug(f"A problem happened while parsing flavourinfo for {name}, continuing anyway. Exception: {ex}")
        if not json:
            block = [*f.nice_str(newlines=True, colors=use_colors).split('\n'), '']
            if profile_flavour == f:
                prefix = color_str('>>> ', bold=True, fg='bright_green', use_colors=use_colors)
                block += [
                    color_str("Currently selected by profile ", bold=True, use_colors=use_colors) +
                    color_str(f'"{config.file.profiles.current}"\n', bold=True, fg="bright_green")
                ]
                block = [prefix + line for line in block]
            results += block
        else:
            d = dict(f)
            d["description"] = f.flavour_info.description if (f.flavour_info and f.flavour_info.description) else f.description
            if "flavour_info" in d and d["flavour_info"]:
                for k in set(d["flavour_info"].keys()) - set(['description']):
                    d[k] = d["flavour_info"][k]
            del d["flavour_info"]
            d["pkgbuild"] = f.pkgbuild.path if f.pkgbuild else None
            d["package"] = f.pkgbuild.name
            d["arches"] = sorted(f.pkgbuild.arches) if f.pkgbuild else None
            results += [d]
    print()
    if json:
        print(dumps({r['name']: r for r in results}, indent=4))
    else:
        for r in results:
            print(r)
