from datetime import date

def tidy_dates(params):
    """ Convert any date objects to a date string """

    date_keys = ("from_date", "to_date", "date")
    for date_key in date_keys:
        if date_key in params:
            if isinstance(params[date_key], date):
                date_obj = params[date_key]
                params[date_key] = date_obj.strftime("%Y-%m-%d")

    return params
