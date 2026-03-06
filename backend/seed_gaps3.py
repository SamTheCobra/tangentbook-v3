"""Fill final remaining 3rd-order effect gaps."""

import sys
sys.path.insert(0, ".")

from database import SessionLocal
from models import Thesis, Effect, EquityBet, StartupOpportunity
import uuid

db = SessionLocal()

def uid():
    return str(uuid.uuid4())

def add_3rd(thesis_id, parent_id, title, desc, bets, opps, thi_base=50):
    eid = uid()
    db.add(Effect(
        id=eid, thesis_id=thesis_id, parent_effect_id=parent_id, order=3,
        title=title, description=desc, thi_score=thi_base,
        thi_direction="confirming", thi_trend="stable",
        inheritance_weight=0.65, user_conviction_score=5,
    ))
    db.flush()
    for b in bets:
        db.add(EquityBet(
            id=uid(), effect_id=eid, ticker=b[0], company_name=b[1],
            company_description=f"{b[1]} — positioned in {title.lower()}",
            role="BENEFICIARY", rationale=f"Play on {title.lower()}",
            time_horizon="3-7yr", is_feedback_indicator=False, feedback_weight=0.0,
        ))
    for o in opps:
        db.add(StartupOpportunity(
            id=uid(), effect_id=eid, name=o[0], one_liner=o[1],
            timing="RIGHT_TIMING", time_horizon="1-3yr",
        ))

