"""
Deduplicate tickers and startup opportunities across parent/child effect levels.
- Thesis-level bets stay as-is (they're the "anchors")
- 2nd order effects get unique tickers that don't overlap with thesis
- 3rd order effects get unique tickers that don't overlap with their parent 2nd order
- Same for startup opportunities
"""

import sys
sys.path.insert(0, ".")

from database import SessionLocal
from models import Thesis, Effect, EquityBet, StartupOpportunity, generate_uuid

db = SessionLocal()

# Replacement ticker pools per theme area
# Each pool has: (ticker, company_name, role, rationale)
TICKER_POOLS = {
    "usd_debasement": [
        ("GDXJ", "VanEck Junior Gold Miners", "BENEFICIARY", "Junior gold miners amplify gold price moves with higher leverage"),
        ("PAXG", "Paxos Gold Token", "BENEFICIARY", "Gold-backed crypto asset bridges physical and digital stores of value"),
        ("WPM", "Wheaton Precious Metals", "BENEFICIARY", "Streaming model profits from rising precious metal prices"),
        ("AG", "First Majestic Silver", "BENEFICIARY", "Silver mining pure-play benefits from monetary metal demand"),
        ("BITO", "ProShares Bitcoin Strategy", "BENEFICIARY", "Bitcoin futures ETF gives regulated crypto exposure"),
        ("RIOT", "Riot Platforms", "BENEFICIARY", "Bitcoin mining at industrial scale as digital gold production"),
        ("DBA", "Invesco DB Agriculture", "BENEFICIARY", "Agricultural commodities rise with inflation and dollar weakness"),
        ("UUP", "Invesco DB US Dollar", "HEADWIND", "Dollar strength fund loses as debasement thesis plays out"),
        ("TLT", "iShares 20+ Year Treasury", "CANARY", "Long bonds signal inflation expectations and real rate changes"),
        ("DXY", "Dollar Index ETF", "HEADWIND", "Dollar weakness confirms debasement thesis"),
        ("PHYS", "Sprott Physical Gold", "BENEFICIARY", "Physical gold trust offers allocated bullion exposure"),
        ("KGC", "Kinross Gold", "BENEFICIARY", "Mid-tier gold producer with low-cost operations"),
        ("AEM", "Agnico Eagle Mines", "BENEFICIARY", "Premium gold miner with strong operational track record"),
        ("FNV", "Franco-Nevada", "BENEFICIARY", "Gold royalty streaming model provides leveraged exposure"),
        ("SAND", "Sandstorm Gold", "BENEFICIARY", "Diversified royalty company across precious metals"),
        ("EQX", "Equinox Gold", "BENEFICIARY", "Growth-oriented gold producer building production base"),
        ("BTG", "B2Gold Corp", "BENEFICIARY", "Low-cost gold producer in emerging market jurisdictions"),
        ("GLDM", "SPDR Gold MiniShares", "BENEFICIARY", "Low-cost gold ETF for retail investors"),
    ],
    "glp1": [
        ("TMDX", "TransMedics Group", "BENEFICIARY", "Organ transplant logistics benefits from declining organ disease"),
        ("ISRG", "Intuitive Surgical", "BENEFICIARY", "Robotic surgery leader benefits from surgical procedure shifts"),
        ("ALGN", "Align Technology", "BENEFICIARY", "Dental/aesthetic alignment benefits from health-conscious consumers"),
        ("INSP", "Inspire Medical", "BENEFICIARY", "Sleep apnea device maker benefits as weight loss reduces apnea"),
        ("GDRX", "GoodRx", "BENEFICIARY", "Prescription savings platform benefits from GLP-1 drug demand"),
        ("LFST", "LifeStance Health", "BENEFICIARY", "Mental health provider benefits as weight loss drives therapy"),
        ("BYRN", "Byrna Technologies", "CANARY", "Non-lethal defense shows consumer confidence trends"),
        ("KR", "Kroger", "HEADWIND", "Grocery volumes decline as appetite suppression reduces consumption"),
        ("VITL", "Vital Farms", "BENEFICIARY", "Premium food brand wins as consumers eat less but better"),
        ("SMPL", "Simply Good Foods", "HEADWIND", "Snack food brand faces volume pressure from appetite reduction"),
        ("CELH", "Celsius Holdings", "CANARY", "Fitness energy drink signals health-conscious consumer behavior"),
        ("PLNT", "Planet Fitness", "BENEFICIARY", "Gym membership grows as GLP-1 users adopt active lifestyles"),
        ("WRBY", "Warby Parker", "CANARY", "Consumer discretionary signals health spending priorities"),
        ("LULU", "Lululemon", "BENEFICIARY", "Athletic wear demand grows as health-conscious lifestyle expands"),
        ("HLF", "Herbalife", "HEADWIND", "Weight loss supplement demand declines with pharma alternatives"),
        ("WW", "WW International", "HEADWIND", "Traditional weight loss programs disrupted by GLP-1 drugs"),
    ],
    "ai_infra": [
        ("IREN", "Iris Energy", "BENEFICIARY", "Bitcoin/AI data center operator with renewable energy focus"),
        ("VRT", "Vertiv Holdings", "BENEFICIARY", "Power and cooling infrastructure for data centers"),
        ("ANET", "Arista Networks", "BENEFICIARY", "Data center networking for AI workloads"),
        ("PWR", "Quanta Services", "BENEFICIARY", "Electrical infrastructure builder for grid expansion"),
        ("FSLR", "First Solar", "BENEFICIARY", "Solar panel maker benefits from data center power demand"),
        ("NEE", "NextEra Energy", "BENEFICIARY", "Renewable utility powers data center expansion"),
        ("ENPH", "Enphase Energy", "BENEFICIARY", "Microinverters for distributed solar powering edge compute"),
        ("SEDG", "SolarEdge", "CANARY", "Solar inverter demand signals distributed energy build-out"),
        ("AES", "AES Corp", "BENEFICIARY", "Utility with data center PPA expertise"),
        ("EMR", "Emerson Electric", "BENEFICIARY", "Industrial automation and power management for AI facilities"),
        ("GEV", "GE Vernova", "BENEFICIARY", "Power generation equipment for grid expansion"),
        ("POWI", "Power Integrations", "BENEFICIARY", "Power conversion chips for efficient AI infrastructure"),
        ("CLSK", "CleanSpark", "BENEFICIARY", "Bitcoin mining with clean energy focus"),
        ("OKLO", "Oklo Inc", "BENEFICIARY", "Advanced fission micro-reactor for data center power"),
        ("NNE", "Nano Nuclear", "BENEFICIARY", "Portable nuclear reactors for remote power generation"),
        ("LEU", "Centrus Energy", "BENEFICIARY", "Enriched uranium supplier for nuclear power renaissance"),
    ],
    "reskilling": [
        ("COUR", "Coursera", "BENEFICIARY", "Online education platform for workforce reskilling"),
        ("UDMY", "Udemy", "BENEFICIARY", "Skills marketplace for professional development"),
        ("PRCT", "PROCEPT BioRobotics", "CANARY", "Robotic procedure adoption signals skill transition"),
        ("PAYC", "Paycom Software", "BENEFICIARY", "HR tech benefits from credential management complexity"),
        ("PCTY", "Paylocity", "BENEFICIARY", "HR platform gains as talent management grows complex"),
        ("KNBE", "KnowBe4", "BENEFICIARY", "Security awareness training as reskilling example"),
        ("CDAY", "Ceridian HCM", "BENEFICIARY", "Workforce management platform for career transitions"),
        ("HUBS", "HubSpot", "CANARY", "SaaS adoption signals digital skill demand"),
        ("WDAY", "Workday", "BENEFICIARY", "Enterprise HR platform for skills-based workforce planning"),
        ("UPWK", "Upwork", "BENEFICIARY", "Freelance platform benefits from gig economy growth"),
        ("FVRR", "Fiverr", "BENEFICIARY", "Freelance marketplace for fractional skill deployment"),
        ("LRN", "Stride Inc", "BENEFICIARY", "Online K-12 education as credential alternative"),
        ("ATGE", "Adtalem Global", "BENEFICIARY", "Career-focused education and professional training"),
        ("LOPE", "Grand Canyon Ed", "BENEFICIARY", "University with strong career-focused programs"),
    ],
    "electricity": [
        ("CEG", "Constellation Energy", "BENEFICIARY", "Nuclear fleet operator benefits from power demand surge"),
        ("VST", "Vistra Corp", "BENEFICIARY", "Power generator profits from electricity price increases"),
        ("NRG", "NRG Energy", "BENEFICIARY", "Integrated power company benefits from grid strain"),
        ("SO", "Southern Company", "BENEFICIARY", "Regulated utility with nuclear and renewables portfolio"),
        ("ETR", "Entergy Corp", "BENEFICIARY", "Nuclear utility serving high-growth industrial markets"),
        ("PCG", "PG&E Corp", "CANARY", "California utility faces grid reliability challenges"),
        ("SMR", "NuScale Power", "BENEFICIARY", "Small modular reactor developer for distributed nuclear"),
        ("BWXT", "BWX Technologies", "BENEFICIARY", "Nuclear components manufacturer for reactor builds"),
        ("DUK", "Duke Energy", "BENEFICIARY", "Major utility planning nuclear capacity additions"),
        ("CCJ", "Cameco Corp", "BENEFICIARY", "Uranium mining leader benefits from nuclear renaissance"),
        ("UEC", "Uranium Energy", "BENEFICIARY", "US uranium producer for domestic nuclear fuel supply"),
        ("FLNC", "Fluence Energy", "BENEFICIARY", "Grid-scale battery storage solutions"),
        ("STEM", "Stem Inc", "BENEFICIARY", "AI-driven energy storage optimization"),
        ("ACHR", "Archer Aviation", "CANARY", "eVTOL signals electrification infrastructure demand"),
    ],
    "human_premium": [
        ("LYV", "Live Nation", "BENEFICIARY", "Live events monopoly benefits from authenticity premium"),
        ("SPOT", "Spotify", "CANARY", "Music streaming signals content consumption shifts"),
        ("PINS", "Pinterest", "CANARY", "Visual discovery platform signals handmade/artisan interest"),
        ("CHWY", "Chewy", "CANARY", "E-commerce personalization signals authenticity demand"),
        ("ETSY", "Etsy", "BENEFICIARY", "Handmade marketplace directly benefits from artisan premium"),
        ("ABNB", "Airbnb", "BENEFICIARY", "Experiential travel benefits from authenticity demand"),
        ("DIS", "Walt Disney", "BENEFICIARY", "Theme parks and live entertainment benefit from experience demand"),
        ("BKNG", "Booking Holdings", "BENEFICIARY", "Travel platform benefits from experiential tourism growth"),
        ("DUOL", "Duolingo", "BENEFICIARY", "Language learning benefits from human connection premium"),
        ("MTCH", "Match Group", "CANARY", "Dating apps signal desire for authentic human connection"),
        ("W", "Wayfair", "HEADWIND", "Mass-market home goods face artisan premium competition"),
        ("RH", "Restoration Hardware", "BENEFICIARY", "Luxury home furnishings with artisan craftsmanship positioning"),
    ],
    "senior_living": [
        ("AMED", "Amedisys", "BENEFICIARY", "Home health and hospice provider for aging population"),
        ("ENSG", "Ensign Group", "BENEFICIARY", "Skilled nursing facility operator for senior care"),
        ("WELL", "Welltower", "BENEFICIARY", "Senior housing REIT benefits from aging demographics"),
        ("PEAK", "Healthpeak Properties", "BENEFICIARY", "Life science and senior housing REIT"),
        ("OHI", "Omega Healthcare", "BENEFICIARY", "Skilled nursing facility REIT for aging population"),
        ("IRTC", "iRhythm Technologies", "BENEFICIARY", "Remote cardiac monitoring for elderly patients"),
        ("GMED", "Globus Medical", "BENEFICIARY", "Spine surgery devices for aging-related conditions"),
        ("BJ", "BJ's Wholesale", "CANARY", "Consumer staples signal senior spending patterns"),
        ("OSCR", "Oscar Health", "BENEFICIARY", "Health insurance innovator for Medicare expansion"),
        ("DOCS", "Doximity", "BENEFICIARY", "Physician network benefits from telemedicine for seniors"),
        ("HIMS", "Hims & Hers", "CANARY", "Telehealth platform signals digital health adoption"),
        ("ACLS", "Axcelis Technologies", "CANARY", "Semiconductor equipment signals tech infrastructure build"),
    ],
    "micro_luxury": [
        ("TPR", "Tapestry", "HEADWIND", "Accessible luxury faces premiumization pressure"),
        ("CPRI", "Capri Holdings", "HEADWIND", "Legacy luxury brands lose relevance with Gen Z"),
        ("REAL", "RealReal", "BENEFICIARY", "Luxury consignment benefits from secondhand premium"),
        ("POSH", "Poshmark", "BENEFICIARY", "Fashion resale marketplace benefits from circular luxury"),
        ("TJX", "TJ Maxx", "CANARY", "Off-price retail signals value-seeking behavior"),
        ("RVLV", "Revolve Group", "BENEFICIARY", "DTC fashion platform targeting Gen Z luxury"),
        ("FTCH", "Farfetch", "CANARY", "Digital luxury marketplace signals online luxury demand"),
        ("RL", "Ralph Lauren", "CANARY", "Heritage brand signals luxury market positioning shifts"),
        ("SKX", "Skechers", "CANARY", "Comfort footwear signals casual luxury trend"),
        ("ONON", "On Holding", "BENEFICIARY", "Premium athletic brand benefits from micro-luxury trend"),
        ("BIRK", "Birkenstock", "BENEFICIARY", "Heritage comfort brand benefits from affordable luxury"),
        ("DECK", "Deckers Outdoor", "BENEFICIARY", "HOKA and UGG brands capture micro-luxury demand"),
    ],
    "sleep": [
        ("CSPR", "Casper Sleep", "BENEFICIARY", "DTC mattress brand benefits from sleep investment"),
        ("TPX", "Tempur-Pedic", "BENEFICIARY", "Premium mattress maker benefits from sleep optimization"),
        ("SNBR", "Sleep Number", "BENEFICIARY", "Smart bed maker benefits from sleep technology trend"),
        ("AAPL", "Apple", "CANARY", "Apple Watch sleep tracking signals health-tech convergence"),
        ("GOOG", "Alphabet", "CANARY", "Fitbit sleep tracking signals consumer sleep interest"),
        ("JNJ", "Johnson & Johnson", "CANARY", "Consumer health signals sleep supplement demand"),
        ("PHG", "Philips", "BENEFICIARY", "Sleep apnea devices and sleep diagnostics provider"),
        ("HZNP", "Horizon Therapeutics", "CANARY", "Sleep disorder pharma signals therapeutic demand"),
        ("CALM", "Calm", "BENEFICIARY", "Sleep and meditation app benefits from wellness trend"),
        ("PRPL", "Purple Innovation", "BENEFICIARY", "Comfort technology mattress maker for sleep optimization"),
        ("LESL", "Leslie's", "CANARY", "Home investment signals bedroom upgrade spending"),
        ("WSM", "Williams-Sonoma", "CANARY", "Home furnishing signals bedroom investment trends"),
    ],
    "yield_curve": [
        ("SCHW", "Charles Schwab", "BENEFICIARY", "Brokerage profits from NIM expansion with steeper curve"),
        ("ZION", "Zions Bancorp", "BENEFICIARY", "Regional bank NIM directly benefits from curve steepening"),
        ("CFG", "Citizens Financial", "BENEFICIARY", "Super-regional bank profits from improved lending margins"),
        ("HBAN", "Huntington Bancshares", "BENEFICIARY", "Midwest bank benefits from steeper yield curve"),
        ("EWBC", "East West Bancorp", "BENEFICIARY", "Cross-border banking benefits from rate normalization"),
        ("FHN", "First Horizon", "BENEFICIARY", "Southeast bank benefits from curve steepening"),
        ("VNO", "Vornado Realty", "HEADWIND", "Office REIT faces CRE refinancing pressure"),
        ("SLG", "SL Green Realty", "HEADWIND", "NYC office REIT faces highest CRE refinancing risk"),
        ("STWD", "Starwood Property", "CANARY", "CRE lending signals distressed property opportunities"),
        ("BXMT", "Blackstone Mortgage", "CANARY", "CRE mortgage REIT signals refinancing wave timing"),
        ("PNC", "PNC Financial", "BENEFICIARY", "Large regional bank benefits from NIM expansion"),
        ("MTB", "M&T Bank", "BENEFICIARY", "CRE-focused bank positioned for refinancing cycle"),
    ],
    "attention": [
        ("SNAP", "Snap Inc", "HEADWIND", "Social media faces regulation and attention backlash"),
        ("PINS", "Pinterest", "CANARY", "Visual discovery signals attention-seeking behavior shifts"),
        ("TTWO", "Take-Two Interactive", "CANARY", "Gaming signals attention allocation competition"),
        ("RBLX", "Roblox", "HEADWIND", "Youth gaming platform faces screen time regulation"),
        ("NFLX", "Netflix", "CANARY", "Streaming signals appointment viewing vs doom-scrolling"),
        ("NYT", "New York Times", "BENEFICIARY", "Quality journalism benefits from trust premium"),
        ("DLB", "Dolby Labs", "BENEFICIARY", "Premium audio/visual benefits from focused content consumption"),
        ("SONO", "Sonos", "BENEFICIARY", "Premium audio for intentional listening experience"),
        ("SE", "Sea Limited", "HEADWIND", "Digital entertainment faces attention economy saturation"),
        ("ZM", "Zoom Video", "CANARY", "Video communication signals work pattern changes"),
        ("CALM", "Calm app", "BENEFICIARY", "Meditation and focus app benefits from attention crisis"),
        ("TRMR", "Tremor International", "HEADWIND", "Digital advertising faces attention fragmentation"),
    ],
    "analogue": [
        ("FUJI", "Fujifilm Holdings", "BENEFICIARY", "Film and instant camera maker benefits from analog revival"),
        ("KODK", "Kodak", "BENEFICIARY", "Film photography brand benefits from nostalgic analog demand"),
        ("BNED", "Barnes & Noble Ed", "BENEFICIARY", "Physical bookstore benefits from analog revival"),
        ("HAS", "Hasbro", "BENEFICIARY", "Board game maker benefits from screen-free entertainment"),
        ("MAT", "Mattel", "BENEFICIARY", "Physical toy maker benefits from analog play trend"),
        ("SPG", "Simon Property", "BENEFICIARY", "Mall REIT benefits from physical retail renaissance"),
        ("SHC", "Sotera Health", "CANARY", "Health services signal analog/in-person care demand"),
        ("AMZN", "Amazon", "HEADWIND", "E-commerce faces physical retail comeback pressure"),
        ("MCS", "Marcus Corp", "BENEFICIARY", "Movie theaters and hotels benefit from in-person experiences"),
        ("BKE", "Buckle", "BENEFICIARY", "Physical retail chain benefits from in-store experience"),
        ("MNST", "Monster Beverage", "CANARY", "Consumer beverage signals social gathering trends"),
        ("WMG", "Warner Music", "BENEFICIARY", "Music label benefits from vinyl and physical media revival"),
    ],
    "verification": [
        ("OKTA", "Okta", "BENEFICIARY", "Identity management leader for digital verification"),
        ("CRWD", "CrowdStrike", "BENEFICIARY", "Cybersecurity leader benefits from verification demand"),
        ("ZS", "Zscaler", "BENEFICIARY", "Zero-trust security benefits from identity verification"),
        ("PANW", "Palo Alto Networks", "BENEFICIARY", "Cybersecurity platform benefits from deepfake threats"),
        ("VRNS", "Varonis Systems", "BENEFICIARY", "Data security benefits from evidence integrity needs"),
        ("TENB", "Tenable", "BENEFICIARY", "Vulnerability management for digital evidence security"),
        ("RPD", "Rapid7", "CANARY", "Security analytics signals verification demand"),
        ("S", "SentinelOne", "CANARY", "AI-powered cybersecurity signals deepfake defense needs"),
        ("PING", "Ping Identity", "BENEFICIARY", "Identity verification specialist for digital ID infrastructure"),
        ("EVTC", "EVERTEC", "BENEFICIARY", "Payment and digital ID infrastructure in Latin America"),
        ("SSNC", "SS&C Technologies", "BENEFICIARY", "Financial services software for verified transactions"),
        ("INTU", "Intuit", "CANARY", "Financial software signals digital identity needs"),
    ],
    "cognitive": [
        ("NTRA", "Natera", "CANARY", "Genetic testing signals cognitive health awareness"),
        ("ILMN", "Illumina", "CANARY", "Genomics platform signals brain health research"),
        ("NVAX", "Novavax", "CANARY", "Biotech signals health innovation investment cycles"),
        ("SAVA", "Cassava Sciences", "BENEFICIARY", "Alzheimer's drug developer benefits from cognitive health focus"),
        ("PRAX", "Praxis Precision", "BENEFICIARY", "CNS drug developer for brain health conditions"),
        ("SAGE", "Sage Therapeutics", "BENEFICIARY", "Brain health pharmaceutical company"),
        ("AXSM", "Axsome Therapeutics", "BENEFICIARY", "CNS therapeutics for cognitive and mood disorders"),
        ("BMRN", "BioMarin Pharma", "CANARY", "Rare disease biotech signals brain health investment"),
        ("NBIX", "Neurocrine Bio", "BENEFICIARY", "Neuroscience-focused pharma for brain disorders"),
        ("CHRS", "Coherus Bio", "CANARY", "Biosimilar maker signals healthcare cost dynamics"),
        ("MNKD", "MannKind Corp", "CANARY", "Drug delivery innovation signals pharma shifts"),
        ("RCKT", "Rocket Pharma", "CANARY", "Gene therapy signals precision medicine adoption"),
    ],
    "chips_china": [
        ("LMT", "Lockheed Martin", "BENEFICIARY", "Defense prime gets blank check from geopolitical tension"),
        ("RTX", "RTX Corp", "BENEFICIARY", "Defense conglomerate benefits from military spending surge"),
        ("NOC", "Northrop Grumman", "BENEFICIARY", "Defense prime benefits from Asia-Pacific threat response"),
        ("GD", "General Dynamics", "BENEFICIARY", "Defense and IT contractor benefits from security spending"),
        ("HII", "Huntington Ingalls", "BENEFICIARY", "Naval shipbuilder benefits from Pacific fleet expansion"),
        ("LDOS", "Leidos", "BENEFICIARY", "Defense IT and intelligence contractor"),
        ("SAIC", "Science Applications", "BENEFICIARY", "Defense tech integrator benefits from security spending"),
        ("PLTR", "Palantir", "BENEFICIARY", "Defense AI platform benefits from intelligence demand"),
        ("ARM", "Arm Holdings", "BENEFICIARY", "Chip architecture alternative to x86 gains from diversification"),
        ("CDNS", "Cadence Design", "BENEFICIARY", "Chip design tools benefit from domestic semiconductor push"),
        ("SNPS", "Synopsys", "BENEFICIARY", "EDA tools benefit from chip design reshoring"),
        ("ON", "ON Semiconductor", "BENEFICIARY", "US chip maker benefits from supply chain diversification"),
    ],
    "dead_internet": [
        ("TTD", "Trade Desk", "CANARY", "Digital ad platform signals bot traffic impact on advertising"),
        ("MGNI", "Magnite", "CANARY", "Programmatic ad exchange signals ad fraud from bots"),
        ("DV", "DoubleVerify", "BENEFICIARY", "Ad verification benefits from bot traffic detection demand"),
        ("IAS", "Integral Ad Science", "BENEFICIARY", "Ad verification and brand safety in bot-heavy internet"),
        ("PARA", "Paramount", "BENEFICIARY", "Traditional media benefits from trusted content demand"),
        ("FOX", "Fox Corp", "BENEFICIARY", "Cable news benefits from trust premium over social media"),
        ("NWSA", "News Corp", "BENEFICIARY", "Print/digital journalism benefits from bot-free content"),
        ("WPP", "WPP", "HEADWIND", "Ad agency faces bot traffic undermining campaign ROI"),
        ("IPG", "Interpublic", "HEADWIND", "Ad conglomerate faces influencer marketing implosion"),
        ("GOOG", "Alphabet", "HEADWIND", "Search degradation from AI content threatens core business"),
        ("RDDT", "Reddit", "BENEFICIARY", "Human-verified community platform gains as social trust erodes"),
        ("SNAP", "Snap", "HEADWIND", "Social platform faces bot and authenticity crisis"),
    ],
}

