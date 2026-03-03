import json
import re
from collections import defaultdict

# Load all claims
claims = []
with open('/Users/davidgoldblatt/Desktop/marcus_scrape/claims_condensed.jsonl') as f:
    for line in f:
        claims.append(json.loads(line.strip()))

claim_by_id = {c['id']: c for c in claims}

def has_all(text, terms):
    t = text.lower()
    return all(term.lower() in t for term in terms)

def has_any(text, terms):
    t = text.lower()
    return any(term.lower() in t for term in terms)

def target_has(target, terms):
    t = target.lower()
    return any(term.lower() in t for term in terms)

assignments = {}
cluster_claims = defaultdict(list)

cluster_defs = []

# ========================================================================
# CLUSTER DEFINITIONS (ordered by specificity -- more specific first)
# ========================================================================

# --- Specific product/model clusters ---

cluster_defs.append({
    'cluster_id': 'sora_video_unreliable',
    'canonical_statement': 'AI video generation (especially Sora) cannot simulate real physics and produces physically impossible outputs.',
    'match': lambda c: (
        (has_any(c['claim'], ['sora']) or target_has(c['target'], ['sora', 'video generat', 'ai video'])) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'job'])
    ) or (
        has_any(c['claim'], ['video generat', 'text-to-video', 'text to video', 'ai video']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'job'])
    )
})

cluster_defs.append({
    'cluster_id': 'o3_not_breakthrough',
    'canonical_statement': 'OpenAI\'s o1/o3 reasoning models are not the breakthrough claimed; they still exhibit fundamental LLM limitations.',
    'match': lambda c: (
        has_any(c['claim'], [' o1 ', ' o1,', ' o1.', ' o3 ', ' o3,', ' o3.', 'o1/', 'o3/', 'chain-of-thought', 'reasoning model',
                             'inference-time', 'inference time']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military'])
    ) or (
        target_has(c['target'], ['o3', 'o1', 'inference-time', 'inference time']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military'])
    )
})

cluster_defs.append({
    'cluster_id': 'gpt5_disappointing',
    'canonical_statement': 'GPT-5 is a moderate quantitative improvement that fails in the same qualitative ways as predecessors, confirming scaling limits.',
    'match': lambda c: (
        has_any(c['claim'], ['gpt-5', 'gpt5']) or target_has(c['target'], ['GPT-5', 'gpt-5', 'gpt5'])
    ) and not has_any(c['claim'], ['copyright', 'regulation', 'deepfake'])
})

cluster_defs.append({
    'cluster_id': 'gpt4_overhyped',
    'canonical_statement': 'GPT-4 was overhyped; it represents incremental improvement, not a paradigm shift, with the same fundamental limitations.',
    'match': lambda c: (
        (has_any(c['claim'], ['gpt-4', 'gpt4']) or target_has(c['target'], ['GPT-4', 'gpt-4', 'gpt4'])) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military'])
    )
})

# --- Specific person clusters ---

cluster_defs.append({
    'cluster_id': 'altman_overpromises',
    'canonical_statement': 'Sam Altman systematically overpromises and underdelivers on AI capabilities, timelines, and ethical commitments.',
    'match': lambda c: (
        (has_any(c['claim'], ['altman', 'sam altman']) or target_has(c['target'], ['altman', 'sam altman'])) and
        not has_any(c['claim'], ['copyright', 'bubble', 'military', 'china']) and
        not target_has(c['target'], ['openai', 'OpenAI'])
    )
})

cluster_defs.append({
    'cluster_id': 'musk_ai_hypocrisy',
    'canonical_statement': 'Elon Musk is hypocritical on AI safety; his ventures (xAI, DOGE, Tesla) demonstrate reckless deployment and pursuit of power.',
    'match': lambda c: (
        has_any(c['claim'], ['musk', 'elon', 'xai', 'grok', 'doge', 'tesla']) and
        not has_any(c['claim'], ['copyright', 'bubble']) and
        not (has_any(c['claim'], ['openai']) and not has_any(c['claim'], ['musk', 'elon']))
    ) or (
        target_has(c['target'], ['musk', 'tesla', 'xai', 'grok', 'doge', 'optimus']) and
        not has_any(c['claim'], ['copyright', 'bubble'])
    )
})

cluster_defs.append({
    'cluster_id': 'lecun_criticism',
    'canonical_statement': 'Yann LeCun\'s positions (anti-symbolic, dismissive of risks) have been counterproductive for the AI field.',
    'match': lambda c: (
        (has_any(c['claim'], ['lecun', 'le cun', 'yann']) or target_has(c['target'], ['lecun', 'le cun', 'yann'])) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military'])
    )
})

cluster_defs.append({
    'cluster_id': 'hinton_criticism',
    'canonical_statement': 'Geoffrey Hinton\'s late pivot to AI risk advocacy is complicated by decades of dismissing symbolic AI and safety.',
    'match': lambda c: (
        (has_any(c['claim'], ['hinton', 'geoffrey']) or target_has(c['target'], ['hinton'])) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'lecun', 'yann'])
    )
})

# --- OpenAI organizational clusters ---

cluster_defs.append({
    'cluster_id': 'openai_untrustworthy',
    'canonical_statement': 'OpenAI has become untrustworthy, prioritizing profit over safety, breaking promises, and misleading the public.',
    'match': lambda c: (
        (has_any(c['claim'], ['openai']) or target_has(c['target'], ['openai'])) and
        has_any(c['claim'], ['untrust', 'mislead', 'dishonest', 'broken', 'promise', 'profit over safety', 'reckless', 'credib',
                             'not be trusted', 'eroded', 'public trust', 'bad faith', 'ethics', 'safety cultur', 'abandon', 'mission',
                             'non-profit', 'nonprofit', 'for-profit', 'governance', 'safety team', 'fired', 'dissolution',
                             'sham', 'broke', 'disingenuous', 'hypocrisy', 'irresponsib', 'toxic', 'scandal',
                             'whistleblow', 'sued', 'lawsuit', 'board', 'candor', 'candid', 'knew', 'intention',
                             'drama', 'investigation', 'firing', 'concerns', 'legitimate', 'true', 'known risk',
                             'push toward', 'commercializ', 'rhetoric', 'gap', 'skeptic', 'strayed', 'original',
                             'NDA', 'non-disparage', 'equity', 'theater', 'secretly', 'loan guarantee', 'denied',
                             'ignored', 'warning', 'mental health', 'engagement metric', 'humanitarian',
                             'not behaved', 'dissolve', 'internal', 'left', 'safety researcher', 'attrition',
                             'priorit', 'vision', 'sole technical', 'vendor financing', 'dressed up']) and
        not has_any(c['claim'], ['copyright', 'deepfake', 'military', 'GPT-5', 'GPT-4', 'gpt-5', 'gpt-4',
                                  'competi', 'moat', 'valuation', 'money', 'revenue', 'loses money',
                                  'China', 'china', 'o1', 'o3', 'Orion', 'musk', 'Q*', 'AGI is not',
                                  'Amodei', 'bubble'])
    )
})

cluster_defs.append({
    'cluster_id': 'openai_wont_stay_dominant',
    'canonical_statement': 'OpenAI will not maintain dominance and faces serious competitive, financial, and organizational challenges.',
    'match': lambda c: (
        (has_any(c['claim'], ['openai']) or target_has(c['target'], ['openai'])) and
        has_any(c['claim'], ['dominan', 'competi', 'lead', 'market share', 'moat', 'advantage', 'ahead', 'position', 'valuation',
                             'not remain', 'weaken', 'decline', 'trouble', 'unsustain', 'WeWork', 'wework', 'overvalued',
                             'revenue', 'unprofitable', 'not profitable', 'money-losing', 'behind', 'catch up', 'commodity',
                             'no moat', 'vulnerable', 'price', 'cut', 'viab', 'loses money', 'losing money', 'profit',
                             'not expect', 'fund', 'investor', 'backing', 'depend', 'urgently', 'strategy', 'expensive',
                             'financial', 'survive', 'success is not', 'fraying', 'Microsoft', 'reproduced', 'replicable',
                             'months', 'Grok', 'Kai-Fu', 'slowing', 'Orion', 'spend', '$150 billion', 'runway',
                             'not assured', 'diminish', 'perceived', 'bailout', 'government', 'make sense',
                             'not make sense', 'do not make sense', 'not a profit', 'loss']) and
        not has_any(c['claim'], ['copyright', 'deepfake', 'military', 'GPT-5', 'GPT-4', 'gpt-5', 'gpt-4',
                                  'board', 'firing', 'candor', 'mission', 'rhetoric', 'skeptic',
                                  'safety cultur', 'trust', 'promise', 'ethics', 'NDA', 'theater', 'denied',
                                  'warning', 'engagement', 'humanitarian', 'not behaved', 'dissolve',
                                  'left', 'attrition', 'vendor financ', 'secretly'])
    )
})

