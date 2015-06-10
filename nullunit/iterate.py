import json

from procutils import execute, execute_lines


ITERATE_STATES = [ 'clone', 'checkout', 'target', 'done' ]

GIT_CMD = '/usr/bin/git'
MAKE_CMD = '/usr/bin/make'

def readState( file, uri, branch ):
  try:
    state = json.loads( open( file, 'r' ).read() )
  except:
    state = {
              'state': ITERATE_STATES[0],
              'uri': uri,
              'branch': branch
           }

  return state


def writeState( file, state ):
  open( file, 'w' ).write( json.dumps( state ) )


def doStep( state, mcp, packrat ):
  if state[ 'state' ] == 'clone':
    mcp.sendStatus( 'Cloning' )
    doClone( state )
    state[ 'state' ] = 'checkout'
    return False

  elif state[ 'state' ] == 'checkout':
    mcp.sendStatus( 'Checkout' )
    doCheckout( state )
    state[ 'state' ] = 'target'
    return False

  elif state[ 'state' ] == 'target':
    mcp.sendStatus( 'Target' )
    doTarget( state, packrat )
    state[ 'state' ] = 'done'
    return False

  elif state[ 'state' ] == 'done':
    mcp.sendStatus( 'Ran' )
    return True


def doClone( state ):
  execute( '%s clone %s' % ( GIT_CMD, state[ 'uri' ] ) )


def doCheckout( state ):
  execute( '%s checkout %s' % ( GIT_CMD, state[ 'branch' ] ) )


def doTarget( state, packrat ):
  execute( '%s %s' % ( MAKE_CMD, state[ 'target' ] ) )

  if state[ 'target' ] == 'dpkg':
    file_name = execute_lines( '%s dpkg-file' )[-1]
    packrat.addPackageFile( file_name )
