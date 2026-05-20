# Folder Guide

What each folder does and how to use it.

---

## A-agents/

**Purpose:** Your AI team definitions

**What goes here:**
- Agent personality files (one per agent)
- Each file defines: who they are, what they read, how they work

**Current agents:**
- `adam-agent.md` - Your COO. Orchestrates the team and runs all workflows.
- `tom-agent.md` - Your guide to the ABC-TOM system.
- `copywriter-agent.md` - Writes content and communications.
- `gatekeeper-agent.md` - Reviews quality.
- `researcher-agent.md` - Web research and angle-finding.
- `analyst-agent.md` - Turns raw material into structured documents.
- `strategist-agent.md` - Strategic analysis from business/growth perspective.
- `devils-advocate-agent.md` - Challenges assumptions, finds blind spots.
- `chief-of-staff-agent.md` - Synthesizes multiple perspectives into decision briefs.

**How to create a new agent:**
1. Create `[role]-agent.md` in this folder
2. Copy structure from existing agent
3. Define: identity, required reading, responsibilities
4. Use prompt: `T-tools/01-prompts/04-BONUS/01-create-new-agent.md`

**Tips:**
- One job per agent (don't make generalists)
- Be specific about what "good" means
- Always include Required Reading section

---

## B-brain/

**Purpose:** Knowledge your agents need. **Brain is what you bring.**

**What goes here:**
- `01-context/01-context.md` - Answer questions about yourself and your business
- `02-my-samples/` - Your past writing, organized by track (01-content, 02-communication, 03-thinking)
- `_INBOX/` - Quick capture point. Drop anything new here first, organize later.
- Research documents, reference materials, data

> Note: `api-keys-registry.md` lives in `C-core/`, not B-brain. Keep it private, don't share.

**How to use:**
1. Fill in `01-context/01-context.md` to get started
2. Add your past content to `02-my-samples/` in the subfolder matching your track
3. Add communication/references as needed
4. Use `_INBOX/` when you're not sure where something goes. Sort it later.

**Brain vs Memory:**
- Brain = What YOU bring to the system (your knowledge, research, examples)
- Memory = What you LEARN TOGETHER with the system (patterns, feedback, decisions)

**"Brain is what you bring. Memory is what you learn together."**

**Tips:**
- More knowledge = smarter agents
- Add real examples, not descriptions
- Keep it organized (subfolders help)
- When in doubt, drop it in _INBOX

---

## C-core/

**Purpose:** Your brand's DNA

**The three files:**

### project-brief.md
What you do, who you serve, what makes you different.
- Your mission
- The problem you solve
- What makes you unique

### voice-dna.md
How your brand speaks.
- Tone and style
- Words you use / avoid
- Formatting preferences
- Example sentences

### icp-profile.md
Your ideal customer.
- Who they are
- What they want
- Their problems
- Where they hang out

**How to fill these:**
1. Answer questions in `B-brain/01-context/01-context.md`
2. Run prompt `T-tools/01-prompts/[your-track]/01-learn-from-context.md` (e.g., `01-content`, `02-communication`, or `03-thinking`)
3. Claude fills in C-core automatically

**Not sure what a filled-in file looks like?**
Check `@ALL-GUIDES-HERE/07-core-examples/` for real examples across 4 roles (freelancer, product manager, content creator, CEO/business owner).

**Tips:**
- Be specific (not "professional" but "short sentences, no jargon")
- Include examples
- These start stable but evolve through The Loop (insights from Memory get promoted here)

---

## T-tools/

**Purpose:** Skills, workflows, and prompts

**Structure:**
```
T-tools/
├── 01-prompts/                             → Copy-paste instructions
├── 02-skills/                              → Expert playbooks
└── 03-workflows/                           → Multi-step processes
```

### 01-prompts/
Numbered instructions for common actions.
```
01-content/
├── 01-learn-from-context.md
├── 02-learn-from-samples.md
├── 03-create-content.md
└── 04-close-the-loop.md
02-communication/
└── ... (same 01-04 structure)
03-thinking/
└── ... (same 01-04 structure)
04-BONUS/
├── 01-create-new-agent.md
├── 02-enhance-agent-with-research.md
├── 03-create-new-skill.md
└── ... (up to 15-client-onboarding-flow.md)
```

### 02-skills/
Specialized knowledge for specific tasks.
- `social-post-skill/` - Social media best practices
- `blog-post-skill/` - Blog post structure and writing
- `newsletter-skill/` - Newsletter writing and engagement
- `case-study-skill/` - Turn client wins into social proof
- `internal-communication-skill/` - Team announcements and updates
- `sales-proposal-skill/` - Client proposals, offers, and persuasive communication
- `professional-email-skill/` - Email writing
- `document-summary-skill/` - Summarizing documents and interviews
- `meeting-notes-skill/` - Meeting note capture and structure
- `prd-skill/` - Product requirement documents
- `stakeholder-update-skill/` - Stakeholder status updates
- `strategic-decision-skill/` - Decision brief framework
- `research-briefing-skill/` - Research briefing structure
- `hebrew-writing-skill/` - Hebrew writing quality
- `web-research-skill/` - Web research techniques
- `tom-guide/` - System guidance
- `adam-coo/` - COO orchestration

**Quick guide to T-tools:**
- **Skills** = Knowledge. What an agent knows HOW to do. (e.g., "how to write a newsletter")
- **Prompts** = Triggers. What YOU paste to start something. (e.g., "create a social post about X")
- **Workflows** = Pipelines. Multi-step processes that connect agents and skills. (e.g., "draft → review → revise → approve")

Rule of thumb: If it's knowledge, make it a skill. If it's a shortcut you paste, make it a prompt. If it has 3+ steps with handoffs between agents, make it a workflow.

### 03-workflows/
Multi-step processes that chain actions. One workflow per track:
- `content-workflow.md` - Idea → research → draft → review → publish (social posts, blogs, newsletters)
- `communication-workflow.md` - Recipient context → strategy → draft → review → send (proposals, emails, internal updates, HR, community)
- `thinking-decision-workflow.md` - Decision → analysis → debate → synthesis → review
- `thinking-summary-workflow.md` - Raw material → extraction → polish → review

**How to create new tools:**
- New skill: `T-tools/01-prompts/04-BONUS/03-create-new-skill.md`
- New workflow: `T-tools/01-prompts/04-BONUS/04-create-new-workflow.md`
- Skills go in their own subfolder
- Prompts are numbered for order

---

## O-output/

**Purpose:** Everything your agents create

**Organization:**
```
O-output/
└── your-project/
    ├── final-[type].md      ← YOUR DELIVERABLE (copy-paste ready)
    └── _process/
        ├── research/draft    ← Internal work
        └── review files      ← Quality checks
```

**How to use:**
- One project per folder
- The final file is always at the project root (copy-paste ready)
- All process files (drafts, reviews, research) go in `_process/`
- Open any project folder: your deliverable is right there

**Tips:**
- Consistent naming helps you find things
- Don't delete process files (you might need them)
- Let agents save here automatically

---

## M-memory/

**Purpose:** What you learn together with the system. **Memory is what you learn together.**

**The three files:**

### learning-log.md
Execution patterns. What worked, what didn't.
- "Short hooks perform better"
- "Avoid starting with questions"
- "The gatekeeper catches too much, lower threshold"

### feedback-audience.md
Audience signals. What they say after you publish.
- Comments and reactions
- Questions people ask
- What resonates

### feedback-system.md
Your corrections and preferences when working with agents.
- "Make the opening shorter"
- "Don't use bullet points in emails"
- "I prefer casual tone for LinkedIn"

### decisions.md
Strategic rationale. Why you chose what you chose.
- "We focus on LinkedIn because that's where ICP is"
- "We don't use emojis in headlines"
- "Bilingual content, Hebrew for local, English for newsletter"

**When to update:**
- `learning-log.md` → After each review cycle
- `feedback-audience.md` → After publishing and seeing reactions
- `feedback-system.md` → Whenever you correct an agent's output
- `decisions.md` → When you make strategic choices

**Why this matters:**
Agents read memory before starting work. Every entry makes future output better. This is the compounding effect.

**The Loop:** The best insights from Memory don't just stay here. They get promoted back into Brain (as new knowledge) and Core (as updated rules). That's what closes The Loop and makes the system compound.

Run `04-close-the-loop.md` from your track folder to close The Loop explicitly.

---

## Quick Reference

| Folder | Contains | Changes How Often |
|--------|----------|-------------------|
| A-agents/ | Team definitions | Rarely |
| B-brain/ | Knowledge, examples (what you bring) | Often (as you learn) |
| C-core/ | Brand DNA | Rarely (but evolves through The Loop) |
| T-tools/ | Skills, prompts, workflows | Sometimes (as you need more) |
| O-output/ | Created content | Every project |
| M-memory/ | Learnings (what you learn together) | After every project |

---

## The Pattern: The ABC-TOM Loop

1. **ABC feeds the system** (who you are, what you know)
2. **TOM executes** (skills create output, memory captures learning)
3. **The Loop: Memory feeds back into Brain and Core** (best learnings become knowledge and rules)
4. **The system starts stronger next time** (and keeps compounding)

This is The Loop. It's what makes the difference between a static template and a living system that grows with you.

---

> **© Tom Even**
> Workshops: [www.getagents.today](https://www.getagents.today)
> Newsletter: [www.agentsandme.com](https://www.agentsandme.com)
