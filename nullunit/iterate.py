import json
import os
import glob
import shutil
import logging
import socket
import re
from datetime import datetime
from nullunit.common import getPackrat

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
  if re.search( '^make(\[[0-9]+\])?: \*\*\* No rule to make .* Stop\.$', results[0] ):
    return True

  if re.search( '^make(\[[0-9]+\])?: Nothing to be done for .*\.$', results[0] ):
    return True

  return False


def _isPackageBuild( state ):
  return state[ 'target' ] in ( 'dpkg', 'rpm', 'respkg', 'resource' )


def readState( file ):
  try:
    state = json.loads( open( file, 'r' ).read() )
  except:
    return None

  return state


def writeState( file, state ):
  open( file, 'w' ).write( json.dumps( state ) )


def doStep( state, mcp, config ):
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
    if doRequires( state, mcp, config ):
      state[ 'state' ] = 'target'

    else:
      state[ 'state' ] = 'failed'
      mcp.setSuccess( False )

  elif start_state == 'target':
    if doTarget( state, mcp, config ):
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

  for ( root, dirname_list, filename_list ) in os.walk( state[ 'dir' ] ):  # go through and `touch` everything.
    for filename in filename_list:
      try:                                                                   # clock skew is a fact of life, we are building everything anyway
        os.utime( os.path.join( root, filename ), None )                     # this helps make not complain about the future
      except OSError:
        pass


def doRequires( state, mcp, config ):
  logging.info( 'iterate: getting requires "%s"' % state[ 'requires' ] )
  args = []

  if not _isPackageBuild( state ):
    args.append( 'RESOURCE_NAME="%s"' % config.get( 'mcp', 'resource_name' ) )
    args.append( 'RESOURCE_INDEX=%s' % config.get( 'mcp', 'resource_index' ) )

  env = os.environ
  env[ 'DEBIAN_PRIORITY' ] = 'critical'
  env[ 'DEBIAN_FRONTEND' ] = 'noninteractive'
  ( results, rc ) = execute_lines_rc( '%s -s %s %s' % ( MAKE_CMD, state[ 'requires' ], ' '.join( args ) ), state[ 'dir' ], env=env )

  if rc != 0:
    if rc == 2 and _makeDidNothing( results ):
      return True

    else:
      logging.info( 'iterate: error getting requires' )
      mcp.setResults( 'Error getting requires:\n' + '\n'.join( results ) )
      return False

  for required in results:
    if required.startswith( 'make:' ): # make was unhappy about something, skip that line.... if it was important it will come out later
      continue

    required = required.strip()
    if not required:
      continue

    logging.info( 'iterate: installing "%s"' % required )
    execute( PKG_INSTAL % required )

  return True

def doTarget( state, mcp, config ):
  args = []
  if _isPackageBuild( state ):
    packrat = getPackrat( config )
    if not packrat:
      raise Exception( 'iterate: Error Connecting to packrat' )

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

  else:
    args.append( 'RESOURCE_NAME="%s"' % config.get( 'mcp', 'resource_name' ) )
    args.append( 'RESOURCE_INDEX=%s' % config.get( 'mcp', 'resource_index' ) )

  logging.info( 'iterate: executing target "%s"' % state[ 'target' ] )
  ( target_results, rc ) = execute_lines_rc( '%s %s %s' % ( MAKE_CMD, state[ 'target' ], ' '.join( args ) ), state[ 'dir' ] )

  if rc != 0:
    if rc == 2 and _makeDidNothing( target_results ):
      mcp.setResults( 'Nothing Built' )
      return True

    else:
      mcp.setResults( ( 'Error with target %s\n' % state[ 'target' ] ) + '\n'.join( target_results ) )
      return False

  mcp.setResults( '\n'.join( target_results ) )

  if _isPackageBuild( state ):
    logging.info( 'iterate: getting package file "%s"' % state[ 'requires' ] )
    mcp.sendStatus( 'Package Build' )
    ( results, rc ) = execute_lines_rc( '%s -s %s-file' % ( MAKE_CMD, state[ 'target' ] ), state[ 'dir' ] )
    if rc != 0 or len( results ) == 0:
      mcp.setResults( ( 'Error getting %s-file\n' % state[ 'target' ] ) + '\n'.join( results ) )
      return False

    for file_name in results:
      try:
        ( file_name, version ) = file_name.split( ':' )
      except ValueError:
        version = None

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
        result = packrat.addPackageFile( src, 'Package File "%s"' % os.path.basename( file_name ), 'MCP Auto Build from %s.  Build on %s at %s' % ( state[ 'url' ], socket.getfqdn(), datetime.utcnow() ), version )

      except Exception as e:
        logging.exception( 'iterate: Exception "%s" while adding package file "%s"' % ( e, file_name ) )
        mcp.setResults( 'Exception adding package file' )
        src.close()
        return False

      src.close()

      if isinstance( result, list ):
        raise Exception( 'Packrat was unable to detect distro, options are "%s"' % result )

      target_results.append( '=== File "%s" uploaded.' % os.path.basename( file_name ) )

      if not result:
        mcp.sendStatus( 'Packge(s) NOT (all) Uploaded' )
        return False

      if not packrat.checkFileName( os.path.basename( file_name ) ):
        raise Exception( 'Recently added file "%s" not showing in packrat.' % os.path.basename( file_name ) )

    packrat.logout()

    mcp.sendStatus( 'Package(s) Uploaded' )

    mcp.setResults( '\n'.join( target_results ) )

  return True
