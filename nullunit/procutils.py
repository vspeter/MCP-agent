import subprocess
import os
import shlex
from datetime import datetime

debug_stdout = None

global_env = os.environ

def NonZeroException( Exception ):
  pass


def open_output( filename ):
  global debug_stdout
  debug_stdout = open( filename, 'w' )


def _execute( cmd, dir, stdout, stderr, stdin, env ):
  debug_stdout.write( '\n=================================================\n' )
  debug_stdout.write( '%s\n' % datetime.utcnow() )
  debug_stdout.write( 'Executing:\n' )
  debug_stdout.write( cmd )
  if stdin:
    debug_stdout.write( '\nstdin:\n' )
    debug_stdout.write( stdin )
  debug_stdout.write( '\n-------------------------------------------------\n' )
  try:
    if stdin:
      proc = subprocess.Popen( shlex.split( cmd ), cwd=dir, env=env, stdout=stdout, stderr=stderr, stdin=subprocess.PIPE )
      ( output, _ ) = proc.communicate( stdin )
    else:
      proc = subprocess.Popen( shlex.split( cmd ), cwd=dir, env=env, stdout=stdout, stderr=stderr )
      ( output, _ ) = proc.communicate()
  except Exception as e:
    raise Exception( 'Exception %s while executing "%s"' % ( e, cmd ) )

  debug_stdout.write( '\n-------------------------------------------------\n' )
  debug_stdout.write( 'rc: %s\n' % proc.returncode )
  debug_stdout.write( '%s\n' % datetime.utcnow() )

  if proc.returncode != 0:
    raise NonZeroException( 'Error Executing "%s"' % cmd )

  return output


def execute( cmd, dir=None, stdin=None ):
  _execute( cmd, dir, debug_stdout, debug_stdout, stdin, global_env )


def execute_lines( cmd, dir=None, stdin=None ):
  stdout = _execute( cmd, dir, subprocess.PIPE, debug_stdout, stdin, global_env )
  return stdout.splitlines()
