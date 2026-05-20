### Preparation: Installing the Project Files

1. Download the ZIP file and extract it.
2. Drag the extracted folder into your Obsidian Vault.
3. On Windows? It sometimes creates an extra ".obsidian" folder inside the Vault. Ignore it.
4. Make sure you can see all folders (A-agents, B-brain, C-core, T-tools, etc.) in the left sidebar in Obsidian. They're inside the the-system folder you extracted from the ZIP file.

### Preparation: Opening Claude Code

1. Open a new session in Claude Code.
2. **Important:** Select the the-system folder as your working directory. This is how Claude knows where to read, edit, and create files.

---

### Step 1: Choose Your Track

Before you start, pick the track that fits your work:

**Content** (תוכן)
Publishable content that people read: social posts, newsletters, blog posts, articles.
*For: marketers, creators, founders, anyone who publishes content. Also great for thought leadership.*

**Communication** (תקשורת)
Professional text to a specific recipient: emails, Slack messages, internal updates, community messages, and more.
*For: founders, freelancers, consultants, HR, managers, anyone who writes professional messages.*

**Thinking** (חשיבה)
Decision briefs: you bring a decision you need to make, multiple agents debate it from different angles, and you get a structured brief with different perspectives.
*For: CEOs, PMs, business owners, managers, team leads, anyone who makes decisions.*

**Not sure which to pick?** Ask yourself:
- Do you publish things people read? → **Content**
- Do you write professional text to specific people? → **Communication**
- Do you need help making a decision? → **Thinking**

---

## Phase 1: Feed the Brain

*Do this in Obsidian first. before running any prompts. Just fill in the two files below.*

### Step 2: Fill in Your Information

Open the file `B-brain/01-context/01-context.md`

Fill in the text with your information (copy-paste from the document you filled in beforehand).

**Don't have a "business"?** No problem. This works for anyone:
- If you work at a company: write about your role, your team, and the people you serve
- If you're a freelancer: write about what you do and who your clients are
- If you're exploring: write about what you want to create and who it's for

**Do not change file names.** The prompts are linked to them.

### Step 3: Add Your Writing Samples

Open the samples folder that matches your track:
- **Content** → `B-brain/02-my-samples/01-content/`
- **Communication** → `B-brain/02-my-samples/02-communication/`
- **Thinking** → `B-brain/02-my-samples/03-thinking/`

Each folder has a README explaining exactly what to paste. Read it first.

Paste your text (Hebrew or English) into each of the 3 files: `sample-01`, `sample-02`, `sample-03`.

**Pro tip:** The better your samples, the better the output. Pick pieces you're proud of.

✋ **Finish both steps above before moving on. Don't run any prompts yet.**

---

## Phase 2: Run Your New Team

*Now go to Claude Code. Run one prompt at a time. Wait for it to finish before pasting the next one.*

All 4 prompts are inside your track folder under `T-tools/01-prompts/`:
- Content track → `T-tools/01-prompts/01-content/`
- Communication track → `T-tools/01-prompts/02-communication/`
- Thinking track → `T-tools/01-prompts/03-thinking/`

**Prompt 1. Learn From Context**

- Copy the entire content of `01-learn-from-context.md`
- Paste it in Claude Code and send.
- Claude reads your answers and automatically updates the C-core files: `project-brief`, `icp-profile`, `voice-dna`.

**Prompt 2. Learn From Samples**

- Copy `02-learn-from-samples.md` and paste it.
- Claude reads the 3 samples and updates the Core documents, the agents, and Memory.

**Prompt 3. Create Your Output**

- Copy the `03-...` file from your track folder and paste it.
- Fill in the details:
  - **Content:** your topic or idea for a post/newsletter/article
  - **Communication:** who you're writing to and what about
  - **Thinking:** the decision you need to make and the options you're considering
- Adam (your COO agent) manages the entire team to create the output. The result is saved in `O-output/`.

What each track produces:

- **Content** A piece of publishable content (social post, blog post, or newsletter). 3 agents collaborate: Researcher finds angles → Copywriter writes in your voice → Gatekeeper reviews quality.
- **Communication** Professional text to a specific recipient (email, Slack message, internal update, community message). 3 agents collaborate: Strategist analyzes the situation → Copywriter writes in your voice → Gatekeeper reviews quality.
- **Thinking** A decision brief. You bring the decision you need to make, and 4 agents debate it from different perspectives (Strategist → Devil's Advocate → Chief of Staff → Gatekeeper). You get a structured brief with options and recommendations.

**Prompt 4. Close The Loop**

- Copy `04-close-the-loop.md` and paste it.
- Adam reviews what was just created, logs what worked and what didn't to M-memory, and promotes strong insights to C-core.
- This is what makes the system get smarter over time.

---

### Important Tip: Permissions

When Claude asks for permission to read or edit files, click **"Allow always for session"** so you don't have to approve each action separately.

---

### What Happens Next?

- Your output is saved in the `O-output/` folder as a new file. You can read it both in Obsidian and in Claude's chat.
- Want to keep going? There are 15 bonus prompts (01-15) in `T-tools/01-prompts/04-BONUS/` for creating new agents, skills, workflows, API connections, content calendars, and more.
- You can also try a different track. Pick a different track folder and run Prompt 3 again to see the same system produce a completely different output.
- **Tip:** Got a file and not sure where it goes? Drop it in `B-brain/_INBOX/`. It's your junk drawer. Sort it later, or ask Claude to sort it for you.

Yalla, good luck.
