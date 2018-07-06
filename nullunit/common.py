import configparser
import logging

from nullunit.MCP import MCP
from nullunit.Packrat import Packrat

CONFIG_FILE = '/etc/mcp/nullunit.conf'


def getConfig():
  config = configparser.ConfigParser()

  try:
    config.read( CONFIG_FILE )
  except configparser.Error as e:
    logging.error( 'Error reading config file: {0}'.format( e ) )
    return None

  return config


def getMCP( config ):
  try:
    return MCP( config.get( 'mcp', 'host' ), config.get( 'mcp', 'proxy' ), config.getint( 'mcp', 'instance_id' ), config.get( 'mcp', 'instance_cookie' ) )
  except configparser.Error:
    logging.error( 'Error retreiving MCP host, proxy, instance_id, and/or instance_cookie from config file.' )
    return None


def getPackrat( config ):
  try:
    return Packrat( config.get( 'packrat', 'host' ), config.get( 'packrat', 'proxy' ), config.get( 'packrat', 'name' ), config.get( 'packrat', 'psk' ) )
  except configparser.Error:
    logging.error( 'Error retreiving Packrat host, and/or proxy from config file' )
    return None
