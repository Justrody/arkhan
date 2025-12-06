import argparse
import random
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

from faker import Faker
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import (
    User,
    UserRole,
    Paper,
    Vote,
)
from app.services.auth import get_password_hash

fake = Faker()

DEFAULT_ADMIN = {
    "username": "admin",
    "email": "admin@mail.tld",
    "password": "P@ssw0rd",
}

TECH_TAGS = [
    "web",
    "devops",
    "cryptography",
    "networking",
    "linux",
    "cloud",
    "malware",
    "pentesting",
    "architecture",
]

PAPER_TEMPLATES = [
    "Introduction to {topic}",
    "Advanced {topic} Techniques",
    "{topic} Best Practices",
    "Understanding {topic} in Depth",
    "A Practical Guide to {topic}",
    "{topic}: From Zero to Hero",
    "Mastering {topic}",
    "{topic} Security Considerations",
    "Building Secure {topic} Applications",
    "The Complete {topic} Handbook",
    "{topic} Performance Optimization",
    "Common {topic} Mistakes and How to Avoid Them",
    "Real-world {topic} Case Studies",
]

TOPICS = [
    "Python Async Programming",
    "Web Application Security",
    "REST API Design",
    "SQL Injection Prevention",
    "Docker Container Security",
    "Kubernetes Networking",
    "Buffer Overflow Exploits",
    "Memory Safe Programming",
    "OAuth 2.0 Implementation",
    "JWT Authentication",
    "Rate Limiting Strategies",
    "XSS Prevention",
    "CSRF Protection",
    "Secure File Upload",
    "Password Hashing",
    "Cryptographic Primitives",
    "Reverse Engineering Binaries",
    "Malware Analysis",
    "Network Protocol Analysis",
    "Linux Kernel Security",
    "GraphQL Security",
    "Microservices Architecture",
    "Event-Driven Systems",
    "Distributed Systems",
    "Database Optimization",
]


def slugify(text: str) -> str:
    text = text.lower().strip()

    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)

    return text


def generate_markdown_content() -> str:
    sections = random.randint(3, 6)
    content_parts = []

    content_parts.append(
        f"## Introduction\n\n{fake.paragraph(nb_sentences=5)}\n"
    )

    section_titles = [
        "Background",
        "Prerequisites",
        "Implementation",
        "Architecture",
        "Security Considerations",
        "Best Practices",
        "Performance",
        "Testing",
        "Deployment",
        "Monitoring",
        "Common Issues",
    ]

    for i in range(sections):
        title = random.choice(section_titles)
        section_titles.remove(title)

        content_parts.append(f"## {title}\n\n")
        content_parts.append(f"{fake.paragraph(nb_sentences=4)}\n\n")

        if random.random() > 0.5:
            lang = random.choice(["python", "bash"])
            content_parts.append(f"```{lang}\n")
            if lang == "python":
                content_parts.append(f"def {fake.word()}_{fake.word()}():\n")
                content_parts.append(f"    # {fake.sentence()}\n")
                content_parts.append(f"    result = {fake.word()}\n")
                content_parts.append("    return result\n")
            elif lang == "bash":
                content_parts.append("#!/bin/bash\n")
                content_parts.append("# {fake.sentence()}\n")
                content_parts.append("echo \"hello world\"\n")
            content_parts.append("```\n\n")

        if random.random() > 0.6:
            content_parts.append("Key points:\n\n")
            for _ in range(random.randint(3, 5)):
                content_parts.append(f"- {fake.sentence()}\n")
            content_parts.append("\n")

        content_parts.append(f"{fake.paragraph(nb_sentences=3)}\n\n")

    content_parts.append(
        f"## Conclusion\n\n{fake.paragraph(nb_sentences=4)}\n"
    )

    return "".join(content_parts)


def create_admin(db: Session) -> User:
    admin = db.query(User).filter(
        User.username == DEFAULT_ADMIN["username"]
    ).first()

    if admin:
        print("admin user already exists")
        return admin

    admin = User(
        username=DEFAULT_ADMIN["username"],
        email=DEFAULT_ADMIN["email"],
        password=get_password_hash(DEFAULT_ADMIN["password"]),
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    print("created admin user")
    return admin


def create_users(db: Session, count: int = 10) -> list[User]:
    users = []

    existing_emails = {u.email for u in db.query(User).all()}
    existing_usernames = {u.username for u in db.query(User).all()}

    roles = [UserRole.USER] * 7

    created = 0
    attempts = 0

    max_attempts = count * 3

    while created < count and attempts < max_attempts:
        attempts += 1

        email = fake.email()
        username = fake.user_name()[:50]

        if username in existing_usernames or email in existing_emails:
            continue

        existing_usernames.add(username)
        existing_emails.add(email)

        days_ago = random.randint(1, 365)
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)

        user = User(
            username=username,
            email=email,
            password=get_password_hash("P@ssw0rd"),
            role=random.choice(roles),
            is_active=True,
            created_at=created_at,
            updated_at=created_at + timedelta(
                days=random.randint(0, days_ago)
            ),
        )

        users.append(user)
        created += 1

    db.add_all(users)
    db.commit()

    print(f"created {len(users)} users")
    return users


