import json
import os
import glob
import shutil
import logging
import socket
import re
from datetime import datetime

from procutils import execute, execute_lines_rc

GIT_CMD = '/usr/bin/git'
MAKE_CMD = '/usr/bin/make'
WORK_DIR = '/nullunit'

if os.path.exists( '/usr/bin/apt-get' ):
  PKG_INSTAL = '/usr/bin/apt-get install -y %s'

elif os.path.exists( '/usr/bin/yum' ):
  PKG_INSTAL = '/usr/bin/yum install -y %s'

else:
  raise Exception( 'can\'t detect package manager' )

def _makeDidNothing( results ):
  if len( results ) != 1:
    return False

  # make sure something like "make: *** No rule to make target `XXXX', needed by `XXXX'.  Stop." still fails
  if re.search( '^make: \*\*\* No rule to make .* Stop\.$', results[0] ):
    return True

  if re.search( '^make: Nothing to be done for .*\.$', results[0] ):
    return True

  return False


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
  logging.info( 'iterate: Executing Stage "%s"' % start_state )

  if start_state == 'clone':
    state[ 'dir' ] = doClone( state )
    state[ 'state' ] = 'checkout'

  elif start_state == 'checkout':
    doCheckout( state )
    state[ 'state' ] = 'requires'

  elif start_state == 'requires':
    if doRequires( state, mcp ):
      state[ 'state' ] = 'target'

    else:
      state[ 'state' ] = 'failed'
      mcp.setSuccess( False )

  elif start_state == 'target':
    if doTarget( state, packrat, mcp ):
      state[ 'state' ] = 'done'
      mcp.setSuccess( True )

    else:
      state[ 'state' ] = 'failed'
      mcp.setSuccess( False )

  mcp.sendStatus( 'Stage "%s" Complete' % start_state )
  logging.info( 'iterate: Stage "%s" Complete' % start_state )


def doClone( state ):
  try:
    os.makedirs( WORK_DIR )

  except OSError as e:
    if e.errno == 17: # allready exists
      shutil.rmtree( WORK_DIR )
      os.makedirs( WORK_DIR )

    else:
      raise e

  logging.info( 'iterate: cloning "%s"' % state[ 'url' ] )
  execute( '%s clone %s' % ( GIT_CMD, state[ 'url' ] ), WORK_DIR )
  return glob.glob( '%s/*' % WORK_DIR )[0]


def doCheckout( state ):
  logging.info( 'iterate: checking out "%s"' % state[ 'branch' ] )
  execute( '%s checkout %s' % ( GIT_CMD, state[ 'branch' ] ), state[ 'dir' ] )


def doRequires( state, mcp ):
  logging.info( 'iterate: getting requires "%s"' % state[ 'requires' ] )
  env = os.environ
  env[ 'DEBIAN_PRIORITY' ] = 'critical'
  env[ 'DEBIAN_FRONTEND' ] = 'noninteractive'
  ( results, rc ) = execute_lines_rc( '%s -s %s' % ( MAKE_CMD, state[ 'requires' ] ), state[ 'dir' ], env=env )

  if rc != 0:
    if rc == 2 and _makeDidNothing( results ):
      return True

    else:
      logging.info( 'iterate: error getting requires' )
      mcp.setResults( 'Error getting requires:\n' + '\n'.join( results ) )
      return False

  for required in results:
    required = required.strip()
    if not required:
      continue

    logging.info( 'iterate: installing "%s"' % required )
    execute( PKG_INSTAL % required )

  return True

def doTarget( state, packrat, mcp ):
  if state[ 'target' ] in ( 'dpkg', 'rpm', 'resource' ):
    logging.info( 'iterate: executing target clean' )
    ( results, rc ) = execute_lines_rc( '%s clean' % MAKE_CMD, state[ 'dir' ] )

    if rc != 0:
      if rc == 2 and not _makeDidNothing( results ):
        mcp.setResults( 'Error with clean\n' + '\n'.join( results ) )
        return False

    ( results, rc ) = execute_lines_rc( '%s %s-setup' % ( MAKE_CMD, state[ 'target' ] ), state[ 'dir' ] )

    if rc != 0:
      if rc == 2 and not _makeDidNothing( results ):
        mcp.setResults( ( 'Error with %s-setup\n' % state[ 'target' ] ) + '\n'.join( results ) )
        return False

  logging.info( 'iterate: executing target "%s"' % state[ 'target' ] )
  ( target_results, rc ) = execute_lines_rc( '%s %s' % ( MAKE_CMD, state[ 'target' ] ), state[ 'dir' ] )

  if rc != 0:
    if rc == 2 and _makeDidNothing( target_results ):
      mcp.setResults( 'Nothing Built' )
      return True

    else:
      mcp.setResults( ( 'Error with target %s\n' % state[ 'target' ] ) + '\n'.join( target_results ) )
      return False

  mcp.setResults( '\n'.join( target_results ) )

  if state[ 'target' ] in ( 'dpkg', 'rpm', 'resource' ):
    logging.info( 'iterate: getting package file "%s"' % state[ 'requires' ] )
    mcp.sendStatus( 'Package Build' )
    ( results, rc ) = execute_lines_rc( '%s -s %s-file' % ( MAKE_CMD, state[ 'target' ] ), state[ 'dir' ] )
    if rc != 0 or len( results ) == 0:
      mcp.setResults( ( 'Error getting %s-file\n' % state[ 'target' ] ) + '\n'.join( results ) )
      return False

    for file_name in results:
      if file_name[0] != '/': #it's not an aboslute path, prefix is with the working dir
        file_name = os.path.realpath( os.path.join( state[ 'dir' ], file_name ) )

      if packrat.checkFileName( os.path.basename( file_name ) ):
        mcp.setResults( 'Filename "%s" is allready in use in packrat, skipping the file in upload.' % os.path.basename( file_name ) )
        logging.warning( 'Filename ""%s" allready on packrat, skipping...' % os.path.basename( file_name ) )
        target_results.append( '=== File "%s" skipped.' % os.path.basename( file_name ) )
        continue

      logging.info( 'iterate: uploading "%s"' % file_name )
      src = open( file_name, 'r' )
      try:
        result = packrat.addPackageFile( src, 'Package File "%s"' % os.path.basename( file_name ), 'MCP Auto Build from %s.  Build on %s at %s' % ( state[ 'url' ], socket.getfqdn(), datetime.utcnow() ) )

      except Exception as e:
        logging.exception( 'iterate: Exception "%s" while adding package file "%s"' % ( e, file_name ) )
        mcp.setResults( 'Exception adding package file' )
        src.close()
        return False

      src.close()

      target_results.append( '=== File "%s" uploaded.' % os.path.basename( file_name ) )

      if not result:
        mcp.sendStatus( 'Packge(s) NOT (all) Uploaded' )
        return False

      if not packrat.checkFileName( os.path.basename( file_name ) ):
        raise Exception( 'Recently added file "%s" not showing in packrat.' % os.path.basename( file_name ) )

    mcp.sendStatus( 'Package(s) Uploaded' )

    mcp.setResults( '\n'.join( target_results ) )

  return True