# --- Core technical limitation clusters ---

cluster_defs.append({
    'cluster_id': 'hallucination_unsolvable',
    'canonical_statement': 'LLM hallucination/confabulation is an inherent architectural limitation that cannot be fully solved within the current paradigm.',
    'match': lambda c: (
        has_any(c['claim'], ['hallucin', 'confabul', 'fabricat', 'making things up', 'invents facts', 'false statement',
                             'invent citation', 'fake citation', 'fake referenc', 'made-up', 'made up fact',
                             'truthiness', 'false information', 'factuality', 'factual', 'truth', 'invalid answer',
                             'invalid proof', 'invalid output']) and
        has_any(c['claim'], ['llm', 'language model', 'gpt', 'chatgpt', 'ai', 'generative', 'neural', 'model', 'system',
                             'chatbot', 'deep research', 'persist']) and
        not has_any(c['claim'], ['copyright', 'military', 'deepfake', 'election', 'sora', 'video generat', 'code', 'coding',
                                  'image generat', 'openai', 'altman', 'musk', 'trump', 'china', 'bubble', 'job',
                                  'agent', 'robot', 'child', 'regulation'])
    )
})

cluster_defs.append({
    'cluster_id': 'llms_cannot_reason_reliably',
    'canonical_statement': 'LLMs cannot perform genuine, reliable reasoning; they approximate it through statistical pattern matching that breaks on novel problems.',
    'match': lambda c: (
        has_any(c['claim'], ['reason', 'reasoning', 'logical', 'logic', 'inference', 'deduct', 'arithmetic', 'math',
                             'first principle', 'from first', 'abstract relation', 'abstract rule',
                             'pointillistic', 'systematic reason']) and
        has_any(c['claim'], ['llm', 'language model', 'gpt', 'chatgpt', 'ai system', 'ai cannot', 'current ai', 'deep learning',
                             'neural net', 'generat', 'model', 'machine']) and
        has_any(c['claim'], ['cannot', 'can\'t', 'fail', 'unable', 'not', 'lack', 'poor', 'flaw', 'brittle', 'limit', 'inadequa',
                             'struggle', 'no', 'unreli', 'weak', 'error', 'wrong', 'incorrect', 'degrad', 'never fully',
                             'still struggling', 'blurry']) and
        not has_any(c['claim'], ['copyright', 'military', 'surveil', 'deepfake', 'regulat', 'bubble', 'hallucin', 'sora',
                                  'video generat', 'image generat', 'job', 'china', 'neurosymbolic', 'musk', 'trump',
                                  'openai', 'altman', 'code', 'coding', 'robot', 'agent', 'child', 'o1', 'o3'])
    )
})

cluster_defs.append({
    'cluster_id': 'scaling_wont_reach_agi',
    'canonical_statement': 'Simply scaling up LLM architectures (more data, parameters, compute) will not produce AGI or solve fundamental capability gaps.',
    'match': lambda c: (
        (has_any(c['claim'], ['scal', 'bigger', 'larger model', 'more data', 'more compute', 'more param', '$100b', 'trillion parameter',
                              'training time', 'data alone', 'double every', 'capability ceiling', 'capability wall']) and
         has_any(c['claim'], ['agi', 'not', 'won\'t', 'will not', 'cannot', 'insufficient', 'diminish', 'not enough', 'not the path',
                              'plateau', 'wall', 'limit', 'fail', 'inadequa', 'maximal', 'law', 'over', 'ended', 'era',
                              'ran out', 'run out', 'no longer', 'unlikely', 'devalued', 'premise', 'ceiling', 'approach',
                              'still', 'same', 'grifter'])) or
        (has_any(c['claim'], ['scaling']) and has_any(c['claim'], ['hit', 'wall', 'plateau', 'diminis', 'return', 'maximal', 'law',
                                                                     'not enough', 'not lead', 'not produce', 'fail', 'over',
                                                                     'ended', 'premise', 'devalued', 'ran out', 'run out',
                                                                     'played out', 'exhausted', 'grifter', 'sufficient']))
    ) and not has_any(c['claim'], ['regulation', 'copyright', 'bubble', 'stock', 'revenue', 'valuation', 'profit', 'deepfake',
                                    'military', 'o1', 'o3', 'inference-time', 'openai', 'altman', 'musk', 'trump', 'china',
                                    'nvidia', 'job', 'code'])
})

cluster_defs.append({
    'cluster_id': 'agi_not_imminent',
    'canonical_statement': 'AGI is not imminent and claims of near-term AGI by AI labs are unfounded hype.',
    'match': lambda c: (
        has_any(c['claim'], ['agi', 'artificial general intelligence', 'general intelligence', 'super-intelligent',
                             'superintelligent', 'human-level ai']) and
        has_any(c['claim'], ['not imminent', 'not close', 'far away', 'decades', 'won\'t arrive', 'not coming', 'not near',
                             'years away', 'premature', 'not achiev', 'overhype', 'not going to', 'will not arrive',
                             'nowhere near', 'false', 'not deliver', 'not produce', 'unlikely', 'further away',
                             'nowhere close', 'not happen', 'still do not have', 'still don\'t', 'not demonstrate',
                             'will not be achieved', 'not qualified', 'do not qualify', 'long way', 'many breakthroughs',
                             'quite possibly', 'century', 'someday', 'eventually', 'not by 202', 'zero chance',
                             'almost zero', 'underestimate', 'not plausible', 'absurd', 'doubtful', 'seriously doubt',
                             'not even close', 'not particularly close', 'highly uncertain', 'no single ai',
                             'not logically impossible', 'will be achieved someday', 'fundamental breakthrough',
                             'survived contact', 'equating generative', 'not the same', 'core prerequisite',
                             'resisted solution', 'quarter century', 'unsolved', 'not exhibit',
                             '10:1 odds', 'bet', 'wager', 'task', 'will not be the',
                             'not ready', 'world is also not', 'never deliver', 'will never live', 'enormous limitation',
                             'huge mistake', 'immense mistake', 'built around', 'myth',
                             'direct route', 'not a direct', 'inadequate', 'standalone',
                             'flexible, self-directed', 'was meant to be', 'marketed as',
                             'cannot live up', 'off by decades', 'take years', 'take decades',
                             'generation', 'Nobel', 'pure fantasy',
                             'Dario Amodei', 'pushed back', 'revise', 'downward']) and
        not has_any(c['claim'], ['regulation', 'copyright', 'bubble', 'stock', 'deepfake', 'military',
                                  'neurosymbolic', 'definition', 'redefin', 'goalpost', 'standard', 'lower',
                                  'openai', 'altman', 'musk', 'trump', 'china', 'scaling', 'o1', 'o3',
                                  'gpt-4', 'gpt-5', 'code', 'job', 'robot', 'humanoid', 'video',
                                  'image', 'sora', 'agent', 'copyright', 'economic'])
    )
})

cluster_defs.append({
    'cluster_id': 'agi_definition_diluted',
    'canonical_statement': 'AI labs are diluting the definition of AGI to declare premature victory and justify their business models.',
    'match': lambda c: (
        has_any(c['claim'], ['definition', 'redefin', 'goalpost', 'lower the bar', 'lower the standard', 'moving the', 'what counts as',
                             'AGI should', 'true AGI', 'real AGI', 'standard for AGI', 'level 5', 'level 4', 'level 3', 'level 2',
                             'criteria', 'classical criteria', 'economic terms', 'conflates economics',
                             'Marcus-Brundage', 'cognitive task']) and
        has_any(c['claim'], ['agi', 'artificial general intelligence'])
    )
})

# --- Financial/economic clusters ---

cluster_defs.append({
    'cluster_id': 'genai_bubble_will_burst',
    'canonical_statement': 'The generative AI industry is a financial bubble with massive spending relative to revenue that will eventually burst.',
    'match': lambda c: (
        (has_any(c['claim'], ['bubble', 'bust', 'crash', 'overvalued', 'dot-com', 'dotcom', 'tulip', 'overinvest', 'speculative',
                              'flame out', 'fading', 'collapse', 'winter', 'downturn', 'capital destruction',
                              'greatest capital', 'recession', 'bailout', 'too big to fail',
                              'revenue shortfall', 'debt buildup', 'irrational', 'fold', 'stripped for parts',
                              'radically different by', 'oracle craze', 'non-binding', 'market cap']) and
         has_any(c['claim'], ['ai', 'genai', 'generative', 'llm', 'tech', 'oracle', 'industry'])) or
        (has_any(c['claim'], ['revenue', 'profit', 'spending', 'investment', 'valuation']) and
         has_any(c['claim'], ['unsustain', 'never recoup', 'not profitable', 'unprofitable', 'money-losing', 'collapse',
                              'overval', 'bubble', 'bust', 'not a sustainable', 'irrational', 'flame out', 'fold',
                              'lose significant money', 'decline']))
    ) and not has_any(c['claim'], ['copyright', 'military', 'deepfake', 'regulation', 'openai', 'nvidia', 'code',
                                    'china', 'musk', 'trump', 'altman', 'robot', 'hallucin', 'benchmark', 'agent'])
})

