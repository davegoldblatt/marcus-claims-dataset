#!/usr/bin/env python3
"""Score chunk_00 claims with specificity, falsifiability, evaluation_date, status_at_eval.

Scoring rubric:
- specificity: high (names specific system/company + measurable outcome + timeframe),
                med (some specifics but vague on others),
                low (broad, sweeping, or unfalsifiable)
- falsifiability: yes (4/4: clear subject, measurable predicate, timeframe, threshold),
                  partial (2-3/4),
                  no (0-1/4)
- status_at_eval: How does this claim look as of March 2026?
  For descriptive claims about the state AT THE TIME they were written, evaluate whether
  they were accurate at that time. For predictive claims, evaluate against what has happened.
"""

import json

with open("/Users/davidgoldblatt/Desktop/marcus_scrape/pass2_chunks/chunk_00.jsonl") as f:
    claims = [json.loads(line.strip()) for line in f if line.strip()]

scores = {
    # claim_0001: "Current large AI systems like DALL-E 2, GPT-3, Flamingo, and Gato do not exhibit anything resembling human intelligence"
    # Names specific systems. As of May 2022 this was a defensible descriptive claim. By 2026, successors are far more capable but still not "human intelligence." Mixed because the original systems named don't, but the framing "anything resembling" is debatable.
    "claim_0001": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0002: "Scaling up neural networks has not yet produced systems that reliably understand the world."
    # As of 2022, broadly accurate. By 2026, LLMs show much better world understanding but still unreliable in many ways. The "yet" makes this a point-in-time claim.
    "claim_0002": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0003: "Persistent comprehension failures may indicate need for fundamental rethink"
    # "May indicate" - hedged and unfalsifiable.
    "claim_0003": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0004: "Neural networks have not demonstrated the ability to reliably create and manipulate symbols"
    # Descriptive about 2022 state. By 2026, LLMs show much more symbol manipulation ability (code, math, logic). As of 2022 it was more defensible.
    "claim_0004": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0005: "SOTA in 2022 still cannot reliably interpret symbolic spatial descriptions like 'red cube on blue cube'"
    # Specific, testable, and was accurate for 2022. DALL-E 2, Imagen had trouble with this.
    "claim_0005": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "supported"},

    # claim_0006: "Most of the world's functional software still relies on knowledge engineering"
    # Broadly true - browsers, OS, databases etc. are still rule-based. Supported.
    "claim_0006": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0007: "No current AI system can read arbitrary text and build a model of what the speaker is saying and intending."
    # By 2026, LLMs are quite good at this for many texts, though not perfectly. The claim was about 2022 when it was more true.
    "claim_0007": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0008: "Success of deep learning on specific problems does not guarantee it can solve all AI problems."
    # Logical truism, not testable.
    "claim_0008": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0009: "Fundamental failure modes of neural networks have persisted unchanged since 1988"
    # By 2026, hallucinations and compositionality issues persist but have improved significantly. The claim that they're "unchanged" is arguably contradicted.
    "claim_0009": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0010: "Very little evidence that scaling alone will achieve human-level generalization"
    # As of 2026, scaling + RLHF + chain-of-thought has produced impressive but not human-level generalization. The "alone" qualifier makes this defensible.
    "claim_0010": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0011: "Systems like Gato do not work like the brain, learn like a child, understand language, align with human values, or merit trust for mission-critical tasks"
    # Gato specifically. Most of this was accurate about Gato in 2022.
    "claim_0011": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0012: "Building AGI will require incorporating insights from human cognition"
    # Unfalsifiable until AGI is built.
    "claim_0012": {"specificity": "low", "falsifiability": "no", "status_at_eval": "pending"},

    # claim_0013: "CNET's AI-generated articles had errors in 41 of 77 articles"
    # Specific factual claim, verified at the time.
    "claim_0013": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "supported"},

    # claim_0014: "As AI improves in surface fluency, humans become worse at catching errors"
    # Automation complacency is well-documented. Supported by research.
    "claim_0014": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0015: "AI-generated misinformation will increase substantially in 2023"
    # This clearly happened - massive growth in AI-generated spam, disinfo in 2023.
    "claim_0015": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0016: "All current AI is immature, relying on it for legal or medical advice poses serious risks"
    # As of early 2023, broadly true. By 2026, AI is being used in medical and legal contexts with mixed results.
    "claim_0016": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0017: "LLMs do not represent robust world models of how events unfold over time"
    # By 2026, LLMs show some temporal reasoning but still make significant errors. The "robust" qualifier makes this defensible.
    "claim_0017": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0018: "Lack of world models is the central flaw in LLMs"
    # This is a theoretical claim about what the central flaw is. Not easily testable.
    "claim_0018": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0019: "GPT systems still do not possess genuine understanding"
    # Depends on definition of "genuine understanding" - philosophically contested.
    "claim_0019": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0020: "Neural networks have struggled with compositionality, abstraction, and silly errors since the early 1990s"
    # Historical claim, accurate.
    "claim_0020": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0021: "Adding more hidden layers did not solve fundamental problems of compositionality and abstraction"
    # By 2026, deeper networks (transformers) have significantly improved on compositionality. The claim that it didn't "solve" is technically true (not fully solved) but misleading.
    "claim_0021": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0022: "LLM hallucinations caused by inability to track instances vs kinds"
    # Causal claim about mechanism. Some evidence supports this but it's not the full picture.
    "claim_0022": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0023: "Deep learning has hit a wall on abstraction and compositionality"
    # By 2026, there's been significant progress on these. "Hit a wall" seems too strong.
    "claim_0023": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0024: "AGI cannot be achieved without solving abstraction, compositionality, and type-token distinction"
    # Can't be evaluated until AGI exists or doesn't.
    "claim_0024": {"specificity": "low", "falsifiability": "no", "status_at_eval": "pending"},

    # claim_0025: "Current AI systems are superficial and fail through accumulation of edge cases"
    # Partially true even in 2026 - edge cases still matter, but systems are far less superficial.
    "claim_0025": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0026: "LLMs are not on the path to human-level AI; they are a diversion"
    # By 2026, LLMs are clearly the dominant paradigm and have made dramatic progress. This looks wrong.
    "claim_0026": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0027: "LLMs have more superficial understanding than a house cat"
    # By 2026, this is very hard to defend. LLMs demonstrate reasoning in many domains beyond a cat.
    "claim_0027": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0028: "General public doesn't yet understand limitations of LLMs"
    # Still broadly true in 2026 - many people over-trust AI outputs.
    "claim_0028": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0029: "Bard hallucination cost Alphabet $100B in market value"
    # Specific factual claim, well-documented.
    "claim_0029": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "supported"},

    # claim_0030: "AI has long history of demos that never become solid products"
    # Historical claim, broadly accurate, though by 2026 many AI products are indeed solid.
    "claim_0030": {"specificity": "low", "falsifiability": "no", "status_at_eval": "mixed"},

    # claim_0031: "Scaling makes output sound more authoritative but not more truthful"
    # By 2026, larger models ARE more factual than smaller ones (demonstrated empirically). This was somewhat wrong.
    "claim_0031": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0032: "Hallucinations are inherent architectural byproduct of how LLMs compress inputs"
    # This is a causal claim about architecture. Hallucinations have been reduced but not eliminated. The architectural explanation is partially supported.
    "claim_0032": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0033: "Hallucination problems will eventually be solved but may require fresh discoveries and take years"
    # By 2026, hallucinations reduced but not eliminated. Still in progress. The hedging makes this hard to evaluate.
    "claim_0033": {"specificity": "low", "falsifiability": "no", "status_at_eval": "mixed"},

    # claim_0034: "If hallucination not solved soon, users may abandon chat-based search"
    # By 2026, chat-based search (Perplexity, ChatGPT, Google AI Overviews) is growing despite hallucinations.
    "claim_0034": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0035: "Neither company has subjected their chat search to full scientific review"
    # True at the time (Feb 2023).
    "claim_0035": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "supported"},

    # claim_0036: "~90% probability AI needs paradigm shift for AGI"
    # AGI hasn't arrived, so this is still pending.
    "claim_0036": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0037: "~80% probability symbol manipulation needed for AGI"
    # AGI hasn't arrived, still pending. Though current AI progress without explicit symbol manipulation is notable.
    "claim_0037": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0038-0041: Claims about what AGI will require (symbolic knowledge, cognitive models, variable operations, type/token)
    # All pending until AGI exists.
    "claim_0038": {"specificity": "low", "falsifiability": "no", "status_at_eval": "pending"},
    "claim_0039": {"specificity": "low", "falsifiability": "no", "status_at_eval": "pending"},
    "claim_0040": {"specificity": "low", "falsifiability": "no", "status_at_eval": "pending"},
    "claim_0041": {"specificity": "low", "falsifiability": "no", "status_at_eval": "pending"},

    # claim_0042: "<20% chance AGI with scaling and CNNs+RNNs+Transformers alone"
    # Still pending - no AGI yet, but remarkable progress with transformers.
    "claim_0042": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0043: "Fundamental concepts for human-level AI are still missing"
    # Even LeCun agrees with this. Broadly supported as of 2026.
    "claim_0043": {"specificity": "low", "falsifiability": "no", "status_at_eval": "mixed"},

    # claim_0044: "LLMs show improvement with scale on some measures but not others"
    # Empirically supported - BigBench and other benchmarks show uneven scaling.
    "claim_0044": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0045: "Text-to-image systems like Imagen do not understand semantic meaning of text prompts"
    # As of 2022/early 2023, this was defensible. By 2026, much better but "understand" is philosophical.
    "claim_0045": {"specificity": "high", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0046: "Imagen relies on approximate keyword matching rather than deep language understanding"
    # As a descriptive claim about Imagen specifically, this was defensible.
    "claim_0046": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0047: "No one currently knows how to build a system that derives compositional semantics from syntax"
    # By 2026, LLMs do compositional tasks much better, but whether they derive semantics "from syntax" in the linguistic sense is debatable.
    "claim_0047": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0048: "Prompt engineering insufficient for building reliable AI"
    # Broadly supported - prompt engineering alone is not the answer; it's one tool among many.
    "claim_0048": {"specificity": "low", "falsifiability": "no", "status_at_eval": "supported"},

    # claim_0049: "Text-to-image systems represent phrases as flat strings rather than hierarchical structures"
    # Technically accurate about the architecture of 2022 systems.
    "claim_0049": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0050: "LLMs merely mimic statistical patterns and provide no explanatory value"
    # "No explanatory value" is too strong - LLMs have been useful in scientific discovery. But they don't explain causally.
    "claim_0050": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0051: "Ability to predict word sequences doesn't reveal anything about human language cognition"
    # Strong claim. Some research shows LLM internal representations correlate with brain activity. "Anything" is too absolute.
    "claim_0051": {"specificity": "low", "falsifiability": "no", "status_at_eval": "contradicted"},

    # claim_0052: "LLMs approximate blank-slate learning systems"
    # Architecturally, they do start with relatively few inductive biases. Supported.
    "claim_0052": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0053: "LLM accuracy depends heavily on resemblance of test items to training data"
    # Supported by research on distribution shift and memorization.
    "claim_0053": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0054: "LLMs lack genuine abstraction, comprehension bound to training data"
    # By 2026, LLMs show significant abstraction abilities (novel problem solving, etc.) but also clear limitations.
    "claim_0054": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0055: "LLM failures argue for Kantian systems with built-in space/time/causality"
    # Philosophical/normative claim, not testable.
    "claim_0055": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0056: "Even largest neural nets with hundreds of billions of parameters top out at 80% on 3-digit math"
    # By 2026, GPT-4, Claude, etc. do 3-digit math near-perfectly. This has been clearly contradicted.
    "claim_0056": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "contradicted"},

    # claim_0057: "LaMDA and GPT-3 are not remotely intelligent"
    # Depends on definition of "intelligent." As specific systems from 2022, they were limited.
    "claim_0057": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0058: "LLMs only match patterns from statistical databases"
    # Reductive characterization. Whether what they do is "only" pattern matching is philosophically contested.
    "claim_0058": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0059: "LaMDA is not sentient"
    # Broadly supported by scientific consensus.
    "claim_0059": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0060: "LLMs like LaMDA may not play any important role in the future of AI"
    # Clearly contradicted - LLMs are THE dominant paradigm in AI by 2026.
    "claim_0060": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0061: "Passing Turing Test not equivalent to building genuinely intelligent programs"
    # Philosophical claim, widely agreed upon.
    "claim_0061": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0062: "No AI system anyone knows how to build as of 2022 is sentient"
    # Scientific consensus supports this.
    "claim_0062": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0063: "LLM outputs lack any connection to the external world"
    # By 2026, multimodal models, tool use, and grounding provide connections. "Any" is too strong.
    "claim_0063": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0064: "LLM field will hit dead end unless it integrates cognitive models and reference"
    # By 2026, LLMs haven't hit a dead end - they keep improving. But the field IS integrating more tools. Pending for the long-term prediction.
    "claim_0064": {"specificity": "low", "falsifiability": "no", "status_at_eval": "mixed"},

    # claim_0065: "LLM misinformation problems will remain unsolved without cognitive models and reference"
    # Misinformation is still a problem but has been reduced significantly through various means (RLHF, RAG, etc.)
    "claim_0065": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0066: "Current AI systems do not build or use cognitive models of the world"
    # As of 2023 when written, arguably true. By 2026, there's evidence LLMs develop internal world models.
    "claim_0066": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0067: "LLMs sidestep fundamental linguistic issues and this will prove their downfall"
    # By 2026, LLMs are more successful than ever. "Downfall" hasn't happened.
    "claim_0067": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0068: "LLMs have no grasp whatsoever on truth"
    # "No grasp whatsoever" is too absolute. LLMs are factually correct much of the time.
    "claim_0068": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0069: "Current LLM approaches are implicitly behaviorist and face same challenges"
    # Philosophical/theoretical claim, not easily testable.
    "claim_0069": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0070: "Progress requires new ML approach focused on hierarchical structure to meaning"
    # Pending - LLMs have progressed substantially without this explicit approach.
    "claim_0070": {"specificity": "low", "falsifiability": "no", "status_at_eval": "mixed"},

    # claim_0071: "Improvements from GPT-2 to GPT-3 have not remedied lack of cognitive world models"
    # As a descriptive claim about GPT-2 to GPT-3 specifically, this was defensible.
    "claim_0071": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0072: "GPT-4 will still exhibit failures in physical, temporal, causal reasoning"
    # Clearly supported - GPT-4 does have such failures, easily findable.
    "claim_0072": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "supported"},

    # claim_0073: "Transformer architecture alone cannot produce genuine model of how world works"
    # By 2026, there's evidence transformers develop internal world models, but whether they're "genuine" is debatable.
    "claim_0073": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0074: "LLMs inherently weak at understanding physical/psychological world unless hybridized"
    # By 2026, LLMs show surprisingly good physical/psychological reasoning in many cases, though imperfect.
    "claim_0074": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0075: "GPT-3 still has poor grasp of reality"
    # Descriptive claim about GPT-3 specifically. Accurate for GPT-3.
    "claim_0075": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0076: "GPT-3 is fluent but unreliable interpreter of the world"
    # Accurate for GPT-3 specifically.
    "claim_0076": {"specificity": "high", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0077: "Tesla's financial viability depends on solving FSD"
    # By 2026, Tesla's stock is driven by many factors. FSD matters but Tesla isn't "worth zero" without it.
    "claim_0077": {"specificity": "high", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0078: "Neither Tesla nor Waymo is close to fully autonomous vehicle for all conditions"
    # By 2026, Waymo operates commercial robotaxi service in multiple cities. Tesla FSD v12+ is much improved but not fully autonomous. This is largely contradicted for Waymo specifically (in its operational domains).
    "claim_0078": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0079: "Core unsolved problem for self-driving is handling outlier situations"
    # Still broadly true as of 2026, though Waymo has made significant progress through simulation and real-world data.
    "claim_0079": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0080: "Full self-driving will remain pipe dream until outlier problem solved"
    # Waymo operates commercially, suggesting it's not a "pipe dream" though it's geofenced. Mixed.
    "claim_0080": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0081: "Current L2 self-driving is nowhere close to handling real-world complexity"
    # By 2026, Tesla FSD v12+ and Waymo go well beyond L2. This was about 2022 L2 systems.
    "claim_0081": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0082: "Fully autonomous Level 5 driverless cars will not arrive any time soon"
    # By 2026, no true L5 exists. Waymo is L4 in limited domains. Supported.
    "claim_0082": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0083: "Tesla's naming misleads customers, causing accidents and deaths"
    # Well-documented by NHTSA investigations and media reports. Supported.
    "claim_0083": {"specificity": "high", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0084: "AI systems relying on statistical matching without grammar rules not close to understanding language"
    # By 2026, LLMs demonstrate surprising language understanding without explicit grammar rules.
    "claim_0084": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0085: "No convincing account of how children uniquely learn language"
    # Academic claim about state of linguistics research. Broadly accurate.
    "claim_0085": {"specificity": "low", "falsifiability": "no", "status_at_eval": "supported"},

    # claim_0086: "LLMs like GPT-3 are stochastic imitations with very little genuine coherence or comprehension"
    # GPT-3 specifically was indeed limited. Later models show much more coherence.
    "claim_0086": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0087: "All normal children acquire language; no existing machine does this"
    # By 2026, LLMs process language remarkably well, but the "going from sentences to meaning and back" in the human sense is debatable.
    "claim_0087": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0088: "LLMs will be used to mass-produce fake content for SEO manipulation"
    # Clearly happened - massive growth in AI-generated spam sites for SEO.
    "claim_0088": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0089: "AI-generated fake websites may become single biggest threat Google ever faced"
    # Google has dealt with the issue but it is indeed a major challenge. "Single biggest" is very strong.
    "claim_0089": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0090: "If AI misinformation overwhelms search, the value of search could collapse"
    # By 2026, search hasn't collapsed though AI spam is a problem. The conditional hasn't fully materialized.
    "claim_0090": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0091: "LLM unreliability becomes more dangerous when embedded in robots"
    # Reasonable concern, no major robot disasters from LLMs yet. General principle is sound.
    "claim_0091": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0092: "Embedding unreliable LLMs in robots that misunderstand instructions could cause major damage"
    # Causal prediction that hasn't materialized yet but is plausible.
    "claim_0092": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0093: "AI field has no compelling solution to alignment problems in LLMs"
    # As of early 2023, fair. By 2026, RLHF, Constitutional AI, etc. have made progress but alignment is far from solved.
    "claim_0093": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0094: "Building robots on LLMs that lack world comprehension cannot succeed"
    # By 2026, LLM-powered robots (Google RT-2, etc.) show promising results. "Cannot succeed" is too absolute.
    "claim_0094": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0095: "Vast gulf between AI demos and real-world reliable products"
    # Broadly true historically, though by 2026 many AI products are in production.
    "claim_0095": {"specificity": "low", "falsifiability": "no", "status_at_eval": "mixed"},

    # claim_0096: "More data alone unlikely to solve core problems of robotics"
    # Broadly supported - robotics progress requires more than just data.
    "claim_0096": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0097: "LLM-powered robots face same edge-case problems as self-driving cars"
    # Reasonable and supported by the state of the art.
    "claim_0097": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0098: "Reliable general-purpose household robots will not materialize in the next several years"
    # As of 2026 (written 2023), no reliable household humanoid robots exist. Supported.
    "claim_0098": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0099-0102: Claims about human innate learning mechanisms. These are claims about cognitive science, not AI predictions.
    "claim_0099": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},
    "claim_0100": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},
    "claim_0101": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "untestable"},
    "claim_0102": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0103: "Meta's Make-A-Video makes fundamental errors about physical attributes"
    # Specific and true for Make-A-Video in 2022.
    "claim_0103": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "supported"},

    # claim_0104: "AI stuck in uncanny valley, will persist for some time"
    # By 2026, AI outputs in text, image, and video have improved dramatically. "Some time" is vague. The uncanny valley for video has significantly narrowed.
    "claim_0104": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0105: "No AI system has demonstrated human-child-level compositional understanding"
    # By 2026, this is much more debatable. Modern LLMs handle many compositional tasks well.
    "claim_0105": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0106: "Current AI systems fundamentally weak at compositionality"
    # By 2026, LLMs handle compositionality much better (DALL-E 3, GPT-4, etc.).
    "claim_0106": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0107: "Every claimed solution to compositionality in neural networks has fallen apart on inspection"
    # As of 2023, there's some truth. But by 2026, systems are much more robust compositionally.
    "claim_0107": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0108: "A potential AI winter would be caused by hype exceeding reality"
    # As of 2026, no AI winter has occurred. The prediction itself is conditional.
    "claim_0108": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0109: "Compositionality is the fundamental barrier for current AI"
    # By 2026, compositionality has improved dramatically. It wasn't THE wall.
    "claim_0109": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0110: "Google likely tested Imagen on Winoground and failed and chose not to disclose"
    # Speculative, no way to verify.
    "claim_0110": {"specificity": "high", "falsifiability": "partial", "status_at_eval": "untestable"},

    # claim_0111: "Image generation systems don't understand function of objects like wheels"
    # By 2026, image gen is much better at physical understanding but still imperfect.
    "claim_0111": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0112: "Text-to-image systems have inconsistent compositional ability"
    # Accurate for 2022/2023 systems. By 2026, much improved but some inconsistency remains.
    "claim_0112": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0113: "Text-to-image may revolutionize art but doesn't represent progress toward AGI"
    # The first part is clearly true. The second is debatable - multimodal models are part of AGI progress.
    "claim_0113": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0114: "LeCun's 2022 claims mirror Marcus's 2018 arguments"
    # Priority/credit claim. Subjective and not really testable.
    "claim_0114": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "untestable"},

    # claim_0115: "Cognitive models and reasoning will not emerge from simply scaling language training corpora"
    # By 2026, scaling + RLHF + chain-of-thought HAS produced emergent reasoning. Whether this counts as "cognitive models" is debatable.
    "claim_0115": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0116: "GPT-2 lacks explicit common sense knowledge, explicit reasoning, explicit cognitive models"
    # True about GPT-2 specifically. The word "explicit" is key.
    "claim_0116": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0117: "Robotics is consistently harder than people anticipate"
    # Historical pattern, supported by evidence.
    "claim_0117": {"specificity": "low", "falsifiability": "no", "status_at_eval": "supported"},

    # claim_0118: "Self-driving car techniques may not transfer to domestic robotics"
    # Reasonable claim, supported by different requirements of home environments.
    "claim_0118": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0119: "Core challenge in robotics is real-world robustness, not demos"
    # Broadly supported by the state of the field.
    "claim_0119": {"specificity": "low", "falsifiability": "no", "status_at_eval": "supported"},

    # claim_0120: "Marcus's 2012 concerns about AI (causal reasoning, abstract understanding, etc.) still stand"
    # As of 2023, largely true. By 2026, significant progress on some fronts (reasoning, abstraction) but not fully solved.
    "claim_0120": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0121: "Neural network performance on logic benchmarks driven by statistical artifacts"
    # Research continues to show this for some benchmarks. Partially supported.
    "claim_0121": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0122: "SOTA models exploit spurious statistical patterns rather than learning meaning"
    # By 2026, models are better but shortcut learning is still documented. The absolute framing ("instead of") is too strong.
    "claim_0122": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0123: "As of 2022, AI has not achieved genuine comprehension and very few jobs replaced"
    # At the time, broadly true. By 2026, AI is replacing some jobs and comprehension has improved. As a 2022 descriptive claim, supported.
    "claim_0123": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0124: "AI augmentation fundamentally easier than full replacement"
    # Broadly supported by evidence as of 2026.
    "claim_0124": {"specificity": "low", "falsifiability": "no", "status_at_eval": "supported"},

    # claim_0125: "Humanoid domestic robots require general intelligence"
    # By 2026, no humanoid domestic robots work reliably, consistent with this claim.
    "claim_0125": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0126: "Nature paper incorrectly reported explained variance overstating GPT-2/brain link"
    # Specific technical claim about a paper. If Marcus's R-squared point is correct, this is a legitimate critique.
    "claim_0126": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "supported"},

    # claim_0127: "Tesla's Optimus demo lacked vision and strategy for cognitive AI"
    # Descriptive about the 2022 demo. Broadly agreed by observers.
    "claim_0127": {"specificity": "high", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0128: "AI requires paradigm-shift level innovation; scaling won't suffice for AGI"
    # No AGI yet, so the prediction hasn't been fully tested. But significant progress through scaling.
    "claim_0128": {"specificity": "low", "falsifiability": "no", "status_at_eval": "pending"},

    # claim_0129: "Common sense is the biggest challenge for robotics, needed for home safety"
    # Broadly supported by state of robotics as of 2026.
    "claim_0129": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0130: "Humanoid robotics poses challenges well beyond current AI capabilities"
    # Supported - no reliable humanoid robots in homes as of 2026.
    "claim_0130": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0131: "Students will use LLMs to produce convincing but false academic work"
    # Clearly happened - massive adoption of ChatGPT for academic cheating.
    "claim_0131": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0132: "LLMs mix real and fabricated information seamlessly"
    # Supported - this remains a known problem.
    "claim_0132": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0133: "Declining cost of LLM knockoffs will cause AI misinformation to rise exponentially"
    # Supported - open-source models have proliferated and AI-generated content has exploded.
    "claim_0133": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0134: "LLMs effective at generating misinformation but poor at detecting it"
    # By 2026, LLMs are actually used for content moderation and fact-checking too. The "poor at detecting" part is less true now.
    "claim_0134": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0135: "LLMs have no way of reasoning about truth, scaling won't solve this"
    # By 2026, LLMs with chain-of-thought and tool use can verify facts. "No way" is too absolute. But hallucinations persist.
    "claim_0135": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0136: "LLMs are inherently unreliable"
    # Too vague to fully test. LLMs are much more reliable by 2026 but still not 100%.
    "claim_0136": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0137: "No one knows how to reliably prevent LLMs from generating insults, bad advice, or fabrications"
    # By 2026, significant progress via RLHF, Constitutional AI, etc. but 100% prevention is still not achieved. "Reliably" and "100%" were his qualifiers.
    "claim_0137": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0138: "LLMs produce text not actions, nobody knows how to reliably translate to actions"
    # By 2026, function calling, tool use, and agent frameworks (Claude, GPT function calling, etc.) work well. This is clearly contradicted.
    "claim_0138": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0139: "LLMs may never be reliable for inferring user intent"
    # By 2026, LLMs are quite good at understanding user intent. The "may never" hedging makes it hard to fully contradict.
    "claim_0139": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0140: "Turning LLMs into reliable home-control products at scale is still far away"
    # By 2026, LLMs are integrated into smart home products but reliability varies. Limited progress.
    "claim_0140": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0141: "No evidence LLMs have self-knowledge, key component of sentience"
    # Supported by scientific consensus.
    "claim_0141": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0142: "Cicero's success relies on hand-crafted architecture, more like classical AI"
    # Accurate technical description of Cicero.
    "claim_0142": {"specificity": "high", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0143: "Cicero's techniques may have limited generalizability"
    # Cicero hasn't been adapted to many other tasks. Supported.
    "claim_0143": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0144: "Adapting Cicero to tasks beyond Diplomacy would be very difficult"
    # No major adaptations have been reported. Supported.
    "claim_0144": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0145: "ML most valuable when embedded in structured systems with neurosymbolic components"
    # By 2026, the trend is toward LLMs + tools/RAG, which partially aligns but isn't exactly "neurosymbolic."
    "claim_0145": {"specificity": "low", "falsifiability": "no", "status_at_eval": "mixed"},

    # claim_0146: "Cicero uses far more innate structure than typical recent AI systems"
    # Accurate description.
    "claim_0146": {"specificity": "high", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0147: "May not be enough data for scaling maximalism to work"
    # By 2026, synthetic data and improved data efficiency partially address this. The concern was prescient but not yet proven.
    "claim_0147": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0148: "May not be enough compute for scaling maximalism"
    # By 2026, massive investment in AI compute (H100s, custom chips). Not a binding constraint yet.
    "claim_0148": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0149: "Some important AI tasks may not improve with scale"
    # Some evidence supports this (certain reasoning tasks plateau) but many tasks do improve.
    "claim_0149": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0150: "If scaling plateaus at 80% on important tasks, scaling maximalism fails"
    # Conditional claim. Some tasks have broken past thresholds, others haven't.
    "claim_0150": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0151: "Scaling maximalism will not get us to AGI"
    # No AGI yet, so pending. But progress through scaling has been remarkable.
    "claim_0151": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0152: "Like Moore's Law, scaling laws are empirical not causal, won't reach AGI"
    # Pending - no AGI, but the analogy to Moore's Law is interesting.
    "claim_0152": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0153: "AI field over-investing in scaling at expense of other approaches"
    # Normative claim - can't be tested.
    "claim_0153": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0154: "ChatGPT is unreliable, makes reasoning/fact errors, hallucinates"
    # Supported - ChatGPT (GPT-3.5) does have these issues.
    "claim_0154": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0155: "LLMs can be automated to generate misinformation at unprecedented scale"
    # Clearly supported.
    "claim_0155": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0156: "Cost of generating AI-powered disinformation approaching zero"
    # Supported - open-source models make it essentially free.
    "claim_0156": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0157: "Nation-states will use LLMs for propaganda at unprecedented volume"
    # Supported by reports of Russian, Chinese, Iranian use of AI for propaganda.
    "claim_0157": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0158-0160: Normative/policy claims
    "claim_0158": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},
    "claim_0159": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},
    "claim_0160": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0161: "Countering AI misinformation will require new kind of AI, LLMs poor at detecting it"
    # By 2026, LLMs are actually used for detection. The claim that a "new kind" is needed hasn't been validated.
    "claim_0161": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0162: "LLMs lack truth verification mechanisms, need integration with classical AI tools"
    # Normative/prescriptive claim. RAG and tool use DO integrate these, somewhat validating the prescription.
    "claim_0162": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0163: "Broad cross-section of AI leaders in 2022 agreed current AI not close to AGI"
    # Descriptive about a specific event. Accurate.
    "claim_0163": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0164: "ChatGPT is unreliable, doesn't understand physical/psychological world, hallucinates"
    # For ChatGPT (GPT-3.5), these are documented issues. Supported.
    "claim_0164": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0165: "LLM-based search engines fundamentally flawed because they fabricate information"
    # By 2026, LLM search (Perplexity, Google AI) is widely used despite hallucination risks. "Fundamentally flawed" is too strong.
    "claim_0165": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0166: "LLMs are text predictors that combine information fragments, not databases"
    # Technically accurate description of the mechanism.
    "claim_0166": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0167: "LLMs extremely difficult to update, requiring full retraining taking weeks/months"
    # By 2026, fine-tuning, RAG, and in-context learning provide faster updates. Full retraining isn't always needed.
    "claim_0167": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0168: "LLM-powered search will face long, difficult transition from demo to reliable product"
    # By 2026, LLM search products are widely deployed (Perplexity, Google AI Overviews). The transition was faster than suggested.
    "claim_0168": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0169: "LLM-powered search mixes true and false info authoritatively"
    # Still a documented concern. Supported.
    "claim_0169": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0170: "ChatGPT is far from AGI, less optimistic assessment is more accurate"
    # ChatGPT (GPT-3.5) was indeed far from AGI. Supported.
    "claim_0170": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0171: "LLMs becoming commodities with no unique protectable IP"
    # By 2026, there IS significant differentiation (GPT-4, Claude, Gemini differ meaningfully). But open-source models are commoditizing the lower end.
    "claim_0171": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0172: "OpenAI leadership's financial behavior inconsistent with genuine belief they're close to AGI"
    # Interpretive claim about motivations. Can't be objectively verified.
    "claim_0172": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "untestable"},

    # claim_0173: "ChatGPT is easily confused despite broad capabilities"
    # For ChatGPT (GPT-3.5), yes. Supported.
    "claim_0173": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0174: "GPT-4 will still lack ability to construct internal world models"
    # Research suggests GPT-4 does develop some internal representations that function like world models (Othello, spatial reasoning). Mixed.
    "claim_0174": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0175: "GPT-4 will be reckless and hard to control"
    # GPT-4 is significantly more controllable than GPT-3 via RLHF. "Reckless" overstates it.
    "claim_0175": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0176: "GPT-4 will still make obviously stupid errors"
    # Yes, GPT-4 does make surprising errors. Supported.
    "claim_0176": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0177: "GPT-4's reasoning about physical, psychological, and mathematical world will still be unreliable"
    # GPT-4 is much better at math and reasoning but still makes errors. "Unreliable" depends on threshold.
    "claim_0177": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0178: "GPT-4 will not be trustworthy enough for reliable medical advice"
    # GPT-4 passed USMLE but still makes medical errors. Not fully trustworthy for independent medical advice. Mixed but leaning supported.
    "claim_0178": {"specificity": "high", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0179: "GPT-4 will still produce fluent hallucinations, escalating misinformation risk"
    # GPT-4 does hallucinate, though less than GPT-3.5. Supported.
    "claim_0179": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0180: "GPT-4's output won't be reliably usable as input for downstream programs"
    # By 2026, function calling and structured outputs in GPT-4 work well. Contradicted.
    "claim_0180": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0181: "GPT-4 will not be a general-purpose AGI"
    # Correct - GPT-4 is not AGI. Supported.
    "claim_0181": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "supported"},

    # claim_0182: "Alignment will remain critical unsolved problem with GPT-4"
    # Alignment remains a major challenge. Supported.
    "claim_0182": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0183: "Scaling LLMs useful but insufficient for AGI"
    # No AGI yet, but scaling has been remarkably productive. Pending on the AGI part.
    "claim_0183": {"specificity": "low", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0184: "Trustworthy AGI will require structured systems with built-in knowledge and explicit reasoning"
    # Pending until AGI exists.
    "claim_0184": {"specificity": "low", "falsifiability": "no", "status_at_eval": "pending"},

    # claim_0185: "Within a decade, AI focus will shift from pure scaling to integrating LLMs with other techniques"
    # Already happening by 2025-2026: RAG, tool use, agents, multi-modal, chain-of-thought. Supported.
    "claim_0185": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0186: "By 2043, historians will conclude overemphasis on LLMs and shift to more structured systems"
    # Far future, pending.
    "claim_0186": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0187-0189: Normative claims about what "real AI" would be like.
    "claim_0187": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},
    "claim_0188": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},
    "claim_0189": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0190: "Need for human labor to filter AI outputs is consequence of shallow data-driven approaches"
    # RLHF still requires human feedback. But the causal explanation is debatable.
    "claim_0190": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0191: "First death attributable to LLMs will occur in 2023"
    # No confirmed death directly attributable to LLMs in 2023. There was a Belgian case linked to chatbot interaction but attribution is disputed. Likely contradicted.
    "claim_0191": {"specificity": "high", "falsifiability": "yes", "status_at_eval": "mixed"},

    # claim_0192: "AGI will be achieved, possibly before end of this century"
    # Long-term, pending.
    "claim_0192": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "pending"},

    # claim_0193: "LLMs not remotely close to AGI, missing semantics, reasoning, common sense, theory of mind"
    # By 2026, LLMs show improvements in reasoning, some theory of mind. "Not remotely close" may be too strong. But AGI hasn't been achieved.
    "claim_0193": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0194: "Current AI funding wasted on approaches probably not on right path to AGI"
    # Normative claim.
    "claim_0194": {"specificity": "low", "falsifiability": "no", "status_at_eval": "untestable"},

    # claim_0195: "Main remaining barrier to AGI is software architecture, not data or compute"
    # By 2026, many would disagree - compute and data remain significant factors. But algorithm/architecture matters too.
    "claim_0195": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0196: "Most AI investment goes to LLMs, which are approximation to intelligence, frustrating distraction"
    # The factual part (most investment goes to LLMs) is true. The evaluative part is normative.
    "claim_0196": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "mixed"},

    # claim_0197: "Within 5 years, substantial AI research will shift from pure LLM approaches"
    # Written Feb 2023. By March 2026, there IS significant work on agents, tool use, multimodal, reasoning beyond pure LLMs. But LLMs remain central. The deadline (Feb 2028) hasn't passed. Already showing signs of being supported.
    "claim_0197": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},

    # claim_0198: "Achieving AGI will require integrating deep learning with explicit knowledge and cognitive models"
    # Pending until AGI exists. Though the trend toward tool use and RAG partially supports the integration thesis.
    "claim_0198": {"specificity": "low", "falsifiability": "no", "status_at_eval": "pending"},

    # claim_0199: "Current AI can't even check output against Wikipedia"
    # By 2026, RAG systems routinely check against external sources including Wikipedia. Clearly contradicted.
    "claim_0199": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "contradicted"},

    # claim_0200: "ChatGPT is far inferior intelligence that cannot be trusted"
    # ChatGPT (GPT-3.5 era) had significant limitations. Supported as a description of that system.
    "claim_0200": {"specificity": "med", "falsifiability": "partial", "status_at_eval": "supported"},
}

# Verify all claims scored
assert len(scores) == 200, f"Expected 200 scores, got {len(scores)}"

# Merge and write
with open("/Users/davidgoldblatt/Desktop/marcus_scrape/pass2_chunks/chunk_00_scored.jsonl", "w") as f:
    for claim in claims:
        cid = claim["id"]
        s = scores[cid]
        claim["specificity"] = s["specificity"]
        claim["falsifiability"] = s["falsifiability"]
        claim["evaluation_date"] = "2026-03-02"
        claim["status_at_eval"] = s["status_at_eval"]
        f.write(json.dumps(claim, ensure_ascii=False) + "\n")

print(f"Wrote {len(claims)} scored claims to chunk_00_scored.jsonl")

# Summary stats
from collections import Counter
spec_counts = Counter(s["specificity"] for s in scores.values())
fals_counts = Counter(s["falsifiability"] for s in scores.values())
stat_counts = Counter(s["status_at_eval"] for s in scores.values())
print(f"\nSpecificity: {dict(spec_counts)}")
print(f"Falsifiability: {dict(fals_counts)}")
print(f"Status: {dict(stat_counts)}")
