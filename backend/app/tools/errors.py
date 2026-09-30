class ApprovalRequired(Exception):
    def __init__(self, approval_id: int):
        super().__init__(f"Human approval required (request {approval_id})")
        self.approval_id = approval_id


class ToolExecutionError(Exception):
    """A tool call failed; details are in the audit trail."""