cluster_defs.append({
    'cluster_id': 'nvidia_vulnerable',
    'canonical_statement': 'Nvidia\'s dominance and valuation are vulnerable to efficiency gains and potential industry downturn.',
    'match': lambda c: (
        has_any(c['claim'], ['nvidia']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'military'])
    )
})

cluster_defs.append({
    'cluster_id': 'ai_roi_disappointing',
    'canonical_statement': 'AI ROI has been deeply disappointing; companies spend far more on AI than they earn, productivity gains remain elusive.',
    'match': lambda c: (
        (has_any(c['claim'], ['roi', 'return on investment', 'revenue', 'profit', 'monetiz', 'business model', 'economic value',
                             'earnings', 'recoup', 'cost', 'spend', 'worth', 'GDP', 'killer app', 'commercial', 'viable',
                             'economics', 'adoption', 'enterprise', 'production', 'deploy', 'proof-of-concept', 'testing',
                             'value', 'underwhelm', 'disappoint', 'materialize', 'measurable return', 'no measurable',
                             'success stor', 'slowing download', 'declining daily', 'vibe coding',
                             'copilot thought', 'economics have never made sense', 'outweigh', '50:1',
                             'restructur', 'rebuilt', 'enormous expense', 'diversif',
                             'commodit', 'price war', 'moat', 'identical', 'no competitive']) and
         has_any(c['claim'], ['ai', 'llm', 'generat', 'chatgpt', 'copilot', 'genai', 'tech', 'LLM'])) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'military', 'bubble', 'nvidia', 'openai',
                                  'china', 'musk', 'trump', 'hallucin', 'reason', 'altman', 'gpt-4', 'gpt-5',
                                  'sora', 'robot', 'agent', 'child', 'image generat', 'o1', 'o3', 'benchmark',
                                  'neurosymbolic'])
    )
})

# --- Regulation & policy clusters ---

cluster_defs.append({
    'cluster_id': 'ai_needs_regulation',
    'canonical_statement': 'AI systems need robust government regulation because industry self-regulation is insufficient to protect the public.',
    'match': lambda c: (
        has_any(c['claim'], ['regulat', 'legislat', 'governance', 'policy', 'government should', 'FDA', 'SB-1047', 'EU AI Act',
                             'oversight', 'regulatory', 'legal framework', 'congress', 'law should', 'approval process',
                             'pre-deployment', 'label', 'disclose', 'restrict', 'mandate', 'by law', 'taxed',
                             'no restriction', 'zero regulation', 'foundation model', 'kill switch',
                             'forbid', 'enforcement', 'federal law', 'proof-of-human', 'cryptographic',
                             'must pass', 'platform moderation', 'continuous monitoring', 'require',
                             'approval', 'Paris AI Summit', 'guardrail', 'policymaker']) and
        has_any(c['claim'], ['ai', 'llm', 'generative', 'tech', 'chatbot', 'model', 'LLM', 'deepfake', 'machine',
                             'online', 'platform', 'bot']) and
        not has_any(c['claim'], ['copyright', 'intellectual property', 'military', 'china', 'trump', 'musk', 'doge',
                                  'self-regulat', 'altman', 'openai'])
    )
})

cluster_defs.append({
    'cluster_id': 'trump_ai_policy_harmful',
    'canonical_statement': 'The Trump administration\'s AI deregulation and industry capture will harm citizens and benefit only AI companies.',
    'match': lambda c: (
        has_any(c['claim'], ['trump', 'sacks', 'vance']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'tech', 'regul', 'deregul', 'polic', 'executive order', 'university',
                             'authoritar', 'genesis', 'white house']) and
        not has_any(c['claim'], ['musk', 'doge', 'china', 'copyright'])
    )
})

cluster_defs.append({
    'cluster_id': 'industry_self_regulation_fails',
    'canonical_statement': 'AI companies cannot be trusted to self-regulate; they externalize costs while capturing profits.',
    'match': lambda c: (
        (has_any(c['claim'], ['self-regulat', 'voluntary', 'commitment', 'pledge', 'self regulat', 'internal safety',
                             'responsible ai', 'responsible develop', 'trust the compan', 'industry self', 'externali',
                             'big tech', 'disregard', 'consequence', 'society bears', 'maximize profit',
                             'vested interest', 'management fee', 'regardless of whether',
                             'captured', 'big tech', 'silicon valley', 'reckless', 'consequences of their product',
                             'independent of big tech', 'all three major', 'incentive']) and
        has_any(c['claim'], ['ai', 'openai', 'tech', 'llm', 'industry', 'compan', 'silicon valley', 'investor',
                             'deepmind', 'inflection']))
    ) and not has_any(c['claim'], ['copyright', 'regulation should', 'china', 'trump', 'musk', 'deepfake',
                                    'military', 'gpt-4', 'gpt-5', 'bubble', 'hallucin'])
})

# --- Paradigm/architecture clusters ---

cluster_defs.append({
    'cluster_id': 'need_hybrid_neurosymbolic',
    'canonical_statement': 'Progress toward AGI requires hybrid neurosymbolic architectures combining neural networks with structured symbolic reasoning.',
    'match': lambda c: (
        has_any(c['claim'], ['neurosymbolic', 'neuro-symbolic', 'symbolic', 'symbol', 'knowledge engineer',
                             'classical ai', 'structured knowledge', 'combine neural', 'symbolic reasoning', 'hybrid approach',
                             'variable binding', 'innate structure', 'prior knowledge', 'explicit cognitive',
                             'operations over variable', 'type/token', 'type-token', 'AlphaProof', 'AlphaGeometry',
                             'formal reasoning', 'formal method', 'structured system', 'complementary strength',
                             'Cicero', 'FunSearch', 'hand-crafted', 'innate', 'nativism', 'nativist',
                             'cognitive science', 'key ingredient', 'innate learning mechanism',
                             'what makes human cognition']) and
        has_any(c['claim'], ['need', 'requir', 'should', 'must', 'essential', 'path', 'approach', 'promis', 'solution',
                             'better', 'integrat', 'combin', 'alternative', 'key', 'missing', 'lack', 'advocate', 'call for',
                             'without', 'manipulat', 'crucial', 'will be', 'immune', 'dramatically', 'improve', 'embedded',
                             'far more', 'uses', 'relies', 'central', 'unique', 'endow', 'innate', 'human', 'excel',
                             'narrowly specialized', 'IMO', 'geometry', 'strong', 'superior', 'prominent', 'ingredient',
                             'evidence', 'logically', 'divergence'])
    ) and not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'military', 'bubble', 'china', 'trump', 'musk',
                                    'openai', 'altman', 'job', 'agent', 'code', 'image', 'sora'])
})

cluster_defs.append({
    'cluster_id': 'ai_needs_new_paradigm',
    'canonical_statement': 'Fundamentally new AI approaches are needed because the current deep learning/LLM paradigm has inherent, unfixable limitations.',
    'match': lambda c: (
        (has_any(c['claim'], ['new approach', 'new architect', 'new paradigm', 'fundamental rethink', 'fundamentally new',
                             'alternative approach', 'different approach', 'paradigm shift', 'next generation', 'move past',
                             'new technolog', 'radically different', 'rethink', 'novel approach', 'overdue for', 'paradigm',
                             'drawing board', 'back to the', 'beyond current', 'one tool among', 'only a small part',
                             'going back to', 'reconceptualize', 'not on the right path', 'wrong path', 'being wasted',
                             'starving alternative', 'divert', 'at the expense', 'what comes next', 'pivot',
                             'innovating beyond', 'integrating LLMs with other', 'shift from', 'decline of LLM',
                             'alternative AI', 'newcomer', 'stop dismissing', 'develop alternative',
                             'too little in non-LLM', 'intellectual and economic diversification',
                             'delusional and absurd', 'dead end', 'exclusively on the LLM']) and
        has_any(c['claim'], ['ai', 'llm', 'deep learning', 'neural', 'generat', 'tech']))
    ) and not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'military', 'bubble', 'neurosymbolic', 'symbolic',
                                    'china', 'musk', 'trump', 'openai', 'altman', 'job', 'robot', 'code', 'image', 'sora',
                                    'agent', 'gpt-4', 'gpt-5', 'o1', 'o3', 'hallucin', 'benchmark', 'child'])
})

