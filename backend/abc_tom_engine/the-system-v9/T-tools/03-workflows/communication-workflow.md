# Communication Workflow

> Adam (COO) orchestrates the Strategist, Copywriter, and Gatekeeper to produce any professional communication you send to a real human: client proposals, sales emails, HR messages, internal updates, community announcements, partner outreach, hard conversations, follow-ups.

> **The principle:** every message has a recipient and a desired response. Strategy figures out the response. Writing earns it. Review protects it.

---

## What Counts As Communication

Anything you write where one specific person (or one specific group) needs to read it, understand it, and ideally do something about it.

| Type | Recipient | Desired Response |
|------|-----------|------------------|
| **Client proposal** | A specific lead or client | Sign / pay / agree |
| **Sales email** | A prospect | Reply / book / explore |
| **Internal update** | Your team or manager | Align / decide / unblock |
| **HR message** | A teammate | Understand the change / feel respected |
| **Community message** | A WhatsApp/Slack/Discord group | Engage / show up / share |
| **Partner outreach** | A potential collaborator | Open the door |
| **Hard conversation** | Someone you respect | Resolve without damage |
| **Follow-up** | Anyone who went silent | Restart the thread |

**If your output is 1-to-many and public** (a post, a newsletter, a blog), use the **Content Workflow** instead.
**If your output is a decision brief or analysis,** use the **Thinking Workflow** instead.

---

## Process Overview

```
[You] tell Adam: who is this for, what do you want to happen, what's the context
          ↓
[Adam] reads C-core, picks the right communication type, assigns the team
          ↓
[Strategist] analyzes the recipient, the goal, the right approach
          ↓
[Copywriter] writes the message in your voice, matched to the type
          ↓
[Gatekeeper] reads it as the recipient. Approves or sends back.
          ↓
[Adam] delivers final output, copy-paste ready, and updates memory
```

---

## Step 0: Type Selection (Adam's First Move)

Before anything else, Adam picks the **communication type**. This drives everything: which skill the Copywriter uses, what tone the Strategist recommends, what the Gatekeeper checks for.

| You Said... | Type | Skill Used |
|-------------|------|------------|
| "Proposal for [client]" | Client Proposal | `sales-proposal-skill` |
| "Cold email to [lead]" or "Sales email" | Sales Email | `professional-email-skill` |
| "Reply to [name]" / "Email back to..." | Professional Email | `professional-email-skill` |
| "Update for the team" / "Status update" | Internal Update | `stakeholder-update-skill` or `internal-communication-skill` |
| "Slack message" / "Internal note" | Internal Communication | `internal-communication-skill` |
| "Message to [employee]" / "HR message" | HR Communication | `internal-communication-skill` (HR mode) |
| "WhatsApp to [community]" / "Community post" | Community Message | `internal-communication-skill` (community mode) |
| "Partner outreach" / "Intro email" | Partner Outreach | `professional-email-skill` (outreach mode) |
| "Follow-up" | Follow-up | `professional-email-skill` (follow-up mode) |

If unsure, Adam asks ONE question: **"Who's reading this and what do you want them to do?"**

---

## Step 1: Preparation

### Adam Reads Context

- `C-core/project-brief.md` (who you are)
- `C-core/voice-dna.md` (how you sound)
- `C-core/icp-profile.md` (who you talk to. Use only if recipient is a client/prospect/audience match)
- `M-memory/learning-log.md` (what worked before)
- `M-memory/decisions.md` (any standing rules: pricing, positioning, what we said no to)

### Adam Creates Project Folder

The folder name follows the type:

```
O-output/
└── [type]-[recipient-or-topic]/
    ├── final.md                       ← THE DELIVERABLE (copy-paste ready)
    └── _process/
        ├── strategist-analysis.md     ← Recipient and approach
        ├── copywriter-draft.md        ← Written message
        └── gatekeeper-review.md       ← Quality review
```

**Examples:**
- `proposal-acme-corp/`
- `email-sarah-followup/`
- `update-q3-status/`
- `hr-promotion-yael/`
- `community-launch-announcement/`

---

## Step 2: Strategist Analyzes

### What the Strategist Does