# Map: parent_effect_id → list of (title, desc, bets, opps)
REMAINING = {
    # AI Infrastructure → Edge & Inference (UUID)
    "a69b6794-ac76-432d-9eae-a30ed233c15e": [
        ("On-Device AI Replaces Cloud Calls", "Smartphones and laptops run AI locally, reducing cloud dependency and latency.", [("QCOM", "Qualcomm"), ("AAPL", "Apple")], [("EdgeKit", "SDK for deploying AI models to mobile devices"), ("LocalLLM", "Consumer app running private LLM entirely on-device")]),
        ("Industrial IoT Gets AI Brains", "Factory sensors and robots run AI inference locally for real-time decisions.", [("INTC", "Intel"), ("TXN", "Texas Instruments")], [("SmartFactory", "Edge AI platform for manufacturing quality control"), ("SensorBrain", "AI inference chip designed for industrial IoT sensors")]),
        ("Privacy-First AI Computing", "On-device AI processing keeps data local, addressing privacy concerns.", [("AAPL", "Apple"), ("CRM", "Salesforce")], [("PrivateAI", "On-device AI assistant that never sends data to the cloud"), ("DataLocal", "Enterprise AI platform guaranteeing data never leaves the device")]),
    ],
    # Cognitive Decline → Critical Thinkers
    "effect_cognitive_human_premium_hiring": [
        ("Liberal Arts Degrees Regain Value", "Philosophy, history, and literature majors become prized for critical thinking skills.", [("COUR", "Coursera"), ("LOPE", "Grand Canyon Education")], [("ThinkDegree", "Online liberal arts program emphasizing critical thinking for tech workers"), ("HumanSkill", "Certification in human reasoning and critical analysis")]),
        ("Cognitive Testing Enters Hiring", "Companies add cognitive assessment to hiring — not IQ tests but reasoning evaluations.", [("PAYC", "Paycom"), ("DAY", "Dayforce")], [("ReasonTest", "Cognitive reasoning assessment platform for hiring"), ("ThinkScore", "AI-resistant critical thinking evaluation for job candidates")]),
        ("Executive Coaching Pivots to Cognition", "C-suite coaching shifts from leadership soft skills to cognitive performance optimization.", [("PTON", "Peloton"), ("CALM", "Calm")], [("CogCoach", "Executive cognitive performance coaching with neurofeedback"), ("BrainPeak", "Cognitive optimization program for knowledge workers")]),
    ],
    # Cognitive Decline → Schools Ban AI
    "effect_cognitive_education_overhaul": [
        ("Waldorf and Montessori Schools Surge", "Screen-free education philosophies see massive enrollment growth.", [("LRN", "Stride Inc"), ("ATGE", "Adtalem Global")], [("ScreenFree School", "Franchise of tech-minimal K-8 schools"), ("NatureEd", "Outdoor-first curriculum platform for schools going screen-free")]),
        ("Handwriting Returns to Curriculum", "Research showing handwriting improves learning drives policy changes.", [("AAPL", "Apple"), ("GOOG", "Alphabet")], [("PenPal Pro", "Smart pen that digitizes handwritten notes while preserving the analog experience"), ("WriteLab", "Curriculum adding handwriting practice back into digital-native schools")]),
        ("Testing Reform Accelerates", "Standardized testing shifts to oral, project-based, and performance assessments.", [("ACT", "ACT Inc"), ("ETS", "ETS")], [("ProjectGrade", "Platform for managing and assessing project-based learning"), ("OralExam AI", "Practice platform for oral examination preparation")]),
    ],
    # Cognitive Decline → Brain Training (UUID)
    "76f2819b-c9d0-422c-bd1a-97be7b66325b": [
        ("Nootropics Market Goes Clinical", "Brain supplements get clinical validation, moving from wellness fad to real medicine.", [("HIMS", "Hims & Hers"), ("GIS", "General Mills")], [("NeuroPill", "Clinically-validated nootropic subscription based on cognitive biomarkers"), ("BrainPharm", "Clinical trials platform for cognitive enhancement supplements")]),
        ("Brain-Computer Interfaces for Wellness", "Consumer BCIs move from medical devices to wellness tools for cognitive training.", [("NKLA", "Nikola"), ("ISRG", "Intuitive Surgical")], [("MindLink", "Consumer EEG headband for daily cognitive training and meditation"), ("NeuroPeak", "Brain-computer interface training program for focus and memory")]),
        ("Cognitive Health Insurance Riders", "Health insurers add cognitive health coverage as dementia prevention becomes priority.", [("UNH", "UnitedHealth"), ("CI", "Cigna")], [("BrainCover", "Supplemental insurance product covering cognitive health screening and training"), ("CogniCheck", "Annual cognitive health assessment integrated with insurance wellness programs")]),
    ],
    # Senior Living → Home Health Tech (UUID)
    "676da396-fd31-45fd-a0b1-cc5f3baf1762": [
        ("Smart Home Monitoring for Seniors", "Ambient sensors detect falls, wandering, and routine changes without wearables.", [("AAPL", "Apple"), ("GOOG", "Alphabet")], [("AmbientCare", "Sensor system monitoring elderly daily routines and alerting families"), ("FallGuard", "AI-powered fall detection using home security cameras")]),
        ("Medication Management Tech Surges", "Smart pill dispensers and medication tracking prevent dangerous errors.", [("ABT", "Abbott Labs"), ("TMO", "Thermo Fisher")], [("MedBot", "Automated pill dispenser with video verification and family alerts"), ("PillTrack", "Medication adherence app with pharmacy integration")]),
        ("Virtual Companion Services Emerge", "AI companions provide social interaction and monitoring for isolated elderly.", [("AMZN", "Amazon"), ("META", "Meta")], [("CompanionAI", "AI companion for seniors — conversation, reminders, family connection"), ("SilverChat", "Video calling platform designed for elderly with simplified UI")]),
    ],
    # Electricity → Grid Modernization (UUID)
    "ee179848-5916-4906-8037-da2641f6db63": [
        ("Smart Meter Rollout Accelerates", "Utilities replace dumb meters with smart meters enabling real-time grid management.", [("ITRI", "Itron"), ("LNT", "Alliant Energy")], [("MeterOS", "Smart meter data analytics platform for utilities"), ("GridPulse", "Real-time grid health monitoring using smart meter data")]),
        ("Vehicle-to-Grid Becomes Reality", "EVs become mobile batteries, selling power back to the grid during peak demand.", [("TSLA", "Tesla"), ("F", "Ford")], [("V2Grid", "Vehicle-to-grid management platform for fleet operators"), ("ChargeBank", "App letting EV owners earn money by selling stored energy to the grid")]),
        ("Grid Cybersecurity Becomes Critical", "Smart grid increases attack surface, creating massive demand for grid security.", [("PANW", "Palo Alto Networks"), ("CRWD", "CrowdStrike")], [("GridShield", "Cybersecurity platform designed specifically for utility SCADA systems"), ("PowerSOC", "Managed security operations center for electric utilities")]),
    ],
    # GLP-1 → Hospitals (needs 2 more)
    "effect_glp1_hospitals": [
        ("Outpatient Surgery Centers Boom", "Healthier patients shift from inpatient to outpatient procedures, benefiting surgery centers.", [("SCA", "Surgery Partners"), ("USPH", "US Physical Therapy")], [("OutPatient OS", "Operating platform for ambulatory surgery centers"), ("SurgeryMatch", "Platform matching patients with the best outpatient surgery centers")]),
        ("Health System Revenue Diversification", "Hospitals pivot to wellness, prevention, and chronic care management to replace surgical revenue.", [("CVS", "CVS Health"), ("UNH", "UnitedHealth")], [("WellnessHub", "Hospital-affiliated wellness center operating platform"), ("PreventCare", "Chronic disease prevention program for health systems")]),
    ],
    # GLP-1 → Fashion (needs 2 more)
    "effect_glp1_fashion": [
        ("Resale Market Floods with Larger Sizes", "Rapid weight loss creates a glut of barely-worn clothing in larger sizes on resale platforms.", [("POSH", "Poshmark"), ("TDUP", "ThredUp")], [("SizeSwap", "Peer-to-peer clothing exchange for weight transition"), ("DonateFlow", "Logistics connecting weight-loss clothing donations to shelters")]),
        ("Premium Basics Win Over Fast Fashion", "Consumers invest in fewer, better-fitting essentials as body confidence grows.", [("LEVI", "Levi Strauss"), ("VFC", "VF Corp")], [("Essentials Club", "Premium basics subscription — perfect-fit staples refreshed quarterly"), ("BodyFit AI", "Virtual try-on using phone body scan to guarantee fit")]),
    ],
    # Gen Z → Secondhand Luxury (UUID)
    "4b3ee852-bb93-438b-811d-3b43fb51c929": [
        ("Luxury Authentication Tech Becomes Industry", "AI and blockchain power authentication of luxury goods at scale.", [("REAL", "The RealReal"), ("ETSY", "Etsy")], [("LegitCheck AI", "Phone-based AI authentication verifying luxury goods via computer vision"), ("AuthChain", "Blockchain provenance tracking for luxury items from manufacture to resale")]),
        ("Luxury Rental Market Explodes", "Gen Z rents luxury items for events and social media rather than buying.", [("RENT", "Rent the Runway"), ("W", "Wayfair")], [("RentTheIcon", "Luxury item rental — wear Chanel for a weekend"), ("LuxShare", "Peer-to-peer luxury item sharing for special occasions")]),
        ("Vintage Luxury Outperforms New", "Pre-owned luxury items from iconic eras command higher prices than new products.", [("RMS", "Hermès"), ("MC", "LVMH")], [("VintageVault", "Curated vintage luxury marketplace with authentication and grading"), ("EraStyle", "Styling service specializing in vintage luxury curation")]),
    ],
    # Analogue Revival → Paper Shortage
    "effect_analogue_paper_shortage": [
        ("Specialty Paper Mills Reopen", "Demand for high-quality paper, film, and analog materials exceeds supply.", [("IP", "International Paper"), ("PKG", "Packaging Corp")], [("FinePress", "Boutique paper mill producing premium stationery and art paper"), ("PaperDirect", "D2C specialty paper subscription for artists and writers")]),
        ("Film Photography Equipment Prices Surge", "35mm cameras and darkroom equipment become collectible premium goods.", [("SONY", "Sony"), ("FUJI", "Fujifilm")], [("FilmRevival", "Refurbished film camera marketplace with repair services"), ("DarkroomKit", "All-in-one darkroom setup kit for home film development")]),
        ("Analog Art Supply Brands Thrive", "High-quality analog art supplies (paints, pencils, inks) see premium demand.", [("KOSS", "Koss Corp"), ("CROX", "Crocs")], [("ArtCrate", "Monthly subscription of curated analog art supplies"), ("StudioSupply", "B2B platform supplying schools and studios with analog art materials")]),
    ],
    # Analogue Revival → Third Places
    "effect_analogue_third_places": [
        ("Board Game Cafés Become Franchise", "Board game cafés scale from indie to franchise as demand for IRL social spaces grows.", [("HAS", "Hasbro"), ("MAT", "Mattel")], [("GameNight Café", "Board game café franchise model — food, games, community"), ("PlaySpace", "Platform for booking private game rooms and event spaces")]),
        ("Community Workshop Spaces Multiply", "Makerspaces, pottery studios, and craft workshops expand as alternatives to screens.", [("ETSY", "Etsy"), ("JOBY", "Joby Aviation")], [("MakerLocal", "Marketplace for booking time at local workshop spaces"), ("CraftPass", "Monthly pass giving access to a network of craft workshops")]),
        ("Neighborhood Social Clubs Return", "Membership-based local social clubs offering meals, activities, and community.", [("SBUX", "Starbucks"), ("CMG", "Chipotle")], [("LocalClub", "App for discovering and joining neighborhood social clubs"), ("CommunityHouse", "Franchise of membership social spaces with food, events, and community")]),
    ],
    # Analogue Revival → Physical Retail (UUID)
    "4ab48a16-49d9-4edc-b571-b1f0cef7ccbf": [
        ("Independent Bookstores Hit Record Numbers", "New indie bookstore openings outpace closures for first time in decades.", [("AMZN", "Amazon"), ("BKS", "B&N Education")], [("BookstoreOS", "Management software designed for independent bookstores"), ("LocalReads", "App for discovering and supporting local independent bookstores")]),
        ("Pop-Up Retail Becomes Permanent", "Temporary pop-up shops become permanent retail strategy for digital-native brands.", [("SHOP", "Shopify"), ("SQ", "Block")], [("PopUpPro", "Platform managing pop-up retail from location to POS to inventory"), ("SpaceMatch", "Marketplace connecting empty retail spaces with brands for short-term leases")]),
        ("Experiential Retail Draws Foot Traffic", "Stores become experiences — workshops, tastings, demonstrations — not just transaction points.", [("TGT", "Target"), ("COST", "Costco")], [("RetailXP", "Consulting firm redesigning stores as experience destinations"), ("ShopEvent", "Platform helping retailers host in-store events and workshops")]),
    ],
    # USD Debasement → Commodity-Backed Digital Currencies (UUID)
    "92f2dfdc-cdec-4a76-bc45-36ee2bb46dc3": [
        ("Gold-Backed Stablecoins Go Mainstream", "Tokenized gold becomes a standard treasury reserve for corporations and nations.", [("GLD", "SPDR Gold"), ("COIN", "Coinbase")], [("GoldRail", "Cross-border payment system using gold-backed stablecoins"), ("StableMint", "Platform for issuing custom commodity-backed tokens")]),
        ("BRICS Currency Backed by Commodities", "BRICS nations launch commodity-backed trade settlement currency, challenging dollar hegemony.", [("BHP", "BHP Group"), ("RIO", "Rio Tinto")], [("TradeSettle", "Settlement platform for commodity-backed bilateral trade agreements"), ("ReserveOS", "Treasury management for corporations hedging FX with commodity-backed reserves")]),
        ("Central Bank Digital Currencies Compete", "CBDCs race to launch, some backed by commodities, creating a new monetary landscape.", [("V", "Visa"), ("MA", "Mastercard")], [("CBDCBridge", "Interoperability platform connecting different national CBDCs"), ("DigitalFX", "Foreign exchange platform for trading between CBDCs and crypto")]),
    ],
    # Yield Curve → Regional Bank Consolidation (UUID)
    "1c0dfacf-2b82-4e8e-95a4-8005acd5e876": [
        ("Community Bank M&A Advisory Surges", "Wave of forced mergers creates massive demand for bank M&A advisory services.", [("GS", "Goldman Sachs"), ("LAZ", "Lazard")], [("BankDeal", "M&A advisory platform specializing in community bank acquisitions"), ("DealRoom", "Virtual data room designed for bank merger due diligence")]),
        ("Fintech Banks Capture Displaced Depositors", "Depositors from merged/closed community banks flow to digital-first alternatives.", [("SOFI", "SoFi"), ("ALLY", "Ally Financial")], [("DepositCapture", "Marketing platform targeting depositors of merging banks"), ("SwitchBank", "Automated bank switching service handling direct deposit and bill pay migration")]),
        ("Bank Branch Real Estate Hits Market", "Closed bank branches create commercial real estate opportunities in small towns.", [("KIM", "Kimco Realty"), ("NNN", "NNN REIT")], [("BranchConvert", "Consulting firm converting closed bank branches to community spaces"), ("SmallTownHub", "Platform repurposing bank branch locations into co-working and community centers")]),
    ],
}

