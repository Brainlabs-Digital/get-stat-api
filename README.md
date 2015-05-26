STAT API
=========

A simple wrapper around the getstat.com API.

# Usage example

```python
from stat_api import Stat
subdomain = 'try'
api_key = 'yourapikey'
stat = Stat(subdomain, api_key)
data = stat.request("/sites/list", project_id=999)
```

`data` should now be a Python object of the returned sites as per the [documentation](https://help.getstat.com/knowledgebase/requests-and-responses/#sites-list).

## Bulk job helper

```python
from stat_api import StatBulk
subdomain = 'try'
api_key = 'yourapikey'
stat_bulk = StatBulk(subdomain, api_key)
data = stat_bulk.create_job_and_wait_for_result("/bulk/ranks", date="2015-05-24")
```

This will create a bulk job, then poll STAT until the job is done and finally return the result.
