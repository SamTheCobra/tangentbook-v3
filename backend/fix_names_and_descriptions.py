"""
Fix broken startup names, placeholder entries, and empty equity bet descriptions.

Handles 3 categories:
1. Dash names: "Effect Title Truncated — ActualName" -> extract "ActualName"
2. Venture placeholders: "EffectVentureN" -> generate proper name + one-liner from context
3. Empty equity bet descriptions: fill with 2-sentence descriptions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import StartupOpportunity, EquityBet, Effect, Thesis


# ── EQUITY BET DESCRIPTIONS (for bets with empty company_description) ──

EQUITY_DESCRIPTIONS = {
    "FCX": "World's largest publicly traded copper producer with major mines in Arizona, Peru, and Indonesia. Copper prices track real-asset demand and industrial inflation, making it a key canary for commodity-driven debasement.",
    "VRT": "Designs and manufactures critical digital infrastructure — power, cooling, and IT management systems for data centers. Every new AI server rack needs Vertiv's thermal management and power distribution.",
    "ANET": "Builds high-speed networking switches and software for cloud data centers and campus networks. Networking spend is a leading indicator of AI infrastructure buildout velocity.",
    "COUR": "Online learning platform offering courses from top universities and companies worldwide. Direct beneficiary as workers reskill through career transitions and employers shift from degree requirements to skills-based hiring.",
    "UPWK": "Largest freelance talent marketplace connecting businesses with independent professionals. Captures demand as reskilled workers find new gig-economy roles and companies embrace flexible hiring.",
    "LOPE": "Operates Grand Canyon University, a large private university in Phoenix. Traditional 4-year degree model faces disruption as employers increasingly accept bootcamp certs and micro-credentials.",
    "CEG": "Largest operator of nuclear power plants in the US with 13 stations across multiple states. Nuclear is the only scalable carbon-free baseload power source capable of meeting surging grid demand from AI and electrification.",
    "GNRC": "Leading manufacturer of backup power generators and energy storage systems for residential and commercial use. Grid bottlenecks mean more blackouts and instability, driving massive demand for distributed backup power.",
    "LYV": "World's largest live entertainment company operating Ticketmaster and promoting concerts globally. Live experiences are the anti-AI-slop — you can't fake a concert, making them the ultimate authenticity premium.",
    "ETSY": "Online marketplace focused on handmade, vintage, and unique goods from independent sellers. Human provenance becomes a premium label as AI-generated content floods other platforms.",
    "ENSG": "Operates skilled nursing facilities and senior living communities across the US. Captures the care delivery side of the senior population boom as the 65+ demographic surges.",
    "BIRK": "German heritage footwear brand known for cork-footbed sandals that became a global fashion staple. Affordable premium positioning hits the sweet spot of the micro-luxury trade-down from expensive brands.",
    "DUOL": "Language learning app with 100M+ monthly active users using gamification and AI tutoring. Micro-investment in skills represents affordable self-improvement as a form of accessible luxury.",
    "MNST": "Largest energy drink company by US market share with brands including Monster and Reign. Faces headwinds as sleep becomes a status symbol and caffeine consumption gets reframed as unhealthy.",
    "GRMN": "Makes GPS-enabled fitness watches, outdoor handhelds, and marine electronics. Anti-screen beneficiary as consumers seek outdoor fitness hardware over phone-based experiences.",
}


# ── STARTUP NAME/DESCRIPTION MAPPINGS BY EFFECT CONTEXT ──
# For EffectVenture placeholders: map effect title -> list of (name, one_liner, timing)

VENTURE_REPLACEMENTS = {
    "Caffeine Becomes the New Cigarette": [
        ("Decaf Performance Labs", "Formulates nootropic blends that deliver focus and alertness without caffeine or stimulants.", "RIGHT_TIMING"),
    ],
    "Employers Start Mandating Rest": [
        ("RestMetrics", "Workforce analytics platform measuring employee recovery and sleep quality to optimize productivity schedules.", "RIGHT_TIMING"),
    ],
    "The Master Bedroom Becomes a $50K Room": [
        ("SleepSpace Design", "Residential sleep environment consultancy combining acoustic engineering, lighting, and climate control.", "RIGHT_TIMING"),
    ],
    "Paper and Film Supply Can't Keep Up": [
        ("AnalogSupply Co", "Specialty manufacturer scaling production of photographic film, darkroom paper, and analog media supplies.", "RIGHT_TIMING"),
    ],
    "Third Places Make a Physical Comeback": [
        ("Gathering Spaces", "Membership-based co-working and social spaces designed around analog activities — board games, vinyl, crafts.", "RIGHT_TIMING"),
    ],
    "DeFi Replaces Traditional Banking": [
        ("YieldBridge", "Compliance-first DeFi lending protocol that wraps institutional-grade risk management around on-chain yield.", "RIGHT_TIMING"),
        ("ChainBank", "Neobank built entirely on DeFi rails — checking, savings, and lending without traditional banking infrastructure.", "RIGHT_TIMING"),
    ],
    "Bitcoin Mining Industrializes": [
        ("MineHost", "Turnkey hosting service for institutional Bitcoin miners — site selection, power contracts, and operations.", "RIGHT_TIMING"),
    ],
    "Farmland and Timber Become Institutional Assets": [
        ("AcreIndex", "Fractional farmland investment platform giving retail investors access to institutional-quality agricultural land.", "RIGHT_TIMING"),
        ("TimberFi", "Digital marketplace for timber rights and sustainable forestry investments with carbon credit integration.", "TOO_EARLY"),
    ],
    "Housing Affordability Crisis Deepens": [
        ("SharedEquity", "Co-ownership platform splitting home purchases between occupants and investors to lower entry barriers.", "RIGHT_TIMING"),
    ],
    "Ultra-Processed Food Regulation Wave": [
        ("CleanLabel Analytics", "SaaS tool helping food brands reformulate products to comply with emerging ultra-processed food regulations.", "RIGHT_TIMING"),
        ("Ingredient Swap", "B2B marketplace connecting food manufacturers with clean-label ingredient suppliers for reformulation.", "RIGHT_TIMING"),
    ],
    "Functional Food Premium Emerges": [
        ("AdaptogenKitchen", "Consumer brand making functional snacks and beverages with adaptogens, nootropics, and gut-health ingredients.", "RIGHT_TIMING"),
        ("NutriScore Pro", "White-label functional food formulation platform for CPG brands wanting to add health claims.", "CROWDING"),
    ],
    "Hospital Revenue Model Restructuring": [
        ("OutpatientOS", "Revenue cycle management software purpose-built for hospitals transitioning from inpatient to outpatient models.", "RIGHT_TIMING"),
        ("CareShift Analytics", "Predictive analytics helping hospitals model revenue impact of shifting procedures to ambulatory settings.", "RIGHT_TIMING"),
    ],
    "Athleisure Becomes Default Wardrobe": [
        ("FitFabric", "Performance textile mill producing next-gen stretch fabrics for athleisure brands at scale.", "CROWDING"),
        ("WorkFit Studio", "Made-to-measure athleisure for professional settings — looks like office wear, feels like gym clothes.", "RIGHT_TIMING"),
    ],
    "Crypto Becomes Mainstream Store of Value": [
        ("StableYield", "Inflation-indexed savings product for retail users built on stablecoin rails with FDIC-style insurance.", "RIGHT_TIMING"),
    ],
    "Real Assets Become Inflation Shelter": [
        ("RealAsset Index", "ETF-like product tracking a diversified basket of real assets — farmland, timber, gold, infrastructure.", "RIGHT_TIMING"),
    ],
    "Gold-Backed Stablecoins Go Mainstream": [
        ("GoldRail Payments", "Cross-border B2B payment network settling transactions in gold-backed digital tokens.", "TOO_EARLY"),
        ("Mint Protocol", "Platform for issuing custom commodity-backed tokens with built-in auditing and reserve verification.", "TOO_EARLY"),
    ],
    "BRICS Currency Backed by Commodities": [
        ("ReserveOS", "Treasury management platform helping corporations hedge FX exposure using commodity-backed reserve instruments.", "TOO_EARLY"),
    ],
    # AI & Compute
    "AI Chip Demand Outpaces Supply": [
        ("ChipBroker", "Secondary market for AI accelerators — matching sellers of used GPUs with compute-starved startups.", "RIGHT_TIMING"),
    ],
    "Edge AI Becomes Default": [
        ("EdgeRuntime", "Lightweight inference engine optimized for running AI models on consumer devices and IoT hardware.", "RIGHT_TIMING"),
    ],
    "AI Training Data Becomes Scarce": [
        ("SynthData Labs", "Generates high-quality synthetic training data for AI models, reducing reliance on real-world data collection.", "RIGHT_TIMING"),
    ],
    "AI Agents Replace SaaS Workflows": [
        ("AgentOps", "Monitoring and orchestration platform for autonomous AI agents running enterprise workflows.", "RIGHT_TIMING"),
    ],
    "Sovereign AI Programs Emerge": [
        ("NationStack", "Consulting and infrastructure firm helping governments build domestic AI compute capacity.", "TOO_EARLY"),
    ],
    # Energy & Grid
    "Grid Bottleneck Becomes National Security Issue": [
        ("GridMap Intelligence", "Real-time grid congestion analytics and capacity planning for utilities and energy developers.", "RIGHT_TIMING"),
    ],
    "Small Modular Reactors Get Fast-Tracked": [
        ("SMR Site Services", "Site preparation and licensing consultancy specialized in small modular reactor deployments.", "TOO_EARLY"),
    ],
    "Behind-the-Meter Generation Explodes": [
        ("MicroGrid Systems", "Turnkey microgrid solutions for commercial buildings combining solar, battery, and generator assets.", "RIGHT_TIMING"),
    ],
    "Industrial Electrification Accelerates": [
        ("ElectrifyIQ", "Software platform helping industrial facilities plan and execute electrification of gas-powered processes.", "RIGHT_TIMING"),
    ],
    "Energy Storage Becomes Grid-Scale": [
        ("StorageStack", "Development platform for utility-scale battery storage projects — from site selection to interconnection.", "RIGHT_TIMING"),
    ],
    # Longevity & Healthcare
    "Longevity Biotech Pipeline Explodes": [
        ("LongevityScreen", "Consumer diagnostics platform measuring biological age markers and tracking intervention effectiveness.", "RIGHT_TIMING"),
    ],
    "Health Insurance Reprices for Longevity": [
        ("ActuarialAI", "Machine learning platform helping insurers reprice life and health products for longer lifespans.", "TOO_EARLY"),
    ],
    "Senior Housing Shortage Hits": [
        ("SilverNest", "Platform matching seniors with compatible housemates to solve housing affordability and isolation.", "RIGHT_TIMING"),
    ],
    "Preventive Care Becomes Profitable": [
        ("PreventPay", "Value-based care payment platform that rewards providers for keeping patients healthy, not treating illness.", "RIGHT_TIMING"),
    ],
    "Anti-Aging Consumer Market Matures": [
        ("AgeWell Brands", "Direct-to-consumer longevity supplements with clinical-grade formulations and transparent dosing.", "CROWDING"),
    ],
    # GLP-1
    "Bariatric Surgery Volumes Collapse": [
        ("MetabolicMatch", "Platform connecting GLP-1 patients with metabolic health coaches for medication optimization.", "RIGHT_TIMING"),
    ],
    "Grocery Basket Composition Shifts": [
        ("BasketShift Analytics", "SaaS for grocery retailers modeling how GLP-1 adoption changes purchasing patterns by store and region.", "RIGHT_TIMING"),
    ],
    "Fitness Industry Restructures": [
        ("LeanFit Studios", "Boutique fitness concept designed for GLP-1 users — lower intensity, muscle preservation focus.", "RIGHT_TIMING"),
    ],
    "Restaurant Portions Shrink": [
        ("PortionOS", "Menu engineering software helping restaurants redesign portions and pricing for appetite-reduced diners.", "RIGHT_TIMING"),
    ],
    "Life Insurance Repricing": [
        ("RiskRecalc", "Underwriting analytics platform helping life insurers model GLP-1 impact on mortality tables.", "TOO_EARLY"),
    ],
    # Reskilling
    "Credentialing Fragments Beyond Degrees": [
        ("CredStack", "Portable digital credential wallet that verifies and displays micro-credentials from any issuer.", "RIGHT_TIMING"),
    ],
    "Corporate Training Budgets Explode": [
        ("SkillBudget", "Workforce L&D planning tool that allocates training budgets based on skill gap analysis and ROI projections.", "RIGHT_TIMING"),
    ],
    "Gig Economy Absorbs Career Changers": [
        ("GigBridge", "Talent marketplace specifically matching career changers with transitional gig work in their target industry.", "RIGHT_TIMING"),
    ],
    "Traditional Universities Lose Market Share": [
        ("CampusAlt", "Curated marketplace of bootcamps, apprenticeships, and micro-degree programs as university alternatives.", "CROWDING"),
    ],
    "Blue Collar Skills Premium Returns": [
        ("TradeUp", "Apprenticeship matching platform connecting tradespeople with training programs and employers.", "RIGHT_TIMING"),
    ],
    # Sleep Economy
    "Sleep Tech Becomes Medical Grade": [
        ("SleepRx", "Prescription-grade sleep monitoring device bridging consumer wearables and clinical polysomnography.", "RIGHT_TIMING"),
    ],
    "Corporate Wellness Adds Sleep": [
        ("RestScore", "Enterprise sleep wellness platform integrating with HR systems to measure and improve workforce rest.", "RIGHT_TIMING"),
    ],
    "Circadian Lighting Goes Mainstream": [
        ("CircadianHome", "Residential circadian lighting systems that automatically adjust color temperature throughout the day.", "RIGHT_TIMING"),
    ],
    "Sleep Tourism Emerges": [
        ("DreamRetreat", "Luxury sleep retreat booking platform curating hotels and resorts with clinical-grade sleep environments.", "RIGHT_TIMING"),
    ],
    # Physical Revival
    "Record Stores Become Community Hubs": [
        ("Wax Social", "Franchise concept combining record store, listening bar, and event space for vinyl community.", "RIGHT_TIMING"),
    ],
    "Film Photography Has a Renaissance": [
        ("DarkroomDoor", "Network of shared darkroom facilities with equipment rental and classes for film photography enthusiasts.", "RIGHT_TIMING"),
    ],
    "Print Media Commands Premium": [
        ("PressClub", "Subscription platform curating premium independent print magazines and zines.", "RIGHT_TIMING"),
    ],
    "Board Game Cafes Scale": [
        ("GameTable", "Board game cafe franchise with standardized operations, curated libraries, and membership programs.", "CROWDING"),
    ],
    # Luxury Repricing
    "Quiet Luxury Permanently Displaces Logo Culture": [
        ("Discreet", "Personal styling platform specializing in quiet luxury — curating understated premium brands.", "CROWDING"),
    ],
    "Luxury Authentication Tech Becomes Industry": [
        ("VerifyLux", "Phone-based AI authentication service verifying luxury goods via computer vision and blockchain provenance.", "RIGHT_TIMING"),
    ],
    "Luxury Rental Market Explodes": [
        ("RentTheIcon", "Luxury item rental platform — wear designer pieces for a weekend without the permanent price tag.", "RIGHT_TIMING"),
    ],
    "Vintage Luxury Outperforms New": [
        ("VintageVault", "Curated vintage luxury marketplace with professional authentication, grading, and condition reporting.", "RIGHT_TIMING"),
    ],
    "Micro-Luxury Replaces Aspirational Spending": [
        ("TreatWell", "Subscription curation of micro-luxury experiences — premium coffees, artisan goods, small indulgences.", "CROWDING"),
    ],
    # Chip Wars
    "Semiconductor Stockpiling Becomes Policy": [
        ("ChipReserve Advisory", "Strategic advisory firm helping nations design and manage semiconductor stockpile programs.", "TOO_EARLY"),
    ],
    "Chip Design Onshoring Accelerates": [
        ("FabSite", "Site selection and permitting platform for semiconductor fabrication facility construction.", "RIGHT_TIMING"),
    ],
    "Legacy Chip Shortage Worsens": [
        ("LegacyChip Exchange", "Brokerage platform for legacy semiconductor components serving automotive and industrial buyers.", "RIGHT_TIMING"),
    ],
    "RISC-V Adoption Accelerates": [
        ("RISC-V Studio", "Development tools and IP licensing platform accelerating RISC-V chip design for commercial applications.", "TOO_EARLY"),
    ],
    "Export Controls Reshape Supply Chains": [
        ("TradeCompliance AI", "Automated export control compliance platform for semiconductor companies navigating sanctions.", "RIGHT_TIMING"),
    ],
    # Authenticity Premium
    "Human-Made Label Becomes Standard": [
        ("ProvenHuman", "Certification and labeling service verifying human-created content, art, and products.", "RIGHT_TIMING"),
    ],
    "AI Detection Industry Emerges": [
        ("DetectAI", "Enterprise content authentication platform detecting AI-generated text, images, and video.", "RIGHT_TIMING"),
    ],
    "Creator Economy Bifurcates": [
        ("Artisan Platform", "Marketplace exclusively for verified human creators with AI-detection built into uploads.", "RIGHT_TIMING"),
    ],
    "Experience Premium Over Digital Widens": [
        ("RealExperience Co", "Curated platform for verified analog and in-person experiences — classes, workshops, retreats.", "RIGHT_TIMING"),
    ],
    # US Reshoring
    "Factory Construction Boom": [
        ("FactorySite", "Industrial real estate platform specializing in greenfield manufacturing site selection and development.", "RIGHT_TIMING"),
    ],
    "Automation Premium for Domestic Manufacturing": [
        ("AutomateUS", "Turnkey factory automation integrator helping reshored manufacturers deploy robotics at competitive cost.", "RIGHT_TIMING"),
    ],
    "Skilled Trades Shortage Deepens": [
        ("TradeReady", "Accelerated trades training platform combining VR simulation with on-site apprenticeship placement.", "RIGHT_TIMING"),
    ],
    "Supply Chain Transparency Mandates": [
        ("OriginTrace", "Supply chain provenance platform providing end-to-end visibility from raw materials to finished goods.", "RIGHT_TIMING"),
    ],
    "Regional Manufacturing Clusters Form": [
        ("ClusterMap", "Economic development platform helping regions attract and coordinate manufacturing cluster formation.", "TOO_EARLY"),
    ],
    # Multipolar World
    "Reserve Currency Diversification Accelerates": [
        ("FXShield", "Multi-currency treasury management for companies hedging away from dollar-denominated reserves.", "RIGHT_TIMING"),
    ],
    "Trade Bloc Fragmentation": [
        ("BlocTrade Analytics", "Trade intelligence platform mapping shifting trade bloc alignments and tariff regime changes.", "RIGHT_TIMING"),
    ],
    "Technology Standards Fork": [
        ("DualStack", "Consulting firm helping tech companies maintain products across diverging US/China/EU technology standards.", "RIGHT_TIMING"),
    ],
    "Commodity Trade Rerouting": [
        ("FlowMap", "Commodity logistics platform optimizing trade routes around sanctions and bloc-based restrictions.", "RIGHT_TIMING"),
    ],
    "Defense Spending Supercycle": [
        ("DefenseTech Foundry", "Venture studio building dual-use defense technology startups for allied nations.", "RIGHT_TIMING"),
    ],
}

# Generic fallback for effect contexts not in the map
GENERIC_BY_THEME = {
    "usd": ("MacroShield", "Platform helping retail investors build inflation-protected portfolios using hard assets and commodity exposure.", "RIGHT_TIMING"),
    "ai": ("ModelOps", "Infrastructure platform for deploying, monitoring, and scaling AI models in production environments.", "RIGHT_TIMING"),
    "energy": ("PowerPath", "Energy project development platform streamlining permitting and interconnection for distributed generation.", "RIGHT_TIMING"),
    "glp": ("MetabolicHealth Hub", "Digital health platform coordinating GLP-1 treatment with nutrition, fitness, and metabolic monitoring.", "RIGHT_TIMING"),
    "reskill": ("SkillPath", "Career transition platform matching workers with reskilling programs and employers in growing industries.", "RIGHT_TIMING"),
    "sleep": ("RestWell Systems", "Integrated sleep improvement platform combining hardware, software, and coaching for better rest.", "RIGHT_TIMING"),
    "physical": ("Analog Co", "Retail concept celebrating physical media and analog experiences in a digital-saturated world.", "RIGHT_TIMING"),
    "luxury": ("Curated Luxe", "Personal shopping platform specializing in value-driven luxury — vintage, rental, and quiet luxury curation.", "RIGHT_TIMING"),
    "chip": ("SemiStack", "Supply chain intelligence platform for semiconductor procurement and inventory optimization.", "RIGHT_TIMING"),
    "authentic": ("HumanProof", "Content and product certification service verifying human creation and provenance.", "RIGHT_TIMING"),
    "reshor": ("MadeHere", "B2B marketplace connecting domestic manufacturers with brands looking to reshore production.", "RIGHT_TIMING"),
    "multipolar": ("GeoRisk Analytics", "Geopolitical risk assessment platform for supply chain and investment decision-making.", "RIGHT_TIMING"),
    "longevity": ("Lifespan Labs", "Consumer health platform offering longevity biomarker testing and personalized intervention plans.", "RIGHT_TIMING"),
    "senior": ("ElderTech", "Technology platform improving quality of life for aging populations through connected health and social tools.", "RIGHT_TIMING"),
    "health": ("WellnessOS", "Integrated health management platform bridging preventive care, diagnostics, and treatment coordination.", "RIGHT_TIMING"),
    "food": ("FoodTech Platform", "Technology platform helping food companies reformulate products for emerging health and regulatory standards.", "RIGHT_TIMING"),
    "defense": ("ShieldTech", "Dual-use technology development platform serving both defense and commercial applications.", "RIGHT_TIMING"),
    "crypto": ("CryptoRails", "Institutional-grade cryptocurrency infrastructure for compliant trading, custody, and settlement.", "RIGHT_TIMING"),
    "defi": ("DeFi Bridge", "Compliance-wrapped DeFi access layer for traditional financial institutions entering on-chain markets.", "TOO_EARLY"),
}


def fix_dash_names(db):
    """Fix names like 'Effect Title Truncated — ActualName' -> 'ActualName'"""
    startups = db.query(StartupOpportunity).filter(
        StartupOpportunity.name.like('%—%')
    ).all()

    fixed = 0
    for s in startups:
        parts = s.name.split('—')
        if len(parts) >= 2:
            actual_name = parts[-1].strip()
            if actual_name:
                s.name = actual_name
                fixed += 1

    db.commit()
    print(f"Fixed {fixed} dash-pattern names")
    return fixed


def fix_venture_placeholders(db):
    """Fix 'EffectVentureN' and 'ThesisVentureN' placeholder names."""
    ventures = db.query(StartupOpportunity).filter(
        StartupOpportunity.name.like('%Venture%')
    ).all()

    fixed = 0
    used_names = set()  # Track names used per effect to avoid duplicates

    for v in ventures:
        effect = None
        thesis = None
        context = ""

        if v.effect_id:
            effect = db.query(Effect).filter(Effect.id == v.effect_id).first()
            if effect:
                context = effect.title
                thesis = db.query(Thesis).filter(Thesis.id == effect.thesis_id).first()
        elif v.thesis_id:
            thesis = db.query(Thesis).filter(Thesis.id == v.thesis_id).first()
            if thesis:
                context = thesis.title

        # Try exact match first
        replacements = VENTURE_REPLACEMENTS.get(context, [])

        # Find an unused replacement
        replacement = None
        for r in replacements:
            key = f"{context}:{r[0]}"
            if key not in used_names:
                replacement = r
                used_names.add(key)
                break

        if not replacement:
            # Try generic fallback by matching thesis keywords
            thesis_title = (thesis.title if thesis else context).lower()
            for keyword, fallback in GENERIC_BY_THEME.items():
                if keyword in thesis_title:
                    key = f"generic:{fallback[0]}:{context}"
                    if key not in used_names:
                        replacement = fallback
                        used_names.add(key)
                        break

        if replacement:
            v.name = replacement[0]
            v.one_liner = replacement[1]
            v.timing = replacement[2]
            fixed += 1
        else:
            # Last resort: generate from context
            if context:
                # Create a plain descriptive name from the effect context
                words = context.split()[:3]
                plain_name = " ".join(words) + " Platform"
                v.name = plain_name
                v.one_liner = f"Technology platform addressing opportunities created by {context.lower()}."
                fixed += 1

    db.commit()
    print(f"Fixed {fixed} venture placeholder names (of {len(ventures)} total)")
    return fixed


def fix_empty_descriptions(db):
    """Fill empty equity bet company descriptions."""
    bets = db.query(EquityBet).filter(EquityBet.company_description == '').all()

    fixed = 0
    for b in bets:
        desc = EQUITY_DESCRIPTIONS.get(b.ticker)
        if desc:
            b.company_description = desc
            fixed += 1
        else:
            # Generate from company name and rationale
            if b.company_name and b.rationale:
                b.company_description = f"{b.company_name} — {b.rationale}"
                fixed += 1

    db.commit()
    print(f"Fixed {fixed} empty equity bet descriptions (of {len(bets)} total)")
    return fixed


def main():
    db = SessionLocal()
    try:
        print("=== Fixing startup names and descriptions ===\n")

        n1 = fix_dash_names(db)
        n2 = fix_venture_placeholders(db)
        n3 = fix_empty_descriptions(db)

        print(f"\n=== Done: {n1 + n2 + n3} total fixes ===")

        # Verify
        bad_dash = db.query(StartupOpportunity).filter(StartupOpportunity.name.like('%—%')).count()
        bad_venture = db.query(StartupOpportunity).filter(StartupOpportunity.name.like('%Venture%')).count()
        bad_desc = db.query(EquityBet).filter(EquityBet.company_description == '').count()
        print(f"\nRemaining issues: dash={bad_dash}, venture={bad_venture}, empty_desc={bad_desc}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
