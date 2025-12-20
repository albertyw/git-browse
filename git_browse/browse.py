#!/usr/bin/env python3

import argparse
import configparser
import os
import pathlib
import subprocess
import sys
from typing import Optional
import webbrowser

# Configure paths/modules from
# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
file_path = pathlib.Path(__file__).resolve()
parent, root = file_path.parent, file_path.parents[1]
sys.path.append(str(root))
try:
    sys.path.remove(str(parent))
except ValueError:  # Already removed
    pass

from git_browse import (  # NOQA
    bitbucket,
    github,
    gitlab,
    godocs,
    phabricator,
    sourcegraph,
    typedefs,
)


__version__ = "2.15.0"
HOST_REGEXES: dict[str, type[typedefs.Host]] = {
    github.GITHUB_SSH_URL: github.GithubHost,
    github.GITHUB_HTTPS_URL: github.GithubHost,
    github.GITHUB_UBER_SSH_URL: github.GithubHost,
    github.GITHUB_UBER_HTTPS_URL: github.GithubHost,
    github.GITHUB_UBER_OC_URL: github.GithubHost,
    bitbucket.BITBUCKET_SSH_URL: bitbucket.BitbucketHost,
    bitbucket.BITBUCKET_HTTPS_URL: bitbucket.BitbucketHost,
    gitlab.GITLAB_SSH_URL: gitlab.GitlabHost,
    gitlab.GITLAB_HTTPS_URL: gitlab.GitlabHost,
    # phabricator.UBER_SSH_GITOLITE_URL: phabricator.PhabricatorHost,
    # phabricator.UBER_HTTPS_GITOLITE_URL: phabricator.PhabricatorHost,
    # phabricator.UBER_OC_URL: phabricator.PhabricatorHost,
}


def copy_text_to_clipboard(text: str) -> None:
    stdin = text.encode("utf-8")
    try:
        subprocess.run(["pbcopy", "w"], input=stdin, close_fds=True, check=False)
    except FileNotFoundError:
        pass


def get_repository_root() -> pathlib.Path:
    current_path = pathlib.Path.cwd()
    for path in [current_path] + list(current_path.parents):
        git_config = path / ".git"
        if git_config.exists():
            return path
    raise FileNotFoundError(".git/config file not found")


def get_git_config_path() -> pathlib.Path:
    repository_root = get_repository_root()
    git_directory = repository_root / ".git"
    if git_directory.is_file():
        with open(git_directory, "r") as handle:
            data = handle.read()
            git_directory = pathlib.Path(data.split(" ")[1].strip())
    git_config_path = git_directory / "config"
    return git_config_path


def get_git_config_data(git_config_file: pathlib.Path) -> typedefs.GitConfig:
    # strict is removed here because gitconfig allows for multiple "fetch" keys
    config = configparser.ConfigParser(strict=False)
    config.read(git_config_file)
    try:
        git_url = config['remote "origin"']["url"]
    except KeyError as err:
        raise RuntimeError("git config file not parseable") from err
    branches = [b for b in config.keys() if 'branch "' in b]
    branches = [b.lstrip('branch "').rstrip('"') for b in branches]
    default_branch = "master"
    if "master" not in branches:
        if "main" in branches:
            default_branch = "main"
        elif branches:
            default_branch = branches[0]
    git_config = typedefs.GitConfig(git_url, default_branch)
    return git_config


def parse_git_url(
    git_config: typedefs.GitConfig,
    use_sourcegraph: bool = False,
    use_godocs: bool = False,
) -> typedefs.Host:
    host_class = None
    for regex, hc in HOST_REGEXES.items():
        if git_config.try_url_match(regex):
            host_class = hc
            break
    else:
        raise ValueError("git url not parseable")
    if use_sourcegraph:
        host = sourcegraph.SourcegraphHost.create(git_config)
        host.set_host_class(host_class)
    elif use_godocs:
        host = godocs.GodocsHost.create(git_config)
        host.set_host_class(host_class)
    else:
        try:
            host = host_class.create(git_config)
        except RuntimeError:
            # Fall back to sorucegraph if the primary repository host fails
            return parse_git_url(git_config, True, False)
    return host


def get_repository_host(
    use_sourcegraph: bool = False,
    godocs: bool = False,
) -> typedefs.Host:
    git_config_file = get_git_config_path()
    git_config = get_git_config_data(git_config_file)
    repo_host = parse_git_url(git_config, use_sourcegraph, godocs)
    return repo_host


def get_git_object(
    focus_object: str, path: pathlib.Path, host: typedefs.Host,
) -> typedefs.GitObject:
    if not focus_object:
        return typedefs.FocusObject.default()
    object_path = path.joinpath(focus_object).resolve()
    if not object_path.exists():
        focus_hash = get_commit_hash(focus_object)
        if focus_hash:
            return focus_hash
        error = "specified file does not exist: %s" % object_path
        raise FileNotFoundError(error)
    object_path_str = str(object_path.relative_to(get_repository_root()))
    if object_path.is_dir() and object_path_str[-1] != os.sep:
        object_path_str += os.sep
    return typedefs.FocusObject(object_path_str)


def get_commit_hash(identifier: str) -> Optional[typedefs.FocusHash]:
    command = ["git", "show", identifier, "--no-abbrev-commit"]
    process = subprocess.run(
        command,
        capture_output=True,
        universal_newlines=True, check=False,
    )
    if process.returncode != 0:
        return None
    commit_hash = process.stdout.split("\n")[0].split(" ")[1]
    return typedefs.FocusHash(commit_hash)


def open_url(
    url: str,
    dry_run: bool = False,
    copy_clipboard: bool = False,
) -> None:
    print(url)
    if copy_clipboard:
        copy_text_to_clipboard(url)
    if not dry_run:
        webbrowser.open(url)


def main() -> None:
    description = "Open repositories, directories, and files in the browser.\n"
    description += "https://github.com/albertyw/git-browse"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "target",
        nargs="?",
        help="file, directory, git hash, or git branch you wish to browse",
    )
    parser.add_argument(
        "--path",
        default="",
        help="relative path to the current git repository",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Do not open the url in the brower, and only print to stdout",
    )
    parser.add_argument(
        "-c",
        "--copy",
        action="store_true",
        help="Copy url to clipboard, if available",
    )
    parser.add_argument(
        "-s",
        "--sourcegraph",
        action="store_true",
        help="Open objects in sourcegraph",
    )
    parser.add_argument(
        "-g", "--godocs", action="store_true", help="Open objects in godocs",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    args = parser.parse_args()
    if args.sourcegraph and args.godocs:
        print("Sourcegraph and Godocs flags are mutually exclusive")
        return

    host = get_repository_host(args.sourcegraph, args.godocs)
    path = pathlib.Path.cwd().joinpath(args.path)
    git_object = get_git_object(args.target, path, host)
    url = host.get_url(git_object)
    open_url(url, args.dry_run, args.copy)


if __name__ == "__main__":
    main()
