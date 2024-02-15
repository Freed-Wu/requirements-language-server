r"""Option
==========
"""

from pip._internal.commands import create_command

# https://pip.pypa.io/en/stable/reference/requirements-file-format/#supported-options
WHITELIST = [
    "-i",
    "--index-url",
    "--extra-index-url",
    "--no-index",
    "-c",
    "--constraint",
    "-r",
    "--requirement",
    "-e",
    "--editable",
    "-f",
    "--find-links",
    "--no-binary",
    "--only-binary",
    "--prefer-binary",
    "--require-hashes",
    "--pre",
    "--trusted-host",
    "--use-feature",
    "--global-option",
    "--config-settings",
    "--hash",
]

OPTIONS_WITH_EQUAL = {
    opt
    + ("=" if option.nargs and opt in option._long_opts else ""): option.help
    if option.help
    else ""
    for option in create_command("install").parser.option_list_all
    if (option._short_opts + option._long_opts)[0] in WHITELIST
    for opt in option._short_opts + option._long_opts
}

OPTIONS = {opt.rstrip("="): doc for opt, doc in OPTIONS_WITH_EQUAL.items()}
