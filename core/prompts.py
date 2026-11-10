def build_creator_prompt(topic, style, platform, duration, tone, audience):
    return f"""
You are the senior writer and video producer for VYRON Studios.
Create a production-ready video package using the information below.

IDEA: {topic}
FORMAT: {style}
PLATFORM: {platform}
TARGET LENGTH: {duration} minutes
NARRATION TONE: {tone}
AUDIENCE: {audience}

Use this exact Markdown structure:
# Video title
Give 3 clickable but honest title options.
# Core angle
Explain the central idea in 2-3 sentences.
# Opening hook (first 5 seconds)
Write a strong spoken hook and matching visual.
# Full narration
Write a complete narration appropriate for the target duration. Use natural spoken language.
# Scene-by-scene storyboard
Create 6-12 numbered scenes. For each scene include:
- Approximate timestamp
- Visual direction (describe an image or footage a creator could source or generate)
- Voiceover
- On-screen text (short)
- Sound / pacing suggestion
# Thumbnail concept
Describe a clear, readable thumbnail and give 3-5 words of thumbnail text.
# YouTube description
Write a concise description.
# Hashtags
Give 5-8 relevant hashtags.
# Fact-check notes
List claims that must be checked before publishing. Do not invent sources or present uncertain claims as facts.

Keep it original, family-friendly, engaging and accurate. Do not imitate a living creator's exact style.
"""
def build_rewrite_prompt(text):
    return f"""Improve the following VYRON Studios video plan. Make the hook stronger, remove repetition, improve spoken flow, and preserve factual caution. Return the complete revised plan in Markdown.

{text}
"""
