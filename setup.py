from distutils.core import setup
setup(
  name = 'stat_api',
  packages = ['stat_api'], # this must be the same as the name above
  version = '0.3.2',
  description = 'A wrapper for the getstat.com API',
  author = 'Austin Platt',
  author_email = 'austin.platt@distilled.net',
  url = 'https://github.com/DistilledLtd/get-stat-api',
  keywords = ['stat', 'getstat', 'api', 'keyword'],
  classifiers = [],
  install_requires=[
      'requests>=2.7'
  ]
)
