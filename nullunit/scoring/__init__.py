from nullunit.scoring.golang import extract_scores as golang_extract
from nullunit.scoring.pytest import extract_scores as pytest_extract

EXTRACTOR_LIST = [ golang_extract, pytest_extract ]


def extractScore( line_list ):
  for extractor in EXTRACTOR_LIST:
    result = extractor( line_list )
    if result is not None:
      return result

  return None
