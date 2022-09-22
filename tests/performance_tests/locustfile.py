from locust import HttpUser, task

club = "Simply Lift"
competition = "Spring Festival"
places_bought = 2



class ProjectPerfTest(HttpUser):

    @task(6)
    def index(self):
        self.client.get("/")

    @task(6)
    def purchasePlace(self):
        response = self.client.post('/purchasePlaces', data=dict(club=club, competition=competition, places=places_bought))