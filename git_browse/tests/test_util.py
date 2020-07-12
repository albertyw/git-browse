from git_browse import browse


def get_tag():
    return 'v%s' % browse.__version__


def get_tag_commit_hash():
    focus_hash = browse.get_commit_hash(get_tag())
    return focus_hash.identifier
