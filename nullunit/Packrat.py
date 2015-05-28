from cinp import client

DISTRO_VERSION_CACHE = {}

class Packrat( object ):
  def __init__( self, host, proxy ):
    self.cinp = client.CInP( host, '/api/v1', proxy )

  def addPackageFile( self, url, timeout=30 ):
    pass
