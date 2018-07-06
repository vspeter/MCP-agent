import logging

from cinp import client


class MCP( object ):
  def __init__( self, host, proxy, instance_id, cookie ):
    self.cinp = client.CInP( host, '/api/v1/', proxy )
    self.instance_id = instance_id
    self.cookie = cookie

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
