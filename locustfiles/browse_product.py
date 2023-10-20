from locust import HttpUser, task

class WebsiteUser(HttpUser):
    def view_products(self):
        self.client.get('/store/products/')
