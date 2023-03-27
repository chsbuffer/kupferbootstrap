from __future__ import annotations

import logging
import os
import toml
import yaml

from copy import deepcopy
from typing import Any, ClassVar, Optional, Mapping

from config.state import config
from constants import Arch, BASE_DISTROS, KUPFER_HTTPS, REPOS_CONFIG_FILE, REPOSITORIES
from dataclass import DataClass, Munch, toml_inline_dicts, TomlEncoder, TomlPreserveInlineDictEncoder
from utils import sha256sum


REPOS_KEY = 'repos'
NAME_KEY = 'name'
REMOTEURL_KEY = 'remote_url'
LOCALONLY_KEY = 'local_only'
OPTIONS_KEY = 'options'
BASEDISTROS_KEY = 'base_distros'

_current_config: Optional[ReposConfigFile]


class AbstrRepoConfig(DataClass):
    options: Optional[dict[str, str]]
    _strip_hidden: ClassVar[bool] = True
    _sparse: ClassVar[bool] = True


class BaseDistroRepo(AbstrRepoConfig):
    remote_url: Optional[str]


class RepoConfig(AbstrRepoConfig):
    name: str
    remote_url: Optional[str | dict[Arch, str]]
    local_only: Optional[bool]


class BaseDistro(DataClass):
    remote_url: Optional[str]
    repos: dict[str, BaseDistroRepo]


class ReposConfigFile(DataClass):
    remote_url: Optional[str]
    repos: dict[str, RepoConfig]
    base_distros: dict[Arch, BaseDistro]
    _path: Optional[str]
    _checksum: Optional[str]
    _strip_hidden: ClassVar[bool] = True
    _sparse: ClassVar[bool] = True

    def __init__(self, d, **kwargs):
        remote_url = d.get(REMOTEURL_KEY, None)
        super().__init__(d=d, **kwargs)
        for repo_cls, defaults, repos in [
            (RepoConfig, REPO_DEFAULTS, self.get(REPOS_KEY, {})),
            *[(BaseDistroRepo, BASE_DISTRO_DEFAULTS, _distro.repos) for _distro in self.base_distros.values()],
        ]:
            if repos is None:
                continue
            for name, repo in repos.items():
                _repo = defaults | (repo or {})  # type: ignore[operator]
                if REMOTEURL_KEY not in repo and not repo.get(LOCALONLY_KEY, None):
                    _repo[REMOTEURL_KEY] = remote_url
                repos[name] = repo_cls(_repo, **kwargs)
            # self.repos = repos

    def toDict(self, strip_hidden: Optional[bool] = None, sparse: Optional[bool] = None):
        d = super().toDict(strip_hidden=strip_hidden, sparse=sparse)
        if REPOS_KEY in d:
            for v in d[REPOS_KEY].values():
                if isinstance(v, dict) and NAME_KEY in v:
                    v.pop(NAME_KEY)
        return d

    @staticmethod
    def parse_config(path: str) -> ReposConfigFile:
        try:
            with open(path, 'r') as fd:
                data = yaml.safe_load(fd)
            data['_path'] = path
            data['_checksum'] = sha256sum(path)
            return ReposConfigFile(data, validate=True)
        except Exception as ex:
            logging.error(f'Error parsing repos config at "{path}":\n{ex}')
            raise ex

    def toToml(self, strip_hidden=None, sparse=None, encoder=TomlPreserveInlineDictEncoder()):
        d = self.toDict(strip_hidden=strip_hidden, sparse=sparse)
        for key in [REPOS_KEY, ]:
            if key not in d or not isinstance(d[key], Mapping):
                continue
            inline = {name: {k: toml_inline_dicts(v) for k, v in value.items()} for name, value in d[key].items()}
            logging.info(f"Inlined {key}: {inline}")
            d[key] = inline
        return toml.dumps(d, encoder=encoder)

    def toToml_old(self, **kwargs):
        """Dumps specific TOML format, kwargs are ignored."""
        def toml_line(k, v):
            assert isinstance(k, str)
            if isinstance(v, dict):
                assert isinstance(v, Munch)
                return f'{k} = ' + v.toYAML(default_flow_style=True).strip('\n')
            #return toml.dumps({k: (v if not isinstance(v, dict) else toml.}, encoder=toml.encoder.TomlPreserveInlineDictEncoder).strip('\n')

        res = ''
        for k in self.keys():
            if k == REPOS_KEY:
                continue
            res

        for k, v in self.repos.items():
            res += f"[repos.{k}]\n"
            for subk, subv in v.items():
                res += toml_line(subk, subv) + '\n'
            res += '\n'
        return res


REPO_DEFAULTS = {
    LOCALONLY_KEY: None,
    REMOTEURL_KEY: None,
    OPTIONS_KEY: {'SigLevel': 'Never'}
}

BASE_DISTRO_DEFAULTS = {
    REMOTEURL_KEY: None,
    OPTIONS_KEY: None,
}

REPOS_CONFIG_DEFAULT = ReposConfigFile({
    '_path': None,
    '_checksum': None,
    REMOTEURL_KEY: KUPFER_HTTPS,
    REPOS_KEY: {
        'local': REPO_DEFAULTS | {LOCALONLY_KEY: True},
        **{r: deepcopy(REPO_DEFAULTS) for r in REPOSITORIES},
    },
    BASEDISTROS_KEY: {
        arch: {
            'repos': {k: {'remote_url': v} for k, v in arch_def['repos'].items()},
        }
        for arch, arch_def in BASE_DISTROS.items()
    },
})

_current_config = deepcopy(REPOS_CONFIG_DEFAULT)

def get_repo_config(
    initialize_pkgbuilds: bool = False,
    repo_config_file: Optional[str] = None,
) -> tuple[ReposConfigFile, bool]:
    global _current_config
    pkgbuilds_dir = config.get_path('pkgbuilds')
    repo_config_file_default = os.path.join(pkgbuilds_dir, REPOS_CONFIG_FILE)
    if repo_config_file is None:
        repo_config_file_path = repo_config_file_default
    else:
        repo_config_file_path = repo_config_file
    if not os.path.exists(repo_config_file_path):
        if repo_config_file is not None:
            raise Exception(f"Requested repo config {repo_config_file} doesn't exist")
        if not initialize_pkgbuilds:
            logging.warning(f"{repo_config_file_path} doesn't exist, using default Repositories")
            return deepcopy(REPOS_CONFIG_DEFAULT), False
        from packages.pkgbuild import init_pkgbuilds
        init_pkgbuilds()
        return get_repo_config(initialize_pkgbuilds=False, repo_config_file=repo_config_file_path)
    conf = _current_config
    changed = False
    if not conf or conf._path != repo_config_file_path or conf._checksum != sha256sum(repo_config_file_path):
        conf = ReposConfigFile.parse_config(repo_config_file_path)
        if repo_config_file_path == repo_config_file_default:
            _current_config = conf
            changed = True
    return conf, changed


def get_repos(**kwargs) -> list[RepoConfig]:
    config, _ = get_repo_config(**kwargs)
    return list(config.repos.values())
