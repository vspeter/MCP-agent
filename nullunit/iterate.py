import json
import os
import glob

from procutils import execute, execute_lines, NonZeroException


ITERATE_STATES = [ 'clone', 'checkout', 'dependancies', 'target', 'done' ]

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
  if state[ 'state' ] == 'clone':
    mcp.sendStatus( 'Cloning' )
    state[ 'dir' ] = doClone( state )
    state[ 'state' ] = 'checkout'

  elif state[ 'state' ] == 'checkout':
    mcp.sendStatus( 'Checkout' )
    doCheckout( state )
    state[ 'state' ] = 'dependancies'

  elif state[ 'state' ] == 'dependancies':
    mcp.sendStatus( 'Dependancies' )
    doDependancies( state )
    state[ 'state' ] = 'done'

  elif state[ 'state' ] == 'target':
    mcp.sendStatus( 'Target' )
    if doTarget( state, packrat, mcp ):
      state[ 'state' ] = 'done'
      mcp.setSuccess( True )
    else:
      state[ 'state' ] = 'failed'
      mcp.setSuccess( False )

  elif state[ 'state' ] == 'done':
    mcp.sendStatus( 'Done' )


def doClone( state ):
  os.makedirs( WRK_DIR )
  execute( '%s clone %s' % ( GIT_CMD, state[ 'url' ] ), WRK_DIR )
  return glob.glob( '%s/*' % WRK_DIR )[0]


def doCheckout( state ):
  execute( '%s checkout %s' % ( GIT_CMD, state[ 'branch' ] ), state[ 'dir' ] )


def doDependancies( state ):
  deps = execute_lines( '%s %s-deps' % ( MAKE_CMD, state[ 'depends' ] ), state[ 'dir' ] )
  for dep in deps.split():
    execute( '%s install -y %s' % ( APT_GET_CMD, dep ) )


def doTarget( state, packrat, mcp ):
  try:
    results = execute_lines( '%s %s' % ( MAKE_CMD, state[ 'target' ] ), state[ 'dir' ] )
  except NonZeroException:
    mcp.setResults( results )
    return False

  mcp.setResults( results )

  if state[ 'target' ] == 'dpkg':
    mcp.sendStatus( 'Package Build' )
    file_name = execute_lines( '%s dpkg-file', state[ 'dir' ] )[-1]
    packrat.addPackageFile( file_name )
    mcp.sendStatus( 'Package Uploaded' )

  return True
