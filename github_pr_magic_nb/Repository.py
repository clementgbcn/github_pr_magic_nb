class Repository:
    def __init__(self, org, name):
        self.org = org
        self.name = name
        self.last_pr_check = 1

    def get_url(self):
        return "{}/{}".format(self.org, self.name)
