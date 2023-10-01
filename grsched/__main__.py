import errno
import sys
from datetime import date, datetime
from enum import Enum, unique
from textwrap import dedent
from typing import Optional, Tuple

import click
import pytablewriter as ptw
import pytz
from dateutil import tz
from dateutil.parser import parse
from requests.exceptions import HTTPError, TooManyRedirects

from .__version__ import __version__
from ._client import GaroonClient
from ._config import ConfigKey, app_config_mgr
from ._const import MODULE_NAME
from ._filter import col_separator_style_filter, style_filter
from ._logger import LogLevel, initialize_logger, logger


COMMAND_EPILOG = dedent(
    """\
    Issue tracker: https://github.com/thombashi/grsched/issues
    """
)
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], obj={})


@unique
class Context(Enum):
    LOG_LEVEL = 0
    VERBOSITY_LEVEL = 1
    CONFIGS = 2


def _extract_targets(user: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    target = None
    target_type = None

    if user:
        target = user
        target_type = "user"

    return (target, target_type)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, message="%(prog)s %(version)s")
@click.option("--debug", "log_level", flag_value=LogLevel.DEBUG, help="For debug print.")
@click.option(
    "-q",
    "--quiet",
    "log_level",
    flag_value=LogLevel.QUIET,
    help="Suppress execution log messages.",
)
@click.option("-v", "--verbose", "verbosity_level", count=True)
@click.pass_context
def cmd(ctx, log_level: str, verbosity_level: int):
    """
    common cmd help
    """

    ctx.obj[Context.LOG_LEVEL] = LogLevel.INFO if log_level is None else log_level
    ctx.obj[Context.VERBOSITY_LEVEL] = verbosity_level

    initialize_logger(name="{:s}".format(MODULE_NAME), log_level=ctx.obj[Context.LOG_LEVEL])

    try:
        app_configs = app_config_mgr.load()
    except ValueError as e:
        logger.debug(e)
        app_configs = {}

    ctx.obj[Context.CONFIGS] = app_configs


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
def version(ctx):
    """
    Show version information
    """

    import envinfopy

    click.echo(envinfopy.dumps(["grsched"], "markdown"))


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
def configure(ctx):
    """
    Setup configurations of the tool.
    """

    logger.debug("{} configuration file existence: {}".format(MODULE_NAME, app_config_mgr.exists))

    sys.exit(app_config_mgr.configure())


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
@click.argument("event_ids", type=str, nargs=-1)
@click.option(
    "--user", metavar="USER_ID", help="user id of the target. defaults to the login user."
)
def show(ctx, event_ids, user):
    """
    Show specific event(s).
    EVENT_IDS must be space-separated IDs of events to be shown.
    You can also use a special specifier "next" to show the next upcoming event.
    """

    verbosity_level = ctx.obj[Context.VERBOSITY_LEVEL]
    app_configs = ctx.obj[Context.CONFIGS]
    client = GaroonClient(
        subdomain=app_configs[ConfigKey.SUBDOMAIN], basic_auth=app_configs[ConfigKey.BASIC_AUTH]
    )
    target, target_type = _extract_targets(user)
    now = datetime.now(tz=tz.tzlocal())

    for event_id in event_ids:
        logger.debug("event: {}".format(event_id))

        if event_id == "next":
            try:
                events, _has_next = client.fetch_events(
                    start=date(now.year, now.month, now.day), target=target, target_type=target_type
                )
            except (HTTPError, TooManyRedirects) as e:
                logger.error(e)
                sys.exit(errno.EACCES)

            for event in events:
                if event.is_all_day:
                    continue

                if now < event.dtr.start_datetime:
                    print(event.as_markdown())
                    break
            else:
                logger.error("event not found")
                sys.exit(errno.ENOENT)

            continue

        try:
            event = client.fetch_event(event_id)
        except (HTTPError, TooManyRedirects) as e:
            logger.error(e)
            sys.exit(errno.EACCES)

        print(event.as_markdown())


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
@click.option(
    "--user", metavar="USER_ID", help="user id of the target. defaults to the login user."
)
@click.option("--since", metavar="DATETIME", help="datetime.")
def events(ctx, user, since):
    """
    List events.
    """

    verbosity_level = ctx.obj[Context.VERBOSITY_LEVEL]
    app_configs = ctx.obj[Context.CONFIGS]
    target, target_type = _extract_targets(user)
    client = GaroonClient(
        subdomain=app_configs[ConfigKey.SUBDOMAIN], basic_auth=app_configs[ConfigKey.BASIC_AUTH]
    )

    if since:
        since = parse(since)
    else:
        since = datetime.now(tz=tz.tzlocal())

    try:
        events, _has_next = client.fetch_events(
            start=date(since.year, since.month, since.day), target=target, target_type=target_type
        )
    except (HTTPError, TooManyRedirects) as e:
        logger.error(e)
        sys.exit(errno.EACCES)

    matrix = []
    for event in events:
        matrix.append(event.as_row(event.is_all_day))

    writer = ptw.TableWriterFactory().create_from_format_name("space_aligned")
    writer.style_filter_kwargs = {
        "now": datetime.now(pytz.timezone(events[0].timezone)),
        "dtrs": list(map(list, zip(*matrix)))[1],
    }
    writer.add_style_filter(style_filter)
    writer.add_col_separator_style_filter(col_separator_style_filter)

    writer.headers = ["id", "Date and time", "Subject"]
    writer.value_matrix = matrix
    writer.write_table()


@cmd.command(epilog=COMMAND_EPILOG)
@click.pass_context
def users(ctx):
    """
    List users.
    """

    verbosity_level = ctx.obj[Context.VERBOSITY_LEVEL]
    app_configs = ctx.obj[Context.CONFIGS]
    client = GaroonClient(
        subdomain=app_configs[ConfigKey.SUBDOMAIN], basic_auth=app_configs[ConfigKey.BASIC_AUTH]
    )
    matrix = []
    has_next = True
    offset = 0

    while has_next:
        try:
            users, has_next = client.fetch_users(offset=offset)
        except (HTTPError, TooManyRedirects) as e:
            logger.error(e)
            sys.exit(errno.EACCES)

        for user in users:
            matrix.append([user.id, user.name, user.code])

        offset += len(users)

    writer = ptw.TableWriterFactory().create_from_format_name("space_aligned")
    writer.headers = ["id", "name", "code"]
    writer.value_matrix = matrix
    writer.set_theme("altrow")
    writer.write_table()
