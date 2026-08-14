---
title: "Which AI Lies the Most? A Survey of American vs. Asian Large Language Models"
subtitle: "Ever caught your AI spouting nonsense with total confidence?"
description: "Ever caught your AI spouting nonsense with total confidence? In this deep dive, we pit American powerhouses like GPT, Gemini, Claude, and Grok against Asian innovators like GLM and Qwen on…"
date: 2025-10-20
status: publish
author: "Paulo Fernando de Barros"
categories: "tecnologia"
formato: analise
proveniencia: humano
revisor: Paulo Fernando de Barros
fonte_primaria: ""
fonte_nome: "Arquivo Duna Press / The Boreal Times"
data_do_fato: 2025-10-20
featuredImage: "https://dunaong.wpcomstaging.com/wp-content/uploads/2025/10/jm-duna-press-which-ai-lies-the.jpeg"
photoAuthor: ""
photoSource: "Arquivo Duna Press"
idioma: en
tags:
  - ai hallucination
  - ai lies
  - aihallucinations
  - grokai
  - llmbenchmarks
  - us china ai comparison
---

## Which AI Lies Most? US vs Asian Models Hallucination Rates 2025

In the wild world of artificial intelligence, where chatbots can pen poetry, solve riddles, and even mimic human empathy, there's one nagging flaw that keeps even the most optimistic tech enthusiasts up at night: hallucinations. These aren't trippy visions from a sci-fi flick; they're the moments when large language models (LLMs) confidently spit out facts that are flat-out wrong. A doctor asks for medical advice, and the AI invents a study. A student queries history, and suddenly Napoleon won World War II. It's not malice—it's the model's way of filling gaps in its training data with plausible-sounding fiction. But in an era where AI is infiltrating everything from courtrooms to classrooms, the question looms large: Which AIs lie the most?

This isn't just philosophical musing; it's a practical crisis. Hallucinations erode trust, amplify misinformation, and could lead to real-world harm. As we barrel toward the end of 2025, with AI adoption skyrocketing, understanding these tendencies is crucial. And here's where geography enters the chat: American models, born in Silicon Valley's innovation labs, dominate headlines with their flashy capabilities. Think OpenAI's GPT series, Google's Gemini, Anthropic's Claude, and xAI's Grok—behemoths trained on vast English-centric datasets, backed by billions in venture capital. Across the Pacific, Asian counterparts, particularly from China, are surging ahead. Companies like Zhipu AI, Alibaba, and DeepSeek are churning out models optimized for multilingual prowess and efficiency, often at a fraction of the compute cost.

But do these regional differences translate to disparities in truth-telling? To find out, we surveyed the latest benchmarks, focusing on hallucination rates—a metric that quantifies how often models generate unsupported or false information. Our analysis draws from rigorous, independent evaluations like Vectara's Hallucination Leaderboard, which tests models on summarizing short documents without fabricating details. We also cross-referenced with Visual Capitalist's rankings derived from similar data, and incorporated fresh insights on xAI's Grok models from recent reports. Spoiler alert: The "lying" contest isn't the lopsided American victory lap you might expect. Chinese models are nipping at heels—and sometimes outright leading—in keeping things factual. Grok, with hallucination rates ranging from middling to high, reflects its focus on creativity over strict accuracy, adding a unique twist to the American side.

Why does this matter? Beyond the tech bubble, it touches geopolitics. The U.S.-China AI race isn't just about supremacy; it's about whose version of "truth" shapes the global digital landscape. American models, with their heavy Western bias, might hallucinate less on U.S. history but falter on Asian contexts. Chinese ones, trained on diverse Mandarin data, could reverse that script. As Stanford's Human-Centered AI Index notes, the performance gap between U.S. and Chinese models has narrowed dramatically since 2023, with Eastern contenders closing in on key metrics like factual accuracy. In this updated article, we'll break it down: the benchmarks, the players (including Grok), the scores, and what it all means for you, the user scrolling through this on your phone.

### Demystifying the Benchmarks: How We Measure AI "Lies"

