import httpx
from config.settings import settings

class GrafanaClient:
    def __init__(self):
        self.base_url = settings.GRAFANA_BASE_URL
        self.api_key = settings.GRAFANA_API_KEY
        
        if not self.base_url or not self.api_key:
            raise ValueError("GRAFANA_BASE_URL and GRAFANA_API_KEY must be set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def get_contact_points(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/contact-points", headers=self.headers)
            response.raise_for_status()
            return response.json()