# Map thesis titles to theme keys
THESIS_THEME_MAP = {
    "USD Debasement": "usd_debasement",
    "GLP-1 Revolution": "glp1",
    "AI Infrastructure": "ai_infra",
    "Reskilling Economy": "reskilling",
    "Electricity Bottleneck": "electricity",
    "AI Slop Makes Human": "human_premium",
    "Baby Boomers": "senior_living",
    "Gen Z Affordable": "micro_luxury",
    "Sleep Is the New": "sleep",
    "Yield Curve": "yield_curve",
    "Attention Economy": "attention",
    "Screentime Backlash": "analogue",
    "AI Content Explosion": "verification",
    "AI-Induced Cognitive": "cognitive",
    "Betting on Chips": "chips_china",
    "Dead Internet": "dead_internet",
}


def get_theme(thesis_title):
    for key, theme in THESIS_THEME_MAP.items():
        if key.lower() in thesis_title.lower():
            return theme
    return None


def dedup():
    theses = db.query(Thesis).all()
    replaced_bets = 0
    replaced_opps = 0

    for thesis in theses:
        theme = get_theme(thesis.title)
        if not theme or theme not in TICKER_POOLS:
            continue

        pool = list(TICKER_POOLS[theme])
        pool_idx = 0

        # Get thesis-level tickers (these stay)
        thesis_bets = db.query(EquityBet).filter(
            EquityBet.thesis_id == thesis.id,
            EquityBet.effect_id.is_(None)
        ).all()
        used_tickers = set(b.ticker for b in thesis_bets)

        # 2nd order effects
        effects_2nd = db.query(Effect).filter(
            Effect.thesis_id == thesis.id,
            Effect.parent_effect_id.is_(None)
        ).all()

        for e2 in effects_2nd:
            e2_bets = db.query(EquityBet).filter(EquityBet.effect_id == e2.id).all()
            e2_used = set()

            for bet in e2_bets:
                if bet.ticker in used_tickers:
                    # Find a replacement from pool
                    replacement = None
                    while pool_idx < len(pool):
                        candidate = pool[pool_idx]
                        pool_idx += 1
                        if candidate[0] not in used_tickers and candidate[0] not in e2_used:
                            replacement = candidate
                            break

                    if replacement:
                        old_ticker = bet.ticker
                        bet.ticker = replacement[0]
                        bet.company_name = replacement[1]
                        bet.role = replacement[2]
                        bet.rationale = replacement[3]
                        e2_used.add(replacement[0])
                        replaced_bets += 1
                    else:
                        # No more replacements, remove the duplicate
                        db.delete(bet)
                        replaced_bets += 1
                else:
                    e2_used.add(bet.ticker)

            # Track all tickers used at this level for 3rd order dedup
            level_2_tickers = used_tickers | e2_used

            # 3rd order effects
            effects_3rd = db.query(Effect).filter(Effect.parent_effect_id == e2.id).all()
            for e3 in effects_3rd:
                e3_bets = db.query(EquityBet).filter(EquityBet.effect_id == e3.id).all()
                e3_used = set()

                for bet in e3_bets:
                    if bet.ticker in level_2_tickers or bet.ticker in e3_used:
                        replacement = None
                        while pool_idx < len(pool):
                            candidate = pool[pool_idx]
                            pool_idx += 1
                            if candidate[0] not in level_2_tickers and candidate[0] not in e3_used:
                                replacement = candidate
                                break

                        if replacement:
                            bet.ticker = replacement[0]
                            bet.company_name = replacement[1]
                            bet.role = replacement[2]
                            bet.rationale = replacement[3]
                            e3_used.add(replacement[0])
                            replaced_bets += 1
                        else:
                            db.delete(bet)
                            replaced_bets += 1
                    else:
                        e3_used.add(bet.ticker)

    # Dedup startup opportunities by name
    for thesis in theses:
        thesis_opps = db.query(StartupOpportunity).filter(
            StartupOpportunity.thesis_id == thesis.id,
            StartupOpportunity.effect_id.is_(None)
        ).all()
        used_names = set(o.name for o in thesis_opps)

        effects_2nd = db.query(Effect).filter(
            Effect.thesis_id == thesis.id,
            Effect.parent_effect_id.is_(None)
        ).all()

        for e2 in effects_2nd:
            e2_opps = db.query(StartupOpportunity).filter(
                StartupOpportunity.effect_id == e2.id
            ).all()
            e2_names = set()

            for opp in e2_opps:
                if opp.name in used_names:
                    # Rename with effect-specific prefix
                    new_name = f"{e2.title[:20].strip()} — {opp.name}"
                    if new_name in used_names or new_name in e2_names:
                        db.delete(opp)
                    else:
                        opp.name = new_name
                        e2_names.add(new_name)
                    replaced_opps += 1
                else:
                    e2_names.add(opp.name)

            level_2_names = used_names | e2_names

            effects_3rd = db.query(Effect).filter(Effect.parent_effect_id == e2.id).all()
            for e3 in effects_3rd:
                e3_opps = db.query(StartupOpportunity).filter(
                    StartupOpportunity.effect_id == e3.id
                ).all()
                e3_names = set()

                for opp in e3_opps:
                    if opp.name in level_2_names or opp.name in e3_names:
                        new_name = f"{e3.title[:20].strip()} — {opp.name}"
                        if new_name in level_2_names or new_name in e3_names:
                            db.delete(opp)
                        else:
                            opp.name = new_name
                            e3_names.add(new_name)
                        replaced_opps += 1
                    else:
                        e3_names.add(opp.name)

    db.commit()
    print(f"Replaced/removed {replaced_bets} duplicate bets")
    print(f"Replaced/removed {replaced_opps} duplicate startup opps")


