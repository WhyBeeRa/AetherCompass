import math
from typing import List, Tuple
from models import Badge, UserProfile


def check_for_badges(user: UserProfile) -> List[Badge]:
    """
    Checks if user is eligible for any new badges.
    """
    new_badges = []
    
    # Early Adopter: Any user who joined (already handled if we give it to everyone now)
    if Badge.EARLY_ADOPTER not in user.badges:
        new_badges.append(Badge.EARLY_ADOPTER)
    
    # Truth Seeker: At least 10 votes
    if user.votes_count >= 10 and Badge.TRUTH_SEEKER not in user.badges:
        new_badges.append(Badge.TRUTH_SEEKER)
        
    # Master Verifier: At least 50 votes
    if user.votes_count >= 50 and Badge.MASTER_VERIFIER not in user.badges:
        new_badges.append(Badge.MASTER_VERIFIER)
        
    # Model Scout: At least 5 contributions (manual tool adds)
    if user.contributions_count >= 5 and Badge.MODEL_SCOUT not in user.badges:
        new_badges.append(Badge.MODEL_SCOUT)
        
    # Lead Architect: High ELO or high contributions
    if (user.elo >= 1500 or user.contributions_count >= 20) and Badge.LEAD_ARCHITECT not in user.badges:
        new_badges.append(Badge.LEAD_ARCHITECT)
        
    return new_badges