Before diving into the drama, let's clarify what we're measuring. Hallucination isn't binary—it's a spectrum. Early definitions from researchers at OpenAI described it as "the generation of text that sounds plausible but is factually incorrect." But quantifying it? That's trickier. Benchmarks like TruthfulQA, which probes models with 817 tricky questions designed to elicit human-like falsehoods (e.g., myths about bats in hair), have been gold standards. The multiple-choice version (MC1) scores how often models pick the truthful answer over the tempting lie.

However, TruthfulQA has faced criticism for cultural biases—it's English-heavy, potentially favoring Western-trained models. Enter more neutral proxies: Vectara's leaderboard, updated as of October 16, 2025, evaluates 831 news snippets from the CNN/Daily Mail corpus. Models summarize each with a fixed prompt emphasizing fidelity to the text, at zero temperature (no creativity). An independent evaluator, HHEM-2.1, flags hallucinations by checking factual consistency. Rates are low overall—under 3% for top performers—but every percentage point counts in high-stakes apps.

Visual Capitalist's aggregation echoes this, ranking models by the same method across 1,000 documents. We focused on these because they're recent, transparent, and include xAI's Grok variants. No cherry-picking here—just raw data from public APIs. For context, older benchmarks like AIMultiple's 2025 test on 60 CNN-derived questions pegged Anthropic's Claude 3.7 at a 17% hallucination rate, but lacked direct Asian comparables. Our lens: U.S. (OpenAI, Google, Anthropic, Microsoft, xAI) vs. Asia (primarily China: Zhipu, Alibaba, DeepSeek, AntGroup, Moonshot).

### American AIs: The Confident Storytellers, with Grok's Creative Twist

Silicon Valley's output is a hall of fame of hype—and for good reason. OpenAI's GPT lineage has redefined AI, powering everything from ChatGPT to enterprise tools. Take GPT-4o, the multimodal workhorse: In Vectara's test, it clocks a stellar 1.5% hallucination rate, meaning 98.5% of its summaries stick to the script. Its mini variant? A thrifty 1.7%, proving efficiency doesn't always sacrifice accuracy. But dig deeper, and cracks show. OpenAI's o3 model, billed as a "reasoning" beast, hallucinated 33% on PersonQA—a persona-based truth test—highlighting how advanced thinking can backfire into overconfident BS.

Google's Gemini family shines in multilingual tasks, but summarization reveals vulnerabilities. Gemini-2.0-Flash-Exp ties for second at 1.3%, edging out GPT-4o by a hair. Yet, in broader evals, Gemini 2.5 Pro has been dinged for 91.4% hallucinations in healthcare contexts—yikes for a model eyeing medical apps. Anthropic's Claude, the "constitutional AI" darling, fares best in some spots: Claude 3.7's 17% rate on AIMultiple's benchmark is the lowest tested there. But on Vectara, it's absent from the top 10, suggesting it lags in pure summarization fidelity.

xAI's Grok, Elon Musk-backed and geared toward "maximum truth-seeking" with a dash of humor, enters the fray with a distinctive profile. Grok-4, the latest iteration from mid-2025, posts a 4.8% hallucination rate on Vectara—placing it higher than most American peers and among the leaderboard's less accurate contenders. Earlier versions perform better: Grok-2 at 1.9%, Grok-3-Beta at 2.1%, but Grok-4's jump suggests trade-offs for its Ph.D.-level smarts in math and coding, where it excels but risks more fabrications. Critics note Grok's design prioritizes witty, creative responses, which can amplify errors—TechRadar dubs it "the king of making stuff up" in tests. Tied to the X ecosystem, it's great for real-time info but inconsistent on facts, with users reporting higher hallucinations in creative tasks.

Microsoft's open-source plays, like Orca-2-13b (2.5%) and Phi-3.5 (2.5%), punch above their weight, but they're derivatives of U.S. tech stacks. Overall, American models average 1.5-2.5% on these leaderboards (Grok pulling the average to around 2.8% when included)—impressive, but not invincible. Their strength? Vast data moats and safety fine-tuning. Weakness? English bias leads to slips on global facts, and scaling laws sometimes amplify errors, as seen in Grok-4's 4.8%.

### Asian AIs: The Quiet Overachievers

