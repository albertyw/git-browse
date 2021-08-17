#!/usr/bin/env python3

import argparse
import configparser
import os
import pathlib
import re
import subprocess
from typing import Dict, Optional, Type
import webbrowser

from . import bitbucket, github, godocs, phabricator, sourcegraph, types


__version__ = '2.12.0'
HOST_REGEXES: Dict[str, Type[types.Host]] = {
    github.GITHUB_SSH_URL: github.GithubHost,
    github.GITHUB_HTTPS_URL: github.GithubHost,
    bitbucket.BITBUCKET_SSH_URL: bitbucket.BitbucketHost,
    bitbucket.BITBUCKET_HTTPS_URL: bitbucket.BitbucketHost,
    phabricator.UBER_SSH_GITOLITE_URL: phabricator.PhabricatorHost,
    phabricator.UBER_SSH_CONFIG_GITOLITE_URL: phabricator.PhabricatorHost,
    phabricator.UBER_HTTPS_GITOLITE_URL: phabricator.PhabricatorHost,
}


def copy_text_to_clipboard(text: str) -> None:
    stdin = text.encode('utf-8')
    try:
        subprocess.run(['pbcopy', 'w'], input=stdin, close_fds=True)
    except FileNotFoundError:
        pass


def get_repository_root() -> pathlib.Path:
    path = pathlib.Path.cwd()
    for path in [path] + list(path.parents):
        git_config = path / '.git'
        if git_config.exists():
            return path
    raise FileNotFoundError('.git/config file not found')


def get_git_config() -> pathlib.Path:
    repository_root = get_repository_root()
    git_directory = repository_root / '.git'
    if git_directory.is_file():
        with open(git_directory, 'r') as handle:
            data = handle.read()
            git_directory = pathlib.Path(data.split(' ')[1].strip())
    git_config_path = git_directory / 'config'
    return git_config_path


def get_git_url(git_config_file: pathlib.Path) -> str:
    # strict is removed here because gitconfig allows for multiple "fetch" keys
    config = configparser.ConfigParser(strict=False)
    config.read(git_config_file)
    try:
        git_url = config['remote "origin"']['url']
    except KeyError:
        raise RuntimeError("git config file not parseable")
    return git_url


def parse_git_url(
    git_url: str,
    use_sourcegraph: bool = False,
    use_godocs: bool = False,
) -> types.Host:
    for regex, host_class in HOST_REGEXES.items():
        match = re.search(regex, git_url)
        if match:
            break
    if not match:
        raise ValueError("git url not parseable")
    if use_sourcegraph:
        host = sourcegraph.SourcegraphHost.create(match)
        host.set_host_class(host_class)
    elif use_godocs:
        host = godocs.GodocsHost.create(match)
        host.set_host_class(host_class)
    else:
        host = host_class.create(match)
    return host


def get_repository_host(
    use_sourcegraph: bool = False,
    godocs: bool = False,
) -> types.Host:
    git_config_file = get_git_config()
    git_url = get_git_url(git_config_file)
    repo_host = parse_git_url(git_url, use_sourcegraph, godocs)
    return repo_host


def get_git_object(
    focus_object: str, path: pathlib.Path, host: types.Host
) -> types.GitObject:
    if not focus_object:
        return types.FocusObject.default()
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
    return types.FocusObject(object_path_str)


def get_commit_hash(identifier: str) -> Optional[types.FocusHash]:
    command = ['git', 'show', identifier, '--no-abbrev-commit']
    process = subprocess.run(
        command,
        capture_output=True,
        universal_newlines=True,
    )
    if process.returncode != 0:
        return None
    commit_hash = process.stdout.split("\n")[0].split(" ")[1]
    return types.FocusHash(commit_hash)


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
        'target',
        nargs='?',
        help='file, directory, git hash, or git branch you wish to browse'
    )
    parser.add_argument(
        '--path',
        default='',
        help='relative path to the current git repository'
    )
    parser.add_argument(
        '-d',
        '--dry-run',
        action='store_true',
        help='Do not open the url in the brower, and only print to stdout'
    )
    parser.add_argument(
        '-c',
        '--copy',
        action='store_true',
        help='Copy url to clipboard, if available',
    )
    parser.add_argument(
        '-s',
        '--sourcegraph',
        action='store_true',
        help='Open objects in sourcegraph'
    )
    parser.add_argument(
        '-g',
        '--godocs',
        action='store_true',
        help='Open objects in godocs'
    )
    parser.add_argument(
        '-v', '--version', action='version', version=__version__,
    )
    args = parser.parse_args()
    if args.sourcegraph and args.godocs:
        print('Sourcegraph and Godocs flags are mutually exclusive')
        return

    host = get_repository_host(args.sourcegraph, args.godocs)
    path = pathlib.Path.cwd().joinpath(args.path)
    git_object = get_git_object(args.target, path, host)
    url = host.get_url(git_object)
    open_url(url, args.dry_run, args.copy)


if __name__ == "__main__":
    main()
