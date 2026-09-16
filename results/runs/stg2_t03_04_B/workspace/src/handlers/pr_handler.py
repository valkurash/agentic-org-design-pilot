import json
from src.repo import repository

class PRHandler:
    def __init__(self, repo_layer):
        self.repo_layer = repo_layer

    def process_pr(self, pr_data):
        # Simulated processing of PR
        # Using repository layer for any persistent state changes
        self.repo_layer.save_pr(pr_data)
        return {'status': 'processed', 'pr_id': pr_data['pr_id']}

# Instantiate the handler with the repository layer
repo_layer = repository.RepositoryLayer()
pr_handler = PRHandler(repo_layer)

# Load the PR data
with open('data/prs/pr_seed_001.json') as pr_file:
    pr_data = json.load(pr_file)

# Process the PR
result = pr_handler.process_pr(pr_data)
print(f"Processing result: {result['status']} for PR ID: {result['pr_id']}")
