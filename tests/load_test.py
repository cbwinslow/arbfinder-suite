"""
Load testing with Locust
"""

from locust import HttpUser, between, task


class ArbFinderUser(HttpUser):
    """Simulated user for load testing"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    @task(3)
    def get_listings(self):
        """Get listings - most common operation"""
        self.client.get("/api/listings?limit=20")

    @task(2)
    def search_listings(self):
        """Search listings"""
        self.client.get("/api/listings/search?q=nvidia")

    @task(1)
    def get_statistics(self):
        """Get statistics"""
        self.client.get("/api/statistics")

    @task(1)
    def get_comps(self):
        """Get comparable prices"""
        self.client.get("/api/comps")

    def on_start(self):
        """Called when a user starts"""
        # Could include login or setup here
        pass
