import time

import requests

STAT_BASE_URL = 'http://app4.getstat.com/'

ENDPOINTS_DATA = {
    "/projects/list": (),
    "/projects/create": (),
    "/projects/update": (),
    "/projects/delete": (),
    "/sites/list": (),
    "/bulk/list": (),
    "/bulk/status": (),
    "/bulk/site_ranking_distributions": ()
}

class StatInvalidEndpoint(Exception):
    pass

class StatRequestError(Exception):
    pass

class Stat(object):

    def __init__(self, api_key):

        self.base_url =  'http://app4.getstat.com/'
        self.api_key = api_key

    def make_api_request_url(self, endpoint):

        return self.base_url + "api/v2/" + self.api_key + endpoint

    def do_request(self, url, kwargs):

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

        if not endpoint in ENDPOINTS_DATA.keys():
            raise InvalidEndpoint("The endpoint {endpoint} does not exist".format(endpoint))

        url = self.make_api_request_url(endpoint)
        kwargs.update({'format': 'json'})

        return self.do_request(url, kwargs)

    def make_report_stream_url(self, job_id):

        return self.base_url + "/bulk_reports/stream_report/" + str(job_id)

    def get_job_result(self, job_id):

        url = self.make_report_stream_url(job_id)
        params = {"key": self.api_key}
        return self.do_request(url, params)

    def get_job_status(self, job_id):

        params = {"id": job_id}
        return self.request("/bulk/status", **params)['Result']['Status']

    def is_job_done(self, job_id):

        return self.get_job_status(job_id) == 'Completed'


class StatBulkJob(object):

    def __init__(self, api_key):

        self.stat = Stat(api_key)

    def create_job(self, endpoint, **kwargs):

        result = self.stat.request(endpoint, **kwargs)
        job_id = result['Result']['Id']
        return job_id

    def create_job_and_wait_for_result(self, endpoint, **kwargs):

        job_id = self.create_job(endpoint, **kwargs)
        while True:
            time.sleep(5)
            if self.stat.is_job_done(job_id):
                break

        return self.stat.get_job_result(job_id)
