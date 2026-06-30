import json

log_path = "/Users/hoangvan/.gemini/antigravity/brain/c68d7c20-27da-4738-bf75-cbe5f4dcd882/.system_generated/logs/transcript.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = str(data.get('content', ''))
            if 'sập' in content or 'quán sập' in content or 'gg map' in content or 'đường link' in content or 'chết' in content:
                print(f"Step {data.get('step_index')}: {content[:300]}...")
        except Exception:
            pass
