from distutils.core import setup
setup(
  name = 'stat_api',
  packages = ['stat_api'], # this must be the same as the name above
  version = '0.3.1',
  description = 'A wrapper for the getstat.com API',
  author = 'Austin Platt',
  author_email = 'austin.platt@distilled.net',
  url = 'https://github.com/DistilledLtd/get-stat-api', # use the URL to the github repo
  download_url = 'https://github.com/DistilledLtd/get-stat-api/tarball/0.3.1', # I'll explain this in a second
  keywords = ['stat', 'getstat', 'api', 'keyword'], # arbitrary keywords
  classifiers = [],
  install_requires=[
      'requests'
  ]
)
