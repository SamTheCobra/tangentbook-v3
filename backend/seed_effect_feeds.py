"""
Seed bespoke DataFeeds for every 2nd and 3rd order effect.
Each 2nd order effect gets 3-5 feeds, each 3rd order gets 2-3 feeds.
Feeds are specific to the effect topic, not the parent thesis.
"""

import sys
sys.path.insert(0, ".")

from database import SessionLocal
from models import Effect, DataFeed, generate_uuid

db = SessionLocal()

# Map of effect title substring -> list of (name, source, source_type, series_id_or_keyword, confirming_direction)
# FRED feeds use series_id, GTRENDS feeds use keyword

EFFECT_FEEDS = {
    # ── USD Debasement ──────────────────────────────────────────────────
    "Crypto Becomes Mainstream": [
        ("Bitcoin Dominance Search", "GTRENDS", "adoption", None, "bitcoin ETF", "higher"),
        ("Crypto Exchange Volume", "GTRENDS", "flow", None, "crypto exchange", "higher"),
        ("Stablecoin Supply Search", "GTRENDS", "structural", None, "stablecoin", "higher"),
        ("M2 Money Supply", "FRED", "flow", "M2SL", None, "higher"),
    ],
    "DeFi Replaces Traditional Banking": [
        ("DeFi Protocol Search", "GTRENDS", "adoption", None, "defi protocol", "higher"),
        ("Decentralized Exchange Search", "GTRENDS", "flow", None, "decentralized exchange", "higher"),
        ("Fed Funds Rate", "FRED", "policy", "FEDFUNDS", None, "higher"),
    ],
    "Bitcoin Mining Industrializes": [
        ("Bitcoin Mining Search", "GTRENDS", "adoption", None, "bitcoin mining farm", "higher"),
        ("Industrial Electricity Price", "FRED", "structural", "APUS49D72610", None, "lower"),
    ],
    "Real Assets Become Inflation": [
        ("Gold Price Proxy", "FRED", "flow", "PPIACO", None, "higher"),
        ("Housing Starts", "FRED", "structural", "HOUST", None, "higher"),
        ("CPI All Urban", "FRED", "flow", "CPIAUCSL", None, "higher"),
        ("Real Estate Investment Search", "GTRENDS", "adoption", None, "real estate investment", "higher"),
    ],
    "Farmland": [
        ("Farmland Value Search", "GTRENDS", "adoption", None, "farmland investing", "higher"),
        ("Agricultural Price Index", "FRED", "flow", "PPIACO", None, "higher"),
        ("Farm Real Estate Value", "GTRENDS", "structural", None, "farm real estate value", "higher"),
    ],
    "Housing Affordability": [
        ("Mortgage Rate 30yr", "FRED", "flow", "MORTGAGE30US", None, "higher"),
        ("Housing Permits", "FRED", "structural", "PERMIT", None, "lower"),
        ("Rent Search Trend", "GTRENDS", "adoption", None, "rent prices increase", "higher"),
    ],
    "Commodity-Backed Digital": [
        ("Gold Price Index", "FRED", "flow", "PPIACO", None, "higher"),
        ("Digital Currency Search", "GTRENDS", "adoption", None, "gold backed cryptocurrency", "higher"),
        ("Dollar Index", "FRED", "structural", "DTWEXBGS", None, "lower"),
    ],
    "Gold-Backed Stablecoin": [
        ("Gold Stablecoin Search", "GTRENDS", "adoption", None, "gold stablecoin", "higher"),
        ("Gold Price Proxy", "FRED", "flow", "PPIACO", None, "higher"),
    ],
    "BRICS Currency": [
        ("BRICS Currency Search", "GTRENDS", "adoption", None, "BRICS currency", "higher"),
        ("Dollar Weakness", "FRED", "structural", "DTWEXBGS", None, "lower"),
    ],
    "Central Bank Digital": [
        ("CBDC Search Trend", "GTRENDS", "adoption", None, "central bank digital currency", "higher"),
        ("Fed Funds Rate", "FRED", "policy", "FEDFUNDS", None, "higher"),
    ],

    # ── GLP-1 Revolution ────────────────────────────────────────────────
    "Food Giants Get Murdered": [
        ("GLP-1 Weight Loss Search", "GTRENDS", "adoption", None, "ozempic weight loss", "higher"),
        ("Processed Food Search", "GTRENDS", "structural", None, "processed food health", "higher"),
        ("Consumer Sentiment", "FRED", "flow", "UMCSENT", None, "lower"),
        ("Retail Food Sales", "FRED", "flow", "RSAFS", None, "lower"),
    ],
    "Ultra-Processed Food Regulation": [
        ("Food Regulation Search", "GTRENDS", "policy", None, "food regulation health", "higher"),
        ("FDA Approval Search", "GTRENDS", "policy", None, "FDA ban processed food", "higher"),
    ],
    "Functional Food Premium": [
        ("Functional Food Search", "GTRENDS", "adoption", None, "functional food", "higher"),
        ("Health Food Search", "GTRENDS", "flow", None, "health food premium", "higher"),
    ],
    "Fast Food Menus Shrink": [
        ("Fast Food Health Search", "GTRENDS", "adoption", None, "fast food healthy menu", "higher"),
        ("Restaurant Sales", "FRED", "flow", "RSAFS", None, "lower"),
    ],
    "Hospitals Lose Their Cash": [
        ("Bariatric Surgery Search", "GTRENDS", "structural", None, "bariatric surgery decline", "higher"),
        ("Hospital Revenue Search", "GTRENDS", "flow", None, "hospital revenue decline", "higher"),
        ("Healthcare Employment", "FRED", "structural", "PAYEMS", None, "lower"),
        ("Health Insurance CPI", "FRED", "flow", "CPIMEDSL", None, "lower"),
    ],
    "Hospital Revenue Model": [
        ("Hospital Restructuring Search", "GTRENDS", "structural", None, "hospital restructuring", "higher"),
        ("Healthcare Spending", "FRED", "flow", "CPIMEDSL", None, "lower"),
    ],
    "Outpatient Surgery Centers": [
        ("Outpatient Surgery Search", "GTRENDS", "adoption", None, "outpatient surgery center", "higher"),
        ("Healthcare CPI", "FRED", "structural", "CPIMEDSL", None, "higher"),
    ],
    "Health System Revenue Diversification": [
        ("Telehealth Search", "GTRENDS", "adoption", None, "telehealth services", "higher"),
        ("Healthcare Employment", "FRED", "structural", "PAYEMS", None, "higher"),
    ],
    "Fashion Retail Inventory": [
        ("Plus Size Decline Search", "GTRENDS", "adoption", None, "weight loss clothing size", "higher"),
        ("Retail Inventory Search", "GTRENDS", "structural", None, "retail inventory clearance", "higher"),
        ("Retail Sales", "FRED", "flow", "RSAFS", None, "lower"),
    ],
    "Athleisure Becomes Default": [
        ("Athleisure Search", "GTRENDS", "adoption", None, "athleisure trend", "higher"),
        ("Athletic Wear Search", "GTRENDS", "flow", None, "athletic wear sales", "higher"),
    ],
    "Resale Market Floods": [
        ("Clothing Resale Search", "GTRENDS", "adoption", None, "sell used clothing online", "higher"),
        ("Plus Size Resale Search", "GTRENDS", "flow", None, "plus size clothing resale", "higher"),
    ],
    "Premium Basics Win": [
        ("Premium Basics Search", "GTRENDS", "adoption", None, "premium basics clothing", "higher"),
        ("Quality Over Quantity Search", "GTRENDS", "structural", None, "quality clothing buy less", "higher"),
    ],

    # ── AI Infrastructure Supercycle ────────────────────────────────────
    "Power Grid Hits Breaking": [
        ("Electricity Demand", "GTRENDS", "flow", None, "data center electricity demand", "higher"),
        ("Industrial Production", "FRED", "structural", "INDPRO", None, "higher"),
        ("Grid Reliability Search", "GTRENDS", "adoption", None, "power grid reliability", "higher"),
        ("Natural Gas Price", "FRED", "flow", "DCOILWTICO", None, "higher"),
    ],
    "Utility-Scale Battery Storage": [
        ("Battery Storage Search", "GTRENDS", "adoption", None, "utility battery storage", "higher"),
        ("Industrial Production", "FRED", "structural", "INDPRO", None, "higher"),
    ],
    "Microgrids for Critical": [
        ("Microgrid Search", "GTRENDS", "adoption", None, "microgrid installation", "higher"),
        ("Grid Outage Search", "GTRENDS", "flow", None, "power outage data center", "higher"),
    ],
    "Energy Arbitrage Software": [
        ("Energy Arbitrage Search", "GTRENDS", "adoption", None, "energy arbitrage software", "higher"),
        ("Electricity Price Volatility", "GTRENDS", "flow", None, "electricity price spike", "higher"),
    ],
    "Cooling Becomes the Bottleneck": [
        ("Data Center Cooling Search", "GTRENDS", "flow", None, "data center cooling demand", "higher"),
        ("Industrial Production", "FRED", "structural", "INDPRO", None, "higher"),
        ("GPU Demand Search", "GTRENDS", "adoption", None, "GPU demand AI", "higher"),
    ],
    "Liquid Cooling Becomes Standard": [
        ("Liquid Cooling Search", "GTRENDS", "adoption", None, "liquid cooling data center", "higher"),
        ("Server Cooling Search", "GTRENDS", "flow", None, "immersion cooling server", "higher"),
    ],
    "Data Center Location Shifts": [
        ("Nordic Data Center Search", "GTRENDS", "adoption", None, "data center cold climate", "higher"),
        ("Data Center Location Search", "GTRENDS", "structural", None, "data center location strategy", "higher"),
    ],
    "Waste Heat Recovery": [
        ("Waste Heat Search", "GTRENDS", "adoption", None, "data center waste heat", "higher"),
        ("District Heating Search", "GTRENDS", "flow", None, "district heating data center", "higher"),
    ],
    "AI Compute Shifts to Edge": [
        ("Edge Computing Search", "GTRENDS", "adoption", None, "edge computing AI", "higher"),
        ("On Device AI Search", "GTRENDS", "flow", None, "on device AI inference", "higher"),
        ("Industrial Production", "FRED", "structural", "INDPRO", None, "higher"),
    ],
    "On-Device AI Replaces": [
        ("On Device AI Search", "GTRENDS", "adoption", None, "on device AI model", "higher"),
        ("Mobile AI Search", "GTRENDS", "flow", None, "smartphone AI chip", "higher"),
    ],
    "Industrial IoT Gets AI": [
        ("Industrial IoT Search", "GTRENDS", "adoption", None, "industrial IoT AI", "higher"),
        ("Smart Manufacturing Search", "GTRENDS", "flow", None, "smart manufacturing AI", "higher"),
    ],
    "Privacy-First AI": [
        ("Privacy AI Search", "GTRENDS", "adoption", None, "privacy preserving AI", "higher"),
        ("Federated Learning Search", "GTRENDS", "flow", None, "federated learning", "higher"),
    ],

    # ── Reskilling Economy ──────────────────────────────────────────────
    "Credential Inflation Kills": [
        ("Skills Hiring Search", "GTRENDS", "adoption", None, "skills based hiring", "higher"),
        ("Degree Not Required Search", "GTRENDS", "structural", None, "no degree required job", "higher"),
        ("Unemployment Rate", "FRED", "flow", "UNRATE", None, "higher"),
        ("Initial Claims", "FRED", "flow", "ICSA", None, "higher"),
    ],
    "Skills-Based Hiring Goes": [
        ("Skills Hiring Search", "GTRENDS", "adoption", None, "skills assessment hiring", "higher"),
        ("Job Training Search", "GTRENDS", "flow", None, "job skills training", "higher"),
    ],
    "Certification Marketplaces": [
        ("Online Certification Search", "GTRENDS", "adoption", None, "professional certification online", "higher"),
        ("Career Certificate Search", "GTRENDS", "flow", None, "career certificate program", "higher"),
    ],
    "University Revenue Models Collapse": [
        ("University Enrollment Search", "GTRENDS", "adoption", None, "university enrollment decline", "higher"),
        ("Student Loan Search", "GTRENDS", "flow", None, "student loan debt crisis", "higher"),
    ],
    "Staffing Agencies Become": [
        ("Staffing Industry Search", "GTRENDS", "flow", None, "staffing agency talent", "higher"),
        ("Gig Economy Search", "GTRENDS", "adoption", None, "gig economy platform", "higher"),
        ("Job Openings", "FRED", "structural", "JTSJOL", None, "higher"),
    ],
    "AI Staffing Platforms": [
        ("AI Recruiting Search", "GTRENDS", "adoption", None, "AI recruiting platform", "higher"),
        ("Automated Hiring Search", "GTRENDS", "flow", None, "automated hiring tool", "higher"),
    ],
    "Cross-Industry Talent": [
        ("Career Change Search", "GTRENDS", "adoption", None, "career change 2025", "higher"),
        ("Transferable Skills Search", "GTRENDS", "flow", None, "transferable skills career", "higher"),
    ],
    "Fractional Executive": [
        ("Fractional Executive Search", "GTRENDS", "adoption", None, "fractional executive", "higher"),
        ("Part Time Executive Search", "GTRENDS", "flow", None, "part time CFO CTO", "higher"),
    ],
    "Career Anxiety Fuels": [
        ("Career Anxiety Search", "GTRENDS", "adoption", None, "career anxiety", "higher"),
        ("Job Loss Fear Search", "GTRENDS", "structural", None, "fear of losing job AI", "higher"),
        ("Consumer Sentiment", "FRED", "flow", "UMCSENT", None, "lower"),
    ],
    "Career Therapy Becomes": [
        ("Career Counseling Search", "GTRENDS", "adoption", None, "career counseling therapy", "higher"),
        ("Career Coach Search", "GTRENDS", "flow", None, "career transition coach", "higher"),
    ],
    "Substance Abuse Rises": [
        ("Substance Abuse Search", "GTRENDS", "adoption", None, "substance abuse treatment", "higher"),
        ("Unemployment Claims", "FRED", "flow", "ICSA", None, "higher"),
    ],
    "Financial Stress Counseling": [
        ("Financial Stress Search", "GTRENDS", "adoption", None, "financial stress counseling", "higher"),
        ("Consumer Credit", "FRED", "flow", "TOTALSL", None, "higher"),
    ],

    # ── Electricity Bottleneck ──────────────────────────────────────────
    "Nuclear Power Gets a Second": [
        ("Nuclear Energy Search", "GTRENDS", "adoption", None, "nuclear power plant new", "higher"),
        ("SMR Search", "GTRENDS", "flow", None, "small modular reactor", "higher"),
        ("Uranium Price Search", "GTRENDS", "structural", None, "uranium price", "higher"),
        ("Industrial Production", "FRED", "structural", "INDPRO", None, "higher"),
    ],
    "Small Modular Reactors": [
        ("SMR Technology Search", "GTRENDS", "adoption", None, "small modular reactor approval", "higher"),
        ("Nuclear Startup Search", "GTRENDS", "flow", None, "nuclear startup company", "higher"),
    ],
    "Nuclear Workforce Shortage": [
        ("Nuclear Jobs Search", "GTRENDS", "adoption", None, "nuclear engineer jobs", "higher"),
        ("Nuclear Training Search", "GTRENDS", "flow", None, "nuclear workforce training", "higher"),
    ],
    "Data Center Nuclear PPAs": [
        ("Data Center Nuclear Search", "GTRENDS", "adoption", None, "data center nuclear power", "higher"),
        ("PPA Nuclear Search", "GTRENDS", "flow", None, "power purchase agreement nuclear", "higher"),
    ],
    "Reshoring Stalls on Power": [
        ("Reshoring Search", "GTRENDS", "adoption", None, "reshoring manufacturing US", "higher"),
        ("Industrial Electricity Search", "GTRENDS", "flow", None, "industrial electricity cost", "higher"),
        ("Industrial Production", "FRED", "structural", "INDPRO", None, "higher"),
    ],
    "Manufacturing Moves to Power-Rich": [
        ("Manufacturing Relocation Search", "GTRENDS", "adoption", None, "manufacturing relocate cheap power", "higher"),
        ("Electricity Cost Search", "GTRENDS", "flow", None, "cheapest electricity state", "higher"),
    ],
    "On-Site Generation Becomes": [
        ("On Site Generation Search", "GTRENDS", "adoption", None, "on site power generation factory", "higher"),
        ("Industrial Solar Search", "GTRENDS", "flow", None, "industrial solar installation", "higher"),
    ],
    "Industrial Demand Response": [
        ("Demand Response Search", "GTRENDS", "adoption", None, "demand response industrial", "higher"),
        ("Grid Flexibility Search", "GTRENDS", "flow", None, "grid flexibility market", "higher"),
    ],
    "Grid Modernization": [
        ("Smart Grid Search", "GTRENDS", "adoption", None, "smart grid technology", "higher"),
        ("Grid Investment Search", "GTRENDS", "flow", None, "grid modernization investment", "higher"),
        ("Industrial Production", "FRED", "structural", "INDPRO", None, "higher"),
    ],
    "Smart Meter Rollout": [
        ("Smart Meter Search", "GTRENDS", "adoption", None, "smart meter installation", "higher"),
        ("AMI Search", "GTRENDS", "flow", None, "advanced metering infrastructure", "higher"),
    ],
    "Vehicle-to-Grid": [
        ("V2G Search", "GTRENDS", "adoption", None, "vehicle to grid technology", "higher"),
        ("EV Charging Search", "GTRENDS", "flow", None, "bidirectional EV charger", "higher"),
    ],
    "Grid Cybersecurity": [
        ("Grid Security Search", "GTRENDS", "adoption", None, "grid cybersecurity", "higher"),
        ("Critical Infrastructure Search", "GTRENDS", "flow", None, "critical infrastructure protection", "higher"),
    ],

    # ── AI Slop Makes Human-Made Premium ─────────────────────────────────
    "Live Events Become the Only": [
        ("Live Event Search", "GTRENDS", "adoption", None, "live events 2025", "higher"),
        ("Concert Ticket Search", "GTRENDS", "flow", None, "concert ticket prices", "higher"),
        ("Consumer Sentiment", "FRED", "structural", "UMCSENT", None, "higher"),
    ],
    "Live Event Ticket Prices": [
        ("Ticket Price Search", "GTRENDS", "adoption", None, "concert ticket expensive", "higher"),
        ("Event Demand Search", "GTRENDS", "flow", None, "live event demand", "higher"),
    ],
    "Experiential Dining": [
        ("Experience Dining Search", "GTRENDS", "adoption", None, "experiential dining", "higher"),
        ("Fine Dining Search", "GTRENDS", "flow", None, "fine dining experience", "higher"),
    ],
    "Human-Led Tourism": [
        ("Tour Guide Search", "GTRENDS", "adoption", None, "human tour guide premium", "higher"),
        ("Authentic Travel Search", "GTRENDS", "flow", None, "authentic travel experience", "higher"),
    ],
    "Etsy-fication": [
        ("Handmade Search", "GTRENDS", "adoption", None, "handmade artisan products", "higher"),
        ("Etsy Sales Search", "GTRENDS", "flow", None, "sell handmade online", "higher"),
        ("Craft Market Search", "GTRENDS", "structural", None, "craft market growth", "higher"),
    ],
    "Artisan Authentication": [
        ("Artisan Certification Search", "GTRENDS", "adoption", None, "artisan certification authentic", "higher"),
        ("Handmade Verification Search", "GTRENDS", "flow", None, "verify handmade product", "higher"),
    ],
    "Luxury Houses Double Down": [
        ("Luxury Craft Search", "GTRENDS", "adoption", None, "luxury handcrafted", "higher"),
        ("Artisan Luxury Search", "GTRENDS", "flow", None, "artisan luxury brand", "higher"),
    ],
    "Analog Art Market": [
        ("Physical Art Search", "GTRENDS", "adoption", None, "original art painting buy", "higher"),
        ("Art Gallery Search", "GTRENDS", "flow", None, "art gallery exhibition", "higher"),
    ],
    "Education System Can't Grade": [
        ("AI Cheating Search", "GTRENDS", "adoption", None, "AI cheating college", "higher"),
        ("Academic Integrity Search", "GTRENDS", "structural", None, "academic integrity AI", "higher"),
        ("Education Search", "GTRENDS", "policy", None, "AI education policy", "higher"),
    ],
    "Oral Exams Make a Comeback": [
        ("Oral Exam Search", "GTRENDS", "adoption", None, "oral examination university", "higher"),
        ("Viva Voce Search", "GTRENDS", "flow", None, "viva voce assessment", "higher"),
    ],
    "Academic Integrity Tools": [
        ("AI Detection Search", "GTRENDS", "adoption", None, "AI detection tool", "higher"),
        ("Plagiarism AI Search", "GTRENDS", "flow", None, "AI plagiarism detection", "higher"),
    ],
    "Hands-On Learning": [
        ("Hands On Learning Search", "GTRENDS", "adoption", None, "hands on learning program", "higher"),
        ("Experiential Education Search", "GTRENDS", "flow", None, "experiential learning school", "higher"),
    ],

    # ── Baby Boomers → Senior Living ────────────────────────────────────
    "Caregiver Wage Explosion": [
        ("Caregiver Salary Search", "GTRENDS", "adoption", None, "caregiver salary increase", "higher"),
        ("Home Health Aide Search", "GTRENDS", "flow", None, "home health aide shortage", "higher"),
        ("Healthcare Employment", "FRED", "structural", "PAYEMS", None, "higher"),
    ],
    "Caregiver Wage Premium": [
        ("Caregiver Pay Search", "GTRENDS", "adoption", None, "caregiver pay raise", "higher"),
        ("Care Worker Shortage Search", "GTRENDS", "flow", None, "care worker shortage crisis", "higher"),
    ],
    "Immigration Policy Favors Care": [
        ("Care Worker Visa Search", "GTRENDS", "policy", None, "care worker visa immigration", "higher"),
        ("Immigrant Caregiver Search", "GTRENDS", "flow", None, "immigrant caregiver program", "higher"),
    ],
    "Robot Assistance in Elder Care": [
        ("Elder Care Robot Search", "GTRENDS", "adoption", None, "elder care robot", "higher"),
        ("Assistive Technology Search", "GTRENDS", "flow", None, "assistive technology elderly", "higher"),
    ],
    "The $80T Wealth Transfer": [
        ("Wealth Transfer Search", "GTRENDS", "flow", None, "wealth transfer boomer", "higher"),
        ("Inheritance Planning Search", "GTRENDS", "adoption", None, "inheritance planning", "higher"),
        ("Consumer Credit", "FRED", "structural", "TOTALSL", None, "higher"),
    ],
    "Estate Planning Goes Digital": [
        ("Digital Estate Search", "GTRENDS", "adoption", None, "online estate planning", "higher"),
        ("Digital Will Search", "GTRENDS", "flow", None, "digital will service", "higher"),
    ],
    "Donor-Advised Funds Surge": [
        ("DAF Search", "GTRENDS", "adoption", None, "donor advised fund", "higher"),
        ("Charitable Giving Search", "GTRENDS", "flow", None, "charitable giving increase", "higher"),
    ],
    "Millennial Inheritance": [
        ("Inheritance Investment Search", "GTRENDS", "adoption", None, "invest inheritance money", "higher"),
        ("Millennial Wealth Search", "GTRENDS", "flow", None, "millennial wealth increase", "higher"),
    ],
    "Home Health Tech for Aging": [
        ("Aging in Place Search", "GTRENDS", "adoption", None, "aging in place technology", "higher"),
        ("Senior Tech Search", "GTRENDS", "flow", None, "smart home elderly", "higher"),
        ("Healthcare CPI", "FRED", "structural", "CPIMEDSL", None, "higher"),
    ],
    "Smart Home Monitoring for Seniors": [
        ("Senior Monitoring Search", "GTRENDS", "adoption", None, "senior home monitoring", "higher"),
        ("Fall Detection Search", "GTRENDS", "flow", None, "fall detection elderly", "higher"),
    ],
    "Medication Management Tech": [
        ("Medication Tech Search", "GTRENDS", "adoption", None, "medication management app", "higher"),
        ("Pill Dispenser Search", "GTRENDS", "flow", None, "automatic pill dispenser", "higher"),
    ],
    "Virtual Companion": [
        ("Virtual Companion Search", "GTRENDS", "adoption", None, "virtual companion elderly", "higher"),
        ("AI Companionship Search", "GTRENDS", "flow", None, "AI companion senior", "higher"),
    ],

    # ── Gen Z Micro-Luxuries ────────────────────────────────────────────
    "Legacy Luxury Brands Lose Gen Z": [
        ("Gen Z Luxury Search", "GTRENDS", "adoption", None, "gen z luxury brand", "higher"),
        ("Luxury Brand Decline Search", "GTRENDS", "structural", None, "luxury brand sales decline", "higher"),
        ("Retail Sales", "FRED", "flow", "RSAFS", None, "lower"),
    ],
    "Department Stores Accelerate Decline": [
        ("Department Store Search", "GTRENDS", "adoption", None, "department store closing", "higher"),
        ("Mall Vacancy Search", "GTRENDS", "flow", None, "mall vacancy rate", "higher"),
    ],
    "Luxury Conglomerates Acquire DTC": [
        ("DTC Acquisition Search", "GTRENDS", "adoption", None, "DTC brand acquisition luxury", "higher"),
        ("Direct Consumer Brand Search", "GTRENDS", "flow", None, "direct to consumer brand", "higher"),
    ],
    "Sustainability Becomes Purchase": [
        ("Sustainable Fashion Search", "GTRENDS", "adoption", None, "sustainable fashion brand", "higher"),
        ("Ethical Shopping Search", "GTRENDS", "flow", None, "ethical shopping gen z", "higher"),
    ],
    "Micro-Luxury Subscription Fatigue": [
        ("Subscription Fatigue Search", "GTRENDS", "adoption", None, "subscription fatigue cancel", "higher"),
        ("Subscription Box Search", "GTRENDS", "flow", None, "cancel subscription box", "higher"),
        ("Consumer Sentiment", "FRED", "structural", "UMCSENT", None, "lower"),
    ],
    "Subscription Churn Rates Spike": [
        ("Subscription Cancel Search", "GTRENDS", "adoption", None, "cancel subscription service", "higher"),
        ("Churn Rate Search", "GTRENDS", "flow", None, "subscription churn rate", "higher"),
    ],
    "Ownership Premium Returns": [
        ("Buy vs Rent Search", "GTRENDS", "adoption", None, "buy own instead subscribe", "higher"),
        ("Ownership Search", "GTRENDS", "flow", None, "ownership vs subscription", "higher"),
    ],
    "Bundle Wars Intensify": [
        ("Streaming Bundle Search", "GTRENDS", "adoption", None, "streaming bundle deal", "higher"),
        ("Bundle Subscription Search", "GTRENDS", "flow", None, "subscription bundle value", "higher"),
    ],
    "Secondhand Luxury": [
        ("Luxury Resale Search", "GTRENDS", "adoption", None, "luxury resale market", "higher"),
        ("Authentication Service Search", "GTRENDS", "flow", None, "luxury authentication service", "higher"),
        ("Retail Sales", "FRED", "structural", "RSAFS", None, "lower"),
    ],
    "Luxury Authentication Tech": [
        ("Luxury Auth Search", "GTRENDS", "adoption", None, "luxury product authentication", "higher"),
        ("Counterfeit Detection Search", "GTRENDS", "flow", None, "counterfeit luxury detection", "higher"),
    ],
    "Luxury Rental Market Explodes": [
        ("Luxury Rental Search", "GTRENDS", "adoption", None, "rent designer handbag", "higher"),
        ("Fashion Rental Search", "GTRENDS", "flow", None, "luxury fashion rental", "higher"),
    ],
    "Vintage Luxury Outperforms": [
        ("Vintage Luxury Search", "GTRENDS", "adoption", None, "vintage luxury investment", "higher"),
        ("Pre Owned Luxury Search", "GTRENDS", "flow", None, "pre owned luxury value", "higher"),
    ],

    # ── Sleep Status Symbol ─────────────────────────────────────────────
    "Caffeine Becomes the New Cigarette": [
        ("Sleep Health Search", "GTRENDS", "adoption", None, "sleep health importance", "higher"),
        ("Caffeine Quit Search", "GTRENDS", "flow", None, "quit caffeine benefits", "higher"),
        ("Consumer Sentiment", "FRED", "structural", "UMCSENT", None, "higher"),
    ],
    "Decaf and Adaptogen": [
        ("Decaf Search", "GTRENDS", "adoption", None, "decaf coffee trend", "higher"),
        ("Adaptogen Drink Search", "GTRENDS", "flow", None, "adaptogen drink", "higher"),
    ],
    "Caffeine Labeling Laws": [
        ("Caffeine Label Search", "GTRENDS", "policy", None, "caffeine labeling law", "higher"),
        ("Energy Drink Regulation Search", "GTRENDS", "policy", None, "energy drink regulation", "higher"),
    ],
    "Chronotype-Based Productivity": [
        ("Chronotype Search", "GTRENDS", "adoption", None, "chronotype productivity", "higher"),
        ("Sleep Schedule Search", "GTRENDS", "flow", None, "optimal sleep schedule work", "higher"),
    ],
    "Employers Start Mandating Rest": [
        ("Workplace Rest Search", "GTRENDS", "adoption", None, "workplace rest policy", "higher"),
        ("Employee Wellness Search", "GTRENDS", "flow", None, "employee sleep wellness", "higher"),
        ("Labor Productivity Search", "GTRENDS", "structural", None, "labor productivity decline", "higher"),
    ],
    "Nap Rooms Become Standard": [
        ("Nap Room Search", "GTRENDS", "adoption", None, "office nap room", "higher"),
        ("Workplace Sleep Search", "GTRENDS", "flow", None, "nap pod office", "higher"),
    ],
    "Shift Work Regulations": [
        ("Shift Work Law Search", "GTRENDS", "policy", None, "shift work regulation", "higher"),
        ("Work Schedule Law Search", "GTRENDS", "policy", None, "work schedule labor law", "higher"),
    ],
    "Sleep Insurance": [
        ("Sleep Insurance Search", "GTRENDS", "adoption", None, "sleep tracking insurance", "higher"),
        ("Health Insurance Wellness Search", "GTRENDS", "flow", None, "health insurance sleep discount", "higher"),
    ],
    "Master Bedroom Becomes": [
        ("Sleep Tech Search", "GTRENDS", "adoption", None, "sleep technology bedroom", "higher"),
        ("Smart Bedroom Search", "GTRENDS", "flow", None, "smart bedroom setup", "higher"),
        ("Housing Starts", "FRED", "structural", "HOUST", None, "higher"),
    ],
    "Smart Home Sleep Integration": [
        ("Sleep Smart Home Search", "GTRENDS", "adoption", None, "smart home sleep automation", "higher"),
        ("Sleep Environment Search", "GTRENDS", "flow", None, "optimize bedroom sleep", "higher"),
    ],
    "Sleep Retreat Tourism": [
        ("Sleep Retreat Search", "GTRENDS", "adoption", None, "sleep retreat resort", "higher"),
        ("Wellness Tourism Search", "GTRENDS", "flow", None, "wellness tourism sleep", "higher"),
    ],
    "Mattress Tech Innovation": [
        ("Smart Mattress Search", "GTRENDS", "adoption", None, "smart mattress technology", "higher"),
        ("Sleep Tracker Search", "GTRENDS", "flow", None, "sleep tracker mattress", "higher"),
    ],

    # ── Yield Curve Re-steepening ───────────────────────────────────────
    "Commercial Real Estate Refinancing": [
        ("CRE Refinancing Search", "GTRENDS", "flow", None, "commercial real estate refinancing", "higher"),
        ("10Y-2Y Spread", "FRED", "structural", "T10Y2Y", None, "higher"),
        ("Mortgage Rate", "FRED", "flow", "MORTGAGE30US", None, "lower"),
        ("Commercial RE Search", "GTRENDS", "adoption", None, "commercial real estate crisis", "higher"),
    ],
    "Office-to-Residential": [
        ("Office Conversion Search", "GTRENDS", "adoption", None, "office to residential conversion", "higher"),
        ("Remote Work Search", "GTRENDS", "flow", None, "remote work office vacancy", "higher"),
    ],
    "Distressed CRE Creates": [
        ("Distressed CRE Search", "GTRENDS", "adoption", None, "distressed commercial real estate", "higher"),
        ("CRE Investment Search", "GTRENDS", "flow", None, "buy distressed property", "higher"),
    ],
    "CMBS Market Restructuring": [
        ("CMBS Search", "GTRENDS", "adoption", None, "CMBS default rate", "higher"),
        ("Commercial Mortgage Search", "GTRENDS", "flow", None, "commercial mortgage backed securities", "higher"),
    ],
    "Community Banks Make a Comeback": [
        ("Community Bank Search", "GTRENDS", "adoption", None, "community bank growth", "higher"),
        ("Local Banking Search", "GTRENDS", "flow", None, "switch to community bank", "higher"),
        ("10Y-2Y Spread", "FRED", "structural", "T10Y2Y", None, "higher"),
    ],
    "Community Banks Win Local": [
        ("Local Bank Search", "GTRENDS", "adoption", None, "local bank small business loan", "higher"),
        ("Community Banking Search", "GTRENDS", "flow", None, "community bank advantage", "higher"),
    ],
    "Bank Charter Applications": [
        ("Bank Charter Search", "GTRENDS", "adoption", None, "bank charter application", "higher"),
        ("New Bank Search", "GTRENDS", "flow", None, "start a bank", "higher"),
    ],
    "Credit Union Membership": [
        ("Credit Union Search", "GTRENDS", "adoption", None, "join credit union", "higher"),
        ("Credit Union Growth Search", "GTRENDS", "flow", None, "credit union membership growth", "higher"),
    ],
    "Regional Bank Consolidation": [
        ("Bank Merger Search", "GTRENDS", "adoption", None, "regional bank merger", "higher"),
        ("Bank Consolidation Search", "GTRENDS", "flow", None, "bank consolidation wave", "higher"),
        ("Fed Funds Rate", "FRED", "policy", "FEDFUNDS", None, "higher"),
    ],
    "Community Bank M&A Advisory": [
        ("Bank M&A Search", "GTRENDS", "adoption", None, "community bank acquisition", "higher"),
        ("Bank Advisory Search", "GTRENDS", "flow", None, "bank merger advisory", "higher"),
    ],
    "Fintech Banks Capture Displaced": [
        ("Neobank Search", "GTRENDS", "adoption", None, "neobank growth", "higher"),
        ("Digital Bank Search", "GTRENDS", "flow", None, "switch to digital bank", "higher"),
    ],
    "Bank Branch Real Estate": [
        ("Bank Branch Closing Search", "GTRENDS", "adoption", None, "bank branch closing", "higher"),
        ("Bank Property Search", "GTRENDS", "flow", None, "bank branch real estate sale", "higher"),
    ],

    # ── Attention Economy → Anti-Addiction ──────────────────────────────
    "Social Media Gets Regulated": [
        ("Social Media Regulation Search", "GTRENDS", "policy", None, "social media regulation law", "higher"),
        ("Screen Time Limit Search", "GTRENDS", "adoption", None, "screen time limit children", "higher"),
        ("Consumer Sentiment", "FRED", "structural", "UMCSENT", None, "lower"),
    ],
    "Social Media Age Verification": [
        ("Age Verification Search", "GTRENDS", "policy", None, "social media age verification", "higher"),
        ("Kids Online Safety Search", "GTRENDS", "policy", None, "kids online safety act", "higher"),
    ],
    "Gambling App Regulation": [
        ("Gambling App Search", "GTRENDS", "policy", None, "gambling app regulation", "higher"),
        ("Sports Betting Law Search", "GTRENDS", "policy", None, "sports betting regulation", "higher"),
    ],
    "Notification Laws Emerge": [
        ("Notification Law Search", "GTRENDS", "policy", None, "notification regulation law", "higher"),
        ("Digital Wellness Law Search", "GTRENDS", "policy", None, "digital wellness legislation", "higher"),
    ],
    "Dumbphones Become a Status": [
        ("Dumbphone Search", "GTRENDS", "adoption", None, "dumbphone trend", "higher"),
        ("Digital Detox Search", "GTRENDS", "flow", None, "digital detox phone", "higher"),
        ("Feature Phone Search", "GTRENDS", "adoption", None, "feature phone sales", "higher"),
    ],
    "Feature Phone Sales Hit": [
        ("Basic Phone Search", "GTRENDS", "adoption", None, "basic phone no internet", "higher"),
        ("Light Phone Search", "GTRENDS", "flow", None, "light phone minimalist", "higher"),
    ],
    "Laptop-Only Work": [
        ("No Phone Work Search", "GTRENDS", "adoption", None, "laptop only no phone", "higher"),
        ("Digital Minimalism Search", "GTRENDS", "flow", None, "digital minimalism work", "higher"),
    ],
    "Analog Communication": [
        ("Letter Writing Search", "GTRENDS", "adoption", None, "handwritten letter trend", "higher"),
        ("Analog Communication Search", "GTRENDS", "flow", None, "analog communication revival", "higher"),
    ],
    "Deep Focus Becomes a Paid": [
        ("Focus App Search", "GTRENDS", "adoption", None, "focus app productivity", "higher"),
        ("Deep Work Search", "GTRENDS", "flow", None, "deep work coaching", "higher"),
        ("Attention Training Search", "GTRENDS", "structural", None, "attention training program", "higher"),
    ],
    "Focus Coaching Becomes": [
        ("Focus Coach Search", "GTRENDS", "adoption", None, "focus coaching service", "higher"),
        ("Attention Coach Search", "GTRENDS", "flow", None, "attention coaching", "higher"),
    ],
    "Attention-Respecting Products": [
        ("Calm Tech Search", "GTRENDS", "adoption", None, "calm technology design", "higher"),
        ("Humane Tech Search", "GTRENDS", "flow", None, "humane technology product", "higher"),
    ],
    "Meditation and Mindfulness": [
        ("Meditation App Search", "GTRENDS", "adoption", None, "meditation app", "higher"),
        ("Mindfulness Search", "GTRENDS", "flow", None, "mindfulness practice daily", "higher"),
    ],

    # ── Screentime Backlash → Analogue ──────────────────────────────────
    "Paper and Film Supply": [
        ("Film Photography Search", "GTRENDS", "adoption", None, "film photography trend", "higher"),
        ("Paper Notebook Search", "GTRENDS", "flow", None, "paper notebook sales", "higher"),
        ("Analog Trend Search", "GTRENDS", "structural", None, "analog products trend", "higher"),
    ],
    "Specialty Paper Mills": [
        ("Paper Mill Search", "GTRENDS", "adoption", None, "specialty paper production", "higher"),
        ("Stationery Search", "GTRENDS", "flow", None, "premium stationery brand", "higher"),
    ],
    "Film Photography Equipment": [
        ("Film Camera Search", "GTRENDS", "adoption", None, "buy film camera", "higher"),
        ("Kodak Film Search", "GTRENDS", "flow", None, "kodak film price", "higher"),
    ],
    "Analog Art Supply": [
        ("Art Supply Search", "GTRENDS", "adoption", None, "art supply store growth", "higher"),
        ("Traditional Art Search", "GTRENDS", "flow", None, "traditional art medium", "higher"),
    ],
    "Third Places Make a Physical": [
        ("Third Place Search", "GTRENDS", "adoption", None, "third place community", "higher"),
        ("Community Space Search", "GTRENDS", "flow", None, "community gathering space", "higher"),
        ("Consumer Sentiment", "FRED", "structural", "UMCSENT", None, "higher"),
    ],
    "Board Game Caf": [
        ("Board Game Cafe Search", "GTRENDS", "adoption", None, "board game cafe", "higher"),
        ("Board Game Sales Search", "GTRENDS", "flow", None, "board game sales trend", "higher"),
    ],
    "Community Workshop": [
        ("Makerspace Search", "GTRENDS", "adoption", None, "makerspace community", "higher"),
        ("Workshop Space Search", "GTRENDS", "flow", None, "community workshop space", "higher"),
    ],
    "Neighborhood Social": [
        ("Social Club Search", "GTRENDS", "adoption", None, "neighborhood social club", "higher"),
        ("Community Group Search", "GTRENDS", "flow", None, "join community group", "higher"),
    ],
    "Physical Retail Renaissance": [
        ("Physical Store Search", "GTRENDS", "adoption", None, "physical store comeback", "higher"),
        ("Retail Foot Traffic Search", "GTRENDS", "flow", None, "retail foot traffic increase", "higher"),
        ("Retail Sales", "FRED", "structural", "RSAFS", None, "higher"),
    ],
    "Independent Bookstores": [
        ("Independent Bookstore Search", "GTRENDS", "adoption", None, "independent bookstore growth", "higher"),
        ("Local Bookshop Search", "GTRENDS", "flow", None, "local bookshop open", "higher"),
    ],
    "Pop-Up Retail Becomes Permanent": [
        ("Pop Up Store Search", "GTRENDS", "adoption", None, "pop up store permanent", "higher"),
        ("Temporary Retail Search", "GTRENDS", "flow", None, "pop up retail trend", "higher"),
    ],
    "Experiential Retail Draws": [
        ("Experiential Retail Search", "GTRENDS", "adoption", None, "experiential retail store", "higher"),
        ("Retail Experience Search", "GTRENDS", "flow", None, "retail experience design", "higher"),
    ],

    # ── AI Content → Verification Crisis ────────────────────────────────
    "Digital Identity Becomes Mandatory": [
        ("Digital Identity Search", "GTRENDS", "adoption", None, "digital identity verification", "higher"),
        ("Identity Verification Search", "GTRENDS", "flow", None, "identity verification service", "higher"),
        ("Deepfake Detection Search", "GTRENDS", "structural", None, "deepfake detection", "higher"),
    ],
    "Government Digital ID": [
        ("Gov Digital ID Search", "GTRENDS", "policy", None, "government digital ID", "higher"),
        ("National ID Search", "GTRENDS", "policy", None, "national digital identity", "higher"),
    ],
    "Biometric Authentication Goes": [
        ("Biometric Auth Search", "GTRENDS", "adoption", None, "biometric authentication", "higher"),
        ("Face Recognition Search", "GTRENDS", "flow", None, "facial recognition security", "higher"),
    ],
    "Zero-Knowledge Proofs": [
        ("ZKP Search", "GTRENDS", "adoption", None, "zero knowledge proof", "higher"),
        ("Privacy Crypto Search", "GTRENDS", "flow", None, "privacy preserving authentication", "higher"),
    ],
    "Insurance Claims Become Unverifiable": [
        ("Claims Fraud Search", "GTRENDS", "flow", None, "insurance claims fraud AI", "higher"),
        ("Deepfake Insurance Search", "GTRENDS", "adoption", None, "deepfake insurance claim", "higher"),
        ("VIX Volatility", "FRED", "structural", "VIXCLS", None, "higher"),
    ],
    "Claims Verification Costs": [
        ("Claims Verification Search", "GTRENDS", "adoption", None, "insurance verification cost", "higher"),
        ("Fraud Detection Search", "GTRENDS", "flow", None, "AI fraud detection insurance", "higher"),
    ],
    "Video Evidence Standards": [
        ("Video Evidence Search", "GTRENDS", "adoption", None, "video evidence authentication", "higher"),
        ("Digital Evidence Search", "GTRENDS", "flow", None, "digital evidence standard", "higher"),
    ],
    "Deepfake Insurance Products": [
        ("Deepfake Insurance Search", "GTRENDS", "adoption", None, "deepfake insurance product", "higher"),
        ("AI Liability Search", "GTRENDS", "flow", None, "AI liability insurance", "higher"),
    ],
    "Courts Can't Trust Digital": [
        ("Digital Evidence Court Search", "GTRENDS", "adoption", None, "digital evidence court case", "higher"),
        ("AI Evidence Law Search", "GTRENDS", "policy", None, "AI generated evidence law", "higher"),
        ("Forensic Search", "GTRENDS", "structural", None, "digital forensics demand", "higher"),
    ],
    "Digital Evidence Expert Witness": [
        ("Expert Witness Search", "GTRENDS", "adoption", None, "digital forensics expert witness", "higher"),
        ("Court Expert Search", "GTRENDS", "flow", None, "expert witness technology", "higher"),
    ],
    "Notarization Goes Blockchain": [
        ("Blockchain Notary Search", "GTRENDS", "adoption", None, "blockchain notarization", "higher"),
        ("Digital Notary Search", "GTRENDS", "flow", None, "digital notary service", "higher"),
    ],
    "Witness Testimony Gains": [
        ("Witness Testimony Search", "GTRENDS", "adoption", None, "witness testimony importance", "higher"),
        ("Human Testimony Search", "GTRENDS", "flow", None, "human testimony court", "higher"),
    ],

    # ── AI-Induced Cognitive Decline ────────────────────────────────────
    "Critical Thinkers Command 3x": [
        ("Critical Thinking Search", "GTRENDS", "adoption", None, "critical thinking skills demand", "higher"),
        ("Cognitive Skills Search", "GTRENDS", "flow", None, "cognitive skills salary premium", "higher"),
        ("Job Openings", "FRED", "structural", "JTSJOL", None, "higher"),
    ],
    "Liberal Arts Degrees Regain": [
        ("Liberal Arts Search", "GTRENDS", "adoption", None, "liberal arts degree value", "higher"),
        ("Humanities Search", "GTRENDS", "flow", None, "humanities degree job", "higher"),
    ],
    "Cognitive Testing Enters Hiring": [
        ("Cognitive Test Search", "GTRENDS", "adoption", None, "cognitive assessment hiring", "higher"),
        ("IQ Test Hiring Search", "GTRENDS", "flow", None, "cognitive test employment", "higher"),
    ],
    "Executive Coaching Pivots": [
        ("Executive Cognition Search", "GTRENDS", "adoption", None, "executive coaching cognitive", "higher"),
        ("Brain Training Executive Search", "GTRENDS", "flow", None, "brain training executive", "higher"),
    ],
    "Schools Ban AI": [
        ("AI Ban School Search", "GTRENDS", "policy", None, "school ban AI", "higher"),
        ("Back to Basics Education Search", "GTRENDS", "adoption", None, "back to basics education", "higher"),
        ("Education Spending", "GTRENDS", "structural", None, "education spending increase", "higher"),
    ],
    "Waldorf and Montessori": [
        ("Waldorf School Search", "GTRENDS", "adoption", None, "waldorf school enrollment", "higher"),
        ("Montessori Search", "GTRENDS", "flow", None, "montessori school growth", "higher"),
    ],
    "Handwriting Returns": [
        ("Handwriting Search", "GTRENDS", "adoption", None, "handwriting education return", "higher"),
        ("Penmanship Search", "GTRENDS", "flow", None, "cursive handwriting school", "higher"),
    ],
    "Testing Reform": [
        ("Testing Reform Search", "GTRENDS", "policy", None, "standardized testing reform", "higher"),
        ("Assessment Change Search", "GTRENDS", "flow", None, "alternative assessment education", "higher"),
    ],
    "Brain Training": [
        ("Brain Training Search", "GTRENDS", "adoption", None, "brain training app", "higher"),
        ("Cognitive Supplement Search", "GTRENDS", "flow", None, "cognitive supplement nootropic", "higher"),
        ("Healthcare CPI", "FRED", "structural", "CPIMEDSL", None, "higher"),
    ],
    "Nootropics Market Goes": [
        ("Nootropics Search", "GTRENDS", "adoption", None, "nootropics clinical trial", "higher"),
        ("Brain Supplement Search", "GTRENDS", "flow", None, "brain supplement FDA", "higher"),
    ],
    "Brain-Computer Interfaces": [
        ("BCI Search", "GTRENDS", "adoption", None, "brain computer interface", "higher"),
        ("Neuralink Search", "GTRENDS", "flow", None, "brain interface wellness", "higher"),
    ],
    "Cognitive Health Insurance": [
        ("Cognitive Insurance Search", "GTRENDS", "adoption", None, "cognitive health insurance", "higher"),
        ("Brain Health Coverage Search", "GTRENDS", "flow", None, "brain health insurance rider", "higher"),
    ],

    # ── Chips Crashing / China ──────────────────────────────────────────
    "Defense Primes Get a Blank": [
        ("Defense Spending Search", "GTRENDS", "flow", None, "defense spending increase", "higher"),
        ("Military Budget Search", "GTRENDS", "policy", None, "military budget 2025", "higher"),
        ("VIX Volatility", "FRED", "structural", "VIXCLS", None, "higher"),
        ("Dollar Index", "FRED", "flow", "DTWEXBGS", None, "higher"),
    ],
    "Defense Tech Spending": [
        ("Defense Tech Search", "GTRENDS", "adoption", None, "defense technology spending", "higher"),
        ("Military Tech Search", "GTRENDS", "flow", None, "military technology contract", "higher"),
    ],
    "Semiconductor Stockpiling": [
        ("Chip Stockpile Search", "GTRENDS", "policy", None, "semiconductor stockpile", "higher"),
        ("Chip Reserve Search", "GTRENDS", "flow", None, "strategic chip reserve", "higher"),
    ],
    "Taiwan Strait Insurance": [
        ("Taiwan Risk Search", "GTRENDS", "adoption", None, "Taiwan strait risk", "higher"),
        ("Geopolitical Insurance Search", "GTRENDS", "flow", None, "geopolitical risk insurance", "higher"),
    ],
    "iPhone Prices Double": [
        ("iPhone Price Search", "GTRENDS", "flow", None, "iPhone price increase", "higher"),
        ("Chip Shortage Search", "GTRENDS", "structural", None, "chip shortage consumer", "higher"),
        ("Consumer Sentiment", "FRED", "structural", "UMCSENT", None, "lower"),
    ],
    "Device Lifecycle Extensions": [
        ("Phone Repair Search", "GTRENDS", "adoption", None, "phone repair instead buy new", "higher"),
        ("Right to Repair Search", "GTRENDS", "policy", None, "right to repair law", "higher"),
    ],
    "Refurbished Electronics": [
        ("Refurbished Phone Search", "GTRENDS", "adoption", None, "buy refurbished phone", "higher"),
        ("Certified Refurbished Search", "GTRENDS", "flow", None, "certified refurbished electronics", "higher"),
    ],
    "Alternative Chip Architectures": [
        ("RISC-V Search", "GTRENDS", "adoption", None, "RISC-V chip", "higher"),
        ("ARM Chip Search", "GTRENDS", "flow", None, "ARM architecture alternative", "higher"),
    ],
    "US-China Tech Decoupling": [
        ("Tech Decoupling Search", "GTRENDS", "adoption", None, "US China tech decoupling", "higher"),
        ("Export Controls Search", "GTRENDS", "policy", None, "semiconductor export controls", "higher"),
        ("Industrial Production", "FRED", "structural", "INDPRO", None, "higher"),
    ],
    "Tech Stack Bifurcation": [
        ("Tech Bifurcation Search", "GTRENDS", "adoption", None, "tech stack bifurcation", "higher"),
        ("China Tech Ban Search", "GTRENDS", "flow", None, "China tech ban", "higher"),
    ],
    "Semiconductor Equipment Controls": [
        ("ASML Export Search", "GTRENDS", "policy", None, "ASML export control", "higher"),
        ("Chip Equipment Search", "GTRENDS", "flow", None, "semiconductor equipment restriction", "higher"),
    ],
    "Friendly Shoring": [
        ("Friendshoring Search", "GTRENDS", "adoption", None, "friendshoring manufacturing", "higher"),
        ("Nearshoring Search", "GTRENDS", "flow", None, "nearshoring semiconductor", "higher"),
    ],

    # ── Dead Internet → Bot Economy ─────────────────────────────────────
    "Influencer Marketing Implodes": [
        ("Fake Followers Search", "GTRENDS", "adoption", None, "fake followers influencer", "higher"),
        ("Influencer Fraud Search", "GTRENDS", "flow", None, "influencer marketing fraud", "higher"),
        ("Bot Traffic Search", "GTRENDS", "structural", None, "bot traffic internet", "higher"),
    ],
    "Brand Ambassador Programs": [
        ("Brand Ambassador Search", "GTRENDS", "adoption", None, "brand ambassador program", "higher"),
        ("Employee Advocacy Search", "GTRENDS", "flow", None, "employee brand advocacy", "higher"),
    ],
    "Micro-Community Marketing": [
        ("Community Marketing Search", "GTRENDS", "adoption", None, "micro community marketing", "higher"),
        ("Niche Community Search", "GTRENDS", "flow", None, "niche community brand", "higher"),
    ],
    "Authenticity Verification": [
        ("Content Verification Search", "GTRENDS", "adoption", None, "content authenticity verification", "higher"),
        ("Human Verified Search", "GTRENDS", "flow", None, "human verified content", "higher"),
    ],
    "Traditional TV Gets a Second": [
        ("Linear TV Search", "GTRENDS", "adoption", None, "linear TV comeback", "higher"),
        ("Cable TV Search", "GTRENDS", "flow", None, "cable TV subscribers", "higher"),
        ("TV Ad Revenue Search", "GTRENDS", "structural", None, "TV advertising revenue", "higher"),
    ],
    "Live TV News Regains": [
        ("Live News Search", "GTRENDS", "adoption", None, "live TV news trust", "higher"),
        ("TV News Search", "GTRENDS", "flow", None, "TV news viewership", "higher"),
    ],
    "Appointment Viewing": [
        ("Appointment TV Search", "GTRENDS", "adoption", None, "appointment viewing TV", "higher"),
        ("Live TV Event Search", "GTRENDS", "flow", None, "live TV event watch", "higher"),
    ],
    "Physical Newspaper": [
        ("Newspaper Subscription Search", "GTRENDS", "adoption", None, "newspaper subscription increase", "higher"),
        ("Print News Search", "GTRENDS", "flow", None, "print newspaper revival", "higher"),
    ],
    "SEO Dies and Google Search": [
        ("Google Search Quality Search", "GTRENDS", "adoption", None, "google search quality decline", "higher"),
        ("SEO Death Search", "GTRENDS", "flow", None, "SEO dead AI", "higher"),
        ("Alternative Search Search", "GTRENDS", "structural", None, "google search alternative", "higher"),
    ],
    "Human-Curated Search": [
        ("Curated Search Search", "GTRENDS", "adoption", None, "human curated search", "higher"),
        ("Search Curation Search", "GTRENDS", "flow", None, "expert curated search engine", "higher"),
    ],
    "Forum and Community Platforms": [
        ("Reddit Growth Search", "GTRENDS", "adoption", None, "reddit growth users", "higher"),
        ("Online Forum Search", "GTRENDS", "flow", None, "online forum community", "higher"),
    ],
    "Review Economy Rebuilds": [
        ("Verified Review Search", "GTRENDS", "adoption", None, "verified review platform", "higher"),
        ("Fake Review Search", "GTRENDS", "flow", None, "fake review detection", "higher"),
    ],
}