# --- Copyright/IP cluster ---

cluster_defs.append({
    'cluster_id': 'ai_copyright_infringement',
    'canonical_statement': 'Generative AI is built on massive copyright infringement and the industry cannot solve the attribution problem.',
    'match': lambda c: (
        has_any(c['claim'], ['copyright', 'intellectual property', 'pirat', 'stolen', 'fair use', 'training data', 'attribution',
                             'provenance', 'creative work', 'artists', 'writers', 'copyrighted', ' nyt', 'new york times', 'litigation',
                             'creator', 'license', 'regurgitat', 'infringe', 'manifest', 'source material']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'openai', 'model', 'training', 'tech', 'midjourney'])
    )
})

# --- Society/harm clusters ---

cluster_defs.append({
    'cluster_id': 'deepfakes_threaten_democracy',
    'canonical_statement': 'AI-generated deepfakes and misinformation pose a severe threat to democracy, elections, and public trust.',
    'match': lambda c: (
        has_any(c['claim'], ['deepfake', 'misinformation', 'disinformation', 'fake image', 'fake video', 'election', 'propaganda',
                             'political manipulat', 'synthetic media', 'fake news', 'impersonat', 'bot', 'authenticat',
                             'mind control', 'manipulate public opinion', 'shape people']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'threat', 'danger', 'risk', 'harm', 'sway', 'undermin', 'destabiliz', 'erode',
                             'disrupt', 'trust', 'democra', 'sophistic', 'resist', 'mandatory', 'potent', 'inevitable',
                             'society', 'civic', 'institution', 'destroy', 'zero cost', 'scam'])
    )
})

cluster_defs.append({
    'cluster_id': 'ai_surveillance_authoritarian',
    'canonical_statement': 'AI-powered surveillance is inherently authoritarian and its expansion threatens civil liberties.',
    'match': lambda c: (
        has_any(c['claim'], ['surveil', 'facial recogn', 'monitor', 'spy', 'privacy', 'civil libert', 'authoritarian',
                             'police state', 'panopticon', 'social control', 'mass surveil', 'tracking', 'data practic',
                             'data collection', 'personal data', 'collectively', 'resist big tech']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'tech', 'facial', 'digital', 'data', 'compan', 'microsoft', 'altman'])
    )
})

cluster_defs.append({
    'cluster_id': 'ai_military_dangerous',
    'canonical_statement': 'Deploying unreliable AI in military applications and lethal autonomous weapons is extremely dangerous.',
    'match': lambda c: (
        has_any(c['claim'], ['military', 'weapon', 'autonomous weapon', 'lethal', 'drone', 'warfare', 'pentagon', 'defense',
                             'kill chain', 'lavender', 'targeting', 'battlefield', 'nuclear', 'arms race', 'bioweapon',
                             'pathogen']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'autonom', 'unreli', 'danger', 'risk'])
    )
})

cluster_defs.append({
    'cluster_id': 'ai_child_safety',
    'canonical_statement': 'AI systems pose particular dangers to children and teens that remain unaddressed.',
    'match': lambda c: (
        has_any(c['claim'], ['child', 'children', 'teen', 'minor', 'youth', 'kid', 'student', 'young people', 'adolesc', 'CSAM',
                             'predator', 'school', 'homework', 'term paper', 'suicide', 'mental health']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'chatbot', 'social media', 'chatgpt', 'character.ai', 'deep research',
                             'grade', 'learn'])
    ) and not has_any(c['claim'], ['openai', 'altman', 'musk', 'trump', 'china'])
})

cluster_defs.append({
    'cluster_id': 'ai_worsens_inequality',
    'canonical_statement': 'AI concentrates power/wealth while harming marginalized communities through bias, discrimination, and denial of services.',
    'match': lambda c: (
        has_any(c['claim'], ['bias', 'discriminat', 'inequal', 'marginali', 'racist', 'racism', 'racial', 'gender', 'wealth concentrat',
                             'power concentrat', 'oligarch', 'billionaire', 'monopol', 'antitrust', 'big tech power',
                             'inequality', 'concentration of', 'disadvantaged', 'disproportionate', 'rip off', 'deny',
                             'insurance', 'housing', 'employment', 'claims', 'just society', 'dystopia', 'default trajectory',
                             'social cohesion', 'social media', 'recommendation algorithm']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'tech', 'algorithm'])
    ) and not has_any(c['claim'], ['copyright', 'military', 'deepfake', 'bubble', 'china', 'musk', 'trump', 'surveil',
                                    'openai', 'altman', 'code', 'regulation'])
})

cluster_defs.append({
    'cluster_id': 'ai_enviro_costs_ignored',
    'canonical_statement': 'The environmental costs of AI (energy, water, carbon) are substantial, underreported, and growing unsustainably.',
    'match': lambda c: (
        has_any(c['claim'], ['energy', 'water', 'carbon', 'environment', 'climate', 'power consumption', 'electricity', 'data center',
                             'fossil fuel', 'nuclear', 'emission', 'sustainab', 'ecological']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'training', 'compute', 'gpu', 'data center', 'tech'])
    )
})

# --- Technical limitation clusters ---

cluster_defs.append({
    'cluster_id': 'llms_lack_world_models',
    'canonical_statement': 'LLMs do not build genuine world models or understand the world; they manipulate statistical patterns without comprehension.',
    'match': lambda c: (
        has_any(c['claim'], ['world model', 'understand', 'comprehen', 'knowledge of the world', 'meaning', 'semantics', 'grounding',
                             'mental model', 'cognitive', 'concept', 'truth', 'grasp', 'coherence', 'external world', 'reference',
                             'sentient', 'sentience', 'aware', 'consciousness', 'self-aware', 'thinking', 'think like',
                             'believe', 'consistent belief', 'personality', 'drive', 'intelligent', 'intelligence', 'smart',
                             'confused', 'confused despite', 'capable', 'easily confused',
                             'language cognition', 'what the speaker', 'intending',
                             'teach themselves', 'wisdom', 'emotion', 'psychology',
                             'decide', 'pixel prediction', 'how the world works', 'physics from',
                             'sensory data', 'learn physics', 'right and wrong',
                             'genuinely', 'genuine', 'truly', 'real']) and
        has_any(c['claim'], ['llm', 'language model', 'gpt', 'ai', 'deep learning', 'neural net', 'chatgpt', 'generat',
                             'chatbot', 'lamda', 'machine', 'system', 'claude', 'model', 'transformer', 'current']) and
        has_any(c['claim'], ['not', 'lack', 'without', 'no', 'fail', 'cannot', 'don\'t', 'does not', 'do not', 'superficial', 'shallow',
                             'poor', 'limited', 'absence', 'no genuine', 'no real', 'doesn\'t', 'illusion', 'never', 'myth',
                             'neither', 'fooling', 'stochastic', 'no more', 'unreliab', 'merely', 'far from', 'fallacy',
                             'anthropomorphi', 'attribute', 'gullibil', 'not remotely', 'browser',
                             'fooling', 'reveal', 'nothing', 'fundamental', 'different']) and
        not has_any(c['claim'], ['copyright', 'military', 'bubble', 'deepfake', 'election', 'hallucin', 'regulat',
                                  'sora', 'video generat', 'image generat', 'job', 'china', 'musk', 'trump', 'survey',
                                  'code', 'coding', 'medical', 'legal', 'agent', 'child', 'neurosymbolic', 'openai',
                                  'altman', 'robot', 'benchmark', 'scaling', 'bubble', 'nvidia', 'o1', 'o3',
                                  'gpt-4', 'gpt-5', 'hype cycle'])
    )
})

