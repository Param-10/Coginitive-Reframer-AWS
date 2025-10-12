# Demo Video Script (3 Minutes)

**Target:** AWS AI Agent Global Hackathon Judges  
**Duration:** 3:00 maximum (judges will stop watching at 3:00!)  
**Format:** Screen recording + voice-over OR talking head + screen share

---

## 🎬 Script Breakdown

### **[0:00-0:20] Opening & Problem Statement (20 seconds)**

**Visual:** Architecture diagram on screen

**Script:**
> "Hi, I'm [Your Name]. **Cognitive Reframer** is an AI agent that helps people break through decision paralysis and stress by transforming stuck thoughts into actionable insights using evidence-based mental models.
>
> Here's the architecture: Users interact with a frontend on S3, which calls API Gateway, triggering a Lambda-based agent that uses **Amazon Bedrock** for reasoning and **AgentCore patterns** for memory and tool orchestration. The agent selects from 8 cognitive models, generates two distinct reframes, and stores them to DynamoDB for personalization."

**Key Points to Show:**
- Problem (decision paralysis is universal)
- Solution (AI agent + mental models)
- AWS stack (Bedrock + AgentCore highlighted)

---

### **[0:20-1:50] Live Demo (90 seconds)**

**Visual:** Live application in browser

**Script:**
> "Let me show you how it works."
>
> **[Type input]** "I'm worried the product launch will fail and it'll be a disaster."
>
> **[Select tone]** I'll choose 'gentle' for a supportive tone.
>
> **[Click Generate Reframes]** The agent is now:
> 1. Checking for safety issues
> 2. Recalling my past reframes from memory
> 3. Selecting appropriate mental models
> 4. Invoking Bedrock Claude v2 with a structured prompt
>
> **[Results appear]** And here we go! Two reframes:
>
> **First**, using **Inversion**: "Instead of imagining failure, list the fastest ways to fail and stop doing those things." The agent provides specific action steps: list 3 failure modes, assign mitigations, schedule a check-in.
>
> **Second**, using **Dichotomy of Control**: "Separate what you control from what you don't." Action steps include blocking time for high-impact work and clarifying external blockers.
>
> Notice the structured output—this is powered by careful prompt engineering to ensure the LLM returns valid JSON every time.
>
> **[Click Save to Memory]** I'll save this. Now the agent will use this context to personalize future suggestions.
>
> **[Switch to History tab]** Here's my history—the agent learns from past reframes to provide increasingly relevant suggestions.
>
> **[Show safety feature - optional if time]** If I entered something concerning like 'I want to hurt myself,' the agent would skip reframing and show crisis resources instead—safety first.

