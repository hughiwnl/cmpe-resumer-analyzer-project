"""Skill/keyword dictionary used for resume-to-job matching.

This list is intentionally simple (a flat list of strings) so it can be
expanded easily. Add new skills as plain strings — matching in
analyzer.py is case-insensitive and uses word boundaries, so multi-word
skills like "Machine Learning" work the same as single-word ones.
"""

SKILLS = [
    # Programming languages
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C#",
    "Go",
    "Ruby",
    "PHP",
    "Swift",
    "Kotlin",
    "R",
    "Scala",
    "MATLAB",

    # Web / frameworks
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Django",
    "Flask",
    "Spring",
    "HTML",
    "CSS",

    # Data / databases
    "SQL",
    "NoSQL",
    "MongoDB",
    "PostgreSQL",
    "MySQL",
    "Data Analysis",
    "Data Science",
    "Machine Learning",
    "Deep Learning",
    "Pandas",
    "NumPy",
    "TensorFlow",
    "PyTorch",

    # Cloud / DevOps
    "AWS",
    "Azure",
    "GCP",
    "Docker",
    "Kubernetes",
    "CI/CD",
    "Jenkins",
    "Terraform",
    "Linux",

    # Tools
    "Git",
    "GitHub",
    "Jira",
    "REST API",
    "GraphQL",

    # Methodology / soft & process skills
    "Agile",
    "Scrum",
    "Project Management",
    "Leadership",
    "Communication",
    "Problem Solving",
    "Team Collaboration",
]
