<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./.github/assets/hero-dark.svg">
  <img alt="Devanshu Chicholikar. AI engineer and forward deployed engineer in Boston who ships AI to production: MCP, RAG, evals, voice agents. Open to AI Engineer and FDE roles." src="./.github/assets/hero-light.svg" width="100%">
</picture>

I'm an AI engineer in Boston. I ship AI systems to production end to end: MCP servers, RAG with retrieval evals, LLM-as-a-judge eval harnesses and voice agents, plus the full-stack, infra and design work around them. MS in Software Engineering Systems, Northeastern University (2026). Open to AI Engineer and Forward Deployed Engineer roles anywhere in the US.

<p><samp><a href="https://www.devanshuchicholikar.com">portfolio</a> · <a href="https://opencodeintel.com">opencodeintel.com</a> · <a href="https://www.linkedin.com/in/devanshuchicholikar">linkedin</a> · <a href="mailto:chicholikar.d@northeastern.edu">email</a></samp></p>

### Selected work

<p>
<a href="https://github.com/OpenCodeIntel/opencodeintel"><picture><source media="(prefers-color-scheme: dark)" srcset="./.github/assets/card-opencodeintel-dark.svg"><img alt="OpenCodeIntel: Code search for AI coding agents. A web app, a REST API and a 12-tool MCP server. Pipeline: repo to tree-sitter to BM25 + vectors to RRF + rerank to MCP. 94% Hit@1, research eval; 242ms p50 cached, production." src="./.github/assets/card-opencodeintel-light.svg" width="49%"></picture></a>
<a href="https://github.com/DevanshuNEU/overhear"><picture><source media="(prefers-color-scheme: dark)" srcset="./.github/assets/card-overhear-dark.svg"><img alt="Overhear: A QA analyst for voice agents. Grades every call against the clinic&#x27;s real database. Pipeline: call to Retell agent to tool log to code + judge to score. 23/23 planted failures caught; 0.89 macro-F1, 39-call set." src="./.github/assets/card-overhear-light.svg" width="49%"></picture></a>
</p>

<p>
<a href="https://github.com/DevanshuNEU/callbudget"><picture><source media="(prefers-color-scheme: dark)" srcset="./.github/assets/card-callbudget-dark.svg"><img alt="CallBudget: Finds a hard-to-find drug in fewer calls. Predicts stock, calls the likeliest first. Pipeline: drug + area to ranker to call plan to voice agent to learn. 4.3 → 2.3 expected calls to find it; 10% → 0% false &quot;in stock&quot; answers." src="./.github/assets/card-callbudget-light.svg" width="49%"></picture></a>
<a href="https://github.com/OpenCodeIntel/lco"><picture><source media="(prefers-color-scheme: dark)" srcset="./.github/assets/card-saar-dark.svg"><img alt="Saar: A Claude.ai token and cost meter that runs entirely in the browser. On the Chrome Web Store. Pipeline: claude.ai to SSE intercept to tokenizer to overlay. 1,808 Vitest tests, 63 files; No backend data stays in browser." src="./.github/assets/card-saar-light.svg" width="49%"></picture></a>
</p>

<p>
<a href="https://github.com/DevanshuNEU/web-v2"><picture><source media="(prefers-color-scheme: dark)" srcset="./.github/assets/card-portfolio-os-dark.svg"><img alt="Portfolio OS: A desktop operating system in a browser tab. Window manager, terminal and dock, from scratch. Pipeline: Next.js 15 to Zustand to window manager to apps. Next.js 15 TypeScript, Zustand; Live devanshuchicholikar.com." src="./.github/assets/card-portfolio-os-light.svg" width="49%"></picture></a>
<a href="https://github.com/OpenCodeIntel/saar"><picture><source media="(prefers-color-scheme: dark)" srcset="./.github/assets/card-saar-cli-dark.svg"><img alt="saar CLI: Reads a codebase and writes the files coding agents need: AGENTS.md, CLAUDE.md, .cursorrules. Pipeline: repo to static analysis to patterns to AGENTS.md. 22 releases on PyPI; 3 agent context formats." src="./.github/assets/card-saar-cli-light.svg" width="49%"></picture></a>
</p>