def create_papers(
    db: Session, count: int = 20, authors: list[User] = None
) -> list[Paper]:
    if not authors:
        authors = db.query(User).all()

    if not authors:
        print("no users found. create users first")
        return []

    papers = []
    existing_slugs = {p.slug for p in db.query(Paper).all()}

    created = 0
    attempts = 0
    max_attempts = count * 3

    while created < count and attempts < max_attempts:
        attempts += 1

        topic = random.choice(TOPICS)
        template = random.choice(PAPER_TEMPLATES)
        title = template.format(topic=topic)
        slug = slugify(title)

        base_slug = slug
        counter = 1
        while slug in existing_slugs:
            slug = f"{base_slug}-{counter}"
            counter += 1

        existing_slugs.add(slug)

        author = random.choice(authors)
        days_ago = random.randint(1, 180)
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)

        tags = random.sample(TECH_TAGS, random.randint(2, 5))

        paper = Paper(
            title=title,
            slug=slug,
            content=generate_markdown_content(),
            tags=",".join(tags),
            author_id=author.id,
            is_published=random.random() > 0.1,
            vote_count=random.randint(0, 100),
            created_at=created_at,
            updated_at=created_at + timedelta(
                days=random.randint(0, days_ago)
            ),
            published_at=created_at if random.random() > 0.1 else None,
        )

        papers.append(paper)
        created += 1

    db.add_all(papers)
    db.commit()

    for author in authors:
        author.papers_count = db.query(Paper).filter(
            Paper.author_id == author.id
        ).count()
    db.commit()

    print(f"created {len(papers)} papers")
    return papers


def create_votes(
    db: Session, users: list[User] = None, papers: list[Paper] = None
) -> list[Vote]:
    if not users:
        users = db.query(User).all()
    if not papers:
        papers = db.query(Paper).all()

    if not users or not papers:
        print("no users or papers found")
        return []

    votes = []
    existing_votes = set()

    for user in users:
        papers_to_vote = random.sample(
            papers, min(len(papers), random.randint(3, 15))
        )

        for paper in papers_to_vote:
            if paper.author_id == user.id:
                continue

            if (user.id, paper.id) in existing_votes:
                continue

            existing_votes.add((user.id, paper.id))

            vote = Vote(
                user_id=user.id,
                paper_id=paper.id,
                created_at=datetime.now(timezone.utc) - timedelta(
                    days=random.randint(0, 30)
                ),
            )
            votes.append(vote)

    db.add_all(votes)
    db.commit()

    for paper in papers:
        paper.vote_count = db.query(Vote).filter(
            Vote.paper_id == paper.id
        ).count()

    for user in users:
        user_papers = db.query(Paper).filter(Paper.author_id == user.id).all()

        user.votes_received = sum(p.vote_count for p in user_papers)
        user.reputation_points = max(
            0, user.votes_received * 10 + user.papers_count * 50
        )

    db.commit()

    print(f"created {len(votes)} votes")
    return votes


def clean_database(db: Session):
    db.query(Paper).delete()
    db.query(User).delete()

    db.commit()
    print("database cleaned")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--admin", action="store_true", help="create admin user"
    )
    parser.add_argument(
        "--users", type=int, default=0, help="number of users to create"
    )
    parser.add_argument(
        "--papers", type=int, default=0, help="number of papers to create"
        )
    parser.add_argument(
        "--clean", action="store_true", help="clean database before seeding"
        )
    parser.add_argument(
        "--all", action="store_true", help="run all seeds with default values"
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:
        if args.clean:
            clean_database(db)

        if args.admin:
            create_admin(db)
            return

        if args.all or not any([args.users, args.papers]):
            admin = create_admin(db)
            users = create_users(db, count=15)
            all_users = [admin] + users

            papers = create_papers(db, count=25, authors=all_users)
            create_votes(db, users=all_users, papers=papers)

            return

        admin = create_admin(db)

        if args.users > 0:
            create_users(db, count=args.users)

        if args.papers > 0:
            users = db.query(User).all()
            create_papers(db, count=args.papers, authors=users)

        print("\nseeding complete!")

    finally:
        db.close()


if __name__ == "__main__":
    main()
