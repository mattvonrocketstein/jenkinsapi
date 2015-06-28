"""jenkinsapi.command_line.remote
"""
import os
import demjson
import requests

from voluptuous import Invalid, Undefined
from voluptuous import Schema, Required, Optional

from jenkinsapi.jenkins import Jenkins, Requester
from jenkinsapi.command_line.parser import get_parser
from jenkinsapi import __version__ as version

DEFAULT_CONFIG = '~/.jenkins_remote.json'
CONFIG_HELP_URL = 'http://placeholder'

class Handler(object):
    def __init__(self, args):
        self.args = args

    def __call__(self, jenkins):
        self.jenkins = jenkins
        try:
            handler = getattr(self, 'handle_'+self.args.subcommand)
        except AttributeError:
            raise SystemExit('unknown subcommand: '+self.args.subcommand)
        else:
            return handler()

    def handle_list(self):
        print 'handling list'

    def handle_tail(self):
        print 'handling tail'

def handler(args, jenkins):
    # By now the jenkins instance to use has been established
    if args.subcommand=='tail':
        handle_tail(args)

def validate_config(config):
    entry = Schema({
        Required('base_url'): unicode,
        Required('user'): unicode,
        Required('password'): unicode,
        Required('ssl_verify', default=True): bool,
        })
    schema = Schema({
        unicode: entry,
        })
    schema(config)


    # Voluptous supports defaults but seems to do nothing with them.
    defaults = {}
    for k, v in entry.schema.items():
        if not isinstance(k.default, Undefined):
            defaults[str(k)] = k.default
    for nickname, instance_data in config.items():
        for k,v in defaults.items():
            if k not in config[nickname]:
                config[nickname][k] = v

def load_config(args):
    # FIXME: not usable in windows?
    config_file = args.config or DEFAULT_CONFIG
    config_file = os.path.expanduser(config_file)
    if not os.path.exists(config_file):
        err = ('Configuration file at "{0}" does not exist.'
               '  See {1} for information about the file format').format(
            args.config, CONFIG_HELP_URL)
        raise SystemExit(err)
    with open(config_file,'r') as fhandle:
        config = demjson.decode(fhandle.read())
    try:
        validate_config(config)
    except Invalid, e:
        err = 'Bad data in jenkins_remote config.\n  File: "{0}"\n  Error: {1}'
        raise SystemExit(err.format(config_file, str(e)))
    else:
        return [config, config_file]

def get_jenkins(args):
    config, config_file = load_config(args)
    instance_conf = config[args.instance]
    username = instance_conf['user'] or None
    password = instance_conf['password'] or None
    base_url = instance_conf['base_url']
    if not instance_conf['ssl_verify']:
        requester_kargs = dict(
            username=username,
            password=password,
            ssl_verify=False, baseurl=base_url)
        requester = Requester(**requester_kargs)
    else:
        requester = None
    kargs = dict(
        username=username,
        password=password,
        requester=requester,
        lazy=True)
    try:
        j = Jenkins(base_url, **kargs)
    except requests.exceptions.SSLError,e:
        err = ('ERROR: Caught SSLError.  You may want to '
               'reinstance_confure the jenkins instance "{0}" in '
               'file "{1}" with "ssl_verify" set to false.\n  '
               'Original Exception: {2}')
        err = err.format(args.instance, config_file, str(e))
        raise SystemExit(err)
    return j

def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.subcommand in ['version', 'help']:
        if args.subcommand == 'version':
            print version
        if args.subcommand == 'help':
            parser.print_help()
        raise SystemExit()
    else:
        jenkins = get_jenkins(args)
        handler = Handler(args)
        handler(jenkins)