cluster_defs.append({
    'cluster_id': 'llms_no_real_understanding',
    'canonical_statement': 'LLMs are fundamentally statistical pattern matchers / next-word predictors without genuine understanding.',
    'match': lambda c: (
        has_any(c['claim'], ['pattern match', 'autocomplete', 'next word', 'next-word', 'statistical', 'stochastic parrot', 'lookup table',
                             'interpolat', 'memoriz', 'correlat', 'word prediction', 'token predict', 'statistical model',
                             'probabilist', 'mimicry', 'mimic', 'next-token', 'word-sequence', 'plausible-sounding',
                             'plausible text', 'word sequence', 'sound human', 'behaviorist', 'blank-slate', 'blank slate',
                             'regurgitat', 'proxy', 'approximat', 'embedding', 'synonym substitution',
                             'surface-level agreement', 'surface', 'divergence in underlying',
                             'high confidence', 'modulate', 'sparse']) and
        has_any(c['claim'], ['llm', 'language model', 'gpt', 'ai', 'chatgpt', 'neural', 'deep learning', 'generat', 'model']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'job', 'sora', 'china', 'musk', 'trump',
                                  'openai', 'altman', 'hallucin', 'code', 'image generat', 'robot', 'agent', 'child',
                                  'gpt-4', 'gpt-5', 'o1', 'o3', 'benchmark', 'neurosymbolic', 'scaling'])
    )
})

cluster_defs.append({
    'cluster_id': 'ai_benchmarks_misleading',
    'canonical_statement': 'AI benchmarks and demos are frequently misleading, creating false impressions of capabilities.',
    'match': lambda c: (
        has_any(c['claim'], ['benchmark', 'demo', 'evaluation', 'cherry-pick', 'cherrypick', 'metric', 'elo rating',
                             'leaderboard', 'contamina', 'test score', 'saturated', 'gaming', 'Turing Test', 'turing test',
                             'publicity stunt', 'dress rehearsal', 'glimpse', 'initial impressive', 'impressi',
                             'scientific review', 'tested on', 'tested by', 'Llama 4']) and
        has_any(c['claim'], ['mislead', 'flaw', 'overstat', 'inflat', 'not reflect', 'inadequa', 'superficial', 'broken', 'unreli',
                             'poor', 'gaming', 'gamed', 'manipulat', 'fail', 'not a good', 'cherry', 'does not', 'narrow',
                             'contamina', 'overfit', 'limited', 'not measure', 'exagger', 'hype', 'not reliable',
                             'meaningless', 'not', 'don\'t', 'ai', 'undermin', 'gullibil', 'fooling', 'eliza',
                             'competitively', 'invalid', 'measures', 'stunt', 'take years', 'gone badly',
                             'revealed limitation', 'not what', 'false impression', 'not equivalent',
                             'claims', 'subjected', 'reliabilit', 'neither', 'disappointed', 'real-world']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'military', 'china', 'musk', 'trump',
                                  'bubble', 'openai', 'altman', 'code', 'job', 'robot', 'agent', 'child',
                                  'hallucin', 'o1', 'o3', 'gpt-4', 'gpt-5', 'neurosymbolic', 'scaling',
                                  'sora', 'image generat'])
    )
})

cluster_defs.append({
    'cluster_id': 'llms_unreliable_for_critical_apps',
    'canonical_statement': 'LLMs are too unreliable for high-stakes applications including medicine, law, autonomous vehicles, and robotics.',
    'match': lambda c: (
        has_any(c['claim'], ['medical', 'health', 'healthcare', 'legal', 'law', 'autonomous vehic', 'self-driving', 'self driving',
                             'driverless', 'radiology', 'diagnosis', 'clinical', 'patient', 'doctor', 'hospital',
                             'safety-critical', 'high-stakes', 'high stakes', 'critical infrastructure',
                             'robot', 'humanoid', 'household', 'domestic', 'cook', 'kitchen', 'waymo', 'cruise', 'tesla',
                             'level 5', 'level 2', 'autopilot', 'full self driving', 'FSD', 'robotaxi',
                             'common sense', 'commonsense', 'edge case', 'physical world', 'spatial',
                             'remote operator', 'remote driv', 'semi-auton', 'call center', 'call-center',
                             'supervision', 'human operator', 'motor control', 'situational awareness',
                             'human supervision', 'public roads', 'remotely-assisted',
                             'simulation', 'physical simulation', 'household robot', 'entity reasoning',
                             'properties', 'physical reasoning', 'commonsense physical',
                             'physical tasks', 'cook in an arbitrary kitchen']) and
        has_any(c['claim'], ['ai', 'llm', 'gpt', 'generat', 'language model', 'deep learning', 'machine learning', 'neural',
                             'autonomous', 'autonom', 'robot', 'driverless', 'self-driving']) and
        not has_any(c['claim'], ['copyright', 'deepfake', 'election', 'bubble', 'military', 'regulat',
                                  'china', 'openai', 'image generat', 'sora', 'video generat', 'neurosymbolic',
                                  'hallucin', 'altman', 'musk', 'trump', 'scaling', 'benchmark', 'o1', 'o3',
                                  'gpt-4', 'gpt-5', 'code', 'job', 'agent', 'child', 'bubble', 'nvidia'])
    )
})

# --- Risk framing ---

cluster_defs.append({
    'cluster_id': 'ai_existential_risk_real_but_misframed',
    'canonical_statement': 'AI poses real risks, but focus on far-future superintelligence distracts from immediate concrete dangers.',
    'match': lambda c: (
        has_any(c['claim'], ['existential', 'extinction', 'x-risk', 'xrisk', 'superintelligen', 'catastroph', 'doomsday',
                             'end of human', 'near-term risk', 'near-term harm', 'immediate risk', 'present danger', 'current harm',
                             'real risk', 'concrete harm', 'concrete risk', 'actual harm', 'actual risk', 'misuse', 'bad actor',
                             'deliberate', 'catastrophe', 'future ai', 'near term', 'take over',
                             'prepared', 'society is not', 'societal risk', 'death attribut', 'death',
                             'harm is increasing', 'real-world harm', 'unknown unknown',
                             'net positive', 'net negative', 'positive or negative', 'positive force', 'more harm',
                             'limited/overrated', 'stupidity and danger', 'simultaneously dangerous',
                             'honestly confronting', 'techno-optimism', 'recognizing',
                             'released to the public', 'irreversib', 'un-invented', 'cannot be un',
                             'change everything', '5-20 years']) and
        has_any(c['claim'], ['ai', 'llm', 'agi', 'machine', 'generat', 'llm'])
    ) and not has_any(c['claim'], ['copyright', 'deepfake', 'bubble', 'military', 'musk', 'trump', 'regulat', 'china',
                                    'openai', 'altman', 'code', 'child', 'surveil', 'job', 'image', 'sora',
                                    'hallucin', 'robot', 'benchmark', 'scaling', 'o1', 'o3', 'gpt-4', 'gpt-5',
                                    'neurosymbolic', 'agent', 'humanoid', 'driverless', 'autonomous vehic'])
})

# --- Media & narrative clusters ---

cluster_defs.append({
    'cluster_id': 'ai_media_coverage_uncritical',
    'canonical_statement': 'Media coverage of AI is overwhelmingly uncritical, amplifying industry hype without adequate scrutiny.',
    'match': lambda c: (
        has_any(c['claim'], ['media', 'press', 'journal', 'reporter', 'coverage', 'new york times', 'nyt', 'puff piece',
                             'uncritical', 'credulous', 'tech press', '60 minutes', 'MIT Technology Review',
                             ' nyt', 'new york times', 'newspaper', 'AI safety advocate', 'safety community',
                             'AI literacy', 'public needs to learn', 'public understanding',
                             'Sokal', 'hoax', 'joke', 'context about', 'conflict of interest', 'track record',
                             'platforming']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'tech', 'openai', 'company', 'industry', 'AGI', 'agi',
                             'human-sounding', 'speech', 'machine', 'chatbot'])
    ) and not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'military', 'china', 'musk', 'trump',
                                    'bubble', 'code', 'job', 'robot', 'hallucin', 'o1', 'o3', 'gpt-4', 'gpt-5',
                                    'neurosymbolic', 'scaling', 'image generat', 'sora', 'agent', 'child', 'altman'])
})

cluster_defs.append({
    'cluster_id': 'ai_scientists_overstate',
    'canonical_statement': 'Leading AI researchers and labs systematically overstate capabilities and make misleading claims.',
    'match': lambda c: (
        has_any(c['claim'], ['overstat', 'exagger', 'overclaim', 'false claim', 'dishonest', 'decepti', 'inflat',
                             'not what it seems', 'misleading', 'vested interest', 'will to believe', 'counterevidence',
                             'dismissed', 'ignored', 'hint at imminent', 'success theater', 'performing success',
                             'revise their timelines', 'reframing', 'expectations',
                             'Vinod Khosla', 'Amodei', 'pushed back', 'quietly']) and
        has_any(c['claim'], ['researcher', 'scientist', 'lab', 'company', 'industry', 'google', 'meta', 'deepmind', 'anthropic',
                             'hinton', 'lecun', 'hassabis', 'ai compan', 'tech leader', 'leader',
                             'field', 'community', 'Dario', 'dario']) and
        not has_any(c['claim'], ['copyright', 'deepfake', 'bubble', 'military', 'media', 'altman', 'musk', 'openai', 'trump',
                                  'benchmark', 'regulat', 'code', 'robot', 'gpt-4', 'gpt-5', 'image',
                                  'china', 'agent', 'child', 'hallucin', 'scaling', 'neurosymbolic', 'job'])
    )
})

