"""Fill all theses, 2nd-order, and 3rd-order effects to 9 equity bets + 9 startup opps each.
Row 1-3: Core BENEFICIARY (existing)
Row 4-6: Adjacent BENEFICIARY
Row 7-9: HEADWIND + CANARY mix
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal
from models import Thesis, Effect, EquityBet, StartupOpportunity

db = SessionLocal()

# ── TICKER POOLS PER THESIS ──────────────────────────────────────────────────
# Each thesis gets a pool of 12 tickers: 6 adjacent BENEFICIARY + 6 HEADWIND/CANARY
THESIS_POOLS = {
    "thesis_usd_debasement": {
        "adj": [
            ("MSTR", "MicroStrategy", "Bitcoin treasury strategy benefits from dollar weakness"),
            ("GLD", "SPDR Gold Shares", "Gold ETF directly benefits from currency debasement"),
            ("SLV", "iShares Silver Trust", "Silver as industrial + monetary metal hedge"),
            ("FCX", "Freeport-McMoRan", "Copper miner benefits from hard asset repricing"),
            ("NEM", "Newmont Corp", "Largest gold miner, operating leverage to gold price"),
            ("BTC-USD", "Bitcoin", "Digital store of value alternative to depreciating fiat"),
        ],
        "hw": [
            ("UUP", "Invesco DB US Dollar Index", "HEADWIND — dollar strength ETF inversely correlated"),
            ("TLT", "iShares 20+ Year Treasury", "CANARY — long bonds signal real rate expectations"),
            ("DXY", "US Dollar Index", "HEADWIND — strong dollar directly refutes thesis"),
            ("JPM", "JPMorgan Chase", "CANARY — bank earnings show credit expansion pace"),
            ("BRK-B", "Berkshire Hathaway", "CANARY — Buffett's cash position signals inflation view"),
            ("TIPS", "iShares TIPS Bond ETF", "CANARY — TIPS breakeven tracks inflation expectations"),
        ],
        "opps": [
            ("StableYield", "Inflation-indexed yield product for retail savers", "RIGHT_TIMING"),
            ("GoldFi", "Fractional gold-backed payment rails for emerging markets", "RIGHT_TIMING"),
            ("RealAssetDAO", "Tokenized real asset investment collective", "TOO_EARLY"),
            ("HedgeStack", "Automated currency hedging for SMB importers", "RIGHT_TIMING"),
            ("InflationAlert", "Consumer price tracking and budget adjustment app", "RIGHT_TIMING"),
            ("CommodityBox", "Monthly subscription for physical commodity micro-investments", "TOO_EARLY"),
        ],
    },
    "thesis_glp1_revolution": {
        "adj": [
            ("AMGN", "Amgen", "MariTide obesity drug in late-stage trials"),
            ("VKTX", "Viking Therapeutics", "Next-gen oral GLP-1 candidate"),
            ("RHHBY", "Roche", "Acquired CT-388 oral obesity asset"),
            ("DXCM", "DexCom", "CGM devices complement GLP-1 weight management"),
            ("PODD", "Insulet Corp", "Insulin pump maker adapting to GLP-1 era"),
            ("HIMS", "Hims & Hers Health", "Compounding pharmacy riding GLP-1 telehealth wave"),
        ],
        "hw": [
            ("HSY", "Hershey", "HEADWIND — snack consumption drops with appetite suppression"),
            ("MNST", "Monster Beverage", "HEADWIND — energy drink demand falls with weight loss"),
            ("DNUT", "Krispy Kreme", "HEADWIND — indulgent food category under pressure"),
            ("KO", "Coca-Cola", "CANARY — sugary beverage volumes signal appetite shift"),
            ("MCD", "McDonald's", "CANARY — fast food traffic patterns reveal GLP-1 adoption"),
            ("MDLZ", "Mondelez", "HEADWIND — global snacking giant faces demand headwinds"),
        ],
        "opps": [
            ("NutriSync", "AI meal planning optimized for GLP-1 patients", "RIGHT_TIMING"),
            ("ShrinkFit", "Clothing resizing service for rapid weight loss patients", "RIGHT_TIMING"),
            ("GutBiome+", "Microbiome support supplements for GLP-1 users", "RIGHT_TIMING"),
            ("PostGLP", "Post-GLP-1 maintenance coaching platform", "TOO_EARLY"),
            ("BariatricOS", "Practice management software for obesity medicine clinics", "RIGHT_TIMING"),
            ("MetaboTrack", "Wearable metabolic rate monitor for weight management", "TOO_EARLY"),
        ],
    },
    "thesis_ai_infrastructure": {
        "adj": [
            ("ANET", "Arista Networks", "Data center networking for AI clusters"),
            ("VRT", "Vertiv Holdings", "Power and cooling for AI data centers"),
            ("SMCI", "Super Micro Computer", "AI-optimized server manufacturing"),
            ("DELL", "Dell Technologies", "Enterprise AI server and storage solutions"),
            ("QCOM", "Qualcomm", "Edge AI chip opportunity in mobile and IoT"),
            ("MRVL", "Marvell Technology", "Custom AI silicon and data center connectivity"),
        ],
        "hw": [
            ("INTC", "Intel", "HEADWIND — losing AI chip market share to NVDA/AMD"),
            ("HPQ", "HP Inc", "CANARY — PC refresh cycle signals enterprise AI adoption"),
            ("CSCO", "Cisco Systems", "CANARY — network spending patterns reveal AI capex"),
            ("IBM", "IBM", "CANARY — enterprise AI consulting demand indicator"),
            ("ORCL", "Oracle", "HEADWIND — legacy cloud competing for AI workloads"),
            ("STX", "Seagate Technology", "CANARY — storage demand signals AI data growth"),
        ],
        "opps": [
            ("CoolStack", "Immersion cooling systems for high-density AI racks", "RIGHT_TIMING"),
            ("GPUBroker", "Spot market for unused GPU compute capacity", "RIGHT_TIMING"),
            ("InferenceOps", "Managed inference optimization for enterprise AI", "RIGHT_TIMING"),
            ("ChipRecycle", "GPU refurbishment and secondary market platform", "TOO_EARLY"),
            ("AIGrid", "Distributed AI training across renewable energy sources", "TOO_EARLY"),
            ("ModelCompress", "Neural network compression for edge deployment", "RIGHT_TIMING"),
        ],
    },
    "thesis_reskilling_economy": {
        "adj": [
            ("COUR", "Coursera", "Online learning platform for workforce reskilling"),
            ("LOPE", "Grand Canyon Education", "Education services provider for adult learners"),
            ("STRA", "Strategic Education", "Working adult degree programs"),
            ("LRN", "Stride Inc", "Virtual learning technology and curriculum"),
            ("PRDO", "Perdoceo Education", "Career-focused higher education"),
            ("UPWK", "Upwork", "Freelance marketplace benefits from gig reskilling"),
        ],
        "hw": [
            ("HBS", "Harvard Business School Online", "CANARY — elite education demand signals reskilling pressure"),
            ("WFC", "Wells Fargo", "CANARY — consumer lending patterns reveal job market stress"),
            ("TEMP", "TempStaff Index", "CANARY — temp staffing volumes signal labor transitions"),
            ("ADP", "ADP", "CANARY — payroll data reveals workforce churn patterns"),
            ("MAN", "ManpowerGroup", "HEADWIND — traditional staffing model under pressure"),
            ("RHI", "Robert Half", "HEADWIND — white collar staffing declining with AI"),
        ],
        "opps": [
            ("SkillBridge", "AI-powered career transition pathway planner", "RIGHT_TIMING"),
            ("MicroCred", "Blockchain-verified micro-credential marketplace", "RIGHT_TIMING"),
            ("ApprenticeOS", "Modern apprenticeship matching platform", "RIGHT_TIMING"),
            ("RetireReskill", "Late-career reskilling for 55+ workers", "TOO_EARLY"),
            ("UnionTech", "Digital upskilling platform for trade unions", "RIGHT_TIMING"),
            ("PortfolioWork", "Work portfolio builder replacing traditional resumes", "TOO_EARLY"),
        ],
    },
    "thesis_electricity_bottleneck": {
        "adj": [
            ("CEG", "Constellation Energy", "Nuclear fleet operator, AI data center deals"),
            ("VST", "Vistra Corp", "Power generation with nuclear + natural gas fleet"),
            ("SO", "Southern Company", "Utility with nuclear expansion plans"),
            ("ETN", "Eaton Corp", "Electrical equipment for grid modernization"),
            ("PWR", "Quanta Services", "Power infrastructure construction and services"),
            ("NEE", "NextEra Energy", "Renewable energy + utility scale battery storage"),
        ],
        "hw": [
            ("FSLR", "First Solar", "CANARY — solar panel pricing signals renewable economics"),
            ("PLUG", "Plug Power", "HEADWIND — hydrogen alternative to grid electricity"),
            ("ENPH", "Enphase Energy", "CANARY — distributed solar adoption rate"),
            ("RUN", "Sunrun", "CANARY — rooftop solar installations signal grid bypass"),
            ("SEDG", "SolarEdge", "HEADWIND — solar inverter demand signals distributed gen"),
            ("BE", "Bloom Energy", "CANARY — fuel cell adoption signals grid alternative"),
        ],
        "opps": [
            ("GridQ", "AI-optimized electricity queue management for data centers", "RIGHT_TIMING"),
            ("MicroNuke", "Small modular reactor project development platform", "TOO_EARLY"),
            ("WattBank", "Industrial battery-as-a-service for peak shaving", "RIGHT_TIMING"),
            ("PowerBid", "Real-time electricity futures marketplace for enterprises", "RIGHT_TIMING"),
            ("CoolWatt", "Waste heat recovery systems for AI data centers", "RIGHT_TIMING"),
            ("GridGuard", "Predictive maintenance AI for aging grid infrastructure", "RIGHT_TIMING"),
        ],
    },
    "thesis_ai_slop_human_premium": {
        "adj": [
            ("NFLX", "Netflix", "Premium content creation with human curation advantage"),
            ("SPOT", "Spotify", "Human-curated playlists and podcast premium"),
            ("NYT", "New York Times", "Premium journalism commanding attention premium"),
            ("ROKU", "Roku", "Content discovery platform, human curation value"),
            ("WMG", "Warner Music Group", "Human artistry premium in music"),
            ("MTCH", "Match Group", "Human verification premium in dating"),
        ],
        "hw": [
            ("META", "Meta Platforms", "HEADWIND — AI content generation floods social feeds"),
            ("GOOGL", "Alphabet", "CANARY — search quality degradation signals slop growth"),
            ("SNAP", "Snap Inc", "CANARY — user engagement patterns reveal AI fatigue"),
            ("PINS", "Pinterest", "CANARY — visual platform AI content ratio"),
            ("RDDT", "Reddit", "CANARY — community trust signals amid AI infiltration"),
            ("ETSY", "Etsy", "CANARY — handmade marketplace AI listing detection"),
        ],
        "opps": [
            ("HumanSeal", "Verified human-created content certification", "RIGHT_TIMING"),
            ("ArtisanHub", "Marketplace exclusively for human-crafted digital content", "RIGHT_TIMING"),
            ("TruthLayer", "Content provenance tracking for publishers", "RIGHT_TIMING"),
            ("LiveOnly", "Platform for verified live-only streaming events", "RIGHT_TIMING"),
            ("PenCraft", "Human ghostwriting premium marketplace", "CROWDING"),
            ("RealReview", "Verified human product review platform", "RIGHT_TIMING"),
        ],
    },
    "thesis_senior_living_boom": {
        "adj": [
            ("WELL", "Welltower", "Senior housing and healthcare facility REIT"),
            ("VTR", "Ventas", "Healthcare and senior living REIT"),
            ("BKD", "Brookdale Senior Living", "Largest US senior living operator"),
            ("AMED", "Amedisys", "Home health and hospice services"),
            ("ENSG", "Ensign Group", "Skilled nursing and senior living operator"),
            ("SEM", "Select Medical", "Rehabilitation and long-term care facilities"),
        ],
        "hw": [
            ("ZBH", "Zimmer Biomet", "CANARY — joint replacement volumes signal senior activity"),
            ("ISRG", "Intuitive Surgical", "CANARY — surgical robot adoption in elder care"),
            ("ABT", "Abbott Labs", "CANARY — diagnostic testing volumes for aging population"),
            ("MDT", "Medtronic", "CANARY — medical device utilization in senior care"),
            ("HCA", "HCA Healthcare", "CANARY — hospital admission patterns for 65+"),
            ("CVS", "CVS Health", "HEADWIND — retail pharmacy model disrupted by senior telehealth"),
        ],
        "opps": [
            ("ElderTech", "Smart home monitoring for independent senior living", "RIGHT_TIMING"),
            ("CareMatch", "AI-powered caregiver-patient matching platform", "RIGHT_TIMING"),
            ("SilverFit", "Fitness and mobility platform designed for 70+ users", "RIGHT_TIMING"),
            ("MedRemind", "Medication management and compliance system for seniors", "CROWDING"),
            ("GrandConnect", "Intergenerational social connection platform", "TOO_EARLY"),
            ("EstateFlow", "Simplified estate planning for aging boomers", "RIGHT_TIMING"),
        ],
    },
    "thesis_genz_micro_luxury": {
        "adj": [
            ("LVMUY", "LVMH", "Luxury conglomerate with accessible entry-level products"),
            ("TPR", "Tapestry", "Coach/Kate Spade accessible luxury portfolio"),
            ("CPRI", "Capri Holdings", "Versace/Michael Kors micro-luxury positioning"),
            ("DECK", "Deckers Outdoor", "UGG/HOKA brand premium positioning"),
            ("ONON", "On Holding", "Premium athletic footwear for Gen Z"),
            ("BIRK", "Birkenstock", "Heritage brand with luxury repositioning"),
        ],
        "hw": [
            ("TGT", "Target", "CANARY — mass retail traffic signals trade-down behavior"),
            ("DG", "Dollar General", "HEADWIND — discount retail growth signals affordability crisis"),
            ("FIVE", "Five Below", "CANARY — teen discretionary spending patterns"),
            ("WMT", "Walmart", "CANARY — grocery vs discretionary mix reveals spending shifts"),
            ("COST", "Costco", "CANARY — bulk buying patterns signal value consciousness"),
            ("PLBY", "PLBY Group", "HEADWIND — legacy brand struggling with Gen Z relevance"),
        ],
        "opps": [
            ("DropCulture", "Limited-edition micro-luxury drop platform for Gen Z", "RIGHT_TIMING"),
            ("FlexLux", "Luxury item rental and rotation subscription", "RIGHT_TIMING"),
            ("TasteGraph", "AI-powered personal style curation for micro-luxury", "RIGHT_TIMING"),
            ("VintageVault", "Authenticated pre-owned luxury marketplace for Gen Z", "CROWDING"),
            ("MicroBrand", "DTC micro-luxury brand launch platform", "RIGHT_TIMING"),
            ("StatusSnap", "Social commerce for verified luxury item flex", "TOO_EARLY"),
        ],
    },
    "thesis_sleep_status": {
        "adj": [
            ("SNBR", "Sleep Number", "Smart sleep technology and mattress innovation"),
            ("TPX", "Tempur Sealy", "Premium mattress and sleep products"),
            ("PRPL", "Purple Innovation", "Sleep technology and comfort innovation"),
            ("AAPL", "Apple", "Apple Watch sleep tracking drives health awareness"),
            ("GOOG", "Alphabet (Fitbit)", "Fitbit sleep tracking data and insights"),
            ("OURA", "Oura Ring", "Premium sleep tracking wearable (private proxy)"),
        ],
        "hw": [
            ("SBUX", "Starbucks", "HEADWIND — caffeine culture directly opposes sleep priority"),
            ("MNST", "Monster Beverage", "HEADWIND — energy drink reliance signals sleep deficit"),
            ("NFLX", "Netflix", "CANARY — late-night streaming hours signal sleep competition"),
            ("RBLX", "Roblox", "CANARY — gaming session lengths signal sleep displacement"),
            ("DIS", "Disney", "CANARY — streaming engagement hours vs sleep time"),
            ("EA", "Electronic Arts", "CANARY — gaming engagement patterns vs sleep hygiene"),
        ],
        "opps": [
            ("SleepScore", "Employer sleep quality scoring for wellness programs", "RIGHT_TIMING"),
            ("DuskMode", "Smart home automation for circadian rhythm optimization", "RIGHT_TIMING"),
            ("NapPod", "Urban nap pod network for professionals", "TOO_EARLY"),
            ("SomnoCafe", "Sleep-optimized coffee alternative beverages", "RIGHT_TIMING"),
            ("RestReward", "Insurance premium discounts for verified sleep quality", "TOO_EARLY"),
            ("ChronoLight", "Personalized light therapy for sleep optimization", "RIGHT_TIMING"),
        ],
    },
    "thesis_yield_curve_resteepening": {
        "adj": [
            ("SCHW", "Charles Schwab", "Net interest margin expansion from curve steepening"),
            ("USB", "US Bancorp", "Regional bank benefiting from normal yield curve"),
            ("TFC", "Truist Financial", "Rate-sensitive bank with large bond portfolio"),
            ("FITB", "Fifth Third Bancorp", "Regional bank net interest income recovery"),
            ("RF", "Regions Financial", "Southeast bank with rate sensitivity"),
            ("KEY", "KeyCorp", "Rate-sensitive regional bank recovery play"),
        ],
        "hw": [
            ("SHY", "iShares 1-3 Year Treasury", "CANARY — short-term rate expectations"),
            ("AGG", "iShares Core US Aggregate Bond", "CANARY — broad bond market signals"),
            ("HYG", "iShares High Yield Corporate Bond", "CANARY — credit spread signals"),
            ("LQD", "iShares Investment Grade Corporate Bond", "CANARY — corporate borrowing costs"),
            ("MBB", "iShares MBS ETF", "CANARY — mortgage-backed security pricing"),
            ("GOVT", "iShares US Treasury Bond ETF", "CANARY — treasury demand patterns"),
        ],
        "opps": [
            ("RateHedge", "Automated interest rate hedging for mid-market companies", "RIGHT_TIMING"),
            ("BondFlow", "Real-time bond market analytics for retail investors", "RIGHT_TIMING"),
            ("MortgageMoment", "AI-powered mortgage timing optimization", "RIGHT_TIMING"),
            ("YieldMap", "Visual yield curve strategy tool for fixed income", "RIGHT_TIMING"),
            ("CRERefi", "Commercial real estate refinancing marketplace", "RIGHT_TIMING"),
            ("DepositWars", "Bank deposit rate comparison and auto-switching platform", "RIGHT_TIMING"),
            ("CurveAlert", "Yield curve regime change notification service", "RIGHT_TIMING"),
        ],
    },
    "thesis_anti_addiction": {
        "adj": [
            ("GOOG", "Alphabet", "YouTube screen time tools, Digital Wellbeing"),
            ("AAPL", "Apple", "Screen Time features, parental controls"),
            ("TMUS", "T-Mobile", "Family digital wellness features"),
            ("CHTR", "Charter Communications", "Parental control and usage management"),
            ("DLB", "Dolby Labs", "Premium audio for intentional media consumption"),
            ("SONO", "Sonos", "Premium audio hardware for mindful listening"),
        ],
        "hw": [
            ("META", "Meta Platforms", "HEADWIND — engagement maximization business model"),
            ("SNAP", "Snap Inc", "HEADWIND — addictive social media targeting teens"),
            ("TTD", "The Trade Desk", "CANARY — digital ad spend signals attention economy"),
            ("ROKU", "Roku", "CANARY — streaming engagement metrics signal screen time"),
            ("RBLX", "Roblox", "HEADWIND — youth gaming engagement and spending"),
            ("TTWO", "Take-Two Interactive", "CANARY — gaming session length trends"),
        ],
        "opps": [
            ("FocusMode", "Enterprise attention management and deep work tools", "RIGHT_TIMING"),
            ("ScreenBudget", "Family screen time budgeting and allocation app", "RIGHT_TIMING"),
            ("DigitalDetox", "Guided digital detox retreat booking platform", "RIGHT_TIMING"),
            ("MindfulScroll", "Browser extension that adds friction to doom scrolling", "RIGHT_TIMING"),
            ("KidGuard", "AI-powered child online safety and time management", "CROWDING"),
            ("AttentionGym", "Focus training exercises and attention span building", "TOO_EARLY"),
        ],
    },
    "thesis_analogue_revival": {
        "adj": [
            ("SONO", "Sonos", "Premium physical audio equipment for vinyl"),
            ("HAS", "Hasbro", "Board games and physical toy resurgence"),
            ("MAT", "Mattel", "Physical toy and game manufacturer"),
            ("FNKO", "Funko", "Physical collectibles and pop culture figures"),
            ("B&N", "Barnes & Noble", "Physical bookstore revival (private)"),
            ("WMG", "Warner Music Group", "Vinyl record sales growth driver"),
        ],
        "hw": [
            ("AMZN", "Amazon", "CANARY — digital vs physical product mix ratio"),
            ("GOOGL", "Alphabet", "HEADWIND — digital-first ecosystem"),
            ("MSFT", "Microsoft", "CANARY — digital productivity tool adoption"),
            ("CRM", "Salesforce", "CANARY — digital transformation spending"),
            ("SHOP", "Shopify", "CANARY — physical vs digital commerce trends"),
            ("SQ", "Block Inc", "CANARY — in-person payment volumes vs digital"),
        ],
        "opps": [
            ("PaperMill", "Premium stationery and writing instrument subscription", "RIGHT_TIMING"),
            ("AnalogueClub", "Curated board game and tabletop subscription box", "RIGHT_TIMING"),
            ("FilmDrop", "Monthly film photography supply and development service", "RIGHT_TIMING"),
            ("VinylVault", "Rare vinyl discovery and authentication marketplace", "CROWDING"),
            ("TypeBar", "Typewriter rental and repair café franchise", "TOO_EARLY"),
            ("PlotLine", "Independent bookstore discovery and loyalty platform", "RIGHT_TIMING"),
        ],
    },
    "thesis_verification_crisis": {
        "adj": [
            ("INOD", "Innodata", "AI training data annotation and verification"),
            ("YOU", "Clear Secure", "Identity verification at airports and venues"),
            ("VRNT", "Verint Systems", "AI-powered fraud detection and verification"),
            ("GDYN", "Grid Dynamics", "Digital transformation and content verification"),
            ("DOCN", "DigitalOcean", "Cloud infrastructure for verification services"),
            ("TENB", "Tenable", "Cybersecurity and digital asset verification"),
        ],
        "hw": [
            ("AI", "C3.ai", "CANARY — enterprise AI adoption creating verification needs"),
            ("PLTR", "Palantir", "CANARY — government data verification spending"),
            ("SNOW", "Snowflake", "CANARY — data quality and governance demand"),
            ("MDB", "MongoDB", "CANARY — unstructured data growth signals verification load"),
            ("DDOG", "Datadog", "CANARY — monitoring and observability for AI systems"),
            ("ZS", "Zscaler", "CANARY — zero trust security adoption signals trust crisis"),
        ],
        "opps": [
            ("TruthStamp", "Blockchain-based content provenance and verification", "RIGHT_TIMING"),
            ("DeepDetect", "Real-time deepfake detection API for enterprises", "RIGHT_TIMING"),
            ("AuthorID", "AI content authorship attribution service", "RIGHT_TIMING"),
            ("FactChain", "Decentralized fact-checking and claim verification", "TOO_EARLY"),
            ("SignalNoise", "AI-generated vs human content classifier", "RIGHT_TIMING"),
            ("ProofPoint", "Digital evidence chain of custody for legal proceedings", "RIGHT_TIMING"),
        ],
    },
    "thesis_cognitive_decline": {
        "adj": [
            ("LLY", "Eli Lilly", "Donanemab Alzheimer's treatment"),
            ("BIIB", "Biogen", "Lecanemab Alzheimer's treatment partnership"),
            ("AXSM", "Axsome Therapeutics", "CNS disorder treatments"),
            ("SAVA", "Cassava Sciences", "Alzheimer's drug development"),
            ("CORT", "Corcept Therapeutics", "Cortisol-related cognitive treatments"),
            ("BMRN", "BioMarin", "Rare neurological disease treatments"),
        ],
        "hw": [
            ("GOOG", "Alphabet", "CANARY — search behavior complexity signals cognitive trends"),
            ("META", "Meta Platforms", "HEADWIND — social media linked to cognitive decline"),
            ("SNAP", "Snap Inc", "HEADWIND — short-form content and attention span"),
            ("TTWO", "Take-Two Interactive", "CANARY — gaming engagement and cognitive impact"),
            ("DIS", "Disney", "CANARY — content complexity trends signal audience capacity"),
            ("NFLX", "Netflix", "CANARY — viewing duration and content type shifts"),
        ],
        "opps": [
            ("BrainFit", "Personalized cognitive training and monitoring platform", "RIGHT_TIMING"),
            ("NeuroTrack", "Early cognitive decline detection via smartphone tests", "RIGHT_TIMING"),
            ("FocusForge", "Workplace cognitive performance optimization tools", "RIGHT_TIMING"),
            ("MindDiet", "Nutrition-based cognitive health meal planning", "RIGHT_TIMING"),
            ("CogniCare", "Cognitive decline caregiver support and resource platform", "RIGHT_TIMING"),
            ("ThinkTank", "Nootropic supplement quality verification and tracking", "TOO_EARLY"),
        ],
    },
    "thesis_taiwan_chip_risk": {
        "adj": [
            ("AVGO", "Broadcom", "Custom chip design shifting away from TSMC dependence"),
            ("TXN", "Texas Instruments", "US-based analog chip manufacturing"),
            ("GFS", "GlobalFoundries", "Non-Taiwan chip fabrication alternative"),
            ("ON", "ON Semiconductor", "US-based power and sensing semiconductor"),
            ("ADI", "Analog Devices", "US-based precision semiconductor company"),
            ("WOLF", "Wolfspeed", "US silicon carbide chip manufacturing"),
        ],
        "hw": [
            ("TSM", "TSMC", "HEADWIND — Taiwan concentration risk is the thesis itself"),
            ("ASML", "ASML", "CANARY — lithography equipment orders signal fab buildout"),
            ("AMAT", "Applied Materials", "CANARY — chip fab equipment demand patterns"),
            ("LRCX", "Lam Research", "CANARY — etch equipment orders for new fabs"),
            ("KLAC", "KLA Corp", "CANARY — process control equipment for chip quality"),
            ("UMC", "United Microelectronics", "HEADWIND — another Taiwan fab concentration risk"),
        ],
        "opps": [
            ("ChipMap", "Global semiconductor supply chain risk visualization", "RIGHT_TIMING"),
            ("FabTracker", "Real-time chip fab capacity and allocation monitoring", "RIGHT_TIMING"),
            ("SiliconInsure", "Semiconductor supply disruption insurance product", "RIGHT_TIMING"),
            ("ChipReserve", "Strategic chip inventory management for enterprises", "RIGHT_TIMING"),
            ("OnshoreChip", "US chip fab site selection and permitting platform", "TOO_EARLY"),
            ("DualSource", "Multi-fab semiconductor sourcing optimization", "RIGHT_TIMING"),
            ("ChipAudit", "Supply chain verification for semiconductor components", "RIGHT_TIMING"),
        ],
    },
    "thesis_dead_internet": {
        "adj": [
            ("RDDT", "Reddit", "Human-verified community content value"),
            ("PINS", "Pinterest", "Visual discovery with human curation"),
            ("WIKI", "Wikipedia Foundation", "Human-maintained knowledge base (proxy)"),
            ("ABNB", "Airbnb", "Real-world experience marketplace, anti-dead-internet"),
            ("YELP", "Yelp", "Verified human reviews gain premium"),
            ("ANGI", "Angi Inc", "Verified human service providers marketplace"),
        ],
        "hw": [
            ("GOOGL", "Alphabet", "HEADWIND — search quality degradation from AI content"),
            ("META", "Meta Platforms", "HEADWIND — AI-generated content flooding platforms"),
            ("MSFT", "Microsoft", "CANARY — Copilot usage signals AI content generation rate"),
            ("CRM", "Salesforce", "CANARY — AI content generation tool adoption"),
            ("ADBE", "Adobe", "CANARY — AI creative tool usage vs human creation"),
            ("SNAP", "Snap Inc", "CANARY — bot vs real user ratio on social platforms"),
        ],
        "opps": [
            ("HumanWeb", "Curated human-only internet content directory", "RIGHT_TIMING"),
            ("BotBlock", "AI bot detection and blocking service for websites", "RIGHT_TIMING"),
            ("RealTalk", "Verified-human-only social discussion platform", "RIGHT_TIMING"),
            ("AuthentiSearch", "Search engine that filters AI-generated content", "RIGHT_TIMING"),
            ("WebArchive", "Pre-AI internet archive and content preservation", "TOO_EARLY"),
            ("TrustNet", "Reputation system for human content creators", "RIGHT_TIMING"),
            ("PersonProof", "Proof-of-humanity API for online platforms", "RIGHT_TIMING"),
        ],
    },
}


def add_bets_and_opps(entity_id, entity_type, thesis_id_for_pool, current_bets, current_opps, db):
    """Add bets and opps to reach 9 each."""
    pool = THESIS_POOLS.get(thesis_id_for_pool)
    if not pool:
        return

    bets_needed = 9 - current_bets
    opps_needed = 9 - current_opps

    if bets_needed <= 0 and opps_needed <= 0:
        return

    # Get existing tickers to avoid duplicates
    if entity_type == "thesis":
        existing_tickers = {b.ticker for b in db.query(EquityBet).filter(
            EquityBet.thesis_id == entity_id, EquityBet.effect_id == None
        ).all()}
        existing_opp_names = {o.name for o in db.query(StartupOpportunity).filter(
            StartupOpportunity.thesis_id == entity_id, StartupOpportunity.effect_id == None
        ).all()}
    else:
        existing_tickers = {b.ticker for b in db.query(EquityBet).filter(
            EquityBet.effect_id == entity_id
        ).all()}
        existing_opp_names = {o.name for o in db.query(StartupOpportunity).filter(
            StartupOpportunity.effect_id == entity_id
        ).all()}

    # Add bets
    all_candidates = []
    for ticker, name, rationale in pool["adj"]:
        if ticker not in existing_tickers:
            all_candidates.append((ticker, name, rationale, "BENEFICIARY"))
    for ticker, name, rationale in pool["hw"]:
        if ticker not in existing_tickers:
            role = "HEADWIND" if "HEADWIND" in rationale else "CANARY"
            all_candidates.append((ticker, name, rationale.replace("HEADWIND — ", "").replace("CANARY — ", ""), role))

    for i, (ticker, name, rationale, role) in enumerate(all_candidates[:bets_needed]):
        bet = EquityBet(
            ticker=ticker,
            company_name=name,
            company_description=f"{name} — {rationale}",
            role=role,
            rationale=rationale,
            time_horizon="1-3yr",
            is_feedback_indicator=(role == "CANARY"),
            feedback_weight=0.1 if role == "CANARY" else 0.0,
        )
        if entity_type == "thesis":
            bet.thesis_id = entity_id
        else:
            bet.effect_id = entity_id
        db.add(bet)

    # Add opps
    opp_candidates = [(n, o, t) for n, o, t in pool["opps"] if n not in existing_opp_names]
    for i, (name, one_liner, timing) in enumerate(opp_candidates[:opps_needed]):
        opp = StartupOpportunity(
            name=name,
            one_liner=one_liner,
            timing=timing,
            time_horizon="1-3yr",
        )
        if entity_type == "thesis":
            opp.thesis_id = entity_id
        else:
            opp.effect_id = entity_id
        db.add(opp)


# ── MAIN ──────────────────────────────────────────────────────────────────────
print("Filling all entities to 9 bets + 9 opps...")

# 1. Thesis-level
for thesis in db.query(Thesis).all():
    bets = db.query(EquityBet).filter(EquityBet.thesis_id == thesis.id, EquityBet.effect_id == None).count()
    opps = db.query(StartupOpportunity).filter(StartupOpportunity.thesis_id == thesis.id, StartupOpportunity.effect_id == None).count()
    add_bets_and_opps(thesis.id, "thesis", thesis.id, bets, opps, db)
    print(f"  Thesis {thesis.id[:30]:30s} — adding {max(0,9-bets)} bets, {max(0,9-opps)} opps")

# 2. Effects (2nd and 3rd order)
for effect in db.query(Effect).all():
    bets = len(effect.equity_bets)
    opps = len(effect.startup_opportunities)
    add_bets_and_opps(effect.id, "effect", effect.thesis_id, bets, opps, db)
    if 9 - bets > 0 or 9 - opps > 0:
        print(f"  Effect {effect.id[:40]:40s} order={effect.order} — adding {max(0,9-bets)} bets, {max(0,9-opps)} opps")

db.commit()
print("Done! All entities should now have 9 bets + 9 opps.")

# Verify
print("\n=== VERIFICATION ===")
for thesis in db.query(Thesis).all():
    bets = db.query(EquityBet).filter(EquityBet.thesis_id == thesis.id, EquityBet.effect_id == None).count()
    opps = db.query(StartupOpportunity).filter(StartupOpportunity.thesis_id == thesis.id, StartupOpportunity.effect_id == None).count()
    status = "OK" if bets >= 9 and opps >= 9 else "NEEDS MORE"
    if status != "OK":
        print(f"  {thesis.id[:30]:30s} bets={bets} opps={opps} {status}")

short = []
for effect in db.query(Effect).all():
    bets = len(effect.equity_bets)
    opps = len(effect.startup_opportunities)
    if bets < 9 or opps < 9:
        short.append(f"  {effect.id[:40]:40s} order={effect.order} bets={bets} opps={opps}")
if short:
    print(f"\nEffects still short ({len(short)}):")
    for s in short[:10]:
        print(s)
    if len(short) > 10:
        print(f"  ... and {len(short)-10} more")
else:
    print("All effects have 9+ bets and 9+ opps!")

db.close()