print("═══ ADDING REMAINING 3RD ORDER EFFECTS ═══")
for parent_id, thirds in REMAINING.items():
    parent = db.query(Effect).filter(Effect.id == parent_id).first()
    if not parent:
        print(f"  SKIP: {parent_id} not found")
        continue
    existing = len(parent.child_effects)
    needed = 3 - existing
    if needed <= 0:
        print(f"  SKIP: {parent.title} already has {existing} 3rd-order")
        continue
    for td in thirds[:needed]:
        title, desc, bets, opps = td
        add_3rd(parent.thesis_id, parent.id, title, desc, bets, opps, parent.thi_score * 0.8)
        print(f"  ADDED: {parent.title[:35]} → {title}")

db.commit()

# Final audit
print("\n═══ FINAL AUDIT ═══")
theses = db.query(Thesis).order_by(Thesis.title).all()
all_good = True
for t in theses:
    effects_2nd = [e for e in t.effects if e.parent_effect_id is None]
    total_3rd = sum(len(e.child_effects) for e in effects_2nd)
    total_bets2 = sum(len(e.equity_bets) for e in effects_2nd)
    total_opps2 = sum(len(e.startup_opportunities) for e in effects_2nd)
    bets_3rd = sum(sum(len(c.equity_bets) for c in e.child_effects) for e in effects_2nd)
    opps_3rd = sum(sum(len(c.startup_opportunities) for c in e.child_effects) for e in effects_2nd)
    status = "OK" if len(effects_2nd) >= 3 and total_3rd >= 9 else "GAPS"
    if status == "GAPS":
        all_good = False
    print(f"  [{status:4s}] {t.title[:38]:38s} 2nd={len(effects_2nd)} 3rd={total_3rd:2d} bets2={total_bets2} opps2={total_opps2} bets3={bets_3rd:2d} opps3={opps_3rd:2d}")

if all_good:
    print("\nALL THESES FULLY SEEDED!")
else:
    print("\nSome gaps remain — check output above.")

db.close()
