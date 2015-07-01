import json
import os
import glob
import shutil
import logging
import socket
from datetime import datetime

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

  required_list = execute_lines( '%s %s' % ( MAKE_CMD, state[ 'requires' ] ), state[ 'dir' ], env=env )
  if required_list[0].startswith( 'make: Nothing to be done' ):
    return

  for required in required_list:
    required = required.strip()
    if not required:
      continue
    logging.info( 'interate: installing "%s"' % required )
    execute( '%s install -y %s' % ( APT_GET_CMD, required ) )


def doTarget( state, packrat, mcp ):
  results = []
  try:
    results = execute_lines( '%s %s' % ( MAKE_CMD, state[ 'target' ] ), state[ 'dir' ] )
  except NonZeroException:
    mcp.setResults( '\n'.join( results ) )
    return False

  if results[0].startswith( 'make: Nothing to be done' ):
    mcp.setResults( '' )
    return True

  mcp.setResults( '\n'.join( results ) )

  if state[ 'target' ] in ( 'dpkg', 'rpm', 'resource' ):
    mcp.sendStatus( 'Package Build' )
    file_name = os.path.join( state[ 'dir' ], execute_lines( '%s %s-file' % ( MAKE_CMD, state[ 'target' ] ), state[ 'dir' ] )[-1] )
    file = open( file_name, 'r' )
    try:
      result = packrat.addPackageFile( file, 'Package File "%s"' % os.path.basename( file_name ), 'MCP Auto Build from %s.  Build on %s at %s' % ( state[ 'url' ], socket.getfqdn(), datetime.utcnow() ) )
    except Exception as e:
      logging.exception( 'iterate: Exception "%s" while adding package file "%s"' % ( e, file_name ) )
      mcp.setResults( 'Exception adding package file' )
      file.close()
      return False

    file.close()
    if not result:
      mcp.sendStatus( 'Packge NOT Uploaded' )
      return False

    mcp.sendStatus( 'Package Uploaded' )

  return True
