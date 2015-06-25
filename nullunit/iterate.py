import json
import os
import glob
import shutil
import logging

from procutils import execute, execute_lines, NonZeroException


GIT_CMD = '/usr/bin/git'
MAKE_CMD = '/usr/bin/make'
WRK_DIR = '/nullunit'
APT_GET_CMD = '/usr/bin/apt-get'

def readState( file ):
  try:
    state = json.loads( open( file, 'r' ).read() )
  except:
    return None

  return state


def writeState( file, state ):
  open( file, 'w' ).write( json.dumps( state ) )


def doStep( state, mcp, packrat ):
  start_state = state[ 'state' ]
  mcp.sendStatus( 'Executing Stage "%s"' % start_state )
  logging.info( 'nullunit: Executing Stage "%s"' % start_state )

  if start_state == 'clone':
    state[ 'dir' ] = doClone( state )
    state[ 'state' ] = 'checkout'

  elif start_state == 'checkout':
    doCheckout( state )
    state[ 'state' ] = 'requires'

  elif start_state == 'requires':
    doRequires( state )
    state[ 'state' ] = 'target'

  elif start_state == 'target':
    if doTarget( state, packrat, mcp ):
      state[ 'state' ] = 'done'
      mcp.setSuccess( True )
    else:
      state[ 'state' ] = 'failed'
      mcp.setSuccess( False )

  mcp.sendStatus( 'Stage "%s" Complete' % start_state )
  logging.info( 'nullunit: Stage "%s" Complete' % start_state )


def doClone( state ):
  try:
    os.makedirs( WRK_DIR )
  except OSError as e:
    if e.errno == 17: # allready exists
      shutil.rmtree( WRK_DIR )
      os.makedirs( WRK_DIR )

    else:
      raise e

  execute( '%s clone %s' % ( GIT_CMD, state[ 'url' ] ), WRK_DIR )
  return glob.glob( '%s/*' % WRK_DIR )[0]


def doCheckout( state ):
  execute( '%s checkout %s' % ( GIT_CMD, state[ 'branch' ] ), state[ 'dir' ] )


def doRequires( state ):
  env = os.environ
  env['DEBIAN_PRIORITY'] = 'critical'
  env['DEBIAN_FRONTEND'] = 'noninteractive'

  reqired_list = execute_lines( '%s %s' % ( MAKE_CMD, state[ 'requires' ] ), state[ 'dir' ], env=env )
  for reqired in reqired_list:
    logging.info( 'interate: installing "%s"' % reqired )
    execute( '%s install -y %s' % ( APT_GET_CMD, reqired ) )


def doTarget( state, packrat, mcp ):
  results = []
  try:
    results = execute_lines( '%s %s' % ( MAKE_CMD, state[ 'target' ] ), state[ 'dir' ] )
  except NonZeroException:
    mcp.setResults( '\n'.join( results ) )
    return False

  mcp.setResults( '\n'.join( results ) )

  if state[ 'target' ] == 'dpkg':
    mcp.sendStatus( 'Package Build' )
    file_name = execute_lines( '%s dpkg-file', state[ 'dir' ] )[-1]
    packrat.addPackageFile( file_name )
    mcp.sendStatus( 'Package Uploaded' )

  return True
