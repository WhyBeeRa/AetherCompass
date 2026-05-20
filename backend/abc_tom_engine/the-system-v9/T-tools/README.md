# T-tools: Your Toolbox

Skills, prompts, and workflows. The things that give your agents superpowers.

---

## Three Types of Tools

### Prompts (Copy-Paste Instructions)
Saved instructions you paste into Claude Code.

**Workshop flow (01-04). In each track folder:**

| # | File | What It Does |
|---|------|-------------|
| 01 | `learn-from-context.md` | Reads your context file and fills the core files |
| 02 | `learn-from-samples.md` | Reads your writing samples and teaches agents your voice |
| 03 | `create-[output].md` | Creates your first output (varies by track) |
| 04 | `close-the-loop.md` | Promotes insights from Memory to Core |

**Bonus prompts (in `01-prompts/04-BONUS/`):**

| # | File | What It Does |
|---|------|-------------|
| 01 | `create-new-agent.md` | Recruit a new team member |
| 02 | `enhance-agent-with-research.md` | Make an agent world-class with deep research |
| 03 | `create-new-skill.md` | Build an expert playbook |
| 04 | `create-new-workflow.md` | Create a multi-step agent pipeline |
| 05 | `train-agent-on-document.md` | Train an agent on any document you paste |
| 06 | `clone-voice-from-conversation.md` | Extract your real voice from casual messages |
| 07 | `enable-auto-revision-loop.md` | Agents review each other automatically |
| 08 | `connect-api-keys.md` | Connect external tools |
| 09 | `content-calendar.md` | Plan your content schedule |
| 10 | `repurpose-content.md` | One piece becomes 5 formats |
| 11 | `analyze-competitor.md` | Research competition |
| 12 | `create-hook-bank.md` | Build opening line collection |
| 13 | `weekly-review.md` | Review and improve weekly |
| 14 | `audit-my-system.md` | Full system health check with scoring |
| 15 | `client-onboarding-flow.md` | Generate onboarding questionnaire, email, agenda |

### Skills (Expert Playbooks)
Specialized knowledge for specific content types.

**Content skills:**
- `02-skills/social-post-skill/` - Social media best practices
- `02-skills/blog-post-skill/` - Blog post structure and writing
- `02-skills/newsletter-skill/` - Newsletter writing and engagement
- `02-skills/case-study-skill/` - Turn client wins into social proof
- `02-skills/internal-communication-skill/` - Team announcements, policy changes, company updates

**Communication skills:**
- `02-skills/sales-proposal-skill/` - Client proposals and offers
- `02-skills/professional-email-skill/` - Email writing expertise

**Thinking skills:**
- `02-skills/document-summary-skill/` - Summarizing documents and interviews
- `02-skills/meeting-notes-skill/` - Meeting note capture and structure
- `02-skills/prd-skill/` - Product requirement documents
- `02-skills/stakeholder-update-skill/` - Stakeholder status updates
- `02-skills/strategic-decision-skill/` - Decision brief framework
- `02-skills/research-briefing-skill/` - Research briefing structure

**System skills:**
- `02-skills/hebrew-writing-skill/` - Hebrew writing quality
- `02-skills/web-research-skill/` - Web research techniques
- `02-skills/tom-guide/` - System guidance
- `02-skills/adam-coo/` - COO orchestration

### Workflows (Multi-Step Processes)
Recipes that coordinate multiple agents. Adam (COO) orchestrates all workflows.

- `03-workflows/content-workflow.md`. Content track (Researcher → Copywriter → Gatekeeper). Handles social posts, blog posts, newsletters.
- `03-workflows/communication-workflow.md`. Communication track (Strategist → Copywriter → Gatekeeper). Handles proposals, emails, internal updates, HR messages, community posts.
- `03-workflows/thinking-decision-workflow.md`. Decision brief (Strategist → Devil's Advocate → Chief of Staff → Gatekeeper).
- `03-workflows/thinking-summary-workflow.md`. Summary (Analyst → Copywriter → Gatekeeper). Handles meeting notes, documents, PRDs.

---

## Folder Structure

```
T-tools/
├── 01-prompts/
│   ├── 01-content/         → Content track prompts (01-04)
│   ├── 02-communication/   → Communication track prompts (01-04)
│   ├── 03-thinking/        → Thinking track prompts (01-04)
│   └── 04-BONUS/           → Advanced prompts (01-15)
├── 02-skills/
│   ├── social-post-skill/
│   ├── blog-post-skill/
│   ├── newsletter-skill/
│   ├── sales-proposal-skill/
│   ├── professional-email-skill/
│   ├── document-summary-skill/
│   ├── meeting-notes-skill/
│   ├── prd-skill/
│   ├── stakeholder-update-skill/
│   ├── strategic-decision-skill/
│   ├── case-study-skill/
│   ├── internal-communication-skill/
│   ├── research-briefing-skill/
│   ├── hebrew-writing-skill/
│   ├── web-research-skill/
│   ├── tom-guide/
│   └── adam-coo/
└── 03-workflows/
    ├── content-workflow.md
    ├── communication-workflow.md
    ├── thinking-decision-workflow.md
    └── thinking-summary-workflow.md
```

---

## Creating New Tools

**New skill:** Use `01-prompts/04-BONUS/03-create-new-skill.md`
**New prompt:** Create numbered file in the relevant track folder under `01-prompts/`
**New workflow:** Use `01-prompts/04-BONUS/04-create-new-workflow.md`, then save in `03-workflows/`

---

> **© Tom Even**
> Workshops & future dates: [www.getagents.today](https://www.getagents.today)
> Newsletter: [www.agentsandme.com](https://www.agentsandme.com)