1. Reads the recipient context from Adam.
2. Reads `A-agents/strategist-agent.md`.
3. Reads the relevant skill (see type table above).
4. **Analyzes three things:**
   - **The recipient.** What do they care about? What's their reality right now? What's the worst-case interpretation of this message?
   - **The goal.** What specific response makes this a win?
   - **The approach.** Tone (warm/direct/formal/casual). Length (one-liner/short/full). Structure. Risks to defuse.

### Deliverable: `_process/strategist-analysis.md`

```markdown
# Strategic Analysis: [Type] to [Recipient]

## Recipient
- **Who they are:** [role, context, relationship to you]
- **What they care about:** [their world, not yours]
- **Their state right now:** [busy / under pressure / receptive / cold]
- **History:** [past interactions, last touchpoint, open threads]

## Goal
- **Desired response:** [the one specific thing you want them to do]
- **Acceptable response:** [the fallback that's still a win]
- **Failure mode:** [what would make this backfire]

## Recommended Approach
- **Tone:** [warm / direct / formal / playful / careful]
- **Length:** [one-liner / short paragraph / full message / structured proposal]
- **Opening move:** [their world / a shared reference / direct ask / acknowledgment]
- **Key positioning:** [the one thing they need to feel by the end]

## Risks to Address
- **Risk:** [misinterpretation, defensiveness, ghosting]
- **How to defuse:** [specific phrase or framing]

## Notes for the Copywriter
- [Anything the writer must include]
- [Phrases to avoid]
- [What "success" sounds like in their voice]
```

---

## Step 3: Copywriter Writes

### What the Copywriter Does

1. Reads C-core (voice and audience).
2. Reads the Strategist's analysis. The strategy is the brief.
3. Reads the relevant skill (see Step 0 type table).
4. **Writes the message in Tom's voice, matched to the type.**

### Type-Specific Templates

The deliverable is always `_process/copywriter-draft.md`. The structure inside changes by type.

#### Client Proposal Draft

```markdown
# Proposal: [Client Name]
**Date:** [Date] · **Version:** v1

## Their Situation
[Mirror their words. Show you listened.]

## What Changes
[Paint the after state with specifics.]

## Approach
[3-5 clear steps.]

## Investment
[Price with ROI context.]

## Next Step
[One clear action.]
```

#### Sales / Cold Email Draft

```markdown
# Email: [Recipient Name]
**Subject options (3):**
1. [Curiosity-driven]
2. [Direct-value]
3. [Personal-reference]

---

[Opening: their world, not yours. 1-2 lines max.]

[The reason for writing. Direct.]

[The specific value or ask. One thing only.]

[The CTA. One verb, one action.]

[Sign-off in your voice.]
```

#### Internal Update Draft

```markdown
# Update: [Topic]
**To:** [Team / Manager / Stakeholder]
**TL;DR:** [The single line they need if they read nothing else.]

## What Happened
- [Fact, not interpretation]

## What It Means
- [Implication, briefly]

## What's Next
- [Decision needed / action / no action required]

## Where I Need You
- [Specific ask, or "FYI only"]
```

#### HR / Sensitive Message Draft

```markdown
# Message: [Recipient]
**Type:** [Promotion / Feedback / Difficult Conversation / Recognition / Departure]
**Tone:** [Specific tone choice from Strategist]

---

[Opening: acknowledge them as a person before the topic.]

[The message itself. Direct, kind, specific.]

[What this means for them, practically.]

[Open door for response: "Let's talk" / "Reply when ready" / no expectation.]

[Sign-off that matches the relationship.]
```

#### Community Message Draft

```markdown
# Community Message: [Topic]
**Channel:** [WhatsApp group / Slack / Discord / Alumni]
**Length target:** [1 paragraph / 3 lines / longer]

---

[Hook: one line that earns the read.]

[The substance. Personal voice. No corporate tone.]

[The invitation: react, share, show up, or just nod.]

[Optional P.S. that adds warmth.]
```

### Copywriter Notes (always at bottom of draft)

```markdown
## Copywriter Notes
- **Strategic approach used:** [How the analysis shaped this draft]
- **Tone choices:** [Why this tone for this recipient]
- **What I almost wrote but didn't:** [The version that was too corporate / too casual / too pushy]
```

