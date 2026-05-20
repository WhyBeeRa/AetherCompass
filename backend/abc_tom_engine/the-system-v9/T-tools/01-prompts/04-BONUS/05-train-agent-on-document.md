# Prompt: Train Your Agent on a Document

You have knowledge sitting in documents, articles, books, or course notes that your agents don't know about. This prompt fixes that.

Paste any document and Claude will extract the most valuable insights and feed them directly into the right agent's file. Your bookmarks become agent intelligence.

Copy and paste this into your chat:

---

```
I want to train one of my agents using knowledge from a document I have.

---
Agent to train: [Which agent should learn from this? e.g., "copywriter", "strategist", "researcher"]
What this document is: [e.g., "a blog post about storytelling", "a chapter from a sales book", "course notes on product management", "a guide to HR best practices"]
What I want the agent to learn: [e.g., "better storytelling techniques", "how to structure proposals", "a new framework for decisions"]

Document:
[PASTE THE FULL DOCUMENT, ARTICLE, OR NOTES HERE]
---

Please do the following:

1. Read the agent file in A-agents/ to understand its current knowledge

2. Read C-core/project-brief.md and C-core/voice-dna.md to understand the business context

3. Analyze the document and extract:
   - Key principles that are directly useful for this agent's job
   - Specific techniques or frameworks the agent can apply
   - Examples or patterns worth remembering
   - Anything that contradicts or improves the agent's current approach

4. Filter ruthlessly. Only keep insights that:
   - Are specific enough to act on (not generic advice)
   - Are relevant to MY business context
   - Would actually change how the agent works

5. Update the agent file in A-agents/:
   - Add a "Learned From: [document name]" section with the best insights
   - Update any checklists with new quality checks from the document
   - Add frameworks or techniques as concrete instructions (not just references)

6. Check if any skills in T-tools/02-skills/ should also be updated with insights from this document

7. Update M-memory/learning-log.md with what was learned and from where

Show me a summary of what was extracted and what was updated.
```

---

## What You Can Feed It

- Blog posts or articles you bookmarked
- Book chapters (paste the text, not the PDF)
- Course notes or workshop materials
- Industry reports or whitepapers
- Podcast transcripts
- Conference talk summaries
- Internal playbooks or SOPs from your company
- Competitor analysis you found online

**The more specific the document, the better the training.** A 2,000-word deep dive on "how to write cold emails that get replies" will train your agent better than a generic "marketing 101" article.

---

> **© Tom Even**
> Workshops & future dates: [www.getagents.today](https://www.getagents.today)
> Newsletter: [www.agentsandme.com](https://www.agentsandme.com)
