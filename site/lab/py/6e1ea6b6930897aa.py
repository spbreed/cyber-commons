"""Coding Agent — writes code, patches libraries, opens pull requests."""
import subprocess

from .._stubs import HTTP


def handle(message, session):
    return {"branch": _open_branch(message)}


def _open_branch(name):
    """Command injection: the branch name reaches a shell."""
    subprocess.run("git checkout -b " + name, shell=True)
    return name


def sync_vendor(vendor_host):
    """TLS verification disabled against a host the caller names."""
    return HTTP.get("https://" + vendor_host + "/manifest", verify=False)
