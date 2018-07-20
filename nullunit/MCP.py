import logging
import time
import random
import math

from cinp import client

PROCESSOR_API_VERSION = '0.1'

# TODO: move backoff delay and retries to cinp client
DELAY_MULTIPLIER = 15
# delay of 15 results in a delay of:
# min delay = 0, 10, 16, 20, 24, 26, 29, 31, 32, 34, 35, 37, 38, 39, 40 ....
# max delay = 0, 20, 32, 40, 48, 52, 58, 62, 64, 68, 70, 74, 76, 78, 80 .....


def _backOffDelay( count ):
  if count < 1:  # math.log dosen't do so well below 1
    count = 1

  if count > 20:  # really don't need to get any more delaied than this
    count = 20

  factor = int( DELAY_MULTIPLIER * math.log( count ) )
  delay = factor + ( random.random() * factor )
  logging.debug( 'MCP: sleeping for "{0}"'.format( delay ) )
  time.sleep( delay )


class MCP( object ):
  def __init__( self, host, proxy, instance_id, cookie ):
    self.cinp = client.CInP( host, '/api/v1/', proxy )
    self.instance_id = instance_id
    self.cookie = cookie

    count = 0
    while True:
      count += 1
      try:
        root = self.cinp.describe( '/api/v1/Processor' )
        break
      except ( client.Timeout, client.ResponseError ):
        _backOffDelay( count )
        logging.warn( 'MCP: getRequest: retry {0}'.format( count ) )

    if root[ 'api-version' ] != PROCESSOR_API_VERSION:
      raise Exception( 'Expected API version "{0}" found "{1}"'.format( PROCESSOR_API_VERSION, root[ 'api-version' ] ) )

  def signalJobRan( self ):
    logging.info( 'MCP: Signal Job Ran' )
    self.cinp.call( '/api/v1/Processor/Instance:{0}:(jobRan)'.format( self.instance_id ), { 'cookie': self.cookie } )

  def sendStatus( self, status ):
    logging.info( 'MCP: Status "{0}"'.format( status ) )
    self.cinp.call( '/api/v1/Processor/Instance:{0}:(setStatus)'.format( self.instance_id ), { 'cookie': self.cookie, 'status': status } )

  def setSuccess( self, success ):
    logging.info( 'MCP: Success "{0}"'.format( success ) )
    self.cinp.call( '/api/v1/Processor/Instance:{0}:(setSuccess)'.format( self.instance_id ), { 'cookie': self.cookie, 'success': success } )

  def setResults( self, results ):
    if results is not None:
      logging.info( 'MCP: Results "{0}"'.format( results[ -100: ].strip() ) )
    else:
      logging.info( 'MCP: Results <empty>' )

    self.cinp.call( '/api/v1/Processor/Instance:{0}:(setResults)'.format( self.instance_id ), { 'cookie': self.cookie, 'results': results } )

  def setScore( self, score ):
    if score is not None:
      logging.info( 'MCP: Score "{0}"'.format(* score ) )
    else:
      logging.info( 'MCP: Score <undefined>' )

    self.cinp.call( '/api/v1/Processor/Instance:{0}:(setScore)'.format( self.instance_id ), { 'cookie': self.cookie, 'score': score } )

  def uploadedPackages( self, package_files ):
    if not package_files:
      return

    self.cinp.call( '/api/v1/Processor/Instance:{0}:(addPackageFiles)'.format( self.instance_id ), { 'cookie': self.cookie, 'package_files': package_files } )

  def getConfigStatus( self, resource, index=None, count=None ):
    raise Exception( 'Not Updated' )

    logging.info( 'MCP: Config Status for "{0}" index: "{1}", count: "{2}"'.format( resource, index, count ) )
    args = { 'name': resource }
    if index is not None:
      args[ 'index' ] = index

    if count is not None:
      args[ 'count' ] = count

    return self.cinp.call( '/api/v1/Processor/BuildJob:{0}:(getConfigStatus)'.format( self.job_id ), args )

  def getProvisioningInfo( self, resource, index=None, count=None ):
    raise Exception( 'Not Updated' )

    logging.info( 'MCP: Provisioning Info for "{0}" index: "{1}", count: "{2}"'.format( resource, index, count ) )
    args = { 'name': resource }
    if index is not None:
      args[ 'index' ] = index

    if count is not None:
      args[ 'count' ] = count

    return self.cinp.call( '/api/v1/Processor/BuildJob:{0}:(getProvisioningInfo)'.format( self.job_id ), args )

  def setValue( self, value_map  ):
    logging.info( 'MCP: Setting Value "{0}"'.format( value_map ) )

    return self.cinp.call( '/api/v1/Processor/Instance:{0}:(setConfigValues)'.format( self.instance_id ), { 'cookie': self.cookie, 'value_map': value_map } )
