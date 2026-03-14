from typing import List, Dict
from models import ScoutFindings, AuditLog, GalleryItem, VisualQuality

CURATOR_SYSTEM_PROMPT = """
Role: You are the Chief Visual Architect and Curator of Aether. Your job is to transform raw evidence and verified data into an objective, inspiring, and searchable visual gallery.

Objective: Create the "Pinterest for AI" by organizing tool outputs into an aesthetic interface while strictly stripping away marketing fluff.

1. Visual Selection & Objective Standard:
From the "Visual Proof" provided by the Scout, select high-resolution examples.
Group outputs structurally (e.g., "Vector Graphic", "Photorealistic Image"). Do not use promotional language like "Stunning Masterpiece".

2. The Recipe Integration:
Every visual output must be paired with technical "Metadata": The specific prompt used, the tool version, and any relevant parameters (e.g., Seed, Temperature).
Describe what the image *is*, not how *good* it is. Focus on cold facts.

3. Integration of Trust:
Visually anchor the "Trust Score" and "Verified" badge to every showcase item.
If a tool's score drops, update the gallery styling to reflect its "Volatile" status.

4. Intent-Visual Mapping:
Coordinate with the Lab Agent to ensure that when a user searches for an "Intent," the gallery displays the most relevant visual evidence first.

Constraints:
Keep the UI terminology clean, professional, and entirely free of hype.
Prioritize scientific clarity over conversational clutter.
Ensure that every image has an "Open in Tool" or "Try this Prompt" call to action.
"""

class CuratorAgent:
    """
    The Curator: Visual Architect.
    Filters and packages data for the Gallery UI.
    """
    def __init__(self):
        pass

    def _generate_style_tags(self, image_url: str) -> List[str]:
        """
        Stub for Vision API (CLIP/GPT-4o).
        Returns tags based on visual analysis.
        """
        # Mock logic
        if "mj" in image_url or "midjourney" in image_url:
            return ["Photorealistic", "Cinematic", "High Octane"]
        if "code" in image_url or "github" in image_url:
            return ["Terminal", "Code Snippet", "Dark Mode"]
        return ["Generative Art", "Abstract"]

    def _extract_recipe(self, findings: ScoutFindings) -> Dict[str, str]:
        """
        Extracts prompt/settings from raw findings.
        """
        # In reality, this would parse the 'raw_sentiment' or 'description' or image metadata
        return {
            "prompt": f"Imagine a masterpiece using {findings.tool_name}...", 
            "settings": "v6.0 --ar 16:9"
        }

    def curate_gallery(self, findings: ScoutFindings, audit_log: AuditLog) -> List[GalleryItem]:
        """
        The Filter: Only admits high-quality, verified items.
        """
        print(f"Curator: Reviewing candidates for {findings.tool_name}...")
        
        gallery = []
        
        # 1. Quality Filter
        # If the Scout didn't find visuals, or they are "Low Quality" (implied logic), skip.
        # Here we rely on the existence of VisualProof.
        
        if not findings.visual_proofs:
            print("Curator: Rejected. No visual evidence found.")
            return []

        # 2. Trust Filter Integration
        # Only show Trust Badge if score is high enough.
        show_badge = audit_log.new_trust_score >= 70
        
        for proof in findings.visual_proofs:
            # Mocking a quality check per image.
            # In a real system, we'd use an 'Image Aesthetic Scorer' model here.
            
            tags = self._generate_style_tags(str(proof.url))
            recipe = self._extract_recipe(findings)
            
            item = GalleryItem(
                tool_id=findings.tool_name, # conceptual link
                media_url=proof.url,
                media_type=proof.media_type,
                style_tags=tags,
                prompt_recipe=recipe,
                is_featured=audit_log.new_trust_score > 90,
                trust_badge_visible=show_badge,
                audit_log_id=str(audit_log.timestamp)
            )
            gallery.append(item)
            
        print(f"Curator: Selected {len(gallery)} items for the gallery.")
        return gallery
