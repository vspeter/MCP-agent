import logging
from cinp import client

DISTRO_VERSION_CACHE = {}

class MCP( object ):
  def __init__( self, host, proxy, build, resource  ):
    self.cinp = client.CInP( host, '/api/v1', proxy )
    self.build = resource
    self.resource = resource

  def sendStatus( self, status ):
    logging.info( 'MCP: Status "%s"' % status )
    self.cinp.call( '/api/v1/Processor/BuildJob:%s:(setStatus)' % self.build, { 'resource': self.resource, 'status': status } )