def validate():
    """Run validation to confirm zero duplicates."""
    theses = db.query(Thesis).all()
    ticker_dupes = 0
    opp_dupes = 0

    for t in theses:
        thesis_bets = db.query(EquityBet).filter(
            EquityBet.thesis_id == t.id, EquityBet.effect_id.is_(None)
        ).all()
        thesis_tickers = set(b.ticker for b in thesis_bets)

        effects_2nd = db.query(Effect).filter(
            Effect.thesis_id == t.id, Effect.parent_effect_id.is_(None)
        ).all()
        for e2 in effects_2nd:
            e2_bets = db.query(EquityBet).filter(EquityBet.effect_id == e2.id).all()
            e2_tickers = set(b.ticker for b in e2_bets)
            overlap = thesis_tickers & e2_tickers
            if overlap:
                ticker_dupes += len(overlap)
                print(f"  TICKER DUPE: {t.title[:30]} <-> {e2.title[:30]}: {overlap}")

            effects_3rd = db.query(Effect).filter(Effect.parent_effect_id == e2.id).all()
            for e3 in effects_3rd:
                e3_bets = db.query(EquityBet).filter(EquityBet.effect_id == e3.id).all()
                e3_tickers = set(b.ticker for b in e3_bets)
                overlap_2_3 = e2_tickers & e3_tickers
                if overlap_2_3:
                    ticker_dupes += len(overlap_2_3)
                    print(f"  TICKER DUPE: {e2.title[:30]} <-> {e3.title[:30]}: {overlap_2_3}")

        # Opps
        thesis_opps = db.query(StartupOpportunity).filter(
            StartupOpportunity.thesis_id == t.id, StartupOpportunity.effect_id.is_(None)
        ).all()
        thesis_opp_names = set(o.name for o in thesis_opps)

        for e2 in effects_2nd:
            e2_opps = db.query(StartupOpportunity).filter(
                StartupOpportunity.effect_id == e2.id
            ).all()
            e2_opp_names = set(o.name for o in e2_opps)
            overlap = thesis_opp_names & e2_opp_names
            if overlap:
                opp_dupes += len(overlap)

            effects_3rd = db.query(Effect).filter(Effect.parent_effect_id == e2.id).all()
            for e3 in effects_3rd:
                e3_opps = db.query(StartupOpportunity).filter(
                    StartupOpportunity.effect_id == e3.id
                ).all()
                e3_opp_names = set(o.name for o in e3_opps)
                overlap_2_3 = e2_opp_names & e3_opp_names
                if overlap_2_3:
                    opp_dupes += len(overlap_2_3)

    print(f"\n=== VALIDATION RESULT ===")
    print(f"Ticker duplicates: {ticker_dupes}")
    print(f"Startup opp name duplicates: {opp_dupes}")
    if ticker_dupes == 0 and opp_dupes == 0:
        print("PASS: Zero duplicates across all parent/child levels")
    else:
        print("FAIL: Duplicates remain")


if __name__ == "__main__":
    print("=== DEDUPLICATING TICKERS & OPPS ===")
    dedup()
    print("\n=== RUNNING VALIDATION ===")
    validate()
    db.close()
