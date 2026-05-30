"""SalesPilot AI — Intent Scoring Agent.

AI-powered weighted buying intent score from funding, hiring, tech adoption,
competitor dissatisfaction, and expansion signals. Fully explainable.
"""

import json
from app.models.schemas import (
    BuyingIntentScore,
    SignalBreakdown,
    CompanyProfile,
    HiringSignals,
    FundingNews,
    TechStack,
    PainPoints,
    CompetitorIntel,
)
from app.services.llm import get_llm_service


SYSTEM_PROMPT = """You are an expert B2B buying intent scoring analyst. Given research data from
multiple intelligence sources about a company, calculate a buying intent score from 0 to 100.

Use this weighted scoring framework:
- Funding signals (25%): Recent funding = budget available, higher score
- Hiring signals (20%): Active hiring, especially sales/ops roles = growth phase
- Tech adoption gaps (20%): Missing tools or outdated stack = opportunity
- Competitor dissatisfaction (15%): Pricing complaints, migration signals = displacement chance
- Growth/expansion signals (10%): New markets, products, partnerships = budget allocation
- Pain points severity (10%): Operational frustrations = urgent need

For EACH signal category, provide:
- A score from 0-100
- The weight (as decimal, e.g. 0.25)
- The weighted_score (score * weight)
- Specific evidence bullets from the research data

The overall_score should be the sum of all weighted_scores, rounded to nearest integer.
Set confidence to "high" if 4+ signals have strong evidence, "medium" for 2-3, "low" for 0-1.
Provide top_reasons as 3-5 human-readable sentences explaining why this score.

CRITICAL: Be transparent and explainable. This is NOT a black box — judges need to see the reasoning."""


async def run_intent_scoring_agent(
    company_profile: CompanyProfile,
    hiring_signals: HiringSignals,
    funding_news: FundingNews,
    tech_stack: TechStack,
    pain_points: PainPoints,
    competitor_intel: CompetitorIntel,
) -> BuyingIntentScore:
    """Calculate explainable buying intent score from all research signals."""
    llm = get_llm_service()

    # Compact summary to stay within free-tier token limits (~1500 tokens)
    research_summary = f"""COMPANY: {company_profile.name} | {company_profile.industry} | {company_profile.employee_count} employees | {company_profile.business_model}
KEY FACTS: {', '.join(company_profile.key_facts[:3])}

HIRING: {hiring_signals.total_open_roles} open roles | velocity: {hiring_signals.hiring_velocity} | depts: {', '.join(hiring_signals.departments_hiring[:4])}
GROWTH FLAGS: {', '.join(hiring_signals.growth_intent_flags[:3])}

FUNDING: {funding_news.latest_round} | total: {funding_news.total_funding} | investors: {', '.join(funding_news.investors[:3])}
RECENT NEWS: {'; '.join([e.get('title','') for e in ([ev.__dict__ if hasattr(ev,'__dict__') else ev for ev in funding_news.events[:2]])])}

TECH GAPS: {', '.join(tech_stack.potential_gaps[:3])}
CURRENT TOOLS: {', '.join([t.get('name','') if isinstance(t,dict) else getattr(t,'name','') for t in tech_stack.current_tools[:5]])}

PAIN POINTS: {'; '.join([p.get('description','') if isinstance(p,dict) else getattr(p,'description','') for p in pain_points.pain_points[:3]])}

COMPETITORS: {', '.join([v.get('name','') if isinstance(v,dict) else getattr(v,'name','') for v in competitor_intel.current_vendors[:4]])}
DISPLACEMENT: {', '.join(competitor_intel.displacement_opportunities[:2])}
MIGRATION SIGNALS: {', '.join(competitor_intel.migration_signals[:2])}
"""

    result = await llm.analyze(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=f"Calculate the buying intent score for this company:\n\n{research_summary}",
        response_model=BuyingIntentScore,
    )

    # Return None if scoring failed (empty model with default 0 score)
    if result.overall_score == 0 and not result.breakdown:
        return None
    return result