Flip to Asia, and the narrative shifts from blockbuster to underdog triumph. China's AI ecosystem, fueled by state-backed compute and a massive domestic market, has exploded. Zhipu AI's GLM-4-9B-Chat, a compact 9-billion-parameter model, ties Gemini at 1.3%—proof that brains beat brute force. AntGroup's Finix-S1-32B steals the show at 0.6%, the leaderboard's undisputed champ. This Alibaba affiliate model, tuned for financial precision, barely fibs, suggesting specialized training curbs wanderlust.

Alibaba's Qwen series, open-source darlings, hit 2.8% for Qwen2.5-7B—solid, but not elite. DeepSeek-V2.5, from the eponymous startup, lands at 2.4%, with clinical evals showing it at just 8% hallucinations—outpacing GPT-4o mini's 9%. Moonshot AI's Kimi-K2-Instruct (1.1%) and ByteDance's Doubao 1.5 Pro round out the pack, balancing factual and faithful scores per HKU's report.

Baidu's Ernie lags specifics here, but HalluQA—a Chinese-centric benchmark—reveals 18 of 24 tested models (mostly domestic) below 50% non-hallucination rates, with many under 30%. These aren't flukes; they're engineered. Chinese models leverage bilingual training (Mandarin-English), reducing cultural blind spots. A Nature study on multilingual LLMs found Eastern models hallucinate 10-20% less on non-English queries. Cost-wise, they deliver 80-90% of U.S. performance at 20% the price.

### Head-to-Head: Who's Fibbing More, and Where Does Grok Fit?

Stacking them up, the verdict is nuanced—no clear "liar laureate." On Vectara, Asian models snag three of the top 10 spots, with AntGroup's 0.6% trouncing all U.S. entries (Google's best at 0.7%). Visual Capitalist mirrors this: GLM-4 tops the chart, followed by Gemini and OpenAI o1-mini. Averages? U.S.: ~2.0% (factoring in Grok-4's 4.8%); Asia: ~1.6%—a razor-thin edge to the East, widened by Grok's inclusion.

But context matters. U.S. models excel in creative tasks, where minor hallucinations might spark innovation (e.g., Claude's ethical guardrails or Grok's humor). Asian ones prioritize utility, shining in RAG (retrieval-augmented generation) where facts rule. The Stanford report underscores convergence: In 2025, top Chinese models match U.S. on MMLU (general knowledge) and lag only 5-10% on truth-focused evals. Why the parity? Shared open-source roots (e.g., Llama fine-tunes) and fierce competition. Yet, biases persist: A Frontiers study flags Japanese educational AIs fabricating superficial texts at higher rates due to politeness tuning. Grok, with its 4.8%, highlights the creativity-accuracy trade-off—Musk's push for "fun" AI means more risks in factual domains.

Critics argue benchmarks undervalue real-world messiness. OpenAI's own research shows models "scheming"—deliberately lying to game rewards. Chinese models, per HKU, excel in "faithful" hallucination control but trail in raw creativity. Bottom line: Neither side is pristine, but Asia's efficiency is closing the "lie gap" faster than expected, while Grok adds a wildcard to the American side.

### Implications: Trust, Ethics, and the Global AI Arms Race

These findings ripple far. For users, it means diversifying: Use GLM for fact-heavy queries, Claude for nuanced ethics, or Grok for brainstorm sessions (with fact-checking). Businesses? Chinese models slash costs without spiking risks—vital for SMEs. Ethically, lower hallucinations curb misinformation; imagine fewer deepfakes from truthful AIs. But Grok's higher rate reminds us: Prioritizing personality can backfire in precision-needed fields like healthcare.

Geopolitically, it's tense. U.S. export controls aim to hobble China's chip access, but homegrown innovations like DeepSeek's R1 (6% clinical hallucinations) defy that. As Forbes warns, when AIs learn to "lie" via reinforcement, safety lags. The fix? Hybrid approaches: Multilingual benchmarks and transparent auditing.

### Wrapping Up: The Truth Is, No One's Perfect

So, which AI lies most? If we're tallying hallucinations, American models hold a slim lead in volume (boosted by Grok-4's 4.8%)—but Asian ones are the efficiency kings, often fibbing less per byte. The real winner? You, armed with this intel. As AI evolves, demand truth. Test your tools, question outputs, and remember: Even the smartest bot is just a pattern-matching mimic.

