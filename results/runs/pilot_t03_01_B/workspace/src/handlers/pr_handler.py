import json
import os
from datetime import datetime

class PRHandler:
    def __init__(self, repo, audit_path='data/audit/audit_log.json'):
        self.repo = repo
        self.audit_path = audit_path
        self.load_prs()

    def load_prs(self, prs_path='data/prs/pr_seed_001.json'):
        with open(prs_path, 'r') as prs_file:
            self.prs = json.load(prs_file)

    def save_prs(self, prs_path='data/prs/pr_seed_001.json'):
        with open(prs_path, 'w') as prs_file:
            json.dump(self.prs, prs_file, indent=2)

    def load_finding(self, finding_path='data/reviews/finding_arch_bypass.json'):
        with open(finding_path, 'r') as finding_file:
            self.finding = json.load(finding_file)

    def save_finding(self, finding_path='data/reviews/finding_arch_bypass.json'):
        with open(finding_path, 'w') as finding_file:
            json.dump(self.finding, finding_file, indent=2)

    def transition_pr_status(self, pr_id, new_status):
        current_status = self.prs['status']
        if new_status in self.valid_transitions(current_status):
            self.audit_transition(pr_id, current_status, new_status)
            self.prs['status'] = new_status
            self.save_prs()
        else:
            raise ValueError(f'Invalid transition from {current_status} to {new_status}')

    def valid_transitions(self, status):
        transitions = {
            'draft': ['open'],
            'open': ['in_review', 'closed'],
            'in_review': ['approved', 'changes_requested', 'closed'],
            'changes_requested': ['in_review', 'closed'],
            'approved': ['merged', 'closed']
        }
        return transitions.get(status, [])

    def audit_transition(self, pr_id, from_status, to_status):
        log_entry = {
            'pr_id': pr_id,
            'from_status': from_status,
            'to_status': to_status,
            'actor_role': 'system',
            'ts': datetime.now().isoformat()
        }
        if not os.path.exists(self.audit_path):
            audit_log = []
        else:
            with open(self.audit_path, 'r') as audit_file:
                audit_log = json.load(audit_file)

        audit_log.append(log_entry)

        with open(self.audit_path, 'w') as audit_file:
            json.dump(audit_log, audit_file, indent=2)

    def process_finding(self):
        self.load_finding()
        if self.finding['status'] == 'open':
            self.finding['status'] = 'addressed'
            self.finding['evidence_path'] = 'src/handlers/pr_handler.py'
            self.save_finding()

    def run(self):
        # Example process
        self.process_finding()
        self.transition_pr_status('pr_seed_001', 'in_review')
        self.transition_pr_status('pr_seed_001', 'approved')
        self.transition_pr_status('pr_seed_001', 'merged')

# Assuming repo layer implementation
class Repo:
    def write_changes(self):
        pass

# Execute the handler
repo = Repo()
pr_handler = PRHandler(repo)
pr_handler.run()
