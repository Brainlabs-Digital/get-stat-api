import time

import requests

ENDPOINTS_DATA = {
    # projects
    "/projects/list": (),
    "/projects/create": (),
    "/projects/update": (),
    "/projects/delete": (),
    # sites
    "/sites/all": (),
    "/sites/list": (),
    "/sites/ranking_distributions": (),
    "/sites/create": (),
    "/sites/update": (),
    "/sites/delete": (),
    # tags
    "/tags/list": (),
    "/tags/ranking_distributions": (),
    # keywords
    "/keywords/list": (),
    "/keywords/create": (),
    "/keywords/delete": (),
    # rankings
    "/rankings/list": (),
    # serps
    "/serps/show": (),
    # bulk jobs
    "/bulk/list": (),
    "/bulk/ranks": (),
    "/bulk/status": (),
    "/bulk/delete": (),
    "/bulk/site_ranking_distributions": (),
    "/bulk/tag_ranking_distributions": (),
}

class StatInvalidEndpoint(Exception):
    pass

class StatRequestError(Exception):
    pass

class Stat(object):

    def __init__(self, subdomain, api_key):

        self.base_url =  self._make_base_url(subdomain)
        self.api_key = api_key

    def _make_base_url(self, subdomain):

        return "http://" + subdomain + ".getstat.com"

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

        return r.json()['Response']

    def request(self, endpoint, **kwargs):
        """ Make a request to the getstat.com API

        endpoint should correspond to an endpoint listed in the documentation
        kawrgs should be a dictionary of query parameters for the request
        """

        if not endpoint in ENDPOINTS_DATA.keys():
            raise InvalidEndpoint("The endpoint {endpoint} does not exist".format(endpoint))

        url = self._make_api_request_url(endpoint)
        kwargs.update({'format': 'json'})

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

    def create_job_and_wait_for_result(self, endpoint, time_interval=5, **kwargs):
        """ Make a job and wait for the result (by polling for the job status)

        Optionally, set the length of the period to wait between checking if
        the job is done.
        """

        job_id = self.create_job(endpoint, **kwargs)

        while True:
            time.sleep(time_interval)
            if self.stat.is_job_done(job_id):
                break

        return self.stat.get_job_result(job_id)
