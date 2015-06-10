from cinp import client

DISTRO_VERSION_CACHE = {}

class Packrat( object ):
  def __init__( self, host, proxy, name, psk ):
    self.cinp = client.CInP( host, '/api/v1', proxy )
    self.cinp.setAuth( name, psk )

  def addPackageFile( self, url, timeout=30 ):
    pass
