# Prompt: Audit My System

Your system has been running for a while. Some files are rich, some are empty, some are outdated. This prompt gives you a full checkup: what's working, what's missing, and what to fix next.

Think of it as a doctor's visit for your AI team.

Copy and paste this into your chat:

---

```
I want a full audit of my ABC-TOM system. Check everything and tell me what's working, what's missing, and what I should fix next.

Adam, please run this audit:

1. **Core Health Check (C-core/)**
   - Read project-brief.md: Is it filled in? Is it specific enough?
   - Read voice-dna.md: Does it have concrete patterns and examples, or just vague descriptions?
   - Read icp-profile.md: Is the audience clearly defined?
   - Score each: STRONG / NEEDS WORK / EMPTY

2. **Brain Health Check (B-brain/)**
   - Check 01-context/01-context.md: Is it filled in?
   - Check 02-my-samples/: How many samples exist per track? Are they actually filled in or still placeholder text?
   - Check _INBOX/: Is there unsorted material that should be moved?
   - Score: STRONG / NEEDS WORK / EMPTY

3. **Agent Health Check (A-agents/)**
   - Read each agent file
   - Check: Does each agent have clear responsibilities? Does it reference the right C-core files? Does it have quality checklists?
   - Are any agents missing domain expertise that could be added with BONUS/02?
   - Score each agent: STRONG / NEEDS WORK / BASIC

4. **Memory Health Check (M-memory/)**
   - Read learning-log.md: How many entries? Are they specific and useful?
   - Read feedback-audience.md and feedback-system.md: Any patterns worth promoting to C-core?
   - Read decisions.md: Are past decisions logged?
   - Score: ACTIVE / THIN / EMPTY

5. **Tools Health Check (T-tools/)**
   - Scan 02-skills/: Which skills exist? Are they being used?
   - Scan 03-workflows/: Are workflows up to date with the current agent team?
   - Score: STRONG / NEEDS WORK / BASIC

6. **Output Check (O-output/)**
   - How many projects exist? Is the folder structure clean?
   - Score: ACTIVE / SPARSE / EMPTY

7. **Overall System Score**
   Give me a summary table:

   | Area | Score | Top Priority Fix |
   |------|-------|-----------------|
   | C-core | | |
   | B-brain | | |
   | A-agents | | |
   | M-memory | | |
   | T-tools | | |
   | O-output | | |

8. **Top 3 Actions**
   Based on the audit, what are the 3 most impactful things I should do right now to improve the system? Be specific. Not "improve your voice DNA" but "add 3 example sentences to voice-dna.md that show your casual tone."

Show me the full audit report.
```

---

## When to Run This

- **Week 1-2:** After your first few outputs, to catch gaps early
- **Monthly:** As a maintenance check
- **When output quality drops:** Something probably drifted
- **After adding new agents or skills:** To make sure everything connects

---

> **© Tom Even**
> Workshops & future dates: [www.getagents.today](https://www.getagents.today)
> Newsletter: [www.agentsandme.com](https://www.agentsandme.com)
