# launcher/services/ai_service.py
import json
from openai import OpenAI

from launcher.config import AI_API_KEY

print(f"AI API Key loaded: {'yes' if AI_API_KEY else 'NO - KEY IS EMPTY'}")

OPENROUTER_URL = "https://openrouter.ai/api/v1"
MODEL = "openrouter/free"

client = OpenAI(
    base_url=OPENROUTER_URL,
    api_key=AI_API_KEY,
)

def build_prompt(scenes: list, character_appearances: dict) -> str:
    characters = ", ".join(character_appearances.keys())
    scene_list = "\n".join(
        f"{i+1}. {scene}" for i, scene in enumerate(scenes)
    )
    return f"""You are a professional film script analyst.

Given the following script breakdown, provide:
1. A brief summary for each scene (1-2 sentences max)
2. Key shot recommendations for each scene (2-3 shots max)

Characters in script: {characters}

Scenes:
{scene_list}

Respond in this exact JSON format:
{{
  "scenes": [
    {{
      "scene_number": 1,
      "summary": "Brief scene summary here",
      "recommended_shots": ["Shot 1 description", "Shot 2 description"]
    }}
  ]
}}

Return ONLY the JSON. No extra text."""


def analyse_breakdown(scenes: list, character_appearances: dict) -> dict:
    prompt = build_prompt(scenes, character_appearances)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content

    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()

    return json.loads(content)