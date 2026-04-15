from pydantic import BaseModel, Field, HttpUrl, field_validator, field_validator, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class IntentCategory(str, Enum):
    """
    Broad categories for intents, though the system uses semantic search.
    """
    GENERATIVE_ART = "generative_art"
    DATA_ANALYSIS = "data_analysis"
    CODING_ASSISTANT = "coding_assistant"
    WRITING_AID = "writing_aid"
    ENTREPRENEURSHIP = "entrepreneurship"
    COMMUNITY = "community"
    OTHER = "other"

class Badge(str, Enum):
    MODEL_SCOUT = "Model Scout"
    LEAD_ARCHITECT = "Lead Architect"
    EARLY_ADOPTER = "Early Adopter"
    TRUTH_SEEKER = "Truth Seeker"
    MASTER_VERIFIER = "Master Verifier"

class UserIntent(BaseModel):
    """
    Represents the user's raw intent and processed classification.
    """
    raw_query: str
    semantic_tags: List[str] = Field(default_factory=list)
    detected_problems: List[str] = Field(default_factory=list, description="Real-world problems extracted from query")

class ToolReview(BaseModel):
    """
    A review for an AI tool.
    """
    reviewer_id: str
    rating: float = Field(..., ge=0, le=5)
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    verified_purchase: bool = False
    expert_level: str = "Beginner" # Beginner, Intermediate, Expert

class AITool(BaseModel):
    """
    The core data model for an AI tool in Aeather.
    """
    id: str
    name: str
    description: str
    website_url: str # Free, Freemium, Paid
    pricing_model: str # Free, Freemium, Paid
    
    # Trust Engine Data
    trust_score: float = Field(0.0, ge=0, le=100)
    verified_output_badge: bool = False
    last_benchmark_date: Optional[datetime] = None
    
    # Classification
    intents: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Social Proof
    gallery_images: List[str] = Field(default_factory=list)
    reviews: List[ToolReview] = Field(default_factory=list)

    class Config:
        api_mode = True

class VisualProof(BaseModel):
    """
    Direct evidence of a tool's capability.
    """
    url: str
    source_url: str = Field(..., description="Where this proof was found (Tweet, Discord, etc.)")
    media_type: str = "image" # image, video, code_snippet
    description: Optional[str] = None

class ScoutFindings(BaseModel):
    """
    Raw findings from a Scout discovery cycle.
    Separated from AITool to track history and model drift.
    """
    tool_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str
    
    # The Core Truth
    user_intent: str = Field(..., description="Specific problem solved (e.g. 'Automating lead gen' vs 'Marketing tool')")
    raw_sentiment: str = Field(..., description="Technical assertions or complaints from builders")
    tech_stack: str = Field(..., description="No-Code, Low-Code, or API-only")
    
    # Evidence & Reliability
    visual_proofs: List[VisualProof] = Field(default_factory=list)
    reliability_score: float = Field(..., ge=0, le=100, description="Calculated based on evidence vs hype")
    hype_factor: bool = Field(False, description="True if content contains forbidden superlatives")
    
    technical_feasibility: Optional[str] = None

class VisualQuality(str, Enum):
    HIGH = "High" # TV/Movie quality, indistinguishable from reality
    MID = "Mid"   # Good for social media, obvious AI artifacts
    LOW = "Low"   # Glitchy, toy-like

class ToolMetrics(BaseModel):
    """
    The 'Airbnb' style ratings for a tool.
    """
    accuracy: int = Field(..., ge=1, le=5, description="Reliability of output")
    speed: int = Field(..., ge=1, le=5, description="Latency and response time")
    value: int = Field(..., ge=1, le=5, description="Cost vs Performance")
    ease_of_use: int = Field(..., ge=1, le=5, description="No-code vs Developer skills")
    
    # Aether Audit - Phase 2026 Core Metrics
    skill_multiplier: int = Field(default=3, ge=1, le=5, description="Ability to turn a junior into a senior output")
    hallucination_score: int = Field(default=5, ge=1, le=5, description="Reliability vs Hallucinations (5 = Zero Hallucination)")
    
    # UI Metadata for the 3-Card Drop & ToolDetails
    learning_curve: str = Field(default="בינוני", description="קל מאוד, בינוני, קשה, מיועד למפתחים")
    pricing: str = Field(default="Freemium", description="Freemium, תשלום חודשי, פתוח לכולם")
    integration: str = Field(default="Web / API", description="אינטגרציות מרכזיות, למשל Slack, Web, API מותאם")
    
    # Comparison Matrix Labels
    latency_label: str = Field(default="2.4s", description="זמן תגובה ממוצע לתצוגה")
    cost_label: str = Field(default="$0.01 / task", description="עלות מוערכת לביצוע משימה")
    privacy_grade: str = Field(default="Enterprise Safe", description="דרגת פרטיות (למשל A, B, Enterprise Ready)")

    last_verified: datetime = Field(default_factory=datetime.now, description="Critical to track model drift")

class IntentMapping(BaseModel):
    """
    Core Aether Intent Engine mapping.
    Maps a specific user intent to a tool with a verified success score.
    """
    intent_description: str = Field(..., description="E.g., 'Automating investor pitch decks from docs'")
    success_score: float = Field(..., ge=0, le=100, description="How well this tool specifically solves this intent")
    trade_off: Optional[str] = Field(None, description="The catch. E.g., 'Fast, but lacks granular design control'")

class MeasurementProof(BaseModel):
    """
    Direct evidence of a tool's performance in a laboratory setting.
    This is the 'Raw Data' that backs up the objective scores.
    """
    scenario: str = Field(..., description="e.g., 'Writing a Python FastAPI endpoint'")
    prompt: str = Field(..., description="The exact input provided to the tool")
    output: str = Field(..., description="The raw output received from the tool")
    timestamp: datetime = Field(default_factory=datetime.now)
    metrics_captured: Dict[str, Any] = Field(default_factory=dict, description="e.g., {'latency': '1.2s', 'tokens': 450}")


class LabAnalysis(BaseModel):
    """
    The Truth. Structured, verified insights from The Lab.
    """
    tool_name: str
    metrics: ToolMetrics
    visual_quality: VisualQuality
    
    # Semantic Mapping
    job_to_be_done: List[str] = Field(..., description="Broad categories (e.g. 'Lead Enrichment', 'Viral Video Creation')")
    
    # THE AETHER INTENT ENGINE
    intents_mapped: List[IntentMapping] = Field(default_factory=list, description="Specific intents this tool solves and how well")
    
    # Perplexity Layer
    executive_summary: str = Field(..., description="Sentence 1: Peak. Sentence 2: Trade-off.")
    pros: List[str] = Field(default_factory=list, description="Array of Pros with a title, e.g. 'Title: Description'")
    cons: List[str] = Field(default_factory=list, description="Array of Cons with a title, e.g. 'Title: Description'")
    use_cases: List[str] = Field(default_factory=list, description="UI pills array")
    
    # THE LAB: PROOF OF MEASUREMENT (Audit Logs)
    measurement_proofs: List[MeasurementProof] = Field(default_factory=list, description="Raw data samples from direct testing")
    audit_notes: Optional[str] = Field(default="", description="Red flags or critical warnings about the tool")

    # Deep Intelligence Fields (Phase 7)

    limitations: List[str] = Field(default_factory=list, description="What the tool explicitly cannot do / struggles with")
    privacy_policy: Optional[str] = Field(default="Unknown", description="e.g. 'Trains on user data', 'Enterprise only'")
    social_proof: Optional[str] = Field(None, description="Summarized user/developer quote validating capability")
    
    source_findings_id: Optional[str] = None # Link back to raw Scout data