def match_effect(effect_title: str) -> list | None:
    """Find matching feed config for an effect by substring match."""
    for key, feeds in EFFECT_FEEDS.items():
        if key.lower() in effect_title.lower():
            return feeds
    return None


def seed():
    effects = db.query(Effect).all()
    total_created = 0
    matched = 0
    unmatched = []

    for effect in effects:
        # Check if effect already has feeds
        existing = db.query(DataFeed).filter(DataFeed.effect_id == effect.id).count()
        if existing > 0:
            continue

        feed_configs = match_effect(effect.title)
        if not feed_configs:
            unmatched.append(effect.title)
            continue

        matched += 1
        for cfg in feed_configs:
            name, source, source_type, series_id, keyword, confirming = cfg
            feed = DataFeed(
                id=generate_uuid(),
                effect_id=effect.id,
                thesis_id=effect.thesis_id,
                name=name,
                description=f"Bespoke feed for effect: {effect.title}",
                source=source,
                source_type=source_type,
                series_id=series_id,
                keyword=keyword,
                confirming_direction=confirming,
                weight=1.0,
                status="live" if source == "FRED" else "degraded",
            )
            db.add(feed)
            total_created += 1

    db.commit()
    print(f"Created {total_created} bespoke feeds for {matched} effects")
    if unmatched:
        print(f"\n{len(unmatched)} unmatched effects:")
        for t in unmatched:
            print(f"  - {t}")


if __name__ == "__main__":
    seed()
    db.close()
