.. contents:: **grsched**
   :backlinks: top
   :depth: 2


Summary
============================================
A tool to show Garoon schedule at terminals.


Installation
============================================
::

    pip install grsched


Usage
============================================

::

    $ grsched configure
    subdomain []: <input>
    basic auth info (base64 encoded 'login-name:passowrd'): <input>
    $ grsched events
    ...
    $ grsched show next
    ...


Command help
----------------------------
::

    Usage: grsched [OPTIONS] COMMAND [ARGS]...

      common cmd help

    Options:
      --version      Show the version and exit.
      --debug        For debug print.
      -q, --quiet    Suppress execution log messages.
      -v, --verbose
      -h, --help     Show this message and exit.

    Commands:
      configure  Setup configurations of the tool.
      events     List events.
      show       Show specific event(s).
      users      List users.
      version    Show version information

::

    Usage: grsched events [OPTIONS]

      List events.

    Options:
      --user USER_ID    user id of the target. defaults to the login user.
      --since DATETIME  datetime.
      -h, --help        Show this message and exit.

      Issue tracker: https://github.com/thombashi/grsched/issues

::

    Usage: grsched show [OPTIONS] [EVENT_IDS]...

      Show specific event(s). EVENT_IDS must be space-separated IDs of events to
      be shown. You can also use a special specifier "next" to show the next
      upcoming event.

    Options:
      --user USER_ID  user id of the target. defaults to the login user.
      -h, --help      Show this message and exit.

      Issue tracker: https://github.com/thombashi/grsched/issues


Dependencies
============================================
- Python 3.5+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/grsched/network/dependencies>`__
