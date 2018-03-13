import logging
from importlib import import_module
import kateborg

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('Kateborg@main')

plugins = ('axe', 'points', 'nicknames')

for plugin in plugins:
    logger.info('loading plugins.{}...'.format(plugin))
    import_module('plugins.{}'.format(plugin))

kateborg.client.idle()