Project ADVantage
Hackathon Prompt
Find a marketing process that's inhuman in scope or scale, and ship a system or agent that runs it.
Overview 
With the proliferation of AI, content creation, mass marketing, and an overall skyrocket in volume has flooded the market. Decision makers are fatigued and the average decision maker ignores a majority of emails in their inbox. 

As an entrepreneur, building a marketing firm for independent Registered Independent Advisors I’ve tried the following:
Cold calling
Cold LI connection request
DMs
Networking at conferences
Video content
Physical gifts
Ads
Proprietary product offerings
Podcast interviews
And yet, the highest converting strategies for booking a call were:
Personal referrals
Can’t scale once network is exhausted
Personalized outreach … or outreach that “feels personal”
Financial analysis
Personal Loom video
Specific strategy for account

So what’s the theory? Account-based marketing.

Account-based marketing is not a new concept; a B2B strategy that treats individual high-value accounts as "markets of one". Instead of casting a wide net to generate broad leads, ABM aligns sales and marketing to deliver highly personalized, 1-to-1 campaigns aimed at specific decision-makers within target organizations.

Marketing feedback from client/prospect conversations have been, what is the ROI? How can you prove truth or effectiveness. Case studies are great, but add value FIRST. 

The important KPI is number of qualified leads on booked conversations. 

Marketing is great with getting people to see you, but getting them on an actual call is a different beast. 
These calls felt shallow. Felt unprepared no matter what research I did until the following:
Analyzing years of data for the firm
Sharing strategy and ideas up-front
Intriguing the decision maker with their own firm data

Combining all of these became a lethal weapon because rather than just coming with grand ideas and projections, I showcase the low hanging fruit, my competence, and the feeling like the client isn’t just one of many but rather a high touch high service experience. A feeling of “hey this guy actually looked at my business, is actually coming up with some good plans, have identified the exact pain points I’m feeling and or have not/have been able to articulate.” Which leads to a feeling of “let me hear what he has to say.”

I found a highly converting funnel, but a new problem emerged. Time constraints. 

Researching each firm individually took a minimum of:
20 minutes for surface level business analytics and financial analysis
20 minutes of research on website, social media/digital presence, news/press releases, and individual decision maker posts
20 minutes of recording Loom video takes

Minimum of 1 hour per firm and if that is streamlined and efficient. Each firm provides new use cases, new strategies, and different approaches so commonly would take long. 

For one person and nearly 15,000+ firms, even at 30% ICP fit of 5,000 firms, that’s 5,000 hours or 625 work days, or 125 weeks or 2.4 years at full 8 hour work days over 5 days/week. 

So how to we solve this? Account based marketing at inhuman scale and scope using Agentic workflows. 

WORKFLOW
1. The Financial Core (Data Engine)
This is a deterministic, programmatic layer that runs raw Python calculations to guarantee absolute numerical accuracy before any LLM touches the data.
Input: Bulk SEC Form ADV datasets filtered by a target list of unique CRD numbers.
Process: Automatically extracts the specific, pre-mapped columns spanning the last 5 consecutive years. It executes hardcoded financial scripts to calculate:
5-year AUM delta and Compound Annual Growth Rate (CAGR).
Shift in average account sizes and client volume mix.
High-Net-Worth (HNW) dependency and account concentration ratios.
Output: A structured financial_profile.json per CRD# containing zero math hallucinations, complete with raw data points optimized for downstream chart rendering.
2. The Agentic Sub-Suite (The Spoke Agents)
A. The Sovereign Financial Analyst Agent
Role: Acts as an elite-tier business consultant specializing exclusively in wealth management and independent RIAs.
Agentic Autonomy: Instead of just summarizing data, it analyzes the 5-year trajectory. If it detects anomalies—such as an abrupt 40% AUM drop in a single year—it holds a state-flag to prompt the Digital Agent to investigate press releases or team breakaways during its web-scrape phase.
Core Output: Synthesizes the quantitative calculations into 3 distinct, high-signal business inferences (e.g., “Firm is struggling with advisor capacity as client volume grew 20% while AUM stagnated”).
B. The Digital Footprint & AEO Agent
Role: Evaluates the firm’s public-facing digital marketing infrastructure.
Agentic Autonomy: Uses Jina AI to ingest website markdown. It doesn't just read text; it evaluates search intent, keyword alignment, and hooks.
Optional AEO Engine: If the ingested markdown shows strong baseline content, the agent triggers a secondary sub-routine simulating an Answer Engine Optimization (AEO) search visibility test (e.g., "How easily will AI search engines surface this firm for target niches?"). If the website block prevents scanning or fails entirely, the agent autonomously falls back to scanning their official corporate LinkedIn page to preserve the pipeline's continuity.
Core Output: Identifies the top 2 highest-leverage digital blindspots.
3. The Supervisor Orchestrator (The Evaluation Loop)
This is the brain of the project. It monitors the quality of the system and acts as an uncompromising human editor.
Process: It receives the outputs from both the Financial and Digital agents and performs a comparative cross-examination against a strict safety/quality rubric.
The Reflection Loop:
Did the Financial Agent make an inference that contradicts the hardcoded math? REJECT and send back to the Financial Agent for re-evaluation.
Is the identified niche supported by the website copy pulled by Jina AI? If not, the Orchestrator forces a prompt refinement loop until the data converges into a single, cohesive truth.
Output: A fully verified, error-free master payload JSON ready for monetization positioning.
4. The Storytelling Agent
Role: Takes the verified master JSON and converts complex advisory analytics into an emotionally compelling, high-converting copy framework.
Process: It structures the narrative using your agency’s signature conversion format:
The Hook Title: A striking header focused on their specific 5-year trend.
The Context: A breakdown showing you mapped their exact SEC data.
The Compliment: Legitimate praise on an operational metric they are winning at.
The Gap: The low-hanging fruit opportunity where they are leaking revenue.
The CTA: A seamless pitch to book a diagnostic call.
5. The Visual Web Agent & Dynamic Deployment
Role: The frontend generation layer.
Design & Branding Control: Rather than risking broken external assets, this agent applies a unified, premium agency aesthetic (utilizing your company's official logos, consistent fonts, and strict luxury wealth-management styling).
The UI Component Injector: Reads the 5-year numerical arrays from the master JSON and dynamically wires them into pre-styled Tailwind components:
Key Stat Cards: Highlighting AUM growth, client count shifts, and average account sizes.
Interactive Chart Scripts: Injecting the clean 5-year historical trend vectors directly into client-side charting libraries (like Chart.js or lightweight SVG bars) for a visually stunning impact.
Deployment: Renders and pushes the fully responsive Tailwind landing page directly to: profound.precisiongrowthpartners.io/[firmname]



Landing PAge Template v1
┌────────────────────────────────────────────────────────────────────────┐ │ [YOUR AGENCY LOGO] │ │ │ │ HYPE-PERSONALIZED HOOK TITLE │ │ "An Independent 5-Year Growth & Visibility Analysis for [Firm Name]" │ │ ─────────────────────────────────────── │ │ │ │ THE CORE INSIGHT (The Storytelling Agent's Narrative) │ │ "We mapped your historical SEC filings against the shifting local │ │ wealth landscape. Here is exactly where your firm stands..." │ │ │ │ ──────────────────────────────────────────────────────────────────── │ │ │ │ OPERATIONAL HEALTH METRICS │ │ ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────┐ │ │ │ 5-Year AUM CAGR │ │ Avg. Account Size │ │ HNW Dependency│ │ │ │ +14.2% │ │ $2.1M │ │ Low │ │ │ └───────────────────────┘ └───────────────────────┘ └───────────────┘ │ │ │ │ 5-YEAR HISTORICAL TRENDS (Programmatic Chart Script) │ │ [ Visual Line/Bar Chart showing AUM growth vs. Client Volume Mix ] │ │ │ │ ──────────────────────────────────────────────────────────────────── │ │ │ │ THE STRATEGIC OPPORTUNITY (The Low-Hanging Fruit) │ │ • Compelling compliment on what they do exceptionally well. │ │ • The primary revenue leak or digital blindspot identified. │ │ │ │ ──────────────────────────────────────────────────────────────────── │ │ │ │ CALL TO ACTION │ │ "Review Your Customized Implementation Strategy" │ │ [ INLINE CALENDLY EMBED / BOOK A CALL BUTTON ] │ └────────────────────────────────────────────────────────── 