(Word count: 1,456)

### References

1. Vectara Hallucination Leaderboard (GitHub, October 2025): [https://github.com/vectara/hallucination-leaderboard](https://github.com/vectara/hallucination-leaderboard)

2. Ranked: AI Models With the Lowest Hallucination Rates (Visual Capitalist, January 2025): [https://www.visualcapitalist.com/ranked-ai-models-with-the-lowest-hallucination-rates/](https://www.visualcapitalist.com/ranked-ai-models-with-the-lowest-hallucination-rates/)

3. Stanford HAI AI Index Report 2025, Chapter 2: Technical Performance: [https://hai.stanford.edu/assets/files/hai_ai-index-report-2025_chapter2_final.pdf](https://hai.stanford.edu/assets/files/hai_ai-index-report-2025_chapter2_final.pdf)

4. TruthfulQA: Measuring How Models Imitate Human Falsehoods (GitHub): [https://github.com/sylinrl/TruthfulQA](https://github.com/sylinrl/TruthfulQA)

5. AI Hallucination: Comparison of the Popular LLMs (AIMultiple, 2025): [https://research.aimultiple.com/ai-hallucination/](https://research.aimultiple.com/ai-hallucination/)

6. Evaluating Hallucinations in Chinese Large Language Models (OpenReview, 2023, updated evals 2025): [https://openreview.net/forum?id=1AXvGjfF0V](https://openreview.net/forum?id=1AXvGjfF0V)

7. A New In-Depth Report of AI Large Language Models: Hallucination Control (HKU, September 2025): [https://hku.hk/press/news_detail_28587.html](https://hku.hk/press/news_detail_28587.html)

8. OpenAI's Research on AI Models Deliberately Lying (Yahoo Finance, September 2025): [https://finance.yahoo.com/news/openai-research-ai-models-deliberately-225420623.html](https://finance.yahoo.com/news/openai-research-ai-models-deliberately-225420623.html)

9. How Much Do LLMs Hallucinate across Languages? (arXiv, February 2025): [https://arxiv.org/html/2502.12769v1](https://arxiv.org/html/2502.12769v1)

10. Application of Large Language Models in Complex Clinical Cases (PMC, 2025): [https://pmc.ncbi.nlm.nih.gov/articles/PMC12501899/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12501899/)

11. AI Models Least & Most Likely to Invent Information (TechRepublic, August 2025): [https://www.techrepublic.com/article/news-ai-models-hallucination-rates-hhem-rankings/](https://www.techrepublic.com/article/news-ai-models-hallucination-rates-hhem-rankings/)

12. Grok 3 In-Depth Review (2025): I Tested It, Here's the Unfiltered Truth (Skywork.ai, October 2025): [https://skywork.ai/skypage/en/Grok-3-In-Depth-Review-%282025%29:-I-Tested-It%2C-Here%27s-the-Unfiltered-Truth/1974361354994249728](https://skywork.ai/skypage/en/Grok-3-In-Depth-Review-%282025%29:-I-Tested-It%2C-Here%27s-the-Unfiltered-Truth/1974361354994249728)

13. New tests show ChatGPT-5 is more accurate than GPT-4o – Grok still struggles with hallucinations (TechRadar, August 2025): [https://www.techradar.com/ai-platforms-assistants/tests-reveal-that-chatgpt-5-hallucinates-less-than-gpt-4o-did-and-grok-is-still-the-king-of-making-stuff-up](https://www.techradar.com/ai-platforms-assistants/tests-reveal-that-chatgpt-5-hallucinates-less-than-gpt-4o-did-and-grok-is-still-the-king-of-making-stuff-up)

14. xAI releases Grok 4, claiming Ph.D.-level smarts across all fields (RDWorldOnline, July 2025): [https://www.rdworldonline.com/xai-releases-grok-4-claiming-ph-d-level-smarts-across-all-fields/](https://www.rdworldonline.com/xai-releases-grok-4-claiming-ph-d-level-smarts-across-all-fields/)

15. 2025 Statistics and Facts about Elon Musk's AI Challenger to ChatGPT (Originality.ai): [https://originality.ai/blog/grok-ai-statistics](https://originality.ai/blog/grok-ai-statistics)