---

## Step 4: Gatekeeper Reviews

### What the Gatekeeper Does

1. **First read as the recipient.** Not as the sender. What's the gut reaction?
2. **Three checks:**
   - **Voice match.** Does this sound like the actual person, or like AI-with-their-name?
   - **Goal fit.** Will the recipient want to give the desired response?
   - **Risk scan.** Is anything misreadable? Defensive-sounding? Pushy? Cold?
3. **Decision:** APPROVED or REVISIONS NEEDED.

### The Recipient Test

The Gatekeeper imagines the recipient reading this on their phone, between meetings, half-distracted. Does the message work in that real-world context, or only in a perfect read?

### Deliverable: `_process/gatekeeper-review.md`

```markdown
# Gatekeeper Review: [Type] to [Recipient]
**Status:** [APPROVED / REVISIONS NEEDED]

## Recipient Read (Gut Reaction)
[3-5 words describing what the recipient feels at first read.]

## What Works
- [Strength tied to the goal]

## What Needs Improvement
1. **[Issue]** → [Fix]

## Voice Check
- [ ] Sounds like Tom, not AI
- [ ] No em dashes, no AI tells
- [ ] Sentence rhythm matches voice DNA

## Goal Check
- [ ] The desired response feels easy to give
- [ ] No friction at the CTA
- [ ] The recipient knows what to do

## Risk Check
- [ ] No misreadable phrases
- [ ] No accidental power dynamic
- [ ] Length matches the relationship

## Next Step
[Send / Revise specific lines / Rewrite section]
```

---

## Step 5: Revision (If Needed)

Up to 2 revision passes. After v3, Adam pauses and asks Tom for direction. More than 2 rewrites usually means the strategy is off, not the writing.

---

## Step 6: Adam Delivers

1. **Saves final** to `final.md` at the project root (copy-paste ready, nothing else).
2. **Presents to Tom** with a one-paragraph summary: who, what, why this approach, what the desired response is.
3. **If client/external:** flag for Tom's review before sending. Hard stop, no exceptions.
4. **Updates memory:**
   - `M-memory/learning-log.md` → what worked, what almost didn't.
   - `M-memory/decisions.md` → if this set a new precedent (a pricing line, a positioning line, a tone choice).

---

## Quick Checklist

**Before Starting**
- [ ] Type identified (proposal / email / update / HR / community / outreach / follow-up)
- [ ] Recipient is one specific human or one specific group
- [ ] Desired response is named in one sentence
- [ ] C-core read

**Strategy**
- [ ] Recipient analyzed (what THEY care about, not what you care about)
- [ ] Goal and acceptable fallback identified
- [ ] Risks named
- [ ] Tone, length, opening move chosen

**Writing**
- [ ] Voice DNA followed
- [ ] Type-correct skill applied
- [ ] Strategy executed (not ignored)
- [ ] Opens with their world, not yours

**Review**
- [ ] Gatekeeper read it as the recipient
- [ ] Voice match verified
- [ ] No AI tells (em dashes, "delve", "tapestry", "in conclusion")
- [ ] CTA is friction-free

**Wrap-Up**
- [ ] Final saved as copy-paste ready
- [ ] Memory updated
- [ ] Tom flagged if external/sensitive

---

## What Makes This Workflow Work

**One brain per step.** Strategist thinks. Copywriter writes. Gatekeeper protects. No agent does two jobs at once.

**Recipient-first, always.** Every step asks "what does the reader feel?" before "what do I want to say?"

**Type drives everything.** A proposal is not a Slack message. A WhatsApp announcement is not an HR message. The workflow adapts. The agents adapt. The skills adapt.

**The Loop.** Every message you send teaches the system. After delivery, run `04-close-the-loop.md` from the communication track. Patterns get promoted to voice-dna.md. The next message is sharper.

---

> *Strategy gives it direction. Writing gives it personality. Review makes it bulletproof. Type makes it the right tool for the right job.*

---

> **© Tom Even**
> Workshops & future dates: [www.getagents.today](https://www.getagents.today)
> Newsletter: [www.agentsandme.com](https://www.agentsandme.com)