| Project | What it is | Links |
|---|---|---|
| **OpenCodeIntel** | Code-search platform for AI coding agents: hybrid BM25 + vector retrieval, cross-encoder reranking, tree-sitter AST chunking, a 12-tool MCP server | [opencodeintel.com](https://opencodeintel.com) · [source](https://github.com/OpenCodeIntel/opencodeintel) |
| **Overhear** | QA analyst for voice agents: code checks the facts against the clinic database, an LLM-as-a-judge scores tone and safety, evaluated on a 39-call golden dataset | [source](https://github.com/DevanshuNEU/overhear) |
| **CallBudget** | Active-sensing pharmacy search: a learned ranker plans calls, a voice agent places them, calibrated abstention keeps false "in stock" answers at 0% | [walkthrough](https://www.loom.com/share/0231954a438c4b3ab011fd21f4f41bf2) · [source](https://github.com/DevanshuNEU/callbudget) |
| **Saar** | Chrome extension that meters Claude.ai tokens and cost in real time, fully client-side | [getsaar.com](https://getsaar.com) · [source](https://github.com/OpenCodeIntel/lco) |
| **Portfolio OS** | A desktop operating system in a browser tab: window manager, terminal, dock | [live](https://www.devanshuchicholikar.com) · [source](https://github.com/DevanshuNEU/web-v2) |
| **saar CLI** | Static analysis that writes AGENTS.md, CLAUDE.md and .cursorrules for a codebase | [PyPI](https://pypi.org/project/saar/) · [source](https://github.com/OpenCodeIntel/saar) |

### OpenCodeIntel, up close

<img src="./.github/assets/oci-demo.gif" alt="Demo: searching the Flask codebase on opencodeintel.com for 'handle an http exception with a registered error handler'. The top result is handle_http_exception at a 70 percent match, followed by errorhandler and handle_exception." width="100%">

- **94% Hit@1** across 14 open-source codebases on a 665-query research eval, with the reranker's +8.4 points isolated by a 98-run ablation.
- **p50 641ms** for a cold search (embedding, hybrid retrieval and reranking) and **242ms** for cached repeats, measured on production.
- **12 MCP tools** over stdio for local agents and streamable HTTP for hosted Claude.ai connectors.
- One result that went against me: rerankers trained on web text made code search worse. It stays in the research log.

<details>
<summary><b>Architecture</b></summary>
<br>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./.github/assets/oci-architecture-dark.svg">
  <img alt="OpenCodeIntel architecture: web app, REST API and MCP server clients; query path embed, BM25 plus vectors, RRF fusion, Cohere rerank; index path tree-sitter chunks, embeddings, Pinecone and BM25; state in Supabase Postgres and Redis." src="./.github/assets/oci-architecture-light.svg" width="100%">
</picture>
</details>

### Latest

<!-- AUTO:START -->
**2026-10-10** · Portfolio OS · structured data: a walkthrough video goes in subjectOf, not sameAs
<!-- AUTO:END -->

### Experience

- **Graduate Teaching Assistant**, Northeastern University · Sep 2025 to May 2026<br><sub>CSYE 6225 Network Structures and Cloud Computing under Prof. Tejas Parikh: cloud best practices on AWS for 100+ graduate students across two semesters</sub>
- **Software Engineer**, Jaksh Enterprise · Aug 2022 to Jul 2024 · full-time<br><sub>Java / Spring Boot quotation engine for 590+ products; quote-page p95 latency cut 65%</sub>
- **Software Development Engineer Intern**, Pitney Bowes · Jan 2022 to Jul 2022<br><sub>REST APIs and Angular workflows for PitneyShipPro</sub>

Authorized to work in the US (F-1 OPT, STEM-eligible).

### More

[financial-copilot](https://github.com/DevanshuNEU/financial-copilot), an AI expense tracker on React and Supabase Edge Functions · [mem-machines](https://github.com/DevanshuNEU/mem-machines), serverless ingestion on GCP Cloud Run and Pub/Sub · [tool-crowding](https://github.com/DevanshuNEU/tool-crowding), an MCP tool-selection benchmark harness · earlier work, 2020 to 2024, at [github.com/Devanshuc](https://github.com/Devanshuc)

<details>
<summary><b>Why I'm all-in on AI</b></summary>

<br/>

I have been writing code since I was a teenager. The last two years changed what that means. AI tools went from gimmick to "actually helps me ship," and the gap between people who ship with AI and people who do not grew faster than anything I have seen in software.

So I went all in. I read the papers. I read the code. I built a product (OpenCodeIntel) on the bet that AI coding tools need a context layer they do not have yet. I am finding out if I am right.

The next decade of software is going to be written by people who treat AI like infrastructure, not a feature. I want to be one of them. And I want to do it on a team that is already there.

Either we ship something that matters, or we learn fast and try again.

</details>

<sub>ship fast. learn faster. craft over titles. help over hype.</sub>
