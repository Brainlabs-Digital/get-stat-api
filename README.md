STAT API
=========

A simple wrapper around the getstat.com API.

# Usage example

```python
from stat_api import Stat
subdomain = 'try'
api_key = 'yourapikey'
stat = Stat(subdomain, api_key)
project_id = 999
data = stat.request("/sites/list", project_id=project_id)
```

`data` should now be a Python object of the returned sites as per the [documentation](https://help.getstat.com/knowledgebase/requests-and-responses/#sites-list).
