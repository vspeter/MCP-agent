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
    logging.info( 'Packrat: Uploading at %s of %s' % ( pos, size ) )

  def addPackageFile( self, file, justification, provenance ):
    logging.info( 'Packrat: Adding Packge File "%s"' % file.name )
    file_uri = self.cinp.uploadFile( '/api/FILES', file, self._callback )[ 'uri' ]
    logging.info( 'Packrat: Adding file "%s", justification: "%s", provenance: "%s"' % ( file_uri, justification, provenance ) )
    result = self.cinp.call( '/api/v1/Repos/PackageFile(create)', { 'file': file_uri, 'justification': justification, 'provenance': provenance } )
    return result[ 'value' ]
