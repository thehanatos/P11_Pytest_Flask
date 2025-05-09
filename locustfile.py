from locust import HttpUser, task, between


class FlaskAppUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.post("/showSummary", data={"email": "test@email.com"})

    @task
    def view_index(self):
        self.client.get("/")

    @task
    def book_competition(self):
        self.client.get("/book/Summer Festival/Test Club")

    @task
    def purchase_places(self):
        self.client.post("/purchasePlaces", data={
            "competition": "Summer Festival",
            "club": "Test Club",
            "places": 1
        })
