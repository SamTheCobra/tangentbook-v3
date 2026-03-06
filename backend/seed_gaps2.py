"""Fill remaining gaps: Senior Living + Yield Curve 2nd order effects, and all 3rd order effects."""

import sys
sys.path.insert(0, ".")

from database import SessionLocal
from models import Thesis, Effect, EquityBet, StartupOpportunity
import uuid

db = SessionLocal()

def uid():
    return str(uuid.uuid4())

def add_effect(thesis_id, parent_id, order, title, desc, bets, opps, thi_base=50):
    eid = uid()
    db.add(Effect(
        id=eid, thesis_id=thesis_id, parent_effect_id=parent_id, order=order,
        title=title, description=desc, thi_score=thi_base,
        thi_direction="confirming", thi_trend="stable",
        inheritance_weight=0.75 if order == 2 else 0.65,
        user_conviction_score=6 if order == 2 else 5,
    ))
    db.flush()
    for b in bets:
        db.add(EquityBet(
            id=uid(), effect_id=eid, ticker=b[0], company_name=b[1],
            company_description=b[2] if len(b) > 2 else f"{b[1]} — {b[0]}",
            role=b[3] if len(b) > 3 else "BENEFICIARY",
            rationale=b[4] if len(b) > 4 else f"Positioned for {title.lower()}",
            time_horizon="3-7yr", is_feedback_indicator=False, feedback_weight=0.0,
        ))
    for o in opps:
        db.add(StartupOpportunity(
            id=uid(), effect_id=eid, name=o[0], one_liner=o[1],
            timing="RIGHT_TIMING", time_horizon=o[2] if len(o) > 2 else "1-3yr",
        ))
    return eid

# ── SENIOR LIVING: add 3rd 2nd-order effect ──────────────────────────────
t = db.query(Thesis).filter(Thesis.id == "thesis_senior_living_boom").first()
if t:
    existing = [e for e in t.effects if e.parent_effect_id is None]
    if len(existing) < 3:
        add_effect("thesis_senior_living_boom", None, 2,
            "Home Health Tech for Aging in Place",
            "Most seniors want to age at home, not in facilities. Smart home health monitoring and remote care tech fills the gap between independence and institutional care.",
            [("AAPL", "Apple", "Apple Watch health monitoring — fall detection, vitals tracking for seniors", "BENEFICIARY"),
             ("AMZN", "Amazon", "Alexa ecosystem enables aging-in-place through voice-controlled home management", "BENEFICIARY"),
             ("GOOG", "Alphabet", "Google Health AI investments signal ambient monitoring viability", "CANARY")],
            [("SilverNest AI", "AI-powered home monitoring detecting anomalies in elderly daily routines"),
             ("MedPal", "Smart pill dispenser with video verification and family notification"),
             ("CareCircle", "Coordination platform connecting families, aides, and physicians for elder care")],
            thi_base=t.thi_score * 0.85,
        )
        print(f"  ADDED 2nd-order to Senior Living: Home Health Tech")
    db.commit()

# ── YIELD CURVE: add 3rd 2nd-order effect ─────────────────────────────
t = db.query(Thesis).filter(Thesis.id == "thesis_yield_curve_resteepening").first()
if t:
    existing = [e for e in t.effects if e.parent_effect_id is None]
    if len(existing) < 3:
        add_effect("thesis_yield_curve_resteepening", None, 2,
            "Regional Bank Consolidation Wave",
            "Higher-for-longer rates and deposit flight force small banks to merge or sell, creating a consolidation wave that benefits acquirers and fintech alternatives.",
            [("FITB", "Fifth Third Bancorp", "Super-regional bank well-positioned as acquirer in consolidation", "BENEFICIARY"),
             ("SOFI", "SoFi Technologies", "Digital bank capturing deposits fleeing struggling community banks", "BENEFICIARY"),
             ("KRE", "SPDR S&P Regional Banking ETF", "Regional bank ETF performance signals sector stress", "CANARY")],
            [("BankBridge", "M&A advisory platform specializing in community bank acquisitions with AI due diligence"),
             ("DepositShift", "Rate comparison engine helping depositors find best yields, accelerating deposit flight"),
             ("CoreSwap", "Cloud-based core banking system for post-merger integration")],
            thi_base=t.thi_score * 0.85,
        )
        print(f"  ADDED 2nd-order to Yield Curve: Regional Bank Consolidation")
    db.commit()

