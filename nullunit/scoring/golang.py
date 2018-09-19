import re

TEST_MATCH = re.compile( 'coverage: ([0-9\.]+)% of statements' )


def extract_scores( line_list ):
  score_list = []

  for line in line_list:
    match = TEST_MATCH.search( line )
    if match:
      score_list.append( float( match.group( 1 ) ) )

  if len( score_list ) == 0:
    return None

  return sum( score_list ) / len( score_list )
