import logging
from cinp import client

DISTRO_VERSION_CACHE = {}

class Packrat( object ):
  def __init__( self, host, proxy, name, psk ):
    self.name = name
    self.cinp = client.CInP( host, '/api/v1', proxy )
    self.token = self.cinp.call( '/api/v1/Auth(login)', { 'username': self.name, 'password': psk } )[ 'value' ]
    self.cinp.setAuth( name, self.token )

  def logout( self ):
    self.cinp.call( '/api/v1/Auth(logout)', { 'username': self.name, 'token': self.token } )

  def _callback( self, pos, size ):
    logging.debug( 'Packrat: Uploading at %s of %s' % ( pos, size ) )

  def addPackageFile( self, file, justification, provenance, version=None ):
    logging.info( 'Packrat: Adding Packge File "%s"' % file.name )
    file_uri = self.cinp.uploadFile( '/api/FILES', file, self._callback )[ 'uri' ]
    logging.info( 'Packrat: Adding file "%s", justification: "%s", provenance: "%s", distro: "%s"' % ( file_uri, justification, provenance, version ) )
    result = self.cinp.call( '/api/v1/Repos/PackageFile(create)', { 'file': file_uri, 'justification': justification, 'provenance': provenance, 'version': version }, timeout=120 ) # it can sometimes take a while for packrat to commit large files
    return result[ 'value' ]

  def checkFileName( self, file_name ):
    result = self.cinp.call( '/api/v1/Repos/PackageFile(filenameInUse)', { 'file_name': file_name } )
    return result[ 'value' ]
