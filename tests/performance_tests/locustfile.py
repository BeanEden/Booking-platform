from locust import HttpUser, task


valid_email = "admin@irontemple.com"



class ProjectPerfTest(HttpUser):

    @task(6)
    def index(self):
        self.client.get("/")

    @task(6)
    def showSummary(self):
        self.client.post('showSummary', data={'email': [valid_email]})

    @task(6)
    def logout(self):
        self.client.get("logout")


