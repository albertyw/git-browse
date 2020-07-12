from git_browse import browse


def get_tag() -> str:
    return 'v%s' % browse.__version__


def get_tag_commit_hash() -> str:
    focus_hash = browse.get_commit_hash(get_tag())
    assert focus_hash
    return focus_hash.identifier
