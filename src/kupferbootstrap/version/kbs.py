import logging
import os

from typing import Union

from kupferbootstrap.distro.repo_config import ReposConfigFile
from kupferbootstrap.utils import git
from .compare import semver_compare, VerComp

KBS_VERSION: Union[str, None] = None

KBS_VERSION_MIN_KEY = "kbs_min_version"
KBS_VERSION_CI_MIN_KEY = "kbs_ci_version"


def get_kbs_version(kbs_folder: Union[str, None] = None) -> Union[str, None]:
    if KBS_VERSION:
        return KBS_VERSION
    if not kbs_folder:
        kbs_folder = os.path.join(os.path.dirname(__file__), "../" * 3)
    try:
        res = git(
            ["describe", "--tags", "--match", "v*.*.*"],
            use_git_dir=True,
            git_dir=os.path.join(kbs_folder, ".git"),
            capture_output=True,
        )
        if res.returncode:
            output = res.stderr or res.stdout
            if output and not isinstance(output, str):
                output = output.decode().strip()
            raise Exception(
                output
                or f"[Git failed without output. Return Code: {res.returncode}]"
            )
        return (res.stdout or b"").decode().strip()
    except Exception as ex:
        logging.warning(f"Failed to fetch KBS version with git: {ex!s}")
        return None


def compare_kbs_version_generic(
    kbs_version: str,
    minimum_ver: str | None,
) -> Union[VerComp, None]:
    if not minimum_ver:
        return None
    try:
        return semver_compare(minimum_ver.lstrip("v"), kbs_version.lstrip("v"))
    except Exception as ex:
        logging.warning(
            f"Failed to compare KBS version {kbs_version!r} to required minimum version {minimum_ver!r}: {ex!r}"
        )
        return None


def compare_kbs_version(
    kbs_version: str, repo_config: ReposConfigFile
) -> bool | None:
    """Returns True if KBS is new enough for PKGBUILDs"""
    minimum_ver = repo_config.get(KBS_VERSION_MIN_KEY)
    kbs_state = compare_kbs_version_generic(
        kbs_version=kbs_version, minimum_ver=minimum_ver
    )
    if not minimum_ver:
        logging.warning(
            f"Can't check PKGBUILDs for compatible KBS version as {KBS_VERSION_MIN_KEY!r} "
            "is empty in PKGBUILDs repos.yml"
        )
        return None
    if kbs_state == VerComp.RIGHT_OLDER:
        logging.warning(
            f"KBS version {kbs_version!r} is older than {minimum_ver!r} required by PKGBUILDs.\n"
            "Some functionality may randomly be broken.\nYou have been warned."
        )
        return False
    return True


def compare_kbs_ci_version(
    kbs_version: str, repo_config: ReposConfigFile
) -> bool | None:
    """Returns True if KBS is new enough for PKGBUILDs in CI"""
    minimum_ver = repo_config.get(KBS_VERSION_CI_MIN_KEY)
    if not minimum_ver:
        logging.warning(
            "Can't check PKGBUILDs for compatible KBS CI version: "
            f"Minimum CI KBS version {KBS_VERSION_CI_MIN_KEY!r} is empty in PKGBUILDs repos.yml!"
        )
        return None
    kbs_state = compare_kbs_version_generic(
        kbs_version=kbs_version, minimum_ver=minimum_ver
    )
    if kbs_state == VerComp.RIGHT_OLDER:
        logging.error(
            f"KBS CI version {kbs_version!r} is older than {minimum_ver!r} required by PKGBUILDs kbs_ci_version!\n"
            "CI is likely to fail!"
        )
        return False
    return True
