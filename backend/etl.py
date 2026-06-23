import os
import json
import asyncio
import random
import praw
from github import Github
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize API Clients
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT", "AetherBot/0.1")
) if os.getenv("REDDIT_CLIENT_ID") else None

github_client = Github(os.getenv("GITHUB_TOKEN")) if os.getenv("GITHUB_TOKEN") else None
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Add specific subreddits for context
TOOL_CONFIGS = [
    {"name": "ChatGPT", "category": "Text & Productivity", "subreddits": ["ChatGPT", "artificial"]},
    {"name": "Claude 3", "category": "Text & Productivity", "subreddits": ["ClaudeAI", "artificial"]},
    {"name": "Perplexity", "category": "Text & Productivity", "subreddits": ["perplexity_ai"]},
    {"name": "Midjourney", "category": "Design & Images", "subreddits": ["midjourney"]},
    {"name": "DALL-E 3", "category": "Design & Images", "subreddits": ["dalle2"]},
    {"name": "GitHub Copilot", "category": "Dev & Code", "subreddits": ["github", "programming"], "github_repo": "community/community"},
    {"name": "Cursor", "category": "Dev & Code", "subreddits": ["Cursor", "MachineLearning"], "github_repo": "getcursor/cursor"},
    {"name": "ElevenLabs", "category": "Video & Audio", "subreddits": ["ElevenLabs"]},
    {"name": "Runway Gen-2", "category": "Video & Audio", "subreddits": ["runwayml"]},
    {"name": "Veo", "category": "Video & Audio", "subreddits": ["artificial"]},
    {"name": "Zapier", "category": "Automation", "subreddits": ["zapier", "automation"]}
]

async def extract_intent_llm(text: str, tool_name: str) -> dict:
    """Passes raw text to LLM to extract intent and success score, enforcing JSON with retry logic."""
    if not os.getenv("OPENAI_API_KEY"):
        return {"intent": f"Mock intent for {tool_name} (No API Key)", "success_score": 8}
        
    prompt = f"""Analyze the following user review/comment about {tool_name}.
Extract the specific task the user intended to perform ('intent'), and rate the tool's success on a scale of 1-10 ('success_score').
If the text doesn't contain a clear intent or review, return "intent": null, "success_score": null.
Output strictly as a valid JSON object: {{"intent": "...", "success_score": 8}}.

Text:
"{text}"
"""
    attempt = 1
    max_retries = 5
    delay = 2.0
    while attempt <= max_retries:
        try:
            response = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise data extractor."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            err_str = str(e).lower()
            is_retryable = any(kw in err_str or kw in type(e).__name__.lower()
                               for kw in ["429", "rate", "limit", "quota", "overloaded", "temp", "unavailable", "timeout", "503", "500"])
            if is_retryable and attempt < max_retries:
                wait_time = delay * random.uniform(0.8, 1.2)
                print(f"OpenAI API error ({e}). Retrying in {wait_time:.2f} seconds (Attempt {attempt}/{max_retries})...")
                await asyncio.sleep(wait_time)
                delay *= 2.0
                attempt += 1
            else:
                print(f"Error during OpenAI LLM extraction for {tool_name}: {e}")
                return {"intent": None, "success_score": None}

def fetch_reddit_data(tool_name: str, subreddits: list, limit=3):
    """Fetches top posts/comments from Reddit for a given tool."""
    results = []
    if not reddit:
        print("Reddit client not configured. Creating mock data.")
        return [{"text": f"I used {tool_name} to generate awesome things.", "url": "https://reddit.com/mock", "source": "Reddit - Mock"}]
    
    try:
        for sub_name in subreddits:
            subreddit = reddit.subreddit(sub_name)
            # Search for the tool name in the subreddit
            for submission in subreddit.search(tool_name, limit=limit):
                text = f"Title: {submission.title}\n{submission.selftext}"
                url = submission.url
                if submission.selftext:
                    results.append({"text": text, "url": url, "source": f"Reddit - r/{sub_name}"})
    except Exception as e:
        print(f"Error fetching from Reddit for {tool_name}: {e}")
    return results

def fetch_github_data(tool_name: str, repo_name: str, limit=2):
    """Fetches text from GitHub Issues/Discussions."""
    results = []
    if not github_client or not repo_name:
        return results
        
    try:
        repo = github_client.get_repo(repo_name)
        # Search for tools in issues
        search_query = f"{tool_name} repo:{repo_name} type:issue state:closed"
        issues = github_client.search_issues(query=search_query)
        count = 0
        for issue in issues[:limit]:
            text = f"Title: {issue.title}\n{issue.body}"
            url = issue.html_url
            results.append({"text": text, "url": url, "source": f"GitHub - {repo_name}"})
            count += 1
    except Exception as e:
        print(f"Error fetching from GitHub for {tool_name}: {e}")
    
    return results

async def process_tool(config: dict):
    print(f"--- Processing Tool: {config['name']} ---")
    raw_data = []
    
    # Extract from Reddit
    reddit_results = fetch_reddit_data(config['name'], config.get('subreddits', []), limit=3)
    raw_data.extend(reddit_results)
    
    # Extract from GitHub (if applicable)
    if 'github_repo' in config:
        github_results = fetch_github_data(config['name'], config['github_repo'], limit=2)
        raw_data.extend(github_results)
    
    mapped_intents = []
    # Transform with LLM
    for item in raw_data:
        # Avoid processing huge chunks
        text_chunk = item['text'][:1500] 
        extracted = await extract_intent_llm(text_chunk, config['name'])
        
        if extracted and extracted.get("intent"):
            mapped_intents.append({
                "intent_description": extracted["intent"],
                "success_score": extracted.get("success_score", 5),
                "source": item["source"],
                "original_url": item["url"]
            })
            
    return {
        "tool_name": config["name"],
        "category": config["category"],
        "intents_mapped": mapped_intents
    }

async def run_etl():
    print("Starting Aether ETL Pipeline...")
    all_tools_data = []
    
    for config in TOOL_CONFIGS:
        tool_data = await process_tool(config)
        all_tools_data.append(tool_data)
        
    output_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_tools_data, f, ensure_ascii=False, indent=2)
        
    print(f"ETL completed. Data saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(run_etl())
