from locust import HttpUser, task


class ProjectPerfTest(HttpUser):

        @task(6)
        def clubsTable(self):
            response = self.client.get("/clubs")
