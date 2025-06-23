import json

def load_memories(memory_file_path):
    try:
        with open(memory_file_path, 'r', encoding='utf-8') as f:
            memories = json.load(f)
        return memories
    except Exception as e:
        print(f"[Memory Loader] Failed to load memory: {e}")
        return []
