import subprocess
import os
import shlex
import logging
from datetime import datetime

debug_stdout = None

global_env = os.environ


def open_output( filename ):
  global debug_stdout
  debug_stdout = open( filename, 'w' )


def _execute( cmd, dir, stdout, stdin, env ):
  logging.info( 'procutils: executing "%s" in "%s"' % ( cmd, dir ) )
  debug_stdout.write( '\n=================================================\n' )
  debug_stdout.write( '%s\n' % datetime.utcnow() )
  debug_stdout.write( 'Executing:\n' )
  debug_stdout.write( cmd )

  if stdin:
    debug_stdout.write( '\nstdin:\n' )
    debug_stdout.write( stdin )

  debug_stdout.write( '\n-------------------------------------------------\n' )
  debug_stdout.flush()

  args = {
            'args': shlex.split( cmd ),
            'cwd': dir,
            'env': env,
            'stdout': ( stdout if stdout is not None else debug_stdout ),
            'stderr': subprocess.STDOUT
         }

  try:
    if stdin:
      proc = subprocess.Popen( stdin=subprocess.PIPE, **args )
      ( results, _ ) = proc.communicate( stdin )

    else:
      proc = subprocess.Popen( **args )
      ( results, _ ) = proc.communicate()

  except Exception as e:
    raise Exception( 'Exception %s while executing "%s"' % ( e, cmd ) )

  debug_stdout.write( '\n-------------------------------------------------\n' )
  debug_stdout.write( 'rc: %s\n' % proc.returncode )
  debug_stdout.write( '%s\n' % datetime.utcnow() )
  debug_stdout.flush()

  logging.info( 'procutils: returned "%s"' % proc.returncode )

  return ( results, proc.returncode )


def execute( cmd, dir=None, stdin=None, env=global_env, ok_rc=None ):
  ( _, rc ) = _execute( cmd, dir, None, stdin, env )
  if rc not in ( ok_rc if ok_rc is not None else [ 0 ] ):
    raise Exception( 'Error Executing "%s", rc: %s' % ( cmd, rc ) )


def execute_lines( cmd, dir=None, stdin=None, env=global_env, ok_rc=None ):
  ( results, rc ) = _execute( cmd, dir, subprocess.PIPE, stdin, env )
  if rc not in ( ok_rc if ok_rc is not None else [ 0 ] ):
    raise Exception( 'Error Executing "%s", rc: %s' % ( cmd, rc ) )
  return results.splitlines()