# --- Coding ---

cluster_defs.append({
    'cluster_id': 'ai_coding_overhyped',
    'canonical_statement': 'AI coding tools produce unreliable code with security vulnerabilities; productivity gains are exaggerated.',
    'match': lambda c: (
        has_any(c['claim'], ['code', 'coding', 'programming', 'software engineer', 'github copilot', 'copilot', 'vibe cod',
                             'devin', 'ai-generated code', 'ai-written code', 'ai code', 'software develop', 'software reliab',
                             'software method', 'debug', 'complex software', 'software architect', 'programmer', 'english prompt',
                             'programming language', 'formal programming', 'natural language', 'specify intent']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'gpt', 'chatbot']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'election', 'bubble', 'military', 'china', 'musk', 'trump',
                                  'openai', 'altman', 'hallucin', 'o1', 'o3', 'gpt-4', 'gpt-5', 'scaling',
                                  'neurosymbolic', 'agent', 'image', 'sora', 'robot', 'benchmark', 'child',
                                  'job', 'medical', 'legal'])
    )
})

# --- Image generation ---

cluster_defs.append({
    'cluster_id': 'ai_image_gen_unreliable',
    'canonical_statement': 'AI image generation systems fail at compositional understanding, spatial relationships, and faithful prompt adherence.',
    'match': lambda c: (
        has_any(c['claim'], ['image generat', 'dall-e', 'dall·e', 'midjourney', 'stable diffusion', 'text-to-image', 'text to image',
                             'ai art', 'generated image', 'ai image', 'render', 'alphabet', 'map', 'geographic',
                             'visual', 'multimodal', 'Imagen', 'keyword matching']) and
        has_any(c['claim'], ['fail', 'cannot', 'poor', 'unreli', 'inaccura', 'wrong', 'flaw', 'limit', 'error', 'break', 'struggle',
                             'lack', 'not', 'superficial', 'unpredictab', 'buggy', 'incorrect', 'inconsistent',
                             'approximate', 'rely']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'artist livelihood', 'military', 'sora',
                                  'video generat', 'china', 'musk', 'trump', 'code', 'job', 'openai', 'altman',
                                  'hallucin', 'robot', 'agent', 'o1', 'o3', 'gpt-4', 'gpt-5', 'scaling',
                                  'benchmark', 'neurosymbolic', 'child'])
    )
})

cluster_defs.append({
    'cluster_id': 'llms_lack_compositionality',
    'canonical_statement': 'LLMs and neural nets fundamentally lack compositionality -- the ability to understand novel combinations of concepts.',
    'match': lambda c: (
        has_any(c['claim'], ['compositionality', 'compositional', 'novel combination', 'systematic generalization',
                             'part-specification', 'relational reasoning', 'combine concept',
                             'compositional understanding', 'abstract', 'abstraction', 'type-token', 'type/token',
                             'similarity-independent']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'neural', 'deep learning', 'dall-e', 'dall', 'gpt', 'image generat', 'model'])
    ) and not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'military', 'bubble', 'sora', 'code',
                                    'china', 'musk', 'trump', 'neurosymbolic', 'openai', 'altman', 'robot',
                                    'agent', 'job', 'benchmark', 'child'])
})

# --- Agent cluster ---

cluster_defs.append({
    'cluster_id': 'llm_agents_premature',
    'canonical_statement': 'LLM-based autonomous agents are unreliable and not ready for real-world deployment.',
    'match': lambda c: (
        has_any(c['claim'], ['agent', 'agentic', 'autonomous agent', 'tool use', 'tool-use', 'computer use', 'virtual assistant',
                             'alexa', 'assistant', 'taken at their word', 'claiming to be doing']) and
        has_any(c['claim'], ['llm', 'ai', 'gpt', 'language model', 'Claude', 'claude']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'china', 'musk', 'trump',
                                  'openai', 'altman', 'image', 'sora', 'code', 'hallucin', 'robot', 'humanoid',
                                  'o1', 'o3', 'gpt-4', 'gpt-5', 'neurosymbolic', 'scaling', 'benchmark', 'child',
                                  'job', 'medical', 'legal', 'driverless'])
    )
})

# --- Competition cluster ---

cluster_defs.append({
    'cluster_id': 'china_ai_competition',
    'canonical_statement': 'The US-China AI competition is consequential, and current US policy may be counterproductive.',
    'match': lambda c: (
        has_any(c['claim'], ['china', 'chinese', 'us-china', 'deepseek', 'export control', 'chip ban', 'ai race',
                             'national security', 'CHIPS Act', 'geopolit', 'asia', 'adversar', 'supremacy',
                             'US science', 'NIH', 'NSF', 'American science', 'academic talent', 'global science',
                             'US can only regain', 'US lead', 'single country', 'won by the country']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'tech', 'science', 'research', 'innovat', 'compet', 'race'])
    ) and not has_any(c['claim'], ['copyright', 'deepfake', 'military weapon', 'musk', 'doge', 'openai', 'altman',
                                    'trump', 'bubble'])
})

# --- Planning ---

cluster_defs.append({
    'cluster_id': 'llms_cannot_plan',
    'canonical_statement': 'LLMs cannot perform genuine multi-step planning, fundamentally limited in lookahead and strategy tasks.',
    'match': lambda c: (
        has_any(c['claim'], ['plan', 'planning', 'multi-step', 'lookahead', 'strategy', 'strateg', 'anticipate consequence',
                             'temporal', 'movie', 'narrative', 'describe what is happening']) and
        has_any(c['claim'], ['llm', 'language model', 'gpt', 'ai', 'chatgpt', 'neural', 'deep learning', 'multimodal']) and
        has_any(c['claim'], ['cannot', 'fail', 'lack', 'unable', 'poor', 'limit', 'flaw', 'not', 'struggle', 'brittle', 'no',
                             'unsolved', 'challenge', 'remain', 'weaker']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'job', 'hallucin', 'china',
                                  'musk', 'trump', 'openai', 'image', 'sora', 'robot', 'code', 'agent', 'altman',
                                  'o1', 'o3', 'gpt-4', 'gpt-5', 'scaling', 'benchmark', 'neurosymbolic', 'child'])
    )
})

# --- Safety ---

cluster_defs.append({
    'cluster_id': 'ai_safety_requires_understanding',
    'canonical_statement': 'We cannot make AI safe without understanding how it works; interpretability and formal verification are prerequisites.',
    'match': lambda c: (
        has_any(c['claim'], ['safety', 'alignment', 'align', 'interpretab', 'explainab', 'black box', 'formal verif',
                             'transparen', 'controllab', 'guardrail', 'audit', 'values', 'human values',
                             'consensus', 'instill', 'uninterpretab', 'methodology', 'whack-a-mole',
                             'alternative architect', 'amenable', 'safe AI', 'trustworthy AI',
                             'not prepared', 'too little', 'done too little']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'neural', 'model', 'machine', 'system', 'deep learning', 'cognitive']) and
        has_any(c['claim'], ['need', 'require', 'cannot', 'must', 'prerequis', 'essential', 'without', 'lack', 'insufficient', 'not',
                             'fail', 'impossible', 'unable', 'far from', 'no known', 'no compell', 'difficulty', 'difficult',
                             'best hope', 'lies in', 'build', 'invest', 'improve', 'adequate']) and
        not has_any(c['claim'], ['copyright', 'deepfake', 'election', 'bubble', 'job', 'regulat', 'military', 'musk', 'trump',
                                  'openai', 'china', 'altman', 'child', 'surveil', 'hallucin', 'robot', 'code',
                                  'image', 'sora', 'benchmark', 'neurosymbolic', 'agent', 'gpt-4', 'gpt-5',
                                  'o1', 'o3', 'scaling', 'nvidia'])
    )
})

# --- Hype cycle ---

cluster_defs.append({
    'cluster_id': 'ai_hype_cycle_parallels',
    'canonical_statement': 'The current AI hype cycle follows historical patterns (dot-com, crypto, AI winters) and will end similarly.',
    'match': lambda c: (
        has_any(c['claim'], ['hype', 'ai winter', 'dot-com', 'dotcom', 'crypto', 'historical', 'cycle', 'web3', 'metaverse', 'nft',
                             'previous ai', 'past ai', 'tulip', 'expert system', 'south sea', 'historian',
                             'overemphasis', 'shift back', 'greatest publicity stunt', 'remembered as']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'tech', 'chatgpt']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'military', 'medical', 'china', 'musk', 'trump',
                                  'openai', 'altman', 'benchmark', 'robot', 'code', 'image', 'sora', 'agent',
                                  'gpt-4', 'gpt-5', 'o1', 'o3', 'neurosymbolic', 'scaling', 'nvidia',
                                  'child', 'job', 'hallucin', 'bubble', 'revenue'])
    )
})

# --- Job disruption ---

cluster_defs.append({
    'cluster_id': 'ai_job_disruption_overhyped',
    'canonical_statement': 'Claims that AI will massively replace human jobs are premature; AI augments rather than replaces most workers.',
    'match': lambda c: (
        has_any(c['claim'], ['job', 'employ', 'worker', 'labor', 'workforce', 'automat', 'replac', 'displace', 'unemploy',
                             'productivity', 'augment', 'human labor', 'profession', 'talent', 'programmer',
                             'human software architect', 'require skilled']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'chatgpt', 'robot']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'military', 'china', 'musk', 'bubble',
                                  'hallucin', 'benchmark', 'sora', 'openai', 'scaling', 'o1', 'o3', 'gpt-4', 'gpt-5',
                                  'neurosymbolic', 'altman', 'trump', 'nvidia', 'image generat', 'code',
                                  'agent', 'child', 'robot'])
    )
})

# --- Progress ---

cluster_defs.append({
    'cluster_id': 'ai_progress_not_linear',
    'canonical_statement': 'AI progress is not linear or exponential; easy gains come first and fundamental problems remain unsolved.',
    'match': lambda c: (
        has_any(c['claim'], ['progress', 'improvement', 'diminishing', 'plateau', 'slowdown', 'trajectory', 'linear', 'exponential',
                             'logarithmic', 'asymptot', 's-curve', 'easy gains', 'low-hanging fruit', 'rate of progress',
                             'incremental', 'marginal', 'enormous limitation', 'still far', 'long way', 'panacea',
                             'overrated', 'wildly', 'lived up', 'promised', 'never live', 'does not work well',
                             'may never work', 'trillion dollars', 'not remedied', 'all in on',
                             'same experiment', 'repeating', 'hoping', 'fundamental pattern', 'deep learning has hit',
                             'diminishing return', 'deep learning is adequate', 'basic error',
                             'claimed AI breakthrough', 'rarely turn out', 'general enough']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'deep learning']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'job', 'china', 'musk', 'trump',
                                  'openai', 'altman', 'robot', 'code', 'image', 'sora', 'benchmark', 'scaling',
                                  'hallucin', 'reason', 'neurosymbolic', 'agent', 'child', 'copyright', 'surveil',
                                  'election', 'medical', 'legal', 'o1', 'o3', 'gpt-4', 'gpt-5', 'nvidia'])
    )
})

# --- Security ---

cluster_defs.append({
    'cluster_id': 'llm_security_vulnerabilities',
    'canonical_statement': 'LLMs have fundamental security vulnerabilities (prompt injection, jailbreaking) that cannot be fully patched.',
    'match': lambda c: (
        has_any(c['claim'], ['security', 'prompt inject', 'jailbreak', 'hack', 'exploit', 'attack surface', 'vulnerab', 'data extract',
                             'data leak', 'adversarial', 'poison', 'cyberattack', 'cybersecurity', 'cybercrime', 'bypass',
                             'guardrail', 'skin deep', 'elicit harmful', 'bypassed', 'harmful content',
                             'fine-tun', '$300-500', 'political direction']) and
        has_any(c['claim'], ['llm', 'language model', 'gpt', 'ai', 'chatgpt', 'generat', 'agent', 'openai', 'chatbot']) and
        not has_any(c['claim'], ['copyright', 'deepfake', 'election', 'military', 'surveil', 'regulation', 'child', 'musk',
                                  'china', 'trump', 'bubble', 'code', 'robot', 'altman', 'o1', 'o3', 'gpt-4', 'gpt-5',
                                  'scaling', 'benchmark', 'neurosymbolic', 'image generat', 'sora', 'job', 'agent'])
    )
})

# --- Academic integrity ---

cluster_defs.append({
    'cluster_id': 'ai_academic_integrity',
    'canonical_statement': 'AI threatens scientific/academic integrity through plagiarism, fake research, and information pollution.',
    'match': lambda c: (
        has_any(c['claim'], ['academ', 'education', 'university', 'research', 'science', 'peer review', 'plagiar', 'cheating',
                             'paper mill', 'scientific integr', 'scientific communit', 'replicat', 'scientific paper', 'publication',
                             'deep research', 'scientific literature', 'medical information', 'medical misinformation',
                             'internet', 'pollution', 'echo chamber', 'ai-generated content', 'ingest', 'corrupt',
                             'search engine', 'amazon', 'books', 'social media', 'fact-check', 'rational resolution',
                             'public health', 'information space', 'scientific researcher',
                             'Nobel', 'laureate', 'mathematical research', 'IMO',
                             'scientific discovery', 'conceive and execute',
                             'discover all of physics', 'societal benefit', 'medicine, agriculture',
                             'solve', 'battery']) and
        has_any(c['claim'], ['ai', 'llm', 'chatgpt', 'generat', 'gpt', 'deep research', 'technology']) and
        not has_any(c['claim'], ['copyright', 'deepfake', 'bubble', 'military', 'china', 'musk', 'trump',
                                  'openai', 'altman', 'job', 'code', 'sora', 'image', 'robot', 'agent', 'hallucin',
                                  'regulation', 'scaling', 'neurosymbolic', 'o1', 'o3', 'gpt-4', 'gpt-5',
                                  'benchmark', 'nvidia', 'child', 'humanoid', 'driverless'])
    )
})

# --- Self-correction ---

cluster_defs.append({
    'cluster_id': 'llms_lack_self_correction',
    'canonical_statement': 'LLMs cannot reliably verify or self-correct their outputs, a fundamental cognitive limitation.',
    'match': lambda c: (
        has_any(c['claim'], ['self-correct', 'verify', 'self-check', 'sanity-check', 'fact-check', 'check their', 'check its',
                             'validate', 'monitor their', 'know when they', 'detect error', 'detect their', 'correct its own',
                             'correct their own', 'admit ignor', 'admit they cannot', 'overconfiden', 'confident',
                             'internal consistency', 'calibrat', 'metacognit', 'reflect',
                             'evaluate their own', 'evaluate its own', 'instruction follow', 'follow their own',
                             'human oversight', 'humans are still required', 'judge which']) and
        has_any(c['claim'], ['llm', 'language model', 'gpt', 'ai', 'chatgpt', 'generat', 'neural', 'model', 'system']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'china', 'musk', 'trump',
                                  'openai', 'altman', 'code', 'image', 'sora', 'robot', 'job', 'child',
                                  'o1', 'o3', 'gpt-4', 'gpt-5', 'scaling', 'benchmark', 'neurosymbolic',
                                  'agent', 'nvidia', 'driverless'])
    )
})

# --- Generalization ---

cluster_defs.append({
    'cluster_id': 'generalization_failure',
    'canonical_statement': 'LLMs fail to generalize beyond their training distribution, breaking on novel variations of familiar problems.',
    'match': lambda c: (
        has_any(c['claim'], ['generaliz', 'training distribut', 'out-of-distribut', 'unseen', 'new situation', 'unfamiliar',
                             'outlier', 'edge case', 'robustness', 'distribution shift', 'novel input', 'tail case',
                             'training set', 'training data', 'extrapolat', 'specific test item', 'resemble train',
                             'wording', 'brittl', 'data-greedy', 'data greedy', 'data-hungry', 'easy version',
                             'hard version', 'false impression', 'problem size', 'novel', 'unexpected', 'novel scen',
                             'capability gap', 'hundreds', 'millions', 'intellectual task', 'ordinary human',
                             'game playing', 'creative writing', 'video game',
                             'limited generalizability', 'limited general',
                             'deep learning generalization']) and
        has_any(c['claim'], ['llm', 'language model', 'gpt', 'ai', 'neural', 'deep learning', 'generat', 'model', 'chatgpt',
                             'machine learning', 'current', 'Cicero', 'system']) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'job', 'china', 'musk', 'trump', 'sora',
                                  'openai', 'altman', 'code', 'image generat', 'robot', 'child', 'agent', 'hallucin',
                                  'video generat', 'neurosymbolic', 'o1', 'o3', 'gpt-4', 'gpt-5', 'scaling',
                                  'benchmark', 'nvidia', 'medical', 'legal', 'driverless', 'autonomous'])
    )
})

# --- Pause ---

cluster_defs.append({
    'cluster_id': 'ai_pause_or_slowdown',
    'canonical_statement': 'AI development should be paused or slowed until safety and governance frameworks are in place.',
    'match': lambda c: (
        has_any(c['claim'], ['pause', 'slow down', 'moratorium', 'halt', 'stop develop', 'wait until', 'not rush', 'precaution',
                             'go more slowly', 'hold off', 'slow the pace', 'proceed with caution', 'faster than they can handle',
                             'deployed too fast', 'reckless deploy', 'wait to see', 'waiting to see']) and
        has_any(c['claim'], ['ai', 'llm', 'generat', 'develop', 'deploy', 'train', 'tech'])
    ) and not has_any(c['claim'], ['copyright', 'bubble', 'military', 'china', 'musk', 'trump', 'deepfake', 'openai', 'altman'])
})

# --- Catch-all reliability ---

cluster_defs.append({
    'cluster_id': 'llm_reliability_fundamental',
    'canonical_statement': 'LLM unreliability is a fundamental architectural issue, not a bug fixable with more training or RLHF.',
    'match': lambda c: (
        (has_any(c['claim'], ['unreliab', 'reliab', 'inconsisten', 'unpredictab', 'erratic', 'error rate', 'accuracy',
                             'cannot be trusted', 'not trustworth', 'trust', 'unstable', 'stability', 'stochastic',
                             'same prompt', 'change from month', 'difficult to control', 'reckless', 'powerful but',
                             'update difficulty', 'retraining', 'RLHF', 'fine-tun',
                             'basic task', 'basic error', 'persist', 'known problem', 'same categor', 'same fundamental',
                             'same error', 'same flaw', 'mix of brilliance', 'stupid', 'counting', 'states',
                             'safe', 'guarantee', 'formal guarantee', 'engineer', 'complex system',
                             'no way to', 'impossible to predict', 'cannot predict', 'RAG', 'retrieve',
                             'commodit', 'identical', 'similar', 'no moat', 'price war', 'durab', 'copyable',
                             'un-invent', 'proliferat', 'well-understood', 'replicable',
                             'no known technology', 'no compelling', 'not even control',
                             'chatbot', 'Tay', 'Galactica', 'disturbing behavior', 'taken down',
                             'larger language models', 'more likely to cause',
                             'addiction', 'addictive', 'deceiving',
                             'Q*', 'Q star', 'unlikely to be']) and
        has_any(c['claim'], ['llm', 'language model', 'gpt', 'chatgpt', 'ai', 'generat', 'neural', 'chatbot', 'foundation model',
                             'model', 'Bing', 'bing'])) and
        not has_any(c['claim'], ['copyright', 'regulation', 'deepfake', 'bubble', 'military', 'china', 'musk', 'trump', 'job',
                                  'hallucin', 'reason', 'plan', 'world model', 'understand', 'generaliz', 'self-correct',
                                  'agent', 'code', 'image generat', 'sora', 'video', 'medical', 'legal', 'child', 'survey',
                                  'openai', 'altman', 'gpt-4', 'gpt-5', 'robot', 'benchmark', 'neurosymbolic',
                                  'scaling', 'election', 'artist', 'copyright', 'surveil', 'academic', 'science',
                                  'internet', 'pollution', 'o1', 'o3', 'nvidia'])
    )
})

# --- Miscellaneous catch-all (LAST) ---

cluster_defs.append({
    'cluster_id': 'miscellaneous',
    'canonical_statement': 'Miscellaneous claims that do not fit neatly into any other cluster.',
    'match': lambda c: True
})

# ========================================================================
# RUN ASSIGNMENT
# ========================================================================

for c in claims:
    for cdef in cluster_defs:
        try:
            if cdef['match'](c):
                assignments[c['id']] = cdef['cluster_id']
                cluster_claims[cdef['cluster_id']].append(c)
                break
        except Exception as e:
            pass

unassigned = [c for c in claims if c['id'] not in assignments]

print(f"Assigned: {len(assignments)}")
print(f"Unassigned: {len(unassigned)}")
print()
print("Cluster sizes:")
for cid, clist in sorted(cluster_claims.items(), key=lambda x: -len(x[1])):
    print(f"  {cid}: {len(clist)}")

# ========================================================================
# BUILD OUTPUT FILES
# ========================================================================

# Build revision notes with proper goalpost detection
def build_revision_notes(cid, clist):
    if cid == 'miscellaneous' or len(clist) < 3:
        return None

    dates = sorted(set(c['date'] for c in clist))
    early_claims = [c for c in clist if c['date'] <= dates[len(dates)//3]]
    late_claims = [c for c in clist if c['date'] >= dates[2*len(dates)//3]]

    if not early_claims or not late_claims:
        return None

    # Detect language shifts
    strong_terms = ['cannot', 'never', 'will not', 'impossible', 'no way', 'will never', 'zero', 'none']
    hedge_terms = ['may', 'might', 'unlikely', 'probably', 'still', 'remain', 'yet', 'not yet', 'appears']

    early_strong = sum(1 for c in early_claims if has_any(c['claim'], strong_terms))
    late_hedged = sum(1 for c in late_claims if has_any(c['claim'], hedge_terms))
    early_hedged = sum(1 for c in early_claims if has_any(c['claim'], hedge_terms))
    late_strong = sum(1 for c in late_claims if has_any(c['claim'], strong_terms))

    notes_parts = []

    # Check for timeline shifts
    if cid in ['agi_not_imminent', 'gpt5_disappointing', 'genai_bubble_will_burst']:
        for c in clist:
            if has_any(c['claim'], ['pushed back', 'revised', 'delayed', 'moved', 'shift']):
                notes_parts.append(f"Timeline revision detected: '{c['claim'][:80]}...' ({c['date']})")

    # Check for softening/hardening
    if early_strong > len(early_claims) * 0.4 and late_hedged > len(late_claims) * 0.3:
        notes_parts.append(f"Language softened over time: early claims used stronger categorical language ({early_strong}/{len(early_claims)} used strong terms), later claims more hedged ({late_hedged}/{len(late_claims)} used hedge terms)")

    if late_strong > len(late_claims) * 0.4 and early_hedged > len(early_claims) * 0.3:
        notes_parts.append(f"Language hardened over time: earlier claims were more tentative, later claims more categorical")

    # Always note the span
    notes_parts.append(f"Asserted {len(clist)} times across {len(dates)} distinct dates from {dates[0]} to {dates[-1]}")

    return ". ".join(notes_parts) if notes_parts else None


# File 1: clusters.json
clusters_output = []
for cdef in cluster_defs:
    cid = cdef['cluster_id']
    if cid not in cluster_claims or len(cluster_claims[cid]) == 0:
        continue

    clist = cluster_claims[cid]
    dates = sorted([c['date'] for c in clist])

    clusters_output.append({
        'cluster_id': cid,
        'canonical_statement': cdef['canonical_statement'],
        'first_appearance': clist[0]['id'],
        'claim_count': len(clist),
        'date_range': [dates[0], dates[-1]],
        'revision_notes': build_revision_notes(cid, clist)
    })

# Sort by claim count descending
clusters_output.sort(key=lambda x: -x['claim_count'])

with open('/Users/davidgoldblatt/Desktop/marcus_scrape/clusters.json', 'w') as f:
    json.dump(clusters_output, f, indent=2)

print(f"\nWrote {len(clusters_output)} clusters to clusters.json")

# File 2: claim_clusters.jsonl
with open('/Users/davidgoldblatt/Desktop/marcus_scrape/claim_clusters.jsonl', 'w') as f:
    for c in claims:
        cid = assignments.get(c['id'], 'miscellaneous')
        f.write(json.dumps({'id': c['id'], 'cluster_id': cid}) + '\n')

print(f"Wrote {len(claims)} assignments to claim_clusters.jsonl")

# Validation
assert len(assignments) == len(claims), f"Missing assignments: {len(claims) - len(assignments)}"
total_in_clusters = sum(len(v) for v in cluster_claims.values())
assert total_in_clusters == len(claims), f"Claims in clusters: {total_in_clusters}, total: {len(claims)}"
print("\nValidation passed: all 2218 claims assigned.")

# Count non-misc
non_misc = sum(1 for cid in assignments.values() if cid != 'miscellaneous')
print(f"Non-miscellaneous: {non_misc} ({non_misc/len(claims)*100:.1f}%)")
print(f"Miscellaneous: {len(claims) - non_misc} ({(len(claims)-non_misc)/len(claims)*100:.1f}%)")