class TrustScore(BaseModel):
    """
    The Auditor's Matrix.
    """
    authenticity_score: float = Field(..., ge=0, le=100, description="Reviewer identity verification status")
    evidence_quality_score: float = Field(..., ge=0, le=100, description="Replicability of proofs")
    performance_stability: float = Field(..., ge=0, le=100, description="Drift monitoring score")
    marketing_noise_penalty: float = Field(..., ge=0, le=100, description="Penalty for hype/buzzwords")
    
    total_trust_score: float = Field(..., ge=0, le=100, description="Weighted average: (Auth*0.4)+(Stab*0.3)+(Qual*0.3) - Penalty")
    
    last_audit_date: datetime = Field(default_factory=datetime.now)

class AuditLog(BaseModel):
    """
    The Trail of Truth. History of all verification actions.
    """
    tool_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    action: str = Field(..., description="Verified, Flagged, Badge Revoked")
    reason: str = Field(..., description="Detailed explanation (e.g., 'Model Drift detected > 15%')")
    new_trust_score: float

class GalleryItem(BaseModel):
    """
    Pinterest-style showcase item.
    """
    tool_id: str
    media_url: str
    media_type: str = "image"
    
    # Search & Discovery
    style_tags: List[str] = Field(..., description="Visual categories for search")
    
    # The Recipe (Educational Value)
    prompt_recipe: Dict[str, str] = Field(..., description="Prompt, Negative Prompt, Settings")
    
    # Trust Integration
    is_featured: bool = False
    trust_badge_visible: bool = Field(True, description="Only true if TrustScore > 70")
    audit_log_id: Optional[str] = None

class ManualToolEntry(BaseModel):
    name: str = Field(..., min_length=2)
    description: str
    pros: List[str]
    cons: List[str]
    use_cases: List[str] = Field(default_factory=list)
    trust_score: int = Field(..., ge=10, le=100)
    
    # Extra fields required for internal DB conversion
    intent_category: str
    accuracy: int = Field(4, ge=1, le=5)
    speed: int = Field(4, ge=1, le=5)
    value: int = Field(4, ge=1, le=5)
    ease_of_use: int = Field(4, ge=1, le=5)
    skill_multiplier: int = Field(3, ge=1, le=5)
    hallucination_score: int = Field(4, ge=1, le=5)
    latency_label: str = "2.4s"
    cost_label: str = "$0.01 / task"
    privacy_grade: str = "Enterprise Safe"
    pricing: str = "Freemium"
    learning_curve: str = "בינוני"
    visual_quality: str = "Mid"
    image_url: Optional[str] = None
    
    # Comparison Fields
    latency_label: str = "2.4s"
    cost_label: str = "$0.01 / task"
    privacy_grade: str = "Enterprise Safe"
    integration: str = "Web / API"

    @field_validator('pros', 'cons', 'use_cases', mode='before')
    @classmethod
    def split_and_clean(cls, v):
        if isinstance(v, str):
            # מפצל לפי פסיק, מנקה רווחים ומסנן מחרוזות ריקות
            return [item.strip() for item in v.split(',') if item.strip()]
        return v

class UserProfile(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    points: int = 0
    elo: int = 1200
    badges: List[Badge] = Field(default_factory=list)
    contributions_count: int = 0
    votes_count: int = 0
    last_active: datetime = Field(default_factory=datetime.now)
    is_pro: bool = False

class VendorInsights(BaseModel):
    tool_name: str
    missed_searches: List[Dict[str, Any]]

class ToolContribution(BaseModel):
    name: str
    url: str
    description: str

class LiveMetric(BaseModel):
    """
    Real-time performance metrics for AI models.
    """
    tool_name: str
    provider: str # OpenAI, Anthropic, etc.
    latency_ms: float
    hallucination_score: float # 0 to 100
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "online" # online, slow, offline
    comparison_vs_avg: Optional[float] = None # % difference vs others
