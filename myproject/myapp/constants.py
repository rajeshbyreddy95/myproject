# constants.py


NATURE_CHOICES = (
    ('electronic', 'Electronic'),
    ('physical', 'Physical'),
)


# Unified list of designations (job titles)
DESIGNATIONS = [
    ("ministry_welfare", "Ministry of Welfare"),
    ("district_collector", "District Collector"),
    ("joint_collector", "Joint Collector"),
    ("revenue_dept_officer", "Revenue Department Officer"),
    ("project_officer", "Project Officer"),
    ("mro", "MRO (Mandal Revenue Officer)"),
    ("surveyor", "Surveyor"),
    ("revenue_inspector", "Revenue Inspector"),
    ("vro", "VRO (Village Revenue Officer)"),
    ("superintendent", "Superintendent"),
    ("clerk", "Clerk"),
]

# If your workflow roles should be the same as designations:
ROLE_CHOICES = DESIGNATIONS

# If you need a hierarchy for workflow (and it's the same as the ordering in DESIGNATIONS or a subset), define it:
# For example, if the review chain starts at 'clerk' and goes up to 'ministry_welfare', you can define:
WORKFLOW_ROLES = [
    "clerk",
    "superintendent",
    "project_officer",  # adjust according to your actual workflow
    "mro",
    "surveyor",
    "revenue_inspector",
    "vro",
    "revenue_dept_officer",
    "joint_collector",
    "district_collector",
    "ministry_welfare",
]

ROLE_HIERARCHY = {
    role: WORKFLOW_ROLES[i+1] for i, role in enumerate(WORKFLOW_ROLES[:-1])
}

# And if your status choices follow a similar review pattern:
STATUS_CHOICES = (
    ('submitted', 'Submitted'),
    *[(f'{role}_review', f'Under {dict(DESIGNATIONS).get(role, role).title()} Review') for role in WORKFLOW_ROLES],
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
)

if __name__ == '__main__':
    print("NATURE_CHOICES:")
    print(NATURE_CHOICES)
    print("\nDESIGNATION_CHOICES:")
    print(DESIGNATIONS)
    print("\nWORKFLOW_ROLES:")
    print(WORKFLOW_ROLES)
    print("\nROLE_CHOICES:")
    print(ROLE_CHOICES)
    print("\nROLE_HIERARCHY:")
    print(ROLE_HIERARCHY)
    print("\nSTATUS_CHOICES:")
    print(STATUS_CHOICES)