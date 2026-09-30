DOMAIN = "demo.example"

# (title, body, category, priority, status, resolution, cost, kb source or None, owner)
TICKETS = [
    ("VPN connection timed out", "VPN client says connection timed out from home.",
     "network", "high", "resolved", "Reinstalled VPN profile per vpn-troubleshooting.md", 0.0009, "vpn-troubleshooting.md", "darshi"),
    ("Printer offline on floor 2", "The floor 2 printer shows offline for everyone.",
     "hardware", "medium", "resolved", "Cleared queue, restarted spooler per printer-issues.md", 0.0007, "printer-issues.md", "demo_user"),
    ("Outlook keeps asking for password", "Outlook prompts for my password every few minutes.",
     "software", "medium", "resolved", "Cleared cached credentials (see resolved-1042-outlook.md)", 0.0008, "resolved-1042-outlook.md", "darshi"),
    ("Need access to finance share", "Please grant me read access to the finance folder.",
     "access", "medium", "escalated", "No knowledge-base solution: needs manager approval", 0.0006, None, "demo_user"),
    ("Refund for unused cloud seats", "We were billed for 10 seats we never used.",
     "billing", "low", "escalated", "Billing questions go to finance", 0.0005, None, "darshi"),
    ("Server room badge not working", "My badge fails at the server room door.",
     "access", "critical", "needs_human", None, 0.0, None, "demo_user"),
    ("Reset password for bob.smith", "Bob is locked out and the self-service link never arrives.",
     "account", "high", "pending_approval", None, 0.0011, "password-reset.md", "darshi"),
    ("Laptop screen flickering", "Screen flickers and goes black after the last update.",
     "hardware", "medium", "new", None, 0.0, None, "demo_user"),
]
