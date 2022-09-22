from locust import HttpUser, task


valid_email = "admin@irontemple.com"
club = "Simply Lift"
competition = "Spring Festival"
places_bought = 2


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

    @task(6)
    def purchasePlace(self):
        self.client.post('purchasePlaces',
                         data=dict(club=club,
                                   competition=competition,
                                   places=places_bought))