**Key Actions:**
- Type realistic input (relatable)
- Show loading state (proves it's live)
- Point out two distinct models
- Highlight action steps (concrete, not vague)
- Demonstrate memory/history
- Mention safety (if time)

---

### **[1:50-2:30] Technical Deep-Dive (40 seconds)**

**Visual:** Switch to architecture diagram OR show CloudWatch logs

**Script:**
> "Technically, this demonstrates several **Amazon Bedrock AgentCore** concepts:
>
> **Runtime orchestration**: The Lambda function acts as an agent runtime, making multi-step decisions—validate input, recall memory, select models, invoke Bedrock, store results.
>
> **Memory**: Past reframes are stored in DynamoDB with a GSI for efficient retrieval. The roadmap includes migrating to AgentCore Vector Memory for semantic search using embeddings.
>
> **Tools**: I've built two Lambda tools—`memory_recall` and `schedule_followup`—that the agent calls when needed. These are designed to integrate with AgentCore Gateway.
>
> **Model**: Claude v2 on Bedrock generates the reframes using a carefully engineered prompt with 8 mental models and few-shot examples to ensure consistent JSON output.
>
> The entire system is serverless—Lambda, API Gateway, DynamoDB—so it auto-scales and costs under $150/month for 10,000 users."

**Key Technical Points:**
- AgentCore concepts (Runtime, Memory, Tools)
- Bedrock model explicitly named
- Multi-step reasoning demonstrated
- Serverless architecture
- Production-ready (costs, scaling)

---

### **[2:30-2:50] Impact & Value (20 seconds)**

**Visual:** Back to demo OR impact slides

**Script:**
> "This solves a real problem: millions of knowledge workers face decision paralysis daily. By combining AI with evidence-based cognitive models, we make mental frameworks accessible at the moment of need.
>
> The system is safety-first with self-harm detection, provides immediately actionable steps—not vague advice—and learns from your history to personalize suggestions.
>
> Use cases range from startup founders making tough calls to students managing academic stress to teams navigating complex projects."

**Key Value Props:**
- Real problem (relatable scale)
- Evidence-based (not just LLM prompting)
- Safety-conscious
- Actionable outputs
- Personalization
- Broad applicability

---

### **[2:50-3:00] Closing & Next Steps (10 seconds)**

**Visual:** GitHub repo OR live URL on screen

**Script:**
> "The code is open source on GitHub, the live demo is at [URL], and I've documented everything including deployment scripts and API docs. Next steps include real-time embeddings for semantic memory search, calendar integrations, and a mobile app. Thank you!"

**Show:**
- GitHub URL
- Live demo URL
- Signal you're done

---

## 🎥 Recording Tips

### Tools
- **Loom** (easiest): loom.com - cloud recording, auto-uploads
- **OBS Studio** (advanced): obs-project.com - local recording, full control
- **Zoom** (if you have it): Record yourself presenting + screen share
- **macOS**: QuickTime Player (screen recording) + iMovie (editing)

### Setup Checklist
- [ ] Close all unrelated tabs/windows
- [ ] Disable notifications (macOS: Do Not Disturb)
- [ ] Test microphone (clear audio is critical)
- [ ] Have water nearby
- [ ] Prepare demo data (pre-fill if needed to save time)
- [ ] Open all necessary windows beforehand:
  - Frontend (live URL)
  - Architecture diagram
  - CloudWatch logs (optional)
  - GitHub repo (for closing)

### Recording Strategy

**Option 1: Single Take (Efficient)**
- Script printed next to you
- Practice 2-3 times before recording
- Record straight through
- Minor mistakes are fine (shows authenticity)

**Option 2: Sections (Professional)**
- Record each section separately
- Use editing software to combine
- Add transitions between sections
- More polished but time-intensive

**Option 3: Voice-Over (Safest)**
- Record screen actions first (no audio)
- Record voice separately while watching playback
- Easier to get perfect audio
- Can re-record voice without re-doing demo

### Practice Run Checklist
- [ ] Time yourself (aim for 2:50, leaves 10s buffer)
- [ ] Identify slow sections (speed up)
- [ ] Check pacing (not too fast, not too slow)
- [ ] Verify demo works (test input produces good output)
- [ ] Confirm all URLs/links work

### Production Quality Tips
1. **Audio**: Clear speech, no background noise, good mic
2. **Visual**: 1920x1080 resolution minimum, readable text
3. **Pace**: Not rushed but not dragging
4. **Energy**: Enthusiastic but not over-the-top
5. **Clarity**: Technical terms explained briefly

---

## 📝 Annotations & Captions

Add text overlays for:
- Architecture service names (when showing diagram)
- "Amazon Bedrock" label (when showing results)
- "AgentCore: Runtime, Memory, Tools" (during technical section)
- URLs (GitHub, live demo) at the end

Tools for annotations:
- Loom: Built-in emoji reactions
- OBS: Text overlays
- iMovie/Final Cut: Text and titles
- Camtasia: Professional annotations

---

## 🎯 What Judges Are Looking For

### Technical Execution
✅ **Show:** Bedrock console, CloudWatch logs, or terminal output  
✅ **Mention:** Specific model name (Claude v2)  
✅ **Demonstrate:** Multi-step agent flow

### Functionality
✅ **Prove it works:** Live demo, not mockups  
✅ **Show errors handled:** Quick mention of validation

### Value
✅ **Real problem:** Relatable to judges  
✅ **Clear benefit:** Actionable steps, not vague advice

### Creativity
✅ **Novel approach:** Mental models + AI (not just chatbot)  
✅ **Unique design:** JSON structure for reliability

### Presentation
✅ **Time management:** Under 3:00  
✅ **Clear communication:** Technical but accessible  
✅ **Professional quality:** Good audio/video

---

## 🚫 Common Mistakes to Avoid

1. **Going over 3 minutes** - Judges WILL stop watching
2. **Too much code** - Show results, not implementation details
3. **Unclear problem** - Lead with "why does this matter?"
4. **No live demo** - Mockups/slides are not compelling
5. **Poor audio** - Judges can't understand = instant reject
6. **Reading entire script verbatim** - Sounds robotic
7. **Forgetting to mention Bedrock** - Required for prize category
8. **No URLs shown** - Judges can't test it themselves

---

## ✅ Pre-Recording Checklist

- [ ] Architecture diagram created and saved as PNG
- [ ] Demo working (test input returns good reframes)
- [ ] All URLs confirmed working
- [ ] GitHub repo is public
- [ ] README has screenshots
- [ ] Script practiced 2-3 times
- [ ] Recording software tested
- [ ] Microphone tested
- [ ] Notifications disabled
- [ ] Good lighting (if showing face)
- [ ] Water nearby
- [ ] Calm and ready!

---

## 🎬 Post-Recording Checklist

- [ ] Watch entire video (check for issues)
- [ ] Verify under 3:00
- [ ] Audio clear throughout
- [ ] Demo works correctly in video
- [ ] All text/URLs readable
- [ ] Upload to YouTube (unlisted or public)
- [ ] Get shareable link
- [ ] Test link in incognito window
- [ ] Add to Devpost submission

---

## 📤 Upload & Sharing

### YouTube Upload
1. Go to youtube.com/upload
2. Select video file
3. Title: "Cognitive Reframer - AWS AI Agent Hackathon"
4. Description:
   ```
   Cognitive Reframer - AI agent built with Amazon Bedrock AgentCore
   
   Transforms stressful thoughts into actionable insights using evidence-based mental models.
   
   Tech stack:
   - Amazon Bedrock (Claude v2)
   - AWS Lambda
   - Amazon DynamoDB
   - API Gateway
   - S3 hosting
   
   GitHub: [your-repo-url]
   Live Demo: [your-frontend-url]
   
   Built for AWS AI Agent Global Hackathon 2025
   ```
5. Visibility: **Unlisted** (only people with link can view)
6. Thumbnail: Screenshot from demo
7. Publish and copy link

### Alternative: Vimeo, Loom
- Vimeo: More professional, allows private links
- Loom: Easiest, instant upload, great for quick recordings

---

## 🎉 You're Ready!

With this script, you can record a compelling 3-minute demo that:
1. Clearly explains the problem and solution
2. Demonstrates live functionality
3. Shows technical depth (Bedrock + AgentCore)
4. Communicates value
5. Stays under time limit

**Next:** Record, upload, and submit to Devpost!

Good luck! 🚀

