import time

import requests

from helpers import tidy_dates

ENDPOINTS_DATA = {
    # projects
    "/projects/list": (),
    "/projects/create": ("name"),
    "/projects/update": ("id", "name"),
    "/projects/delete": ("id"),
    # sites
    "/sites/all": ("results"),
    "/sites/list": ("project_id"),
    "/sites/ranking_distributions": ("id", "from_date", "to_date"),
    "/sites/create": ("project_id", "url", "drop_www_prefix", "drop_directories"),
    "/sites/update": ("id", "url", "title", "drop_www_prefix", "drop_directories"),
    "/sites/delete": ("id"),
    # tags
    "/tags/list": ("site_id", "results"),
    "/tags/ranking_distributions": ("id", "from_date", "to_date"),
    # keywords
    "/keywords/list": ("site_id", "results"),
    "/keywords/create": ("site_id", "market", "location", "device", "type",
                         "keyword", "tag", "tag_color"),
    "/keywords/delete": ("id"),
    # rankings
    "/rankings/list": ("keyword_id", "from_date", "to_date"),
    # serps
    "/serps/show": ("keyword_id", "engine", "date"),
    # bulk jobs
    "/bulk/list": ("results"),
    "/bulk/ranks": ("date", "site_id", "currently_tracked_only", "crawled_keywords_only"),
    "/bulk/status": ("id"),
    "/bulk/delete": ("id"),
    "/bulk/site_ranking_distributions": ("date"),
    "/bulk/tag_ranking_distributions": ("date"),
}


class StatInvalidEndpoint(Exception):
    pass


class StatRequestError(Exception):
    pass


class StatResponseError(Exception):
    pass


class InvalidParameters(Exception):
    pass


class StatTimeoutException(Exception):
    pass


class Stat(object):
    """ An object for getting/settings data in STAT using their API """

    def __init__(self, subdomain, api_key):

        self.base_url = self._make_base_url(subdomain)
        self.api_key = api_key

    def _make_base_url(self, subdomain):

        return "https://" + subdomain + ".getstat.com"

    def _make_api_request_url(self, endpoint):

        return self.base_url + "/api/v2/" + self.api_key + endpoint

    def _do_request(self, url, kwargs):
        """ Execute a request """

        r = requests.get(url, kwargs)

        status_code = r.status_code
        if status_code == 400:
            raise StatRequestError("Bad request")
        elif status_code == 401:
            raise StatRequestError("Unauthorized API key")
        elif status_code == 403:
            raise StatRequestError("Usage Limit Exceeded")
        elif status_code == 404:
            raise StatRequestError("Not Found")
        elif status_code == 500:
            raise StatRequestError("Internal Server Error")

        response_data = r.json()
        if 'Response' not in response_data:
            raise StatResponseError(response_data['Result'])

        return r.json()['Response']

    def request(self, endpoint, **kwargs):
        """ Make a request to the getstat.com API

        endpoint should correspond to an endpoint listed in the documentation
        kawrgs should be a dictionary of query parameters for the request
        """

        if endpoint not in ENDPOINTS_DATA.keys():
            raise StatInvalidEndpoint("The endpoint {endpoint} does not exist".format(endpoint))

        allowed_parameters = ENDPOINTS_DATA[endpoint]
        illegal_paramters = [key for key in kwargs.keys()
                             if key not in allowed_parameters]
        if illegal_paramters:
            raise InvalidParameters("The parameter(s) {parameters} are not legal"
                                    " for the endpoint `{endpoint}`".format(
                                        parameters=illegal_paramters,
                                        endpoint=endpoint))

        url = self._make_api_request_url(endpoint)
        kwargs.update({'format': 'json'})
        kwargs = tidy_dates(kwargs)

        return self._do_request(url, kwargs)

    def _make_report_stream_url(self, job_id):

        return self.base_url + "/bulk_reports/stream_report/" + str(job_id)

    def get_job_result(self, job_id):
        """ Get the JSON of a report associated with the given job_id"""

        url = self._make_report_stream_url(job_id)
        params = {"key": self.api_key}
        return self._do_request(url, params)

    def get_job_status(self, job_id):
        """ Return the status of a job """

        params = {"id": job_id}
        return self.request("/bulk/status", **params)['Result']['Status']

    def is_job_done(self, job_id):
        """ Has a job finished executing and the report is ready """

        return self.get_job_status(job_id) == 'Completed'


class StatBulkJob(object):
    """ Helper class to deal with running jobs on STAT """

    def __init__(self, subdomain, api_key):

        self.stat = Stat(subdomain, api_key)

    def create_job(self, endpoint, **kwargs):
        """ Make a job and return the Id associated with it """

        result = self.stat.request(endpoint, **kwargs)
        job_id = result['Result']['Id']
        return job_id

    def create_job_and_wait_for_result(self, endpoint, time_interval=5, max_retries=5, **kwargs):
        """ Make a job and wait for the result (by polling for the job status)

        Optionally, set the length of the period to wait between checking if
        the job is done.
        """

        job_id = self.create_job(endpoint, **kwargs)

        tries = 0
        while True:
            if tries == max_retries:
                raise StatTimeoutException
            time.sleep(time_interval)
            if self.stat.is_job_done(job_id):
                break
            tries += 1

        return self.stat.get_job_result(job_id)
