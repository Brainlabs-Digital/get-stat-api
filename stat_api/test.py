from stat import Stat

stat = Stat(API_KEY)
data = stat.request("/projects/list")