# ── NOW ADD 3RD ORDER EFFECTS FOR ALL 2ND-ORDER EFFECTS ──────────────
# Map actual effect_id → list of 3rd-order effect data
THIRD_ORDERS = {
    # AI Infrastructure
    "effect_ai_power_grid": [
        ("Utility-Scale Battery Storage Boom", "Grid instability drives massive investment in battery storage to buffer intermittent power.", [("GNRC", "Generac"), ("FSLR", "First Solar")], [("StorageOS", "Operating system for grid-scale battery deployments"), ("BatteryBank", "Financing platform for utility-scale battery projects")]),
        ("Microgrids for Critical Infrastructure", "Hospitals, data centers, and military bases build independent microgrids for resilience.", [("PWR", "Quanta Services"), ("EMR", "Emerson Electric")], [("MicroGrid Co", "Turnkey microgrid solutions for hospitals and campuses"), ("ResilienceScore", "Risk scoring for facilities based on grid dependency")]),
        ("Energy Arbitrage Software Explodes", "AI optimizes when to buy, store, and sell electricity as price volatility increases.", [("ENPH", "Enphase Energy"), ("RUN", "Sunrun")], [("WattTrade", "Energy arbitrage platform for commercial buildings"), ("PriceGrid", "Real-time electricity price prediction using weather and demand data")]),
    ],
    "effect_ai_cooling_crisis": [
        ("Liquid Cooling Becomes Standard", "Air cooling can't handle AI chip density — liquid cooling becomes mandatory.", [("VRT", "Vertiv Holdings"), ("JCI", "Johnson Controls")], [("CoolFlow", "Retrofittable liquid cooling kits for existing server racks"), ("ThermalIQ", "Predictive thermal management software optimizing cooling costs")]),
        ("Data Center Location Shifts to Cold Climates", "Nordic, Canadian, and high-altitude sites become premium as free cooling saves billions.", [("EQIX", "Equinix"), ("DLR", "Digital Realty")], [("ArcticHost", "Data center development in sub-arctic locations"), ("ClimaCool", "Climate modeling tool for data center site selection")]),
        ("Waste Heat Recovery Becomes Revenue Stream", "Data centers sell waste heat to district heating networks, turning cost into revenue.", [("TRANE", "Trane Technologies"), ("WMS", "Advanced Drainage Systems")], [("HeatGrid", "Platform connecting data center waste heat with district heating networks"), ("ThermalMarket", "Marketplace for waste heat trading between industrial facilities")]),
    ],
    # Electricity
    "effect_electricity_nuclear_renaissance": [
        ("Small Modular Reactors Break Through", "SMRs get NRC approval and first commercial deployments, solving nuclear scalability.", [("CEG", "Constellation Energy"), ("CCJ", "Cameco")], [("NukeLite", "Project finance platform for SMR deployments"), ("UraniumTracker", "Real-time uranium spot market tracking and supply chain analytics")]),
        ("Nuclear Workforce Shortage Emerges", "Not enough nuclear engineers and technicians to staff the renaissance, creating premium wages.", [("BWX", "BWX Technologies"), ("LEU", "Centrus Energy")], [("NukeSchool", "Accelerated nuclear technician training program"), ("AtomRecruit", "Specialized recruiting platform for nuclear industry talent")]),
        ("Data Center Nuclear PPAs Emerge", "Tech companies sign direct power purchase agreements with nuclear plants.", [("MSFT", "Microsoft"), ("AMZN", "Amazon")], [("AtomPPA", "Marketplace matching data centers with nuclear generators for PPAs"), ("BaseloadBroker", "Brokerage for 24/7 clean energy certificates tied to nuclear")]),
    ],
    "effect_electricity_industrial_reshoring_stall": [
        ("Manufacturing Moves to Power-Rich States", "States with cheap electricity (Texas, Wyoming) win reshoring deals over power-constrained ones.", [("CAT", "Caterpillar"), ("DE", "Deere & Co")], [("PowerMap", "Site selection tool ranking locations by electricity cost and reliability"), ("GridReady", "Power readiness certification for industrial development sites")]),
        ("On-Site Generation Becomes Standard for Factories", "Manufacturers build their own power plants rather than depending on stressed grids.", [("GE", "GE Vernova"), ("BA", "Boeing")], [("FactoryPower", "Turnkey on-site natural gas generation for industrial facilities"), ("PowerAudit", "Energy self-sufficiency assessment for manufacturing plants")]),
        ("Industrial Demand Response Creates New Market", "Factories get paid to reduce power consumption during peak demand, creating a new revenue stream.", [("ROK", "Rockwell Automation"), ("HON", "Honeywell")], [("DemandFlex", "Industrial demand response aggregation platform"), ("LoadShift", "AI that optimizes factory production schedules around electricity prices")]),
    ],
    # Reskilling
    "effect_reskill_credential_inflation": [
        ("Skills-Based Hiring Goes Mainstream", "Companies drop degree requirements, hiring based on demonstrated skills instead.", [("COUR", "Coursera"), ("UPWK", "Upwork")], [("SkillProof", "Portable skills verification platform for hiring"), ("HireRight AI", "AI that matches candidates to jobs based on skills, not credentials")]),
        ("Certification Marketplaces Explode", "Industry certifications become more valued than degrees — new cert providers emerge.", [("LOPE", "Grand Canyon Education"), ("LRN", "Stride Inc")], [("CertStack", "Stackable micro-certification platform"), ("CertAudit", "Quality assurance service verifying certification program rigor")]),
        ("University Revenue Models Collapse", "Traditional universities lose tuition revenue as alternatives prove more effective.", [("CHGG", "Chegg"), ("TWOU", "2U Inc")], [("UniPivot", "Consulting firm helping universities transition to skills-based programs"), ("AlumniNet", "Alumni network monetization platform for universities seeking new revenue")]),
    ],
    "effect_reskill_staffing_boom": [
        ("AI Staffing Platforms Displace Recruiters", "AI matches workers to jobs in real-time, disrupting traditional staffing agencies.", [("HUBS", "HubSpot"), ("ZI", "ZoomInfo")], [("MatchWork", "AI matching platform for temporary and contract workers"), ("GigScore", "Worker reliability scoring based on gig platform performance history")]),
        ("Cross-Industry Talent Mobility Increases", "Workers move between unrelated industries as transferable skills become recognized.", [("PAYC", "Paycom"), ("DAY", "Dayforce")], [("SkillBridge", "Platform mapping skill transferability between industries"), ("CareerGPS", "AI career navigator showing non-obvious industry transition paths")]),
        ("Fractional Executive Market Grows", "Senior execs work fractionally across 3-4 companies, creating a new employment model.", [("FVRR", "Fiverr"), ("UPWK", "Upwork")], [("FractionalC", "Marketplace for fractional C-suite executives"), ("BoardMatch", "Platform connecting fractional executives with companies needing part-time leadership")]),
    ],
    "effect_reskill_mental_health_surge": [
        ("Career Therapy Becomes Specialty", "Therapists specialize in career transition anxiety as a distinct clinical category.", [("TDOC", "Teladoc"), ("TALK", "Talkspace")], [("CareerMind", "Therapy platform specializing in career transition and identity loss"), ("WorkWell", "Employee mental health program focused on AI-related job anxiety")]),
        ("Substance Abuse Rises in Displaced Communities", "Towns dependent on automatable industries see substance abuse spikes.", [("ACHC", "Acadia Healthcare"), ("BHG", "BrightSpring Health")], [("RecoverLocal", "Community-based recovery programs for economically displaced areas"), ("HopeMap", "Resource mapping tool connecting displaced workers with mental health services")]),
        ("Financial Stress Counseling Demand Surges", "Career displacement causes financial crisis, driving demand for financial counseling.", [("SOFI", "SoFi"), ("LC", "LendingClub")], [("MoneyMind", "Financial therapy platform combining financial planning with mental health support"), ("SafetyNet", "Emergency financial assistance platform for workers in career transition")]),
    ],
    # AI Slop
    "effect_slop_live_events_premium": [
        ("Live Event Ticket Prices Double", "Scarcity of trustworthy content makes live events super-premium experiences.", [("LYV", "Live Nation"), ("MSGS", "MSG Sports")], [("LiveProof", "Anti-scalping ticketing with authenticity verification"), ("VenueFlex", "Pop-up venue platform converting spaces into live event locations")]),
        ("Experiential Dining Surges", "Restaurants where chef and ambiance ARE the product see premium pricing.", [("SG", "Sweetgreen"), ("CAVA", "CAVA Group")], [("ChefTable", "Platform booking exclusive chef's table experiences"), ("MealStory", "Farm-to-table dining with full provenance transparency")]),
        ("Human-Led Tourism Premiums", "AI plans trips but human guides and curators become the premium experience.", [("ABNB", "Airbnb"), ("BKNG", "Booking Holdings")], [("LocalGuide", "Platform matching travelers with verified local experts"), ("CultureWalk", "Walking tour platform with local storytellers")]),
    ],
    "effect_slop_artisan_ecommerce": [
        ("Artisan Authentication Becomes Industry", "Platforms verifying human craftsmanship see surging demand.", [("ETSY", "Etsy"), ("W", "Wayfair")], [("MakerProof", "Blockchain verification for handmade provenance"), ("CraftClass", "Platform connecting artisans with students learning traditional crafts")]),
        ("Luxury Houses Double Down on Craft", "Heritage luxury emphasizes hand-craftsmanship as differentiator vs AI-designed products.", [("RMS", "Hermès"), ("MC", "LVMH")], [("AtelierTour", "VR tours of luxury ateliers — see your bag being hand-stitched"), ("CraftDAO", "Artisan collective sharing marketing and logistics infrastructure")]),
        ("Analog Art Market Booms", "Physical art surges as digital art becomes synonymous with AI generation.", [("SOTH", "Sotheby's"), ("CHD", "Church & Dwight")], [("GalleryOS", "SaaS for independent galleries — inventory, sales, artist management"), ("ArtVault", "Climate-controlled art storage and logistics for collectors")]),
    ],
    "effect_slop_education_crisis": [
        ("Oral Exams Make a Comeback", "Schools return to oral and in-person assessment as written work becomes unverifiable.", [("ZME", "Zoom Video"), ("PRCT", "Procept BioRobotics")], [("OralPrep", "AI practice platform for oral examination preparation"), ("ExamLive", "Proctored in-person exam delivery service for schools and companies")]),
        ("Academic Integrity Tools Explode", "Every school needs AI detection and plagiarism prevention tools.", [("GOOG", "Alphabet"), ("MSFT", "Microsoft")], [("IntegrityAI", "Next-gen academic integrity tool combining AI detection with process monitoring"), ("WritingLab", "In-class supervised writing platform proving student authorship")]),
        ("Hands-On Learning Renaissance", "Schools shift to project-based, hands-on learning that can't be AI-generated.", [("AAPL", "Apple"), ("ADBE", "Adobe")], [("MakerSchool", "Curriculum-in-a-box for hands-on STEM education in K-12"), ("BuildLearn", "Physical project kits with assessment rubrics for hands-on skills")]),
    ],
    # Senior Living
    "effect_senior_caregiver_shortage": [
        ("Caregiver Wage Premium Expands", "Massive demand for eldercare workers drives wages up, attracting workers from other sectors.", [("AMN", "AMN Healthcare"), ("AMED", "Amedisys")], [("CareWage", "Wage benchmarking platform for home health agencies competing for workers"), ("CareTrack", "Training and certification platform for home health aides")]),
        ("Immigration Policy Favors Care Workers", "Countries create fast-track visas for eldercare workers as domestic supply falls short.", [("CCRN", "Cross Country Healthcare"), ("SHC", "Sotera Health")], [("CareVisa", "Staffing platform connecting international caregivers with US employers"), ("CultureBridge", "Cultural training program for international caregivers")]),
        ("Robot Assistance in Elder Care", "Assistive robots handle lifting, monitoring, and companionship, augmenting human caregivers.", [("ISRG", "Intuitive Surgical"), ("IRBT", "iRobot")], [("CompanionBot", "Social robot for elderly companionship — conversation, reminders, emergency"), ("LiftAssist", "Robotic lifting system for caregivers reducing back injuries")]),
    ],
    "effect_senior_wealth_transfer": [
        ("Estate Planning Goes Digital", "Digital estate planning tools become essential as $80T moves between generations.", [("LMND", "Lemonade"), ("SCI", "Service Corp Intl")], [("FinalPlan", "Digital end-of-life planning — will, directive, preferences in one place"), ("LegacyVault", "Secure digital inheritance for accounts, passwords, and digital assets")]),
        ("Donor-Advised Funds Surge", "Boomers direct wealth transfer through charitable vehicles, reshaping philanthropy.", [("BLK", "BlackRock"), ("SCHW", "Charles Schwab")], [("GiveSmarter", "AI-powered philanthropic advisory matching donors with high-impact causes"), ("ImpactTracker", "Platform measuring and reporting charitable giving outcomes")]),
        ("Millennial Inheritance Creates Investment Boom", "First-time inheritors flood into investing, creating demand for financial education.", [("HOOD", "Robinhood"), ("IBKR", "Interactive Brokers")], [("InheritWise", "Financial education platform specifically for first-time inheritors"), ("WealthOnboard", "Advisor-matching service for millennials receiving inheritance")]),
    ],
    # Gen Z
    "effect_microlux_legacy_brands_die": [
        ("Department Stores Accelerate Decline", "Traditional department stores lose Gen Z entirely to direct brands and resale.", [("M", "Macy's"), ("JWN", "Nordstrom")], [("ShopDirect", "Platform helping emerging brands sell direct without department store intermediaries"), ("RetailReborn", "Consulting firm converting dead mall space into experience-first retail")]),
        ("Luxury Conglomerates Acquire DTC Brands", "LVMH, Kering acquire digitally-native brands to access Gen Z customers.", [("MC", "LVMH"), ("KER", "Kering")], [("BrandScout", "M&A intelligence platform identifying hot DTC brands for luxury acquirers"), ("DigitalLux", "Digital brand building agency helping acquired DTC brands maintain authenticity")]),
        ("Sustainability Becomes Purchase Requirement", "Gen Z won't buy from brands without verified sustainability credentials.", [("TGT", "Target"), ("NKE", "Nike")], [("GreenProof", "Supply chain sustainability verification for consumer brands"), ("EcoScore", "Consumer app rating products on verified environmental impact")]),
    ],
    "effect_microlux_subscription_fatigue": [
        ("Subscription Churn Rates Spike", "Gen Z rotates rapidly between subscriptions, destroying LTV assumptions.", [("NFLX", "Netflix"), ("SPOT", "Spotify")], [("SubRotate", "Tool helping consumers optimize subscription spending by rotating services"), ("ChurnPredict", "AI predicting subscription churn for companies to intervene early")]),
        ("Ownership Premium Returns", "Owning things permanently becomes desirable again after subscription exhaustion.", [("AAPL", "Apple"), ("BBY", "Best Buy")], [("OwnIt", "Marketplace emphasizing permanent ownership over subscriptions"), ("BuyOnce", "Curation platform for products designed to last — the anti-disposable marketplace")]),
        ("Bundle Wars Intensify", "Platforms aggressively bundle services to reduce churn, creating new megabundles.", [("DIS", "Disney"), ("WBD", "Warner Bros Discovery")], [("BundleCalc", "Calculator showing true cost of bundle vs individual subscriptions"), ("StreamStack", "Universal streaming interface that works across all subscribed platforms")]),
    ],
    # Sleep
    "effect_sleep_caffeine_decline": [
        ("Decaf and Adaptogen Drinks Surge", "As caffeine gets stigmatized, alternative energy and focus drinks explode.", [("KO", "Coca-Cola"), ("SBUX", "Starbucks")], [("AdaptoBrew", "Functional mushroom and adaptogen coffee alternative brand"), ("DecafPremium", "Premium single-origin decaf coffee subscription")]),
        ("Caffeine Labeling Laws Emerge", "Regulations require caffeine content labeling on all beverages and foods.", [("MNST", "Monster Beverage"), ("CELH", "Celsius Holdings")], [("CaffeineTracker", "App scanning barcodes and tracking daily caffeine intake"), ("LabelWise", "Regulatory compliance tool for beverage companies on caffeine labeling")]),
        ("Chronotype-Based Productivity Takes Off", "Companies schedule work around natural energy cycles rather than caffeine-fueled productivity.", [("MSFT", "Microsoft"), ("GOOG", "Alphabet")], [("ChronoWork", "Scheduling tool that optimizes meeting times based on team chronotypes"), ("EnergyMap", "Wearable app showing personal energy levels throughout the day")]),
    ],
    "effect_sleep_employer_mandates": [
        ("Nap Rooms Become Standard Office Amenity", "Major companies install nap rooms, following Google and Nike's lead.", [("CBRE", "CBRE Group"), ("WPM", "Wheaton Precious Metals")], [("NapPod Pro", "Enterprise nap pod system with booking software and cleaning service"), ("RestSpace", "Office design firm specializing in sleep and recovery spaces")]),
        ("Shift Work Regulations Tighten", "Scientific evidence on shift work health risks drives new labor regulations.", [("UPS", "UPS"), ("FDX", "FedEx")], [("ShiftSafe", "Fatigue monitoring wearable with employer alerting for shift workers"), ("NightWell", "Health program designed specifically for nightshift workers")]),
        ("Sleep Insurance Discounts Emerge", "Health insurers offer discounts for employees who demonstrate good sleep habits.", [("UNH", "UnitedHealth"), ("CI", "Cigna")], [("SleepReward", "Insurance integration that rewards verified sleep quality with premium discounts"), ("WellRest", "Corporate wellness program with sleep-specific health outcomes tracking")]),
    ],
    "effect_sleep_bedroom_real_estate": [
        ("Smart Home Sleep Integration", "Bedroom becomes a controlled environment — lighting, sound, temperature all automated.", [("GOOGL", "Alphabet"), ("AAPL", "Apple")], [("SleepRoom", "Sleep-optimized bedroom design service — lighting, sound, air quality"), ("NightMode", "Smart home integration transitioning your home to sleep mode at bedtime")]),
        ("Sleep Retreat Tourism Explodes", "Hotels and resorts designed specifically for optimal sleep become a travel category.", [("H", "Hyatt Hotels"), ("HLT", "Hilton")], [("SleepRetreat", "Network of sleep-optimized retreat centers"), ("DreamStay", "Hotel booking platform filtering properties by sleep quality metrics")]),
        ("Mattress Tech Innovation Cycle Accelerates", "Smart mattresses with temperature, firmness, and biometric tracking become standard.", [("SNBR", "Sleep Number"), ("TPX", "Tempur Sealy")], [("SleepTemp", "Affordable smart mattress pad regulating temperature"), ("DreamData", "Sleep data analytics platform for mattress companies")]),
    ],
    # Yield Curve
    "effect_yield_cre_refinancing_crisis": [
        ("Office-to-Residential Conversions Surge", "Unfinanceable office buildings get converted to apartments, reshaping cities.", [("VNO", "Vornado Realty"), ("SLG", "SL Green Realty")], [("ConvertPro", "Software for modeling office-to-residential conversion feasibility"), ("AdaptiveReuse", "Architecture firm specializing in commercial-to-residential conversions")]),
        ("Distressed CRE Creates Buying Opportunity", "Well-capitalized buyers scoop up distressed commercial real estate at deep discounts.", [("BX", "Blackstone"), ("KKR", "KKR & Co")], [("DistressedDeal", "Marketplace for distressed commercial real estate assets"), ("CREValue", "AI-powered commercial real estate valuation for distressed properties")]),
        ("CMBS Market Restructuring", "Commercial mortgage-backed securities face wave of defaults and restructuring.", [("STWD", "Starwood Property"), ("BXMT", "Blackstone Mortgage")], [("CMBSTracker", "Real-time CMBS default and workout tracking platform"), ("LoanWork", "Digital platform for managing commercial loan workouts and modifications")]),
    ],
    "effect_yield_community_bank_revival": [
        ("Community Banks Win Local Business", "Small banks outcompete big banks on relationship lending and local knowledge.", [("SBNY", "Signature Bank"), ("EWBC", "East West Bancorp")], [("LocalLend", "Platform connecting small businesses with community bank loan officers"), ("BankReview", "Community bank comparison platform with customer reviews and rates")]),
        ("Bank Charter Applications Surge", "New bank charters increase as entrepreneurs see opportunity in community banking.", [("NYCB", "New York Community Bancorp"), ("WAL", "Western Alliance")], [("CharterAssist", "End-to-end platform for new bank charter applications"), ("BankStart", "Banking-as-a-service platform for de novo community banks")]),
        ("Credit Union Membership Explodes", "Consumers flee big bank fees to credit unions, driving record membership growth.", [("COOP", "Mr. Cooper Group"), ("SYF", "Synchrony Financial")], [("CUMatch", "Tool matching consumers with the best credit union for their needs"), ("CUTech", "Technology platform modernizing credit union digital banking experiences")]),
    ],
    # Anti-Addiction
    "effect_antiaddiction_regulation_wave": [
        ("Social Media Age Verification Passes", "Real age verification for social media restricts minor access.", [("META", "Meta Platforms"), ("RBLX", "Roblox")], [("AgeGate", "Privacy-preserving age verification API for platforms"), ("KidSafe", "Social platform designed for under-16s with parental controls")]),
        ("Gambling App Regulation Tightens", "Sports betting apps face advertising restrictions and usage limits.", [("DKNG", "DraftKings"), ("FLUT", "Flutter Entertainment")], [("BetLimit", "Self-exclusion tool working across all gambling platforms"), ("GambleGuard", "AI-powered gambling addiction detection for compliance")]),
        ("Notification Laws Emerge", "Legislation limits push notifications — a direct attack on the engagement economy.", [("MTCH", "Match Group"), ("BMBL", "Bumble")], [("QuietMode", "Enterprise notification management — batch alerts into daily digests"), ("NotifyAudit", "Tool helping apps comply with notification regulations")]),
    ],
    "effect_antiaddiction_dumbphone_boom": [
        ("Feature Phone Sales Hit Record", "Dumbphone and feature phone sales surge as consumers deliberately downgrade.", [("NOK", "Nokia"), ("GRMN", "Garmin")], [("LitePhone", "Premium feature phone brand with only calls, texts, maps, and music"), ("PhoneDetox", "30-day phone downgrade program with coaching and support")]),
        ("Laptop-Only Work Becomes Trend", "Knowledge workers leave phones at home, using only laptops for focused work.", [("AAPL", "Apple"), ("LNVGY", "Lenovo")], [("FocusDesk", "Productivity suite designed for laptop-only workers — no phone needed"), ("DeepWork", "Co-working spaces with phone lockers and zero-distraction policies")]),
        ("Analog Communication Revives", "Letters, phone calls, and in-person meetings regain status as premium communication.", [("USPS", "US Postal Service"), ("FDX", "FedEx")], [("LetterPress", "Modern letter-writing service — premium stationery, stamps, and delivery"), ("CallFirst", "App encouraging phone calls over texts with relationship tracking")]),
    ],
    "effect_antiaddiction_attention_premium": [
        ("Focus Coaching Becomes Industry", "Professional attention coaches charge premium rates for deep focus training.", [("CALM", "Calm"), ("PTON", "Peloton")], [("FocusCoach", "1-on-1 attention training with neurofeedback and accountability"), ("DeepFocus", "Corporate deep focus training program improving knowledge worker output")]),
        ("Attention-Respecting Products Win", "Consumer products designed to minimize distraction command premium pricing.", [("SONO", "Sonos"), ("GRMN", "Garmin")], [("MinimalTech", "Curation platform for technology products designed to minimize distraction"), ("QuietBrand", "Brand certification for products that respect user attention and wellbeing")]),
        ("Meditation and Mindfulness Mainstreams", "Meditation practice moves from wellness niche to standard productivity tool.", [("AAPL", "Apple"), ("GOOG", "Alphabet")], [("MindBridge", "Enterprise meditation program with measurable productivity outcomes"), ("ZenSpace", "Physical meditation spaces in office buildings — bookable quiet rooms")]),
    ],
    # Verification Crisis
    "effect_verification_identity_layer": [
        ("Government Digital ID Programs Launch", "Countries implement national digital identity systems to combat synthetic identity fraud.", [("OKTA", "Okta"), ("CRWD", "CrowdStrike")], [("NationID", "Digital identity infrastructure for government-issued verification"), ("IDLayer", "Universal identity verification API working across government and private sector")]),
        ("Biometric Authentication Goes Multimodal", "Single biometric (face, voice) becomes unreliable — systems combine multiple signals.", [("PANW", "Palo Alto Networks"), ("ZS", "Zscaler")], [("MultiBio", "Multimodal biometric authentication combining face, voice, and behavioral signals"), ("LiveProof", "Liveness detection that's resistant to deepfakes using multiple sensors")]),
        ("Zero-Knowledge Proofs Go Mainstream", "Privacy-preserving verification lets you prove identity without revealing personal data.", [("IBM", "IBM"), ("MSFT", "Microsoft")], [("ZKVerify", "Zero-knowledge proof verification for age, identity, and credentials"), ("PrivateID", "Privacy-preserving digital identity that reveals only necessary information")]),
    ],
    "effect_verification_insurance_chaos": [
        ("Claims Verification Costs Double", "Insurers spend 2x more on claims verification as synthetic media makes fraud easier.", [("AIG", "AIG"), ("TRV", "Travelers")], [("ClaimScan", "AI-powered insurance claims verification detecting synthetic media"), ("FraudNet", "Cross-insurer fraud detection network sharing synthetic media intelligence")]),
        ("Video Evidence Standards Change", "Courts and insurers establish new standards for video evidence authenticity.", [("VRSN", "Verisign"), ("RPD", "Rapid7")], [("EvidenceChain", "Tamper-proof evidence chain-of-custody platform"), ("VideoAuth", "Video authenticity certification service for legal and insurance use")]),
        ("Deepfake Insurance Products Launch", "New insurance products cover financial losses from deepfake attacks.", [("CB", "Chubb"), ("ALL", "Allstate")], [("DeepCover", "Insurance product covering businesses against deepfake-induced losses"), ("RepairAI", "Reputation management for deepfake damage mitigation")]),
    ],
    "effect_verification_legal_evidence_crisis": [
        ("Digital Evidence Expert Witness Demand Surges", "Courts need experts who can authenticate or debunk digital evidence.", [("VRSK", "Verisk Analytics"), ("BAH", "Booz Allen Hamilton")], [("ExpertWitness", "Marketplace connecting lawyers with digital evidence authentication experts"), ("ForensicAI", "AI-powered digital forensics tool for law firms and courts")]),
        ("Notarization Goes Blockchain", "Legal documents require cryptographic timestamps and verification on-chain.", [("DOCU", "DocuSign"), ("NOW", "ServiceNow")], [("ChainNotary", "Blockchain-based document notarization with tamper-proof timestamps"), ("LegalSeal", "Digital notarization service integrated with court filing systems")]),
        ("Witness Testimony Gains Importance", "Human testimony becomes MORE valuable as digital evidence becomes less trustworthy.", [("TRMB", "Trimble"), ("TYL", "Tyler Technologies")], [("WitnessPrep", "Platform for witness preparation and testimony coaching"), ("TestiTrack", "Court testimony management system with secure recording and transcription")]),
    ],
    # Taiwan Chip
    "effect_chips_defense_stocks_surge": [
        ("Defense Tech Spending Accelerates", "Taiwan risk drives massive defense technology spending across US allies.", [("LMT", "Lockheed Martin"), ("RTX", "RTX Corp")], [("DefenseTech Fund", "VC fund focused on dual-use defense technology startups"), ("DroneSwarm", "Autonomous drone swarm technology for perimeter defense")]),
        ("Semiconductor Stockpiling Becomes Policy", "Governments create strategic semiconductor reserves like petroleum reserves.", [("TSM", "Taiwan Semiconductor"), ("INTC", "Intel")], [("ChipReserve", "Advisory firm helping nations design strategic chip stockpiles"), ("SiliconVault", "Controlled-atmosphere storage for long-term semiconductor preservation")]),
        ("Taiwan Strait Insurance Market Grows", "Shipping insurance premiums for Taiwan Strait transit become significant cost.", [("CB", "Chubb"), ("ALL", "Allstate")], [("StraitRisk", "Real-time geopolitical risk scoring for Taiwan Strait routes"), ("TradeShield", "Parametric insurance for geopolitical events in Taiwan Strait")]),
    ],
    "effect_chips_consumer_electronics_shock": [
        ("Device Lifecycle Extensions", "Consumers keep devices longer as replacement costs spike, boosting repair market.", [("AAPL", "Apple"), ("DELL", "Dell")], [("RepairFirst", "Device repair marketplace matching broken electronics with certified technicians"), ("ExtendLife", "Software that optimizes older devices to extend useful life")]),
        ("Refurbished Electronics Market Doubles", "Refurbished phones and laptops surge as new device prices become prohibitive.", [("BBY", "Best Buy"), ("GME", "GameStop")], [("CertRefurb", "Certified refurbished electronics marketplace with warranty"), ("DeviceGrade", "AI-powered grading system for refurbished electronics quality")]),
        ("Alternative Chip Architectures Accelerate", "RISC-V and other open architectures gain adoption as proprietary chips become scarce.", [("AMD", "AMD"), ("QCOM", "Qualcomm")], [("RISCVStudio", "IDE and toolchain for RISC-V chip development"), ("OpenChip", "Collaborative platform for sharing open-source chip designs")]),
    ],
    "effect_chips_tech_cold_war": [
        ("Tech Stack Bifurcation", "World splits into US-allied and China-allied tech stacks, forcing companies to choose sides.", [("CRM", "Salesforce"), ("ORCL", "Oracle")], [("StackSwitch", "Migration tools for companies switching between US and China tech stacks"), ("TechNATO", "Compliance platform for companies navigating tech export controls")]),
        ("Semiconductor Equipment Controls Tighten", "US expands restrictions on chip-making equipment sales to China.", [("AMAT", "Applied Materials"), ("LRCX", "Lam Research")], [("ExportGuard", "Export control compliance software for semiconductor companies"), ("EquipmentTrack", "Supply chain monitoring for semiconductor equipment end-use verification")]),
        ("Friendly Shoring Becomes Standard", "Supply chains restructure to only source from geopolitically allied countries.", [("HON", "Honeywell"), ("GE", "GE Vernova")], [("AllySource", "Supply chain platform filtering suppliers by geopolitical risk alignment"), ("FriendShore", "Consulting firm helping manufacturers relocate supply chains to allied nations")]),
    ],
    # Dead Internet
    "effect_deadinternet_influencer_collapse": [
        ("Brand Ambassador Programs Replace Influencers", "Companies shift to verified employee and customer ambassadors instead of influencers.", [("SHOP", "Shopify"), ("TTD", "The Trade Desk")], [("AmbassadorOS", "Platform managing verified brand ambassador programs"), ("TrueReach", "Advertising verification ensuring real humans see branded content")]),
        ("Micro-Community Marketing Emerges", "Brands market through verified small communities instead of mass influencer campaigns.", [("RDDT", "Reddit"), ("DCT", "Discord")], [("CommunityAds", "Advertising platform for small, verified-human online communities"), ("TribeConnect", "Tool connecting brands with authentic micro-communities of real enthusiasts")]),
        ("Authenticity Verification Services Surge", "Third-party services verifying influencer authenticity become essential for brands.", [("IAS", "Integral Ad Science"), ("DV", "DoubleVerify")], [("InfluenceReal", "Platform verifying influencer authenticity — real followers, real person"), ("AdTruth", "Ad verification ensuring impressions from real humans, not bots")]),
    ],
    "effect_deadinternet_tv_revival": [
        ("Live TV News Regains Trust", "Live, unedited news broadcasts regain audience as pre-recorded content becomes suspect.", [("PARA", "Paramount"), ("CMCSA", "Comcast")], [("LiveVerify", "Technology proving broadcast content is live and unedited"), ("TrustTV", "Rating system for news broadcasts based on live vs produced content ratio")]),
        ("Appointment Viewing Returns", "Live, shared viewing experiences (sports, awards, finales) command premium ad rates.", [("DIS", "Disney"), ("FOXA", "Fox Corp")], [("WatchParty", "Platform for synchronized group viewing of live broadcasts"), ("LivePremium", "Ad marketplace for verified live broadcast ad slots at premium rates")]),
        ("Physical Newspaper Subscriptions Grow", "Physical newspapers gain subscribers as digital news becomes untrustable.", [("NYT", "New York Times"), ("NWSA", "News Corp")], [("PaperRoute", "Premium physical newspaper delivery service for digital-fatigued readers"), ("PrintNews", "On-demand physical newspaper printing from verified digital sources")]),
    ],
    "effect_deadinternet_seo_death": [
        ("Human-Curated Search Emerges", "Search engines with human curation replace algorithmic results.", [("GOOG", "Alphabet"), ("RDDT", "Reddit")], [("CuratedSearch", "Human-curated search engine — real people verify and rank results"), ("SearchGuild", "Expert community hand-picking best resources for specific queries")]),
        ("Forum and Community Platforms Surge", "Verified-human discussion forums replace social media for information seeking.", [("RDDT", "Reddit"), ("PINS", "Pinterest")], [("TrueForums", "Verified-human discussion platform with identity confirmation"), ("ExpertAsk", "Q&A platform where only verified domain experts can answer")]),
        ("Review Economy Rebuilds on Verification", "Review platforms require purchase verification and identity confirmation.", [("AMZN", "Amazon"), ("YELP", "Yelp")], [("TrueReview", "Verified purchase + identity review platform"), ("ReviewDAO", "Decentralized review system with token incentives for honest reviews")]),
    ],
}

