import configparser

cfg_parser = configparser.ConfigParser()
cfg_parser.read(r'assets/settings.rkz')

token = cfg_parser['metrika']['token']
