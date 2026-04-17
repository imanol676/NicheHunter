import os

models_code = {
    "organization.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    lemonsqueezy_customer_id = Column(String, unique=True)
    plan_tier = Column(String, default="Explorer")
    credits_remaining = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subscriptions = relationship("Subscription", back_populates="organization")
    scan_jobs = relationship("ScanJob", back_populates="organization")
    saved_opportunities = relationship("SavedOpportunity", back_populates="organization")
""",
    "subscription.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    lemonsqueezy_subscription_id = Column(String, unique=True)
    status = Column(String)
    plan = Column(String)
    current_period_end = Column(DateTime)
    
    organization = relationship("Organization", back_populates="subscriptions")
""",
    "scan_job.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.db.base import Base

class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    niche_query = Column(String)
    subreddits = Column(ARRAY(String))
    status = Column(String, default="pending")
    posts_found = Column(Integer, default=0)
    pain_points_extracted = Column(Integer, default=0)
    filters = Column(JSONB)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="scan_jobs")
    raw_posts = relationship("RawPost", back_populates="scan_job")
    clusters = relationship("PainPointCluster", back_populates="scan_job")
""",
    "raw_post.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base import Base

class RawPost(Base):
    __tablename__ = "raw_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_job_id = Column(UUID(as_uuid=True), ForeignKey("scan_jobs.id"))
    reddit_id = Column(String, unique=True, index=True)
    subreddit = Column(String)
    title = Column(String)
    body = Column(Text)
    top_comments = Column(Text)
    score = Column(Integer)
    num_comments = Column(Integer)
    reddit_created_at = Column(DateTime)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan_job = relationship("ScanJob", back_populates="raw_posts")
    pain_points = relationship("PainPoint", back_populates="raw_post")
""",
    "pain_point.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from src.db.base import Base

class PainPoint(Base):
    __tablename__ = "pain_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_post_id = Column(UUID(as_uuid=True), ForeignKey("raw_posts.id"))
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("pain_point_clusters.id"), nullable=True)
    description = Column(Text)
    embedding = Column(Vector(1536))
    category = Column(String)
    severity = Column(String)
    confidence_score = Column(Float)
    frequency_count = Column(Integer, default=1)
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    raw_post = relationship("RawPost", back_populates="pain_points")
    cluster = relationship("PainPointCluster", back_populates="pain_points")
""",
    "cluster.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from src.db.base import Base

class PainPointCluster(Base):
    __tablename__ = "pain_point_clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_job_id = Column(UUID(as_uuid=True), ForeignKey("scan_jobs.id"))
    label = Column(String)
    summary = Column(Text)
    size = Column(Integer)
    avg_severity_score = Column(Float)
    centroid = Column(Vector(1536))
    representative_samples = Column(JSONB)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan_job = relationship("ScanJob", back_populates="clusters")
    pain_points = relationship("PainPoint", back_populates="cluster")
    opportunities = relationship("Opportunity", back_populates="cluster")
""",
    "opportunity.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.db.base import Base

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("pain_point_clusters.id"))
    title = Column(String)
    problem_statement = Column(Text)
    market_analysis = Column(Text)
    proposed_solutions = Column(Text)
    monetization_ideas = Column(Text)
    competitive_landscape = Column(Text)
    opportunity_score = Column(Float)
    difficulty = Column(String)
    strategies = Column(JSONB)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cluster = relationship("PainPointCluster", back_populates="opportunities")
    saved_by_orgs = relationship("SavedOpportunity", back_populates="opportunity")
""",
    "saved_opportunity.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base import Base

class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id"))
    user_notes = Column(Text)
    status = Column(String, default="new")
    saved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="saved_opportunities")
    opportunity = relationship("Opportunity", back_populates="saved_by_orgs")
"""
}

MODELS_DIR = "c:\\Users\\imano\\OneDrive\\Escritorio\\proyectos\\painpoint_scraper\\backend\\src\\models"
os.makedirs(MODELS_DIR, exist_ok=True)

for filename, content in models_code.items():
    with open(os.path.join(MODELS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)

init_content = ""
for filename in models_code.keys():
    module_name = filename.replace(".py", "")
    with open(os.path.join(MODELS_DIR, filename), "r", encoding="utf-8") as rf:
        content = rf.read()
        for line in content.split('\\n'):
            if line.startswith("class ") and "(Base):" in line:
                class_name = line.replace("class ", "").replace("(Base):", "").strip()
                init_content += f"from .{module_name} import {class_name}\\n"

init_content += "from .user import User\\n"

with open(os.path.join(MODELS_DIR, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(init_content)
    
print("Models generated successfully!")