print("═══ ADDING 3RD ORDER EFFECTS ═══")
for effect_id, thirds in THIRD_ORDERS.items():
    parent = db.query(Effect).filter(Effect.id == effect_id).first()
    if not parent:
        print(f"  SKIP: {effect_id} not found")
        continue
    existing = len(parent.child_effects)
    if existing >= 3:
        print(f"  SKIP: {parent.title} already has {existing} 3rd-order effects")
        continue
    needed = 3 - existing
    for td in thirds[:needed]:
        title, desc, bets, opps = td
        add_effect(parent.thesis_id, parent.id, 3, title, desc,
                  [(b[0], b[1]) for b in bets],
                  opps,
                  thi_base=parent.thi_score * 0.8)
        print(f"  ADDED: {parent.title} → {title}")

db.commit()

# ── FINAL AUDIT ───────────────────────────────────────────────────────
print("\n═══ FINAL AUDIT ═══")
theses = db.query(Thesis).order_by(Thesis.title).all()
for t in theses:
    effects_2nd = [e for e in t.effects if e.parent_effect_id is None]
    total_3rd = sum(len(e.child_effects) for e in effects_2nd)
    total_bets2 = sum(len(e.equity_bets) for e in effects_2nd)
    total_opps2 = sum(len(e.startup_opportunities) for e in effects_2nd)
    bets_3rd = sum(sum(len(c.equity_bets) for c in e.child_effects) for e in effects_2nd)
    opps_3rd = sum(sum(len(c.startup_opportunities) for c in e.child_effects) for e in effects_2nd)
    print(f"  {t.title[:40]:40s} 2nd={len(effects_2nd)} 3rd={total_3rd:2d} bets2={total_bets2} opps2={total_opps2} bets3={bets_3rd:2d} opps3={opps_3rd:2d}")

db.close()
