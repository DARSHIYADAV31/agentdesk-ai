TICKET = {"title": "VPN is down", "body": "Cannot connect to the VPN since morning",
          "requester_email": "bob@example.com"}


class FakeRunner:
    def __init__(self):
        self.processed, self.approved = [], []

    def process(self, ticket_id):
        self.processed.append(ticket_id)

    def execute_approval(self, approval_id, ticket_id):
        self.approved.append(approval_id)


def login(client, user):
    return client.post("/auth/login", json={"username": user, "password": f"pw-{user}"}).json()


def auth(client, user="ann"):
    return {"Authorization": f"Bearer {login(client, user)['access_token']}"}
