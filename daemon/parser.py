import argparse
import os
import sys

from jina import __resources_path__
from jina.parsers.base import set_base_parser
from jina.parsers.helper import add_arg_group, _SHOW_ALL_ARGS
from jina.parsers.peapods.base import mixin_base_ppr_parser
from jina.parsers.peapods.runtimes.remote import mixin_remote_parser
from .models.enums import PartialDaemonModes


def mixin_daemon_parser(parser):
    """
    # noqa: DAR101
    # noqa: DAR102
    # noqa: DAR103
    """
    gp = add_arg_group(parser, title='Daemon')
    gp.add_argument(
        '--no-fluentd',
        action='store_true',
        default=False,
        help='do not start fluentd, no log streaming',
    )
    gp.add_argument(
        '--store',
        action='store_true',
        default=True,
        help='''
    Load from local store (if any), while starting JinaD
    ''',
    )
    gp.add_argument(
        '--mode',
        type=str,
        choices=list(PartialDaemonModes),
        default=None,
        help='Mode for partial jinad. Can be flow/pod/pea. If none provided main jinad is run.'
        if _SHOW_ALL_ARGS
        else argparse.SUPPRESS,
    )


def get_main_parser():
    """
    Return main parser
    :return: main parser
    """

    parser = set_base_parser()

    mixin_remote_parser(parser)
    mixin_base_ppr_parser(parser)
    mixin_daemon_parser(parser)

    from jina import __resources_path__

    parser.set_defaults(
        port_expose=8000,
        workspace='/tmp/jinad',
        log_config=os.getenv(
            'JINAD_LOG_CONFIG',
            os.path.join(__resources_path__, 'logging.daemon.yml'),
        ),
    )

    return parser


def _get_run_args(print_args: bool = True):
    """Fetch run args for jinad

    :param print_args: True if we want to print args to console
    :return: jinad args
    """
    from jina.helper import colored
    from . import daemon_logger

    parser = get_main_parser()
    from argparse import _StoreAction, _StoreTrueAction

    args, argv = parser.parse_known_args()
    if print_args:

        default_args = {
            a.dest: a.default
            for a in parser._actions
            if isinstance(a, (_StoreAction, _StoreTrueAction))
        }

        with open(os.path.join(__resources_path__, 'jina.logo')) as fp:
            logo_str = fp.read()
        param_str = []
        for k, v in sorted(vars(args).items()):
            j = f'{k.replace("_", "-"): >30.30} = {str(v):30.30}'
            if default_args.get(k, None) == v:
                param_str.append('   ' + j)
            else:
                param_str.append('🔧️ ' + colored(j, 'blue', 'on_yellow'))
        param_str = '\n'.join(param_str)
        daemon_logger.info(f'\n{logo_str}\n▶️  {" ".join(sys.argv)}\n{param_str}\n')
    return args
