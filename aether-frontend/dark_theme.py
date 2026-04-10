import os
import re

directory = 'd:/AntiGravity/AeatherTheAIcompass/aether-frontend/src'

replacements = [
    # Backgrounds
    (r'bg-white\b(?!/5?\d)', 'bg-white/5 backdrop-blur-md'),
    (r'bg-neutral-50\b', 'bg-white/5 backdrop-blur-md'),
    (r'bg-neutral-100\b', 'bg-white/10 backdrop-blur-md'),
    (r'bg-neutral-200\b', 'bg-white/20 backdrop-blur-md'),
    (r'bg-neutral-800\b', 'bg-white/10 backdrop-blur-md'),
    (r'bg-neutral-900\b', 'bg-white/20 backdrop-blur-md'),
    (r'bg-slate-50\b', 'bg-white/5 backdrop-blur-md'),
    (r'bg-slate-100\b', 'bg-white/10 backdrop-blur-md'),
    (r'bg-slate-800\b', 'bg-white/10 backdrop-blur-md'),
    (r'bg-slate-900\b', 'bg-white/20 backdrop-blur-md'),
    
    # Text colors
    (r'text-neutral-900\b', 'text-white'),
    (r'text-neutral-800\b', 'text-white/90'),
    (r'text-neutral-700\b', 'text-white/80'),
    (r'text-neutral-600\b', 'text-white/70'),
    (r'text-neutral-500\b', 'text-white/60'),
    (r'text-neutral-400\b', 'text-white/50'),
    (r'text-slate-900\b', 'text-white'),
    (r'text-slate-800\b', 'text-white/90'),
    (r'text-slate-700\b', 'text-white/80'),
    (r'text-slate-600\b', 'text-white/70'),
    (r'text-slate-500\b', 'text-white/60'),
    (r'text-slate-400\b', 'text-white/50'),
    (r'text-gray-900\b', 'text-white'),
    (r'text-gray-800\b', 'text-white/90'),
    (r'text-gray-700\b', 'text-white/80'),
    (r'text-gray-600\b', 'text-white/70'),
    (r'text-gray-500\b', 'text-white/60'),
    (r'text-gray-400\b', 'text-white/50'),
    (r'text-black\b', 'text-white'),

    # Borders
    (r'border-neutral-100\b', 'border-white/10'),
    (r'border-neutral-200\b', 'border-white/20'),
    (r'border-neutral-300\b', 'border-white/30'),
    (r'border-neutral-800\b', 'border-white/10'),
    (r'border-neutral-900\b', 'border-white/20'),
    (r'border-slate-100\b', 'border-white/10'),
    (r'border-slate-200\b', 'border-white/20'),
    (r'border-slate-800\b', 'border-white/10'),
]

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.jsx'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            for pattern, repl in replacements:
                content = re.sub(pattern, repl, content)
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {filepath}")
