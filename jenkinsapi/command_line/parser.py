""" jenksapi.command_line.parser
"""
from argparse import ArgumentParser

def get_parser():
    """ build the default parser """
    parser = ArgumentParser()
    # parser.set_conflict_handler("resolve")
    parser.add_argument(
        "-v", '--version', default=False, dest='version',
        action='store_true',
        help=("show version information"))
    parser.add_argument(
        "--config", '-c',
        default='~/.jenkins_remote.json', dest='config',
        help=("specify configuration file for jenkins_remote (default is `~/.jenkins_remote.json`)"))
    instance_arg = [
        ("--instance", '-i'),
        dict(default='default', dest='instance',
             help=("specify jenkins instance (default is `jenkins`)"))]
    job_arg = [
        ("--job", '-j'),
        dict(default='', dest='job', required=True,
             help=("specify jenkins job"))]
    subparsers = parser.add_subparsers(help='commands')
    help_parser = subparsers.add_parser('help', help='show help info')
    help_parser.set_defaults(subcommand='help')
    version_parser = subparsers.add_parser(
        'version', help='show goulash version')
    version_parser.set_defaults(subcommand='version')

    tail_parser = subparsers.add_parser('tail', help='tail jenkins build process')
    tail_parser.set_defaults(subcommand='tail')
    tail_parser.add_argument(*instance_arg[0], **instance_arg[1])
    tail_parser.add_argument(*job_arg[0], **job_arg[1])

    list_parser = subparsers.add_parser('ls', help='list jenkins jobs')
    list_parser.set_defaults(subcommand='ls')
    list_parser.add_argument(*instance_arg[0], **instance_arg[1])

    return parser
