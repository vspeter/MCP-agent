import re

TEST_MATCH = re.compile( 'TOTAL.* ([0-9\.]+)%' )


def extract_scores( line_list ):
  for line in line_list:
    match = TEST_MATCH.match( line )
    if match:
      return float( match.group( 1 ) )

  return None
