import logging
from cinp import client

DISTRO_VERSION_CACHE = {}

class MCP( object ):
  def __init__( self, host, proxy, job_id, name, index  ):
    self.cinp = client.CInP( host, '/api/v1', proxy )
    self.job_id = job_id
    self.name = name
    self.index = index

  def sendStatus( self, status ):
    logging.info( 'MCP: Status "%s"' % status )
    self.cinp.call( '/api/v1/Processor/BuildJob:%s:(updateResourceState)' % self.job_id, { 'name': self.name, 'index': self.index, 'status': status } )

  def setSuccess( self, success ):
    logging.info( 'MCP: Success "%s"' % success )
    self.cinp.call( '/api/v1/Processor/BuildJob:%s:(setResourceSuccess)' % self.job_id, { 'name': self.name, 'index': self.index, 'success': success } )

  def setResults( self, results ):
    logging.info( 'MCP: Results "%s"' % results[ :100 ].strip() )
    self.cinp.call( '/api/v1/Processor/BuildJob:%s:(setResourceResults)' % self.job_id, { 'name': self.name, 'index': self.index, 'results': results } )
