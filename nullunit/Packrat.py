import os
import logging
import time
from threading import Thread

from cinp import client

PACKRAT_API_VERSION = '1.5'


class KeepAlive( Thread ):
  def __init__( self, cinp, *args, **kwargs ):
    super( KeepAlive, self ).__init__( *args, **kwargs )
    self.daemon = True
    self.cinp = cinp

  def run( self ):
    while self.cinp:
      self.cinp.call( '/api/v1/User/Session(keepalive)' )
      time.sleep( 60 )


class Packrat( object ):
  def __init__( self, host, proxy, name, psk ):
    self.name = name
    self.cinp = client.CInP( host, '/api/v1/', proxy )

    root = self.cinp.describe( '/api/v1/Repo' )
    if root[ 'api-version' ] != PACKRAT_API_VERSION:
      raise Exception( 'Expected API version "{0}" found "{1}"'.format( PACKRAT_API_VERSION, root[ 'api-version' ] ) )

    # self.token = self.cinp.call( '/api/v1/User/Session(login)', { 'username': self.name, 'password': psk } )
    # self.cinp.setAuth( name, self.token )
    # self.keepalive = KeepAlive( self.cinp )
    # self.keepalive.start()

  def logout( self ):
    # self.keepalive.cinp = None
    # self.cinp.call( '/api/v1/Auth(logout)', { 'token': self.token } )
    pass

  def _callback( self, pos, size ):
    logging.debug( 'Packrat: Uploading at {0} of {1}'.format( pos, size ) )

  def addPackageFile( self, file, justification, provenance, distroversion=None ):
    logging.info( 'Packrat: Adding Packge File "{0}"'.format( file.name ) )
    file_uri = self.cinp.uploadFile( '/api/upload', file, os.path.basename( file.name ), self._callback )
    distroversion_list = self.cinp.call( '/api/v1/Repo/PackageFile(distroversion_options)', { 'file': file_uri } )  # it can sometimes take a while for packrat to commit large files
    if distroversion is not None:
      if distroversion not in distroversion_list:
        raise Exception( 'distroversion "{0}" not in aviable distroverison list "{1}"'.formaT( distroversion, distroversion_list ) )
    else:
      if len( distroversion_list ) != 1:
        raise Exception( 'Unable to auto-detect distroversion, options: "{0}"'.format( distroversion_list ) )
      else:
        distroversion = distroversion_list[0]

    logging.info( 'Packrat: Adding file "{0}", justification: "{1}", provenance: "{2}", distroversion: "{3}"'.format( file_uri, justification, provenance, distroversion ) )
    result = self.cinp.call( '/api/v1/Repo/PackageFile(create)', { 'file': file_uri, 'justification': justification, 'provenance': provenance, 'distroversion': distroversion }, timeout=300 )  # it can sometimes take a while for packrat to commit large files
    return result

  def checkFileName( self, file_name ):
    result = self.cinp.call( '/api/v1/Repo/PackageFile(filenameInUse)', { 'file_name': file_name } )
    return result
