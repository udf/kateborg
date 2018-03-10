import logging
from importlib import import_module
import kateborg

logging.basicConfig(level=logging.DEBUG)

plugins = ('axe',)

for plugin in plugins:
    import_module('plugins.{}'.format(plugin))

kateborg.client.idle()