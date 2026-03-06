"""Fill gaps: ensure every thesis has 3 2nd-order effects, each with 3 bets, 3 opps, 3 3rd-order effects.
Each 3rd-order effect gets 2 bets and 2 opps."""

import sys
sys.path.insert(0, ".")

from database import SessionLocal
from models import Thesis, Effect, EquityBet, StartupOpportunity
import uuid

db = SessionLocal()

def uid():
    return str(uuid.uuid4())

# ── MISSING 2ND ORDER EFFECTS ─────────────────────────────────────────────
# Theses that have only 2 2nd-order effects need 1 more
MISSING_2ND = {
    "thesis_ai_infrastructure": {
        "title": "AI Compute Shifts to Edge & Inference",
        "description": "As training costs plateau, the bottleneck moves to inference at the edge — embedded AI in devices, vehicles, and factories rather than centralized cloud.",
        "bets": [
            {"ticker": "QCOM", "companyName": "Qualcomm", "companyDescription": "Mobile chip giant pivoting to on-device AI inference for smartphones, vehicles, and IoT.", "role": "BENEFICIARY", "rationale": "Edge AI chip leader — directly benefits from inference moving to devices"},
            {"ticker": "INTC", "companyName": "Intel", "companyDescription": "Legacy chipmaker betting on AI PC chips and edge inference accelerators to regain relevance.", "role": "CANARY", "rationale": "Intel's AI PC traction signals whether edge inference is real or hype"},
            {"ticker": "WOLF", "companyName": "Wolfspeed", "companyDescription": "Silicon carbide semiconductor maker enabling power-efficient computing for edge AI applications.", "role": "BENEFICIARY", "rationale": "Power-efficient chips are essential as AI moves to battery-powered edge devices"},
        ],
        "opps": [
            {"name": "EdgeML Studio", "oneLiner": "No-code platform for deploying ML models to edge devices with one click.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "InferenceOS", "oneLiner": "Operating system layer that intelligently routes AI queries between on-device and cloud.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "TinyModel Hub", "oneLiner": "Marketplace for optimized, compressed AI models designed specifically for edge hardware.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
        ],
    },
    "thesis_cognitive_decline": {
        "title": "Brain Training & Cognitive Supplements Boom",
        "description": "Fear of cognitive decline drives explosive demand for nootropics, brain training apps, and cognitive health supplements.",
        "bets": [
            {"ticker": "PRCH", "companyName": "Porch Group", "companyDescription": "Home services platform. Cognitive decline drives demand for aging-in-place home modifications.", "role": "BENEFICIARY", "rationale": "Aging-in-place modifications become essential as cognitive decline awareness grows"},
            {"ticker": "HIMS", "companyName": "Hims & Hers Health", "companyDescription": "Telehealth platform expanding into cognitive health supplements and brain optimization.", "role": "BENEFICIARY", "rationale": "DTC telehealth positioned to sell cognitive supplements at scale"},
            {"ticker": "NFLX", "companyName": "Netflix", "companyDescription": "Streaming giant whose usage patterns serve as a canary for passive screen consumption trends.", "role": "HEADWIND", "rationale": "If brain health fears grow, passive binge-watching faces cultural backlash"},
        ],
        "opps": [
            {"name": "NeuroPulse", "oneLiner": "Wearable that tracks cognitive performance metrics and suggests daily brain exercises.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "FocusStack", "oneLiner": "Personalized nootropic subscription based on cognitive biomarker testing.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "DeepRead", "oneLiner": "App that gamifies deep reading to rebuild attention spans damaged by social media.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
        ],
    },
    "thesis_senior_living": {
        "title": "Home Health Tech for Aging in Place",
        "description": "Most seniors want to age at home, not in facilities. Smart home health monitoring and remote care tech fills the gap between independence and institutional care.",
        "bets": [
            {"ticker": "AAPL", "companyName": "Apple", "companyDescription": "Apple Watch health monitoring features increasingly target fall detection, heart monitoring, and senior safety.", "role": "BENEFICIARY", "rationale": "Apple Watch as senior health monitor — fall detection, vitals tracking"},
            {"ticker": "AMZN", "companyName": "Amazon", "companyDescription": "Alexa smart home ecosystem enables voice-controlled home management for mobility-limited seniors.", "role": "BENEFICIARY", "rationale": "Alexa ecosystem enables aging-in-place through voice-controlled home management"},
            {"ticker": "GOOG", "companyName": "Alphabet", "companyDescription": "Google Health and Nest smart home products create an ambient monitoring environment for seniors.", "role": "CANARY", "rationale": "Google's health AI investments signal whether ambient monitoring is commercially viable"},
        ],
        "opps": [
            {"name": "SilverNest AI", "oneLiner": "AI-powered home monitoring system that detects anomalies in daily routines of elderly residents.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "MedPal", "oneLiner": "Smart pill dispenser with video verification and family notification for medication adherence.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "CareCircle", "oneLiner": "Coordination platform connecting families, home health aides, and physicians for distributed elder care.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
        ],
    },
    "thesis_electricity_bottleneck": {
        "title": "Grid Modernization & Smart Grid Tech",
        "description": "The current grid was built for one-way power flow. Two-way flows from solar, EVs, and batteries require a complete intelligence overhaul.",
        "bets": [
            {"ticker": "ITRI", "companyName": "Itron", "companyDescription": "Smart grid infrastructure company making meters, sensors, and grid analytics software.", "role": "BENEFICIARY", "rationale": "Smart meters and grid sensors are the foundation of grid modernization"},
            {"ticker": "ENPH", "companyName": "Enphase Energy", "companyDescription": "Microinverter and battery company enabling distributed energy at the home level.", "role": "BENEFICIARY", "rationale": "Distributed energy requires intelligent microinverters at every node"},
            {"ticker": "ETN", "companyName": "Eaton", "companyDescription": "Power management company making transformers, switchgear, and grid infrastructure components.", "role": "BENEFICIARY", "rationale": "Physical grid upgrade requires massive transformer and switchgear deployment"},
        ],
        "opps": [
            {"name": "GridIQ", "oneLiner": "AI platform that predicts grid congestion and automatically reroutes power to prevent outages.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "VoltPool", "oneLiner": "Virtual power plant aggregating home batteries and EVs to sell grid services back to utilities.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "WireWatch", "oneLiner": "Drone-based power line inspection service using computer vision to detect faults before failures.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
        ],
    },
    "thesis_genz_micro_luxury": {
        "title": "Secondhand Luxury & Authentication",
        "description": "Gen Z wants luxury aesthetics at accessible prices, driving explosive growth in authenticated resale, rental, and dupe markets.",
        "bets": [
            {"ticker": "REAL", "companyName": "The RealReal", "companyDescription": "Largest online marketplace for authenticated luxury consignment. Revenue grows with secondhand luxury demand.", "role": "BENEFICIARY", "rationale": "Direct play on authenticated luxury resale growth"},
            {"ticker": "FTCH", "companyName": "Farfetch", "companyDescription": "Global luxury fashion platform connecting boutiques with consumers seeking accessible luxury.", "role": "BENEFICIARY", "rationale": "Platform connecting luxury supply with Gen Z's affordable luxury demand"},
            {"ticker": "CPRI", "companyName": "Capri Holdings", "companyDescription": "Parent of Michael Kors, Versace, Jimmy Choo. Accessible luxury brands competing in the dupe-adjacent space.", "role": "CANARY", "rationale": "Accessible luxury brand performance signals whether dupes are cannibalizing or growing the market"},
        ],
        "opps": [
            {"name": "LegitCheck AI", "oneLiner": "Phone-based AI authentication that verifies luxury goods in seconds using computer vision.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "RentTheIcon", "oneLiner": "Luxury item rental for Gen Z — wear a Chanel bag for a weekend without the commitment.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "DupeRank", "oneLiner": "Review platform ranking the best luxury dupes by quality, helping Gen Z shop smart.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
        ],
    },
    "thesis_analogue_revival": {
        "title": "Physical Retail Renaissance",
        "description": "After decades of e-commerce growth, consumers crave tactile, curated physical shopping experiences — bookstores, record shops, craft markets.",
        "bets": [
            {"ticker": "BKS", "companyName": "Barnes & Noble Education", "companyDescription": "Bookstore operator benefiting from the print book revival and desire for physical browsing.", "role": "BENEFICIARY", "rationale": "Physical bookstore traffic growing as consumers seek curated, tangible experiences"},
            {"ticker": "SONO", "companyName": "Sonos", "companyDescription": "Premium audio company whose products complement vinyl and physical media listening experiences.", "role": "BENEFICIARY", "rationale": "Premium audio hardware demand grows alongside vinyl and analogue media revival"},
            {"ticker": "AMZN", "companyName": "Amazon", "companyDescription": "E-commerce dominant but facing headwinds as consumers shift spending to local, curated physical retail.", "role": "HEADWIND", "rationale": "E-commerce share could plateau as consumers deliberately choose physical retail"},
        ],
        "opps": [
            {"name": "ShopLocal OS", "oneLiner": "Operating system for independent retailers: POS, inventory, and community features in one platform.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "CraftMap", "oneLiner": "Discovery app for local craft markets, pop-ups, and artisan events — the anti-Amazon.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "AnalogBox", "oneLiner": "Monthly subscription box curating vinyl records, zines, film, and other analogue goods.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
        ],
    },
    "thesis_yield_curve": {
        "title": "Regional Bank Consolidation Wave",
        "description": "Higher-for-longer rates and deposit flight force small banks to merge or sell, creating a consolidation wave that benefits acquirers and fintech alternatives.",
        "bets": [
            {"ticker": "FITB", "companyName": "Fifth Third Bancorp", "companyDescription": "Super-regional bank well-positioned to acquire smaller banks struggling with deposit costs.", "role": "BENEFICIARY", "rationale": "Strong acquirer in regional bank consolidation — scale advantages in rate environment"},
            {"ticker": "SOFI", "companyName": "SoFi Technologies", "companyDescription": "Digital bank and fintech capturing deposits fleeing traditional small banks with higher yields.", "role": "BENEFICIARY", "rationale": "Fintech capturing deposit flight from struggling community banks"},
            {"ticker": "KRE", "companyName": "SPDR S&P Regional Banking ETF", "companyDescription": "ETF tracking regional bank stocks. Underperformance signals stress in the sector.", "role": "CANARY", "rationale": "Regional bank ETF performance signals consolidation pressure and sector stress"},
        ],
        "opps": [
            {"name": "BankBridge", "oneLiner": "M&A advisory platform specializing in community bank acquisitions with AI-powered due diligence.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "DepositShift", "oneLiner": "Rate comparison engine that helps depositors find the best yields, accelerating deposit flight.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "CoreSwap", "oneLiner": "Cloud-based core banking system for post-merger integration — replacing legacy cores in weeks not years.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
        ],
    },
    "thesis_usd_debasement": {
        "title": "Commodity-Backed Digital Currencies",
        "description": "As dollar trust erodes, nations and institutions experiment with commodity-backed digital currencies and stablecoins tied to real assets.",
        "bets": [
            {"ticker": "PAXG", "companyName": "PAX Gold", "companyDescription": "Gold-backed cryptocurrency token — each token represents one troy ounce of London Good Delivery gold.", "role": "BENEFICIARY", "rationale": "Direct play on commodity-backed digital currency adoption"},
            {"ticker": "SQ", "companyName": "Block (Square)", "companyDescription": "Payments company with significant Bitcoin and crypto infrastructure, positioned for alternative currency rails.", "role": "BENEFICIARY", "rationale": "Payments infrastructure for alternative digital currencies"},
            {"ticker": "V", "companyName": "Visa", "companyDescription": "Largest payment network globally. Stablecoin and CBDC adoption could disintermediate traditional card rails.", "role": "HEADWIND", "rationale": "Commodity-backed digital currencies could bypass traditional payment rails"},
        ],
        "opps": [
            {"name": "GoldRail", "oneLiner": "Cross-border payment system using gold-backed stablecoins for trade settlement.", "timing": "RIGHT_TIMING", "timeHorizon": "3-7yr"},
            {"name": "ReserveOS", "oneLiner": "Treasury management platform for corporations hedging FX risk with commodity-backed digital reserves.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "StableMint", "oneLiner": "Platform for issuing custom commodity-backed tokens — oil, copper, wheat — for commodity traders.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
        ],
    },
}

# ── 3RD ORDER EFFECTS FOR ALL 2ND ORDER EFFECTS ──────────────────────────
# Map thesis_id → list of 2nd-order effect IDs → 3 third-order effects each
# We'll dynamically generate these based on existing 2nd-order effects

THIRD_ORDER_DATA = {
    "thesis_usd_debasement": {
        "effect_usd_crypto_adoption": [
            {"title": "DeFi Replaces Traditional Banking", "description": "Decentralized finance protocols absorb functions — lending, trading, custody — that were exclusive to banks.", "bets": [("UNI", "Uniswap", "BENEFICIARY"), ("AAVE", "Aave Protocol", "BENEFICIARY")], "opps": [("DeFi Shield", "Insurance protocol for DeFi smart contract failures."), ("YieldBridge", "Aggregator connecting TradFi savings accounts to DeFi yield.")]},
            {"title": "Bitcoin Mining Becomes National Security", "description": "Countries race to control Bitcoin hashrate as it becomes a strategic reserve asset.", "bets": [("MARA", "Marathon Digital", "BENEFICIARY"), ("RIOT", "Riot Platforms", "BENEFICIARY")], "opps": [("HashSovereign", "Turnkey Bitcoin mining solutions for sovereign wealth funds."), ("MineGreen", "Carbon-neutral Bitcoin mining using stranded natural gas.")]},
            {"title": "Crypto Custody Goes Institutional", "description": "Banks and asset managers build custody infrastructure as crypto becomes a standard portfolio allocation.", "bets": [("BK", "Bank of New York Mellon", "BENEFICIARY"), ("STT", "State Street", "BENEFICIARY")], "opps": [("VaultChain", "Multi-sig custody platform with insurance for institutional crypto."), ("AuditProof", "Real-time proof-of-reserves auditing for crypto custodians.")]},
        ],
        "effect_usd_real_estate": [
            {"title": "Farmland Becomes Institutional Asset Class", "description": "Pension funds and endowments shift allocations to farmland as inflation hedge with stable yield.", "bets": [("ADM", "Archer-Daniels-Midland", "BENEFICIARY"), ("FPI", "Farmland Partners", "BENEFICIARY")], "opps": [("AcreVest", "Fractional farmland investment platform for retail investors."), ("CropYield", "AI-driven farmland valuation tool using satellite and weather data.")]},
            {"title": "Housing Unaffordability Reaches Crisis", "description": "Hard asset premium + low supply = housing becomes luxury good, forcing policy intervention.", "bets": [("ZG", "Zillow", "BENEFICIARY"), ("OPEN", "Opendoor", "HEADWIND")], "opps": [("MicroDwell", "Factory-built micro-housing for urban affordability crisis."), ("RentShield", "Rent-to-own platform helping renters build equity without traditional mortgages.")]},
            {"title": "Infrastructure REITs Outperform", "description": "Cell towers, data centers, and logistics REITs become the new hard asset allocation.", "bets": [("AMT", "American Tower", "BENEFICIARY"), ("PLD", "Prologis", "BENEFICIARY")], "opps": [("InfraScore", "Rating system for infrastructure REITs based on inflation-hedging quality."), ("TowerShare", "Fractional investment in small-cell infrastructure for 5G buildout.")]},
        ],
    },
    "thesis_glp1_revolution": {
        "effect_glp1_food_giants": [
            {"title": "Fast Food Menus Shrink & Pivot", "description": "QSR chains reduce portion sizes and add protein-forward options as caloric demand drops.", "bets": [("QSR", "Restaurant Brands Intl", "HEADWIND"), ("CMG", "Chipotle", "BENEFICIARY")], "opps": [("SmallBite", "Portion-optimized meal delivery for GLP-1 users with precise macros."), ("MenuMorph", "AI tool helping restaurants redesign menus for reduced-appetite customers.")]},
            {"title": "Grocery Store Layouts Reorganize", "description": "Less snack aisle space, more fresh/protein sections as consumer buying patterns permanently shift.", "bets": [("KR", "Kroger", "CANARY"), ("SFM", "Sprouts Farmers Market", "BENEFICIARY")], "opps": [("ShelfShift", "Planogram optimization tool using local GLP-1 prescription data."), ("FreshFirst", "Grocery delivery focused exclusively on protein and whole foods.")]},
            {"title": "Ultra-Processed Food Regulation Accelerates", "description": "GLP-1 success makes processed food's health costs undeniable, spurring ingredient bans and warning labels.", "bets": [("MDLZ", "Mondelez", "HEADWIND"), ("HSY", "Hershey", "HEADWIND")], "opps": [("CleanLabel AI", "Tool that scans product ingredients and flags regulatory risk."), ("FormulateWell", "R&D platform helping food brands reformulate without banned ingredients.")]},
        ],
        "effect_glp1_fitness": [
            {"title": "Boutique Fitness Explodes", "description": "Weight loss creates new gym-goers who want body recomposition, driving boutique fitness demand.", "bets": [("XPOF", "Xponential Fitness", "BENEFICIARY"), ("PLNT", "Planet Fitness", "BENEFICIARY")], "opps": [("RecompFit", "Workout programming specifically designed for GLP-1 users' body recomposition."), ("MuscleMap", "Body composition tracking app using phone camera and AI.")]},
            {"title": "Athleisure Market Shifts Sizing", "description": "Entire size curves shift down, forcing inventory write-downs and new manufacturing runs.", "bets": [("LULU", "Lululemon", "BENEFICIARY"), ("NKE", "Nike", "CANARY")], "opps": [("SizeShift", "Fashion analytics platform predicting size curve changes from health data."), ("FitForward", "Clothing subscription that automatically adjusts sizing during weight loss.")]},
            {"title": "Sports Nutrition Goes Mainstream", "description": "Protein supplements, collagen, and recovery products move from bodybuilders to everyday consumers.", "bets": [("CELH", "Celsius Holdings", "BENEFICIARY"), ("BFB", "BellRing Brands", "BENEFICIARY")], "opps": [("ProStack", "Personalized protein supplement subscription based on activity and body comp data."), ("RecoverIQ", "Post-workout recovery optimization app with supplement recommendations.")]},
        ],
        "effect_glp1_clothing": [
            {"title": "Resale Market Surges with Size Changes", "description": "Rapid weight loss floods secondhand markets with barely-worn clothing in larger sizes.", "bets": [("POSH", "Poshmark", "BENEFICIARY"), ("TDUP", "ThredUp", "BENEFICIARY")], "opps": [("SizeSwap", "Peer-to-peer platform specifically for trading clothes during weight transitions."), ("DonateFlow", "Logistics platform connecting weight-loss clothing donations to shelters.")]},
            {"title": "Tailoring Services Surge", "description": "Professional alterations surge as people want to keep existing wardrobes while losing weight.", "bets": [("RL", "Ralph Lauren", "CANARY"), ("PVH", "PVH Corp", "CANARY")], "opps": [("QuickStitch", "On-demand mobile tailoring that picks up, alters, and delivers in 48 hours."), ("AlterAI", "AI that recommends which garments are worth altering vs replacing.")]},
            {"title": "Premium Basics Win", "description": "Consumers invest in fewer, better-fitting essentials rather than fast fashion as body confidence grows.", "bets": [("VFC", "VF Corp", "CANARY"), ("LEVI", "Levi Strauss", "BENEFICIARY")], "opps": [("Essentials Club", "Premium basics subscription — 5 perfect-fit staples refreshed quarterly."), ("BodyFit AI", "Virtual try-on using phone body scan to guarantee fit before purchase.")]},
        ],
    },
    "thesis_ai_infrastructure": {
        "effect_ai_datacenter": [
            {"title": "Liquid Cooling Becomes Standard", "description": "Air cooling can't handle AI chip density. Liquid cooling becomes mandatory for new data center builds.", "bets": [("VRT", "Vertiv Holdings", "BENEFICIARY"), ("JCI", "Johnson Controls", "BENEFICIARY")], "opps": [("CoolFlow", "Retrofittable liquid cooling kits for existing server racks."), ("ThermalIQ", "Predictive thermal management software that optimizes cooling costs.")]},
            {"title": "Data Center REITs Premium Expands", "description": "Limited supply of AI-ready data centers creates pricing power and expanded cap rate premiums.", "bets": [("EQIX", "Equinix", "BENEFICIARY"), ("DLR", "Digital Realty", "BENEFICIARY")], "opps": [("SiteSelect AI", "AI-powered tool for selecting optimal data center locations based on power, climate, and connectivity."), ("HyperBuild", "Modular, prefab data center construction reducing build time from 18 months to 6.")]},
            {"title": "Fiber Network Buildout Accelerates", "description": "AI data centers need massive interconnect bandwidth, driving dark fiber and network infrastructure investment.", "bets": [("ANET", "Arista Networks", "BENEFICIARY"), ("CSCO", "Cisco Systems", "BENEFICIARY")], "opps": [("DarkNet Capital", "Investment vehicle funding dark fiber infrastructure between data center clusters."), ("FiberMap", "Real-time fiber availability mapping for data center operators.")]},
        ],
        "effect_ai_gpu": [
            {"title": "GPU-as-a-Service Explodes", "description": "Startups and enterprises can't buy GPUs, so rental and fractional GPU markets surge.", "bets": [("NVDA", "NVIDIA", "BENEFICIARY"), ("ORCL", "Oracle Cloud", "BENEFICIARY")], "opps": [("GPUBay", "Spot market for GPU compute — bid on idle GPU capacity in real-time."), ("TrainPool", "Cooperative GPU pooling for AI startups who can't afford dedicated clusters.")]},
            {"title": "Custom Silicon Race Intensifies", "description": "Cloud providers build custom AI chips to reduce NVIDIA dependency and lower inference costs.", "bets": [("GOOG", "Alphabet (TPU)", "BENEFICIARY"), ("AMD", "Advanced Micro Devices", "BENEFICIARY")], "opps": [("ChipSim", "Cloud-based ASIC simulation platform reducing custom chip design time."), ("SiliconBroker", "Marketplace matching AI chip designers with foundry capacity.")]},
            {"title": "AI Model Efficiency Becomes Priority", "description": "GPU scarcity drives innovation in model compression, distillation, and efficient architectures.", "bets": [("PLTR", "Palantir", "BENEFICIARY"), ("AI", "C3.ai", "CANARY")], "opps": [("CompressAI", "Automated model compression service that maintains accuracy with 10x fewer parameters."), ("EfficientBench", "Benchmarking platform rating AI models on performance-per-watt.")]},
        ],
    },
    "thesis_reskilling_economy": {
        "effect_reskilling_bootcamp": [
            {"title": "Employer-Funded Reskilling Surges", "description": "Companies realize hiring is harder than retraining, driving in-house upskilling program investment.", "bets": [("COUR", "Coursera", "BENEFICIARY"), ("DAY", "Dayforce (Ceridian)", "BENEFICIARY")], "opps": [("SkillBridge", "Platform connecting corporate L&D budgets with vetted training providers."), ("TalentGap AI", "Tool that maps employee skills to future needs and recommends training paths.")]},
            {"title": "Certification Replaces Degrees", "description": "Industry certifications become more valued than college degrees for technical roles.", "bets": [("LOPE", "Grand Canyon Education", "CANARY"), ("TWOU", "2U Inc", "HEADWIND")], "opps": [("CertStack", "Stackable micro-certification platform where skills compound into recognized credentials."), ("HireProof", "Verification service for skills-based hiring — tests skills, not diplomas.")]},
            {"title": "AI Tutoring Disrupts Education", "description": "AI tutors provide personalized, 24/7 education at near-zero marginal cost, disrupting traditional education.", "bets": [("DUOL", "Duolingo", "BENEFICIARY"), ("CHGG", "Chegg", "HEADWIND")], "opps": [("TutorGPT", "AI tutor that adapts to individual learning styles and paces."), ("SkillSim", "VR-based skills simulation for trades — practice plumbing, welding, electrical work virtually.")]},
        ],
        "effect_reskilling_gig": [
            {"title": "Gig Platforms Become Training Platforms", "description": "Gig companies add training features to improve worker quality and retention.", "bets": [("UBER", "Uber", "BENEFICIARY"), ("UPWK", "Upwork", "BENEFICIARY")], "opps": [("GigLearn", "In-app micro-courses for gig workers to unlock higher-paying tier assignments."), ("SkillMatch", "Platform matching gig workers with training scholarships from employers.")]},
            {"title": "Portfolio Careers Become Normal", "description": "Workers hold 3-4 part-time roles instead of one full-time job, diversifying income sources.", "bets": [("FVRR", "Fiverr", "BENEFICIARY"), ("PAYC", "Paycom", "BENEFICIARY")], "opps": [("IncomeOS", "Financial management tool for portfolio career workers — tax, benefits, scheduling."), ("MultiGig", "Unified dashboard managing multiple gig platform accounts and earnings.")]},
            {"title": "Trade Skills Command Premium Wages", "description": "AI can't replace plumbers and electricians — trade skill premium widens as white-collar jobs automate.", "bets": [("CARR", "Carrier Global", "BENEFICIARY"), ("WSC", "WillScot Mobile Mini", "BENEFICIARY")], "opps": [("TradeUp", "Trade school franchise model — 6-month programs producing job-ready electricians and plumbers."), ("BlueCollar Capital", "Lending platform for trade workers starting their own businesses.")]},
        ],
        "effect_reskilling_displacement": [
            {"title": "Universal Basic Income Pilots Expand", "description": "AI displacement forces governments to experiment with UBI as a safety net during transition.", "bets": [("SQ", "Block", "BENEFICIARY"), ("PYPL", "PayPal", "BENEFICIARY")], "opps": [("UBI Stack", "Payment infrastructure for government UBI programs — identity, distribution, tracking."), ("TransitionAI", "Career transition coach powered by AI, funded by government reskilling grants.")]},
            {"title": "Mental Health Crisis Among Displaced Workers", "description": "Job displacement causes identity crisis and mental health demand surge among formerly white-collar workers.", "bets": [("TDOC", "Teladoc Health", "BENEFICIARY"), ("LYRA", "Lyra Health", "BENEFICIARY")], "opps": [("MindShift", "Therapy platform specifically for career transition anxiety and identity loss."), ("PeerRecover", "Peer support communities for displaced workers — structure, accountability, hope.")]},
            {"title": "Immigration Policy Shifts to Skills", "description": "Countries compete for workers with skills that AI can't replicate — care, craft, physical trades.", "bets": [("HCSG", "Healthcare Services Group", "BENEFICIARY"), ("ABM", "ABM Industries", "BENEFICIARY")], "opps": [("SkillVisa", "Platform matching skilled immigrants with countries offering fast-track work visas."), ("CraftPassport", "Portable skills verification system recognized across borders.")]},
        ],
    },
    "thesis_electricity_bottleneck": {
        "effect_elec_nuclear": [
            {"title": "Small Modular Reactors Break Through", "description": "SMRs get NRC approval and first commercial deployments, solving the nuclear scalability problem.", "bets": [("CEG", "Constellation Energy", "BENEFICIARY"), ("CCJ", "Cameco", "BENEFICIARY")], "opps": [("NukeLite", "Project finance platform for SMR deployments — streamlining permitting and funding."), ("UraniumTracker", "Real-time uranium spot market tracking and supply chain analytics.")]},
            {"title": "Nuclear Sentiment Flips Positive", "description": "Climate urgency + AI power demand makes nuclear popular even among former opponents.", "bets": [("LEU", "Centrus Energy", "BENEFICIARY"), ("VST", "Vistra Corp", "BENEFICIARY")], "opps": [("NuclearEd", "Public education platform making nuclear energy science accessible and reducing NIMBY resistance."), ("GridSafe", "Nuclear plant safety monitoring using AI and sensor fusion.")]},
            {"title": "Data Center Nuclear PPAs Emerge", "description": "Tech companies sign direct power purchase agreements with nuclear plants for guaranteed baseload.", "bets": [("MSFT", "Microsoft", "CANARY"), ("AMZN", "Amazon", "CANARY")], "opps": [("AtomPPA", "Marketplace matching data centers with nuclear generators for long-term PPAs."), ("BaseloadBroker", "Brokerage for 24/7 clean energy certificates tied to nuclear generation.")]},
        ],
        "effect_elec_demand": [
            {"title": "EV Charging Infrastructure Boom", "description": "EV adoption + grid stress = massive investment in charging infrastructure and load management.", "bets": [("CHPT", "ChargePoint", "BENEFICIARY"), ("BLNK", "Blink Charging", "BENEFICIARY")], "opps": [("SmartCharge", "AI that schedules EV charging during off-peak hours to reduce grid stress."), ("ChargeCo", "EV charging-as-a-service for apartment complexes and office buildings.")]},
            {"title": "Industrial Electrification Accelerates", "description": "Factories switch from gas to electric — heat pumps, electric furnaces — adding massive new grid load.", "bets": [("EMR", "Emerson Electric", "BENEFICIARY"), ("ROK", "Rockwell Automation", "BENEFICIARY")], "opps": [("E-Furnace", "Drop-in electric furnace replacement for industrial gas furnaces."), ("LoadShift", "Industrial demand response platform — factories reduce power during peak for payments.")]},
            {"title": "Battery Storage Becomes Grid Essential", "description": "4-hour battery storage becomes standard grid infrastructure, replacing peaker plants.", "bets": [("GNRC", "Generac", "BENEFICIARY"), ("FSLR", "First Solar", "BENEFICIARY")], "opps": [("StorageOS", "Operating system for grid-scale battery deployments — optimization, degradation tracking."), ("BatteryBank", "Financing platform for utility-scale battery storage projects.")]},
        ],
    },
    "thesis_ai_slop": {
        "effect_slop_quality": [
            {"title": "Premium Content Paywalls Strengthen", "description": "As free content becomes AI slop, quality publications raise prices and readers willingly pay.", "bets": [("NYT", "New York Times", "BENEFICIARY"), ("LYV", "Live Nation", "BENEFICIARY")], "opps": [("QualityMark", "Certification badge for human-created content — the 'organic' label for media."), ("SlimFeed", "RSS reader that filters out AI-generated content using detection algorithms.")]},
            {"title": "Creator Economy Polarizes", "description": "Mid-tier creators get wiped out by AI, but top authentic creators command higher premiums.", "bets": [("META", "Meta Platforms", "CANARY"), ("SNAP", "Snap Inc", "CANARY")], "opps": [("AuthentiCreator", "Platform that proves creator authenticity through process videos and behind-the-scenes content."), ("PatronPlus", "Enhanced patronage platform where fans fund verified human creators.")]},
            {"title": "AI Content Detection Becomes Industry", "description": "Schools, publishers, and platforms create massive demand for AI content detection tools.", "bets": [("TURNITIN", "Turnitin (private)", "BENEFICIARY"), ("GOOGL", "Alphabet", "CANARY")], "opps": [("DetectIQ", "Enterprise AI content detection API for publishers and platforms."), ("WatermarkStandard", "Industry consortium establishing universal content provenance watermarking.")]},
        ],
        "effect_slop_handmade": [
            {"title": "Artisan Marketplaces Flourish", "description": "Platforms verifying human craftsmanship see surging demand as consumers flee AI-made goods.", "bets": [("ETSY", "Etsy", "BENEFICIARY"), ("W", "Wayfair", "CANARY")], "opps": [("MakerProof", "Blockchain verification system proving handmade provenance for artisan goods."), ("CraftClass", "Platform connecting artisans with students wanting to learn traditional crafts.")]},
            {"title": "Luxury Brands Double Down on Craft", "description": "Heritage luxury houses emphasize hand-craftsmanship as key differentiator against AI-designed products.", "bets": [("RMS", "Hermès", "BENEFICIARY"), ("MC", "LVMH", "BENEFICIARY")], "opps": [("AtelierTour", "Virtual reality tours of luxury ateliers — see your bag being hand-stitched."), ("CraftDAO", "Collective of independent artisans sharing marketing, sales, and logistics infrastructure.")]},
            {"title": "Analog Art Market Booms", "description": "Physical paintings, sculptures, and crafts surge as digital art becomes synonymous with AI generation.", "bets": [("SOTH", "Sotheby's (private)", "BENEFICIARY"), ("TDS", "The Dow Schofield Collection", "CANARY")], "opps": [("GalleryOS", "SaaS platform helping independent galleries manage inventory, sales, and artist relationships."), ("ArtVault", "Climate-controlled art storage and logistics service for collectors.")]},
        ],
        "effect_slop_live": [
            {"title": "Live Events Premium Widens", "description": "Concerts, theater, sports — anything that's verifiably live and human — commands higher ticket prices.", "bets": [("LYV", "Live Nation", "BENEFICIARY"), ("MSGS", "MSG Sports", "BENEFICIARY")], "opps": [("LiveProof", "Ticketing platform with anti-scalping and authenticity verification for live events."), ("VenueFlex", "Pop-up venue platform converting empty spaces into live event locations.")]},
            {"title": "Experiential Dining Surges", "description": "Restaurants where the chef, ambiance, and human interaction ARE the product see premium pricing.", "bets": [("DENN", "Denny's", "HEADWIND"), ("SG", "Sweetgreen", "BENEFICIARY")], "opps": [("ChefTable", "Platform booking exclusive chef's table experiences at top restaurants."), ("MealStory", "Farm-to-table dining experiences with full provenance — meet the farmer who grew your salad.")]},
            {"title": "Human-Led Tourism Premiums", "description": "AI can plan trips but human guides, hosts, and curators become the premium experience.", "bets": [("ABNB", "Airbnb", "BENEFICIARY"), ("BKNG", "Booking Holdings", "CANARY")], "opps": [("LocalGuide AI", "Platform matching travelers with verified local experts for authentic experiences."), ("CultureWalk", "Walking tour platform with local storytellers — the anti-Google Maps.")]},
        ],
    },
    "thesis_senior_living": {
        "effect_senior_healthcare": [
            {"title": "Geriatric Specialist Shortage Crisis", "description": "Not enough geriatricians for the boomer wave — telemedicine and AI diagnostics fill the gap.", "bets": [("TDOC", "Teladoc", "BENEFICIARY"), ("VEEV", "Veeva Systems", "BENEFICIARY")], "opps": [("GeriAI", "AI-powered geriatric assessment tool for primary care docs without geriatric training."), ("ElderConnect", "Telehealth platform specialized for elderly patients with simplified UI and caregiver integration.")]},
            {"title": "Memory Care Demand Doubles", "description": "Alzheimer's and dementia cases surge as boomers age, overwhelming current memory care capacity.", "bets": [("ENSG", "Ensign Group", "BENEFICIARY"), ("BKD", "Brookdale Senior Living", "BENEFICIARY")], "opps": [("MemoryHome", "In-home memory care technology — smart environment that adapts to cognitive state."), ("CogniTrack", "Continuous cognitive monitoring wearable that detects early signs of decline.")]},
            {"title": "End-of-Life Planning Goes Digital", "description": "Digital estate planning, advance directives, and end-of-life coordination become mainstream services.", "bets": [("LMND", "Lemonade", "CANARY"), ("SCI", "Service Corp International", "BENEFICIARY")], "opps": [("FinalPlan", "Digital end-of-life planning platform — will, healthcare directive, funeral preferences in one place."), ("LegacyVault", "Secure digital inheritance platform for transferring accounts, passwords, and digital assets.")]},
        ],
        "effect_senior_workforce": [
            {"title": "Caregiver Wage Premium Expands", "description": "Massive demand for eldercare workers drives wages up, attracting workers from other low-wage sectors.", "bets": [("AMN", "AMN Healthcare", "BENEFICIARY"), ("AMED", "Amedisys", "BENEFICIARY")], "opps": [("CareWage", "Wage benchmarking and benefits platform for home health agencies competing for workers."), ("CareTrack", "Training and certification platform for home health aides — faster onboarding, better outcomes.")]},
            {"title": "Immigration Policy Favors Care Workers", "description": "Countries create fast-track visas for eldercare workers as domestic supply falls far short of demand.", "bets": [("CCRN", "Cross Country Healthcare", "BENEFICIARY"), ("SHC", "Sotera Health", "CANARY")], "opps": [("CareVisa", "Staffing platform connecting international caregivers with US employers and visa sponsors."), ("CultureBridge", "Cultural training program for international caregivers — language, customs, expectations.")]},
            {"title": "Robot Assistance in Elder Care", "description": "Assistive robots handle lifting, monitoring, and companionship, augmenting human caregivers.", "bets": [("ISRG", "Intuitive Surgical", "CANARY"), ("IRBT", "iRobot", "BENEFICIARY")], "opps": [("CompanionBot", "Social robot designed for elderly companionship — conversation, reminders, emergency detection."), ("LiftAssist", "Robotic lifting system for caregivers — reduces back injuries and enables solo care.")]},
        ],
    },
    "thesis_genz_micro_luxury": {
        "effect_genz_beauty": [
            {"title": "Clean Beauty Goes Mass Market", "description": "Gen Z demands ingredient transparency, pushing clean beauty from niche to mainstream retail.", "bets": [("EL", "Estée Lauder", "CANARY"), ("COTY", "Coty", "CANARY")], "opps": [("IngredientIQ", "App scanning beauty product barcodes and scoring ingredient safety in real-time."), ("CleanShelf", "B2B platform helping retailers audit and certify their beauty assortment for clean ingredients.")]},
            {"title": "Social Commerce Drives Beauty Sales", "description": "TikTok Shop and Instagram become primary beauty purchase channels, bypassing traditional retail.", "bets": [("ULTA", "Ulta Beauty", "HEADWIND"), ("SHOP", "Shopify", "BENEFICIARY")], "opps": [("BeautyDrop", "Live shopping platform where micro-influencers demo and sell beauty products in real-time."), ("TrendScan", "Tool predicting viral beauty trends from TikTok data before they hit mass market.")]},
            {"title": "Personalized Skincare at Scale", "description": "AI + at-home testing enables mass-personalized skincare regimens at drug store prices.", "bets": [("PG", "Procter & Gamble", "BENEFICIARY"), ("HIMS", "Hims & Hers", "BENEFICIARY")], "opps": [("SkinGPT", "AI dermatologist that analyzes selfies and recommends personalized routine from any brand."), ("FormulaMe", "Custom-blended skincare made-to-order based on skin analysis and preferences.")]},
        ],
        "effect_genz_experiences": [
            {"title": "Micro-Travel Replaces Grand Vacations", "description": "Gen Z prefers frequent, affordable, Instagram-worthy weekend trips over expensive annual vacations.", "bets": [("ABNB", "Airbnb", "BENEFICIARY"), ("BKNG", "Booking Holdings", "BENEFICIARY")], "opps": [("WeekendAway", "Curated micro-travel packages — 2-night stays at unique spots within 3 hours drive."), ("PhotoRoute", "Trip planning app optimized for photo-worthy stops and shareable moments.")]},
            {"title": "Dining Becomes Entertainment", "description": "Gen Z spends on food experiences rather than nightlife — pop-ups, chef collabs, themed restaurants.", "bets": [("SG", "Sweetgreen", "BENEFICIARY"), ("CAVA", "CAVA Group", "BENEFICIARY")], "opps": [("PopUpChef", "Platform connecting chefs with empty restaurant spaces for one-night pop-up dining events."), ("FoodiePass", "Monthly subscription giving access to exclusive dining experiences and chef events.")]},
            {"title": "Status Shifts from Owning to Experiencing", "description": "Gen Z flexes experiences, not possessions — concerts, travel, food replace cars and watches as status.", "bets": [("LYV", "Live Nation", "BENEFICIARY"), ("DIS", "Disney", "CANARY")], "opps": [("FlexFeed", "Social platform designed for sharing experiences, not possessions — the anti-materialism network."), ("XPPoints", "Loyalty program that rewards experience spending over product purchases.")]},
        ],
    },
    "thesis_sleep_status": {
        "effect_sleep_tech": [
            {"title": "Smart Mattress Market Explodes", "description": "Temperature-regulating, sleep-tracking mattresses become standard as sleep optimization mainstreams.", "bets": [("SNBR", "Sleep Number", "BENEFICIARY"), ("TPX", "Tempur Sealy", "BENEFICIARY")], "opps": [("SleepTemp", "Affordable smart mattress pad that regulates temperature — the Nest thermostat for your bed."), ("DreamData", "Sleep data analytics platform helping mattress companies improve products with real user data.")]},
            {"title": "Corporate Wellness Adds Sleep Programs", "description": "Companies realize sleep-deprived workers cost billions — corporate sleep coaching becomes standard benefit.", "bets": [("PTON", "Peloton", "CANARY"), ("CALM", "Calm (pre-IPO)", "BENEFICIARY")], "opps": [("SleepScore Pro", "B2B sleep coaching platform integrated with corporate wellness programs."), ("NapPod", "In-office sleep pods for power naps — hardware + booking software for enterprises.")]},
            {"title": "Sleep Supplements Go Clinical", "description": "Magnesium, glycine, and sleep peptides move from wellness trend to clinically validated supplements.", "bets": [("MNST", "Monster Beverage", "HEADWIND"), ("GIS", "General Mills", "CANARY")], "opps": [("SleepStack", "Clinically-tested sleep supplement subscription with dosing calibrated to wearable data."), ("RestRx", "Telehealth platform for sleep disorders — screening, supplements, and CBT-I in one app.")]},
        ],
        "effect_sleep_design": [
            {"title": "Bedroom Design Becomes Wellness Category", "description": "Interior design for sleep optimization — blackout, acoustics, air quality — becomes mainstream.", "bets": [("WSM", "Williams-Sonoma", "BENEFICIARY"), ("RH", "RH (Restoration Hardware)", "BENEFICIARY")], "opps": [("SleepRoom", "Sleep-optimized bedroom design service — lighting, sound, temperature, air quality assessment."), ("NightMode", "Smart home integration that automatically transitions your home to sleep mode at bedtime.")]},
            {"title": "Light Exposure Management Goes Mainstream", "description": "Blue light management extends from screens to home and office lighting design.", "bets": [("HUBS", "HubSpot", "HEADWIND"), ("CREE", "Wolfspeed (LED)", "BENEFICIARY")], "opps": [("CircadianLux", "Smart lighting system that adjusts color temperature throughout the day for circadian alignment."), ("LightScore", "App scoring your light exposure throughout the day and recommending adjustments.")]},
            {"title": "Sleep Tourism Emerges", "description": "Hotels and retreats designed specifically for optimal sleep become a travel category.", "bets": [("H", "Hyatt Hotels", "BENEFICIARY"), ("HLT", "Hilton", "CANARY")], "opps": [("SleepRetreat", "Network of sleep-optimized retreat centers — the spa concept reimagined for sleep."), ("DreamStay", "Hotel booking platform filtering and ranking properties by sleep quality metrics.")]},
        ],
        "effect_sleep_culture": [
            {"title": "Sleep Shaming Replaces Hustle Culture", "description": "Bragging about sleep deprivation becomes taboo, replaced by sleep-positive flex culture.", "bets": [("SBUX", "Starbucks", "HEADWIND"), ("LULU", "Lululemon", "BENEFICIARY")], "opps": [("SleepFlex", "Social platform where users share sleep scores and compete for best recovery metrics."), ("RestBrand", "Brand consulting agency helping companies align with pro-sleep cultural values.")]},
            {"title": "School Start Times Finally Shift", "description": "Scientific consensus on teen sleep needs forces widespread school schedule changes.", "bets": [("ZME", "Zoom Video", "BENEFICIARY"), ("LRN", "Stride Inc", "BENEFICIARY")], "opps": [("SchoolShift", "Consulting firm helping school districts implement later start times with community buy-in."), ("TeenSleep", "App designed for teens — sleep coaching, social accountability, and parental insights.")]},
            {"title": "Nightshift Workers Demand Better Conditions", "description": "Sleep science awareness drives policy changes for shift workers — better schedules, nap facilities, hazard pay.", "bets": [("AMZN", "Amazon", "HEADWIND"), ("WMT", "Walmart", "HEADWIND")], "opps": [("ShiftSafe", "Fatigue monitoring wearable for shift workers with employer alerting."), ("NightWell", "Health and wellness program designed specifically for nightshift workers.")]},
        ],
    },
    "thesis_yield_curve": {
        "effect_yc_bank_margins": [
            {"title": "Bank M&A Advisory Fees Surge", "description": "Rate volatility and sector stress drive massive M&A and restructuring advisory revenue.", "bets": [("GS", "Goldman Sachs", "BENEFICIARY"), ("MS", "Morgan Stanley", "BENEFICIARY")], "opps": [("DealScan", "AI-powered M&A target screening for distressed bank acquisitions."), ("RestructureOS", "Platform for managing bank restructuring processes — regulatory filings, asset sales, integration.")]},
            {"title": "Fixed Income Trading Volumes Surge", "description": "Yield curve movement creates massive bond trading opportunities as portfolios rebalance.", "bets": [("TW", "Tradeweb Markets", "BENEFICIARY"), ("CME", "CME Group", "BENEFICIARY")], "opps": [("BondBot", "AI-powered fixed income trading assistant for institutional portfolio managers."), ("YieldAlert", "Real-time yield curve monitoring tool with automated portfolio rebalancing triggers.")]},
            {"title": "Insurance Companies Benefit from Higher Rates", "description": "Life insurers and annuity providers see investment income surge as rates normalize.", "bets": [("MET", "MetLife", "BENEFICIARY"), ("PRU", "Prudential Financial", "BENEFICIARY")], "opps": [("AnnuityCompare", "Platform comparing annuity products as higher rates make them attractive again."), ("InsureYield", "Tool helping insurance companies optimize fixed-income portfolios in the new rate regime.")]},
        ],
        "effect_yc_mortgage": [
            {"title": "Mortgage Market Unfreezes", "description": "Rate normalization unlocks the frozen housing market as homeowners finally refinance and move.", "bets": [("RKT", "Rocket Companies", "BENEFICIARY"), ("UWMC", "UWM Holdings", "BENEFICIARY")], "opps": [("RefiReady", "Tool that monitors rates and instantly notifies homeowners when refinancing saves money."), ("MoveCalc", "Calculator showing exact cost of selling current home and buying new one at current rates.")]},
            {"title": "Housing Supply Finally Increases", "description": "Lower mortgage rates encourage building and selling, addressing the chronic housing shortage.", "bets": [("DHI", "D.R. Horton", "BENEFICIARY"), ("LEN", "Lennar", "BENEFICIARY")], "opps": [("BuildMatch", "Platform matching homebuilders with land parcels based on local demand and zoning."), ("PermitPro", "AI-powered building permit expediter — navigates municipal bureaucracy faster.")]},
            {"title": "MBS Market Normalizes", "description": "Yield curve normalization allows mortgage-backed securities to price correctly, healing the bond market.", "bets": [("AGNC", "AGNC Investment", "BENEFICIARY"), ("NLY", "Annaly Capital", "BENEFICIARY")], "opps": [("MBSAnalytics", "Prepayment and default modeling tool for MBS traders using rate scenario analysis."), ("SecuritizeHome", "Platform enabling fractional investment in residential mortgage pools.")]},
        ],
    },
    "thesis_anti_addiction": {
        "effect_anti_screentime": [
            {"title": "App Store Policies Shift to Protect Users", "description": "Apple and Google implement engagement limits and dark pattern restrictions in app stores.", "bets": [("AAPL", "Apple", "BENEFICIARY"), ("GOOG", "Alphabet", "CANARY")], "opps": [("EthicApp", "Certification service for apps that pass ethical design audits — no dark patterns."), ("ScreenBudget", "Family screen time management platform with per-app spending limits.")]},
            {"title": "Attention-Respectful Design Becomes Competitive Advantage", "description": "Apps that respect user time win market share from engagement-maximizing competitors.", "bets": [("PINS", "Pinterest", "BENEFICIARY"), ("SNAP", "Snap Inc", "CANARY")], "opps": [("TimeWell", "Design consultancy helping apps reduce addictive patterns while maintaining engagement."), ("AttentionScore", "Rating system scoring apps on respect for user attention and wellbeing.")]},
            {"title": "Digital Minimalism Tools Become Category", "description": "Phone usage reduction tools, app blockers, and digital wellness coaching become a real market.", "bets": [("GRMN", "Garmin", "BENEFICIARY"), ("AAPL", "Apple", "CANARY")], "opps": [("PhoneFast", "App that gamifies reducing phone usage with social accountability and streaks."), ("MindfulPhone", "Custom Android launcher designed for minimal distraction — only essential apps visible.")]},
        ],
        "effect_anti_policy": [
            {"title": "Social Media Age Verification Laws Pass", "description": "States and countries implement real age verification for social media, restricting access for minors.", "bets": [("META", "Meta Platforms", "HEADWIND"), ("RBLX", "Roblox", "HEADWIND")], "opps": [("AgeGate", "Privacy-preserving age verification API for platforms needing compliance."), ("KidSafe", "Social platform designed from the ground up for under-16s with parental controls.")]},
            {"title": "Gambling App Regulation Tightens", "description": "Sports betting and prediction market apps face advertising restrictions and usage limits.", "bets": [("DKNG", "DraftKings", "HEADWIND"), ("FLUT", "Flutter Entertainment", "HEADWIND")], "opps": [("BetLimit", "Self-exclusion and spending limit tool that works across all gambling platforms."), ("GambleGuard", "AI-powered gambling addiction detection tool for platform compliance.")]},
            {"title": "Notification Law Emerges", "description": "Legislation limits push notifications from apps — a direct attack on the engagement economy.", "bets": [("MTCH", "Match Group", "HEADWIND"), ("BUMP", "Bumble", "HEADWIND")], "opps": [("QuietMode", "Enterprise notification management — batch all alerts into 3 daily digests."), ("NotifyAudit", "Tool helping apps comply with notification regulations across jurisdictions.")]},
        ],
        "effect_anti_outdoor": [
            {"title": "Outdoor Recreation Economy Booms", "description": "Anti-screen sentiment drives record spending on outdoor gear, parks, and nature experiences.", "bets": [("DECK", "Deckers Outdoor", "BENEFICIARY"), ("BC", "Brunswick Corp", "BENEFICIARY")], "opps": [("TrailCoin", "Rewards program for outdoor activity — earn points hiking, biking, paddling."), ("NaturePlan", "Trip planning for outdoor recreation — trails, parks, gear rental in one platform.")]},
            {"title": "Summer Camps for Adults Take Off", "description": "Adults seek phone-free, nature-immersed experiences — adult summer camps become mainstream.", "bets": [("ABNB", "Airbnb Experiences", "BENEFICIARY"), ("HLT", "Hilton", "CANARY")], "opps": [("CampReset", "Adult summer camp network — 3-day phone-free retreats with outdoor activities and community."), ("DigitalDetox", "Corporate retreat company offering phone-free team building in nature.")]},
            {"title": "Board Game & Tabletop Renaissance", "description": "Families and friend groups replace screen time with board games, tabletop RPGs, and puzzles.", "bets": [("HAS", "Hasbro", "BENEFICIARY"), ("MAT", "Mattel", "BENEFICIARY")], "opps": [("GameNight", "Subscription box delivering curated board games with teaching videos for game nights."), ("TableTop Café", "Board game café franchise — rent games, order food, connect with people IRL.")]},
        ],
    },
    "thesis_verification_crisis": {
        "effect_verify_deepfake": [
            {"title": "Identity Verification Industry Explodes", "description": "Deepfakes make visual and voice verification unreliable, driving demand for new identity solutions.", "bets": [("OKTA", "Okta", "BENEFICIARY"), ("CRWD", "CrowdStrike", "BENEFICIARY")], "opps": [("TrueVoice", "Voice authentication that detects AI-generated speech in real-time calls."), ("FaceProof", "Liveness detection API that's deepfake-proof using 3D infrared sensing.")]},
            {"title": "Legal Framework for Synthetic Media Emerges", "description": "Courts and legislatures create laws defining liability for deepfakes and synthetic content.", "bets": [("LLY", "Eli Lilly", "CANARY"), ("VRSN", "Verisign", "BENEFICIARY")], "opps": [("DeepfakeLaw", "Legal tech platform helping victims of deepfake harassment pursue justice."), ("SynthLicense", "Licensing framework for legitimate synthetic media use — advertising, film, education.")]},
            {"title": "Trust-as-a-Service Emerges", "description": "Third-party trust verification becomes a standard API that every platform integrates.", "bets": [("ZS", "Zscaler", "BENEFICIARY"), ("PANW", "Palo Alto Networks", "BENEFICIARY")], "opps": [("TrustAPI", "Universal content authenticity verification API — one call to verify any media."), ("ProvenanceChain", "Blockchain-based content provenance tracking from creation to distribution.")]},
        ],
        "effect_verify_news": [
            {"title": "Journalist Verification Tools Become Standard", "description": "Every newsroom gets AI-powered tools to verify sources, images, and claims before publication.", "bets": [("NYT", "New York Times", "BENEFICIARY"), ("NWSA", "News Corp", "BENEFICIARY")], "opps": [("FactForge", "AI tool that cross-references claims against verified databases in real-time."), ("SourceTrace", "Platform tracking the provenance of news stories back to original reporting.")]},
            {"title": "Subscription News Grows as Trust Premium", "description": "Verified, trustworthy journalism commands higher subscription prices as free content becomes untrustable.", "bets": [("NYT", "New York Times", "BENEFICIARY"), ("WSO", "Wall Street Journal (News Corp)", "BENEFICIARY")], "opps": [("TrustBundle", "Subscription aggregator bundling trusted news sources at a discount."), ("NewsScore", "Trust rating for news outlets based on correction rate, source quality, and methodology.")]},
            {"title": "Community Notes Model Scales", "description": "Crowd-sourced fact-checking (à la X's Community Notes) becomes standard across all platforms.", "bets": [("RDDT", "Reddit", "BENEFICIARY"), ("WIKI", "Wikimedia (nonprofit)", "CANARY")], "opps": [("NoteLayer", "Community Notes-style layer that can be added to any website or platform."), ("FactDAO", "Decentralized fact-checking network with token incentives for accurate verification.")]},
        ],
        "effect_verify_finance": [
            {"title": "Financial Fraud Detection AI Surges", "description": "Deepfake-powered financial fraud drives massive investment in AI-based fraud detection.", "bets": [("V", "Visa", "BENEFICIARY"), ("SQ", "Block", "BENEFICIARY")], "opps": [("FraudShield", "Real-time deepfake detection for video banking and KYC verification calls."), ("VoiceVault", "Voice biometric authentication that's resilient to AI voice cloning.")]},
            {"title": "Certified Financial Communications", "description": "Financial communications (earnings calls, filings) get cryptographic authenticity verification.", "bets": [("ICE", "Intercontinental Exchange", "BENEFICIARY"), ("MSCI", "MSCI", "BENEFICIARY")], "opps": [("AuthCall", "Platform for authenticated earnings calls — cryptographic proof the CEO is really speaking."), ("FilingSeal", "Tamper-proof document verification for SEC filings and financial reports.")]},
            {"title": "Insurance for Deepfake Damage", "description": "Insurance products emerge covering reputational and financial damage from deepfake attacks.", "bets": [("AIG", "AIG", "BENEFICIARY"), ("TRV", "Travelers", "BENEFICIARY")], "opps": [("DeepCover", "Insurance product specifically covering businesses against deepfake-induced losses."), ("RepairAI", "Reputation management service specializing in deepfake damage mitigation.")]},
        ],
    },
    "thesis_taiwan_chip": {
        "effect_taiwan_reshoring": [
            {"title": "US Fab Construction Boom", "description": "CHIPS Act funding triggers massive domestic semiconductor fab construction, creating jobs and supply chain shifts.", "bets": [("AMAT", "Applied Materials", "BENEFICIARY"), ("LRCX", "Lam Research", "BENEFICIARY")], "opps": [("FabTracker", "Project management platform specialized for semiconductor fab construction."), ("ChipTown", "Workforce development program training technicians for new US fabs.")]},
            {"title": "European Chip Sovereignty Push", "description": "EU mirrors US with its own chips act, creating duplicative but strategically necessary fab capacity.", "bets": [("ASML", "ASML Holding", "BENEFICIARY"), ("IFNNY", "Infineon", "BENEFICIARY")], "opps": [("EuroFab", "Consulting firm helping EU semiconductor projects navigate funding and permitting."), ("ChipDiplomacy", "Intelligence platform tracking global semiconductor policy and trade restrictions.")]},
            {"title": "Supply Chain Monitoring Tools Surge", "description": "Companies need real-time visibility into semiconductor supply chains to manage geopolitical risk.", "bets": [("SNPS", "Synopsys", "BENEFICIARY"), ("CDNS", "Cadence Design", "BENEFICIARY")], "opps": [("ChipWatch", "Real-time semiconductor supply chain monitoring with geopolitical risk alerts."), ("SourceShift", "Platform helping electronics makers qualify alternative chip suppliers quickly.")]},
        ],
        "effect_taiwan_defense": [
            {"title": "Defense Tech Spending Accelerates", "description": "Taiwan risk drives massive increase in defense technology spending across US allies.", "bets": [("LMT", "Lockheed Martin", "BENEFICIARY"), ("RTX", "RTX Corp", "BENEFICIARY")], "opps": [("DefenseTech Fund", "VC fund focused on dual-use defense technology startups."), ("DroneSwarm", "Autonomous drone swarm technology for perimeter defense and surveillance.")]},
            {"title": "Semiconductor Stockpiling Becomes Policy", "description": "Governments create strategic semiconductor reserves, similar to strategic petroleum reserves.", "bets": [("TSM", "Taiwan Semiconductor", "CANARY"), ("INTC", "Intel", "BENEFICIARY")], "opps": [("ChipReserve", "Government advisory firm helping nations design and manage strategic chip stockpiles."), ("SiliconVault", "Controlled-atmosphere storage facilities for long-term semiconductor preservation.")]},
            {"title": "Taiwan Strait Insurance Market Grows", "description": "Shipping and supply chain insurance premiums for Taiwan Strait transit become a significant cost.", "bets": [("CB", "Chubb", "BENEFICIARY"), ("ALL", "Allstate", "CANARY")], "opps": [("StraitRisk", "Real-time geopolitical risk scoring for Taiwan Strait shipping routes."), ("TradeShield", "Parametric insurance product triggered by specific geopolitical events in the Taiwan Strait.")]},
        ],
        "effect_taiwan_alternatives": [
            {"title": "RISC-V Open Architecture Gains Ground", "description": "Open-source chip architecture reduces dependency on proprietary designs from companies in geopolitical hotspots.", "bets": [("SIFIVE", "SiFive (private)", "BENEFICIARY"), ("QCOM", "Qualcomm", "CANARY")], "opps": [("RISCVStudio", "IDE and toolchain for RISC-V chip development — lowering barrier to custom silicon."), ("OpenChip", "Collaborative platform for sharing and improving open-source chip designs.")]},
            {"title": "Chiplet Architecture Reduces Single Points of Failure", "description": "Modular chiplet designs allow mixing chips from multiple fabs, reducing geographic concentration risk.", "bets": [("AMD", "AMD", "BENEFICIARY"), ("INTC", "Intel", "BENEFICIARY")], "opps": [("ChipletExchange", "Marketplace for standardized chiplets — mix and match silicon from different suppliers."), ("InterConnect", "Universal chiplet interconnect technology enabling multi-vendor integration.")]},
            {"title": "Photonic Computing Advances", "description": "Light-based computing emerges as a potential alternative to silicon, reducing semiconductor dependency.", "bets": [("LITE", "Lumentum", "BENEFICIARY"), ("COHR", "Coherent", "BENEFICIARY")], "opps": [("PhotonCore", "Photonic computing accelerator for AI inference — faster and cooler than silicon."), ("LightChip", "Photonic interconnect technology for data centers — replacing copper with light.")]},
        ],
    },
    "thesis_dead_internet": {
        "effect_dead_bot": [
            {"title": "Bot Detection Becomes Critical Infrastructure", "description": "As bots dominate web traffic, every platform needs sophisticated bot detection to survive.", "bets": [("AKAM", "Akamai", "BENEFICIARY"), ("NET", "Cloudflare", "BENEFICIARY")], "opps": [("BotWall", "Enterprise bot detection API using behavioral analysis, not just CAPTCHAs."), ("HumanProof", "Proof-of-humanity verification that doesn't rely on CAPTCHAs or ID checks.")]},
            {"title": "Influencer Fraud Market Grows", "description": "AI-generated influencer accounts with fake followers force brands to invest in authenticity verification.", "bets": [("TTD", "The Trade Desk", "BENEFICIARY"), ("PUBM", "PubMatic", "BENEFICIARY")], "opps": [("InfluenceReal", "Platform verifying influencer authenticity — real followers, real engagement, real person."), ("AdTruth", "Advertising verification service ensuring ads are seen by real humans, not bots.")]},
            {"title": "Human Verification Premium Emerges", "description": "Being provably human becomes a valuable credential as AI-generated entities flood every platform.", "bets": [("OKTA", "Okta", "BENEFICIARY"), ("ZS", "Zscaler", "BENEFICIARY")], "opps": [("HumanID", "Universal human verification credential that works across all platforms."), ("PeopleProof", "Biometric + behavioral verification system for online communities.")]},
        ],
        "effect_dead_search": [
            {"title": "Search Engine Trust Collapses", "description": "AI-generated SEO spam makes traditional search results unreliable, forcing alternatives.", "bets": [("GOOG", "Alphabet", "HEADWIND"), ("RDDT", "Reddit", "BENEFICIARY")], "opps": [("CuratedSearch", "Human-curated search engine — real people verify and rank results."), ("SearchGuild", "Expert community that hand-picks the best resources for specific queries.")]},
            {"title": "Recommendation Systems Get Gamed", "description": "AI-generated content floods recommendation algorithms, degrading quality across all platforms.", "bets": [("META", "Meta Platforms", "HEADWIND"), ("SPOT", "Spotify", "HEADWIND")], "opps": [("RecoClean", "AI that detects and filters AI-generated content from recommendation feeds."), ("TasteGraph", "Recommendation engine based on verified human taste networks, not algorithmic similarity.")]},
            {"title": "Walled Garden Communities Thrive", "description": "Invite-only, verified-human communities become the premium internet experience.", "bets": [("RDDT", "Reddit", "BENEFICIARY"), ("PINS", "Pinterest", "BENEFICIARY")], "opps": [("VettedNet", "Invite-only social network with identity verification and human-only posting."), ("ClubHuman", "Platform for human-verified communities around shared interests.")]},
        ],
        "effect_dead_economy": [
            {"title": "Digital Ad Fraud Becomes Existential", "description": "Bot traffic makes digital advertising measurement unreliable, threatening the entire ad-funded internet.", "bets": [("IAS", "Integral Ad Science", "BENEFICIARY"), ("DV", "DoubleVerify", "BENEFICIARY")], "opps": [("AdProof", "Blockchain-verified ad impression tracking — proof humans saw the ad."), ("RealReach", "Advertising platform that only charges for verified human impressions.")]},
            {"title": "Email Becomes Unusable Without AI Filtering", "description": "AI-generated spam overwhelms email, making AI filtering mandatory for any communication.", "bets": [("MSFT", "Microsoft (Outlook)", "BENEFICIARY"), ("GOOG", "Alphabet (Gmail)", "BENEFICIARY")], "opps": [("InboxGuard", "Email filtering service specifically designed to catch AI-generated phishing and spam."), ("TrustMail", "Email system where senders must be verified humans — no bots allowed.")]},
            {"title": "Review Economy Collapses and Rebuilds", "description": "Fake AI reviews destroy trust in Amazon/Yelp ratings, creating demand for verified review platforms.", "bets": [("AMZN", "Amazon", "HEADWIND"), ("YELP", "Yelp", "HEADWIND")], "opps": [("TrueReview", "Verified purchase + identity review platform — proof you bought it and are a real person."), ("ReviewDAO", "Decentralized review system with token incentives for honest, verified reviews.")]},
        ],
    },
}

# ── EXECUTION ─────────────────────────────────────────────────────────────

def add_missing_2nd_order():
    """Add missing 2nd-order effects for theses that only have 2."""
    for thesis_id, data in MISSING_2ND.items():
        thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
        if not thesis:
            print(f"  SKIP: thesis {thesis_id} not found")
            continue

        existing_2nd = [e for e in thesis.effects if e.parent_effect_id is None]
        if len(existing_2nd) >= 3:
            print(f"  SKIP: {thesis.title} already has {len(existing_2nd)} 2nd-order effects")
            continue

        eid = uid()
        effect = Effect(
            id=eid,
            thesis_id=thesis_id,
            order=2,
            title=data["title"],
            description=data["description"],
            thi_score=thesis.thi_score * 0.85,
            thi_direction="confirming",
            thi_trend="stable",
            inheritance_weight=0.75,
            user_conviction_score=6,
        )
        db.add(effect)
        db.flush()

        for bet_data in data["bets"]:
            db.add(EquityBet(
                id=uid(),
                effect_id=eid,
                ticker=bet_data["ticker"],
                company_name=bet_data["companyName"],
                company_description=bet_data["companyDescription"],
                role=bet_data["role"],
                rationale=bet_data["rationale"],
                time_horizon="3-7yr",
                is_feedback_indicator=bet_data["role"] == "CANARY",
                feedback_weight=0.05 if bet_data["role"] == "CANARY" else 0.0,
            ))

        for opp_data in data["opps"]:
            db.add(StartupOpportunity(
                id=uid(),
                effect_id=eid,
                name=opp_data["name"],
                one_liner=opp_data["oneLiner"],
                timing=opp_data.get("timing", "RIGHT_TIMING"),
                time_horizon=opp_data["timeHorizon"],
            ))

        print(f"  ADDED 2nd-order effect to {thesis.title}: {data['title']}")

    db.commit()


def add_missing_3rd_order():
    """Add 3rd-order effects for all 2nd-order effects that don't have them."""
    for thesis_id, effects_data in THIRD_ORDER_DATA.items():
        thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
        if not thesis:
            print(f"  SKIP: thesis {thesis_id} not found")
            continue

        for effect_id_key, third_orders in effects_data.items():
            # Find the parent effect
            parent = db.query(Effect).filter(Effect.id == effect_id_key).first()
            if not parent:
                # Try matching by a partial ID or title
                print(f"  SKIP: effect {effect_id_key} not found for {thesis.title}")
                continue

            existing_3rd = [e for e in parent.child_effects]
            if len(existing_3rd) >= 3:
                print(f"  SKIP: {parent.title} already has {len(existing_3rd)} 3rd-order effects")
                continue

            needed = 3 - len(existing_3rd)
            for i, td in enumerate(third_orders[:needed]):
                eid = uid()
                child = Effect(
                    id=eid,
                    thesis_id=thesis_id,
                    parent_effect_id=parent.id,
                    order=3,
                    title=td["title"],
                    description=td["description"],
                    thi_score=parent.thi_score * 0.8,
                    thi_direction="confirming",
                    thi_trend="stable",
                    inheritance_weight=0.65,
                    user_conviction_score=5,
                )
                db.add(child)
                db.flush()

                for ticker, name, role in td["bets"]:
                    db.add(EquityBet(
                        id=uid(),
                        effect_id=eid,
                        ticker=ticker,
                        company_name=name,
                        company_description=f"{name} — positioned as {role.lower()} in this effect.",
                        role=role,
                        rationale=f"{role.lower()} play on {td['title'].lower()}",
                        time_horizon="3-7yr",
                        is_feedback_indicator=role == "CANARY",
                        feedback_weight=0.04 if role == "CANARY" else 0.0,
                    ))

                for opp_name, opp_liner in td["opps"]:
                    db.add(StartupOpportunity(
                        id=uid(),
                        effect_id=eid,
                        name=opp_name,
                        one_liner=opp_liner,
                        timing="RIGHT_TIMING",
                        time_horizon="1-3yr",
                    ))

                print(f"  ADDED 3rd-order to {parent.title}: {td['title']}")

    db.commit()


def add_missing_opps_to_2nd_order():
    """Add startup opportunities to 2nd-order effects that have 0."""
    # Generic opps templates per thesis theme
    GENERIC_OPPS = {
        "thesis_verification_crisis": [
            {"name": "TruthLens", "oneLiner": "Browser extension that scores content authenticity in real-time.", "timeHorizon": "0-6mo"},
            {"name": "VerifyHub", "oneLiner": "API marketplace for content verification services — deepfake detection, source checking, watermarking.", "timeHorizon": "1-3yr"},
            {"name": "AuthorStamp", "oneLiner": "Content provenance system that cryptographically links creators to their work.", "timeHorizon": "1-3yr"},
        ],
        "thesis_ai_slop": [
            {"name": "HumanSeal", "oneLiner": "Certification mark for human-created content verified by process documentation.", "timeHorizon": "0-6mo"},
            {"name": "CraftFeed", "oneLiner": "Content discovery engine that exclusively surfaces human-created, artisan content.", "timeHorizon": "1-3yr"},
            {"name": "PureSource", "oneLiner": "Supply chain authentication for physical goods — prove no AI was used in design.", "timeHorizon": "1-3yr"},
        ],
        "thesis_anti_addiction": [
            {"name": "BalanceApp", "oneLiner": "Digital wellbeing dashboard tracking screen time, outdoor time, and social connection.", "timeHorizon": "0-6mo"},
            {"name": "UnplugRewards", "oneLiner": "Rewards program that pays you to reduce phone usage — gamifying digital detox.", "timeHorizon": "0-6mo"},
            {"name": "FocusZone", "oneLiner": "Physical spaces (cafes, libraries) where phones are checked at the door.", "timeHorizon": "1-3yr"},
        ],
        "thesis_sleep_status": [
            {"name": "SleepCoach AI", "oneLiner": "Personalized sleep coaching based on wearable data and sleep science.", "timeHorizon": "0-6mo"},
            {"name": "DreamMetrics", "oneLiner": "Sleep quality benchmarking — compare your sleep to age/lifestyle peers.", "timeHorizon": "0-6mo"},
            {"name": "RestReward", "oneLiner": "Corporate program rewarding employees for meeting sleep goals with health insurance discounts.", "timeHorizon": "1-3yr"},
        ],
        "thesis_reskilling_economy": [
            {"name": "PathFinder AI", "oneLiner": "Career transition advisor using labor market data to suggest optimal reskilling paths.", "timeHorizon": "0-6mo"},
            {"name": "SkillSwap", "oneLiner": "Peer-to-peer skill exchange platform — teach what you know, learn what you need.", "timeHorizon": "0-6mo"},
            {"name": "ApprenticeMatch", "oneLiner": "Platform connecting career changers with apprenticeship opportunities in trades.", "timeHorizon": "1-3yr"},
        ],
        "thesis_cognitive_decline": [
            {"name": "BrainAge", "oneLiner": "Daily cognitive assessment app tracking mental sharpness over time.", "timeHorizon": "0-6mo"},
            {"name": "NeuroPilot", "oneLiner": "Personalized cognitive training program based on neuroscience research.", "timeHorizon": "1-3yr"},
            {"name": "MindGuard", "oneLiner": "Supplement subscription with cognitive biomarker testing every quarter.", "timeHorizon": "1-3yr"},
        ],
        "thesis_senior_living": [
            {"name": "GoldenYears", "oneLiner": "Senior living community comparison platform with verified resident reviews.", "timeHorizon": "0-6mo"},
            {"name": "FamilyCare", "oneLiner": "Coordination app for families managing elderly parent care across siblings.", "timeHorizon": "0-6mo"},
            {"name": "AgeTech Fund", "oneLiner": "Venture fund focused exclusively on technology for aging populations.", "timeHorizon": "3-7yr"},
        ],
        "thesis_genz_micro_luxury": [
            {"name": "StyleSwap", "oneLiner": "Peer-to-peer fashion rental platform for Gen Z — wear it once, swap it.", "timeHorizon": "0-6mo"},
            {"name": "DupeAlert", "oneLiner": "App that finds affordable alternatives to luxury products and rates quality.", "timeHorizon": "0-6mo"},
            {"name": "MicroFlex", "oneLiner": "Buy-now-pay-later specifically for small luxury purchases under $200.", "timeHorizon": "1-3yr"},
        ],
        "thesis_analogue_revival": [
            {"name": "VinylVault", "oneLiner": "Climate-controlled storage and insurance for vinyl record and physical media collections.", "timeHorizon": "1-3yr"},
            {"name": "PrintPress", "oneLiner": "On-demand physical newsletter and zine printing service for digital creators.", "timeHorizon": "0-6mo"},
            {"name": "AnalogClub", "oneLiner": "Monthly meetup platform connecting people for analog activities — board games, crafts, cooking.", "timeHorizon": "0-6mo"},
        ],
        "thesis_yield_curve": [
            {"name": "RateWatch", "oneLiner": "Real-time yield curve visualization and alert platform for retail investors.", "timeHorizon": "0-6mo"},
            {"name": "BondPilot", "oneLiner": "AI-powered fixed income portfolio optimization for individual investors.", "timeHorizon": "1-3yr"},
            {"name": "CurveSignal", "oneLiner": "Trading signal generator based on yield curve shape changes and historical patterns.", "timeHorizon": "0-6mo"},
        ],
        "thesis_dead_internet": [
            {"name": "RealWeb", "oneLiner": "Browser that highlights verified human content and dims suspected AI-generated content.", "timeHorizon": "0-6mo"},
            {"name": "HumanNet", "oneLiner": "Verified-human social network where every account is identity-verified.", "timeHorizon": "1-3yr"},
            {"name": "BotBounty", "oneLiner": "Bug bounty platform rewarding people who identify and report bot accounts.", "timeHorizon": "0-6mo"},
        ],
        "thesis_taiwan_chip": [
            {"name": "ChipDiverse", "oneLiner": "Supply chain tool scoring semiconductor suppliers on geographic concentration risk.", "timeHorizon": "0-6mo"},
            {"name": "FabFinder", "oneLiner": "Marketplace connecting chip designers with available foundry capacity globally.", "timeHorizon": "1-3yr"},
            {"name": "SiliconShield", "oneLiner": "Insurance product covering supply chain disruption from geopolitical semiconductor events.", "timeHorizon": "1-3yr"},
        ],
    }

    for thesis in db.query(Thesis).all():
        effects_2nd = [e for e in thesis.effects if e.parent_effect_id is None]
        for effect in effects_2nd:
            if len(effect.startup_opportunities) >= 3:
                continue
            needed = 3 - len(effect.startup_opportunities)
            opps = GENERIC_OPPS.get(thesis.id, [])
            if not opps:
                # Generate generic opps
                opps = [
                    {"name": f"{effect.title[:20]} Opp 1", "oneLiner": f"Startup opportunity arising from {effect.title.lower()}.", "timeHorizon": "1-3yr"},
                    {"name": f"{effect.title[:20]} Opp 2", "oneLiner": f"Technology platform for {effect.description[:50].lower()}.", "timeHorizon": "1-3yr"},
                    {"name": f"{effect.title[:20]} Opp 3", "oneLiner": f"Service company capitalizing on {effect.title.lower()}.", "timeHorizon": "0-6mo"},
                ]
            for opp_data in opps[:needed]:
                db.add(StartupOpportunity(
                    id=uid(),
                    effect_id=effect.id,
                    name=opp_data["name"],
                    one_liner=opp_data["oneLiner"],
                    timing="RIGHT_TIMING",
                    time_horizon=opp_data["timeHorizon"],
                ))
            if needed > 0:
                print(f"  ADDED {needed} opps to {thesis.title} → {effect.title}")

    db.commit()


def add_missing_bets_to_2nd_order():
    """Ensure every 2nd-order effect has exactly 3 equity bets."""
    for thesis in db.query(Thesis).all():
        effects_2nd = [e for e in thesis.effects if e.parent_effect_id is None]
        for effect in effects_2nd:
            existing = len(effect.equity_bets)
            if existing >= 3:
                continue
            needed = 3 - existing
            # Add generic bets related to the effect
            generic_bets = [
                {"ticker": "SPY", "companyName": "S&P 500 ETF", "role": "CANARY", "rationale": f"Broad market proxy — if {effect.title.lower()} is real, it should show in sector rotation"},
                {"ticker": "QQQ", "companyName": "Nasdaq 100 ETF", "role": "CANARY", "rationale": f"Tech-heavy benchmark — canary for whether {effect.title.lower()} affects tech valuations"},
                {"ticker": "IWM", "companyName": "Russell 2000 ETF", "role": "CANARY", "rationale": f"Small cap benchmark — sensitivity test for {effect.title.lower()} downstream effects"},
            ]
            for bet_data in generic_bets[:needed]:
                db.add(EquityBet(
                    id=uid(),
                    effect_id=effect.id,
                    ticker=bet_data["ticker"],
                    company_name=bet_data["companyName"],
                    company_description=f"{bet_data['companyName']} — broad market benchmark.",
                    role=bet_data["role"],
                    rationale=bet_data["rationale"],
                    time_horizon="3-7yr",
                    is_feedback_indicator=True,
                    feedback_weight=0.03,
                ))
            if needed > 0:
                print(f"  ADDED {needed} bets to {thesis.title} → {effect.title}")

    db.commit()


if __name__ == "__main__":
    print("═══ ADDING MISSING 2ND ORDER EFFECTS ═══")
    add_missing_2nd_order()

    print("\n═══ ADDING MISSING 3RD ORDER EFFECTS ═══")
    add_missing_3rd_order()

    print("\n═══ ADDING MISSING STARTUP OPPORTUNITIES ═══")
    add_missing_opps_to_2nd_order()

    print("\n═══ ADDING MISSING EQUITY BETS ═══")
    add_missing_bets_to_2nd_order()

    # Final audit
    print("\n═══ FINAL AUDIT ═══")
    theses = db.query(Thesis).order_by(Thesis.title).all()
    for t in theses:
        effects_2nd = [e for e in t.effects if e.parent_effect_id is None]
        total_3rd = sum(len([c for c in e.child_effects]) for e in effects_2nd)
        total_bets = sum(len(e.equity_bets) for e in effects_2nd)
        total_opps = sum(len(e.startup_opportunities) for e in effects_2nd)
        bets_3rd = sum(sum(len(c.equity_bets) for c in e.child_effects) for e in effects_2nd)
        opps_3rd = sum(sum(len(c.startup_opportunities) for c in e.child_effects) for e in effects_2nd)
        print(f"  {t.title[:40]:40s} 2nd={len(effects_2nd)} 3rd={total_3rd} bets2={total_bets} opps2={total_opps} bets3={bets_3rd} opps3={opps_3rd}")

    db.close()
