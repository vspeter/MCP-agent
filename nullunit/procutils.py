import subprocess
import os
import shlex
import logging
import re
import string
from datetime import datetime

debug_stdout = None

global_env = os.environ

# TODO: would be nice to cmd output to debug log, and write to debug_stdout as it goes,
#       unfontuntally that will require some pipes and magic, Popen expets a .fileno on the writer sent to it

printable = re.compile( '[^{0}]'.format( string.printable ) )


def open_output( filename ):
  global debug_stdout
  debug_stdout = open( filename, 'w' )


def close_output():
  global debug_stdout
  debug_stdout.close()
  debug_stdout = None


def _execute( cmd, dir, stdin, env ):
  logging.info( 'procutils: executing "{0}" in "{1}"'.format( cmd, dir ) )
  debug_stdout.write( '\n=================================================\n' )
  debug_stdout.write( '{0}\n'.format( datetime.utcnow() ) )
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
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT
         }

  try:
    if stdin:
      proc = subprocess.Popen( stdin=subprocess.PIPE, **args )
      ( stdout, _ ) = proc.communicate( stdin )

    else:
      proc = subprocess.Popen( **args )
      ( stdout, _ ) = proc.communicate()

  except Exception as e:
    raise Exception( 'Exception {0} while executing "{1}"'.format( e, cmd ) )

  debug_stdout.write( stdout )

  debug_stdout.write( '\n-------------------------------------------------\n' )
  debug_stdout.write( 'rc: {0}\n'.format( proc.returncode ) )
  debug_stdout.write( '{0}\n'.format( datetime.utcnow() ) )
  debug_stdout.flush()

  logging.info( 'procutils: returned "{0}"'.format( proc.returncode ) )

  return ( printable.sub( '', stdout )[ -100000: ], proc.returncode )


def execute( cmd, dir=None, stdin=None, env=global_env ):
  ( _, rc ) = _execute( cmd, dir, stdin, env )
  if rc != 0:
    raise Exception( 'Error Executing "{0}", rc: {1}'.format( cmd, rc ) )


def execute_lines_rc( cmd, dir=None, stdin=None, env=global_env ):
  ( results, rc ) = _execute( cmd, dir, stdin, env )
  return ( results.splitlines(), rc )


def execute_lines( cmd, dir=None, stdin=None, env=global_env ):
  ( results, rc ) = _execute( cmd, dir, stdin, env )
  if rc != 0:
    raise Exception( 'Error Executing "{0}", rc: {1}'.format( cmd, rc ) )

  return results.splitlines()
