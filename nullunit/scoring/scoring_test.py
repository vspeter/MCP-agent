# import pytest

from nullunit.scoring import extractScore
from nullunit.scoring.golang import extract_scores as golang_extract
from nullunit.scoring.pytest import extract_scores as pytest_extract

golang_pattern_list = []
golang_score_list = []
pytest_pattern_list = []
pytest_score_list = []

EXTRACTOR_MAP = {
                  'golang': golang_extract,
                  'pytest': pytest_extract
                }

PATTERN_MAP = {
                 'golang': golang_pattern_list,
                 'pytest': pytest_pattern_list
}

SCORE_MAP = {
                 'golang': golang_score_list,
                 'pytest': pytest_score_list
}


def test_overall():
  for tool in EXTRACTOR_MAP.keys():
    for i in range( 0, len( PATTERN_MAP[ tool ] ) ):
      assert extractScore( PATTERN_MAP[ tool ][ i ].splitlines() ) == SCORE_MAP[ tool ][ i ]


def _test_tool( tool ):
  excractor = EXTRACTOR_MAP[ tool ]
  for i in range( 0, len( PATTERN_MAP[ tool ] ) ):
    assert excractor( PATTERN_MAP[ tool ][ i ].splitlines() ) == SCORE_MAP[ tool ][ i ]

  print( list( set( EXTRACTOR_MAP.keys() ) - set( [ tool ] ) ) )
  for other in list( set( EXTRACTOR_MAP.keys() ) - set( [ tool ] ) ):
    for i in range( 0, len( PATTERN_MAP[ other ] ) ):
      assert excractor( PATTERN_MAP[ other ][ i ].splitlines() ) is None


def test_extractor():
  for tool in EXTRACTOR_MAP.keys():
    _test_tool( tool )


golang_pattern_list.append( '''go test -cover . ./dispatch
ok  	mlx-poller	(cached)	coverage: 0.0% of statements [no tests to run]
ok  	mlx-poller/dispatch	0.004s	coverage: 0.0% of statements''' )
golang_score_list.append( 0.0 )

golang_pattern_list.append( '''go test -cover . ./dispatch
ok  	mlx-poller	(cached)	coverage: 0.0% of statements [no tests to run]
ok  	mlx-poller/dispatch	0.004s	coverage: 0.4% of statements''' )
golang_score_list.append( 0.2 )

pytest_pattern_list.append( '''Name                    Stmts   Miss  Cover
----------------------------------------------
project/__init__.py           0      0   100%
project/contractor.py        30     30     0%
project/daemon.py           178    178     0%
project/dhcpd.py             98     98     0%
project/dynamic_pool.py      85     85     0%
project/handler.py           84     84     0%
project/static_pool.py       34     34     0%
----------------------------------------------
TOTAL                       509    509     0%''' )
pytest_score_list.append( 0.0 )


pytest_pattern_list.append( '''=========== test session starts ===========
platform linux -- Python 3.6.5, pytest-3.3.2, py-1.5.2, pluggy-0.6.0
rootdir: /home/peter/Projects/mcp/nullunit, inifile:
plugins: cov-2.5.1
collected 3 items

nullunit/iterate_test.py .                   [ 33%]
nullunit/scoring/scoring_test.py ..          [100%]

========= 3 passed in 0.04 seconds ==========''' )
pytest_score_list.append( None )


pytest_pattern_list.append( '''=========== test session starts ===========
platform linux -- Python 3.6.5, pytest-3.3.2, py-1.5.2, pluggy-0.6.0
rootdir: /home/peter/Projects/mcp/nullunit, inifile:
plugins: cov-2.5.1
collected 3 items

nullunit/iterate_test.py .                   [ 33%]
nullunit/scoring/scoring_test.py ..          [100%]

----------- coverage: platform linux, python 3.6.5-final-0 -----------
Coverage HTML written to dir htmlcov


========= 3 passed in 0.19 seconds ==========''' )
pytest_score_list.append( None )

pytest_pattern_list.append( '''=========== test session starts ===========
platform linux -- Python 3.6.5, pytest-3.3.2, py-1.5.2, pluggy-0.6.0
rootdir: /home/peter/Projects/mcp/nullunit, inifile:
plugins: cov-2.5.1
collected 3 items

nullunit/iterate_test.py .                   [ 33%]
nullunit/scoring/scoring_test.py ..          [100%]

----------- coverage: platform linux, python 3.6.5-final-0 -----------
Name                               Stmts   Miss  Cover
------------------------------------------------------
nullunit/MCP.py                       51     38    25%
nullunit/Packrat.py                   42     27    36%
nullunit/__init__.py                   0      0   100%
nullunit/common.py                    25     17    32%
nullunit/confluence.py                 2      1    50%
nullunit/iterate.py                  261    224    14%
nullunit/iterate_test.py               9      0   100%
nullunit/procutils.py                 62     42    32%
nullunit/scoring/__init__.py           9      0   100%
nullunit/scoring/golang.py            11      0   100%
nullunit/scoring/pytest.py             8      0   100%
nullunit/scoring/scoring_test.py      36      0   100%
------------------------------------------------------
TOTAL                                516    349    32%
Coverage HTML written to dir htmlcov


========= 3 passed in 0.21 seconds ==========''' )
pytest_score_list.append( 32.0 )
