"""Seed the database with all 16 theses from the master prompt."""

import json
from datetime import datetime

from sqlalchemy.orm import Session

from models import (
    Thesis, Effect, EquityBet, StartupOpportunity,
    DataFeed, THISnapshot, ConvictionSnapshot, MacroHeader
)


SEED_DATA = [
    {
        "id": "thesis_usd_debasement",
        "title": "USD Debasement & Hard Asset Premium",
        "subtitle": "The Fed keeps printing money and running massive deficits, making the dollar worth less every year.",
        "description": "Smart money is fleeing into anything that can't be printed — gold, Bitcoin, real estate, commodities — while cash becomes trash. The structural deficit spending makes dollar debasement inevitable, and hard assets are the only rational hedge.",
        "timeHorizon": "3-7yr",
        "tags": ["macro", "monetary", "commodities", "crypto"],
        "initialTHI": 74,
        "initialUserConviction": 8,
        "feeds": [
            {"id": "fred_m2_money_supply", "source": "FRED", "seriesId": "M2SL", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "fred_federal_debt", "source": "FRED", "seriesId": "GFDEBTN", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "fred_cpi_inflation", "source": "FRED", "seriesId": "CPIAUCSL", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "fred_usd_index", "source": "FRED", "seriesId": "DTWEXBGS", "sourceType": "structural", "confirmingDirection": "lower"},
            {"id": "fred_gold_price", "source": "FRED", "seriesId": "GOLDAMGBD228NLBM", "sourceType": "flow", "confirmingDirection": "higher"},
            {"id": "fred_real_interest_rate", "source": "FRED", "seriesId": "REAINTRATREARAT10Y", "sourceType": "structural", "confirmingDirection": "lower"},
            {"id": "gtrends_gold_investment", "source": "GTRENDS", "keyword": "buy gold investment", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_deficit_gdp", "source": "FRED", "seriesId": "FYFSGDA188S", "sourceType": "policy", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "GLD", "companyName": "SPDR Gold Shares", "companyDescription": "Largest physically-backed gold ETF tracking the price of gold bullion. Direct hedge against dollar debasement and monetary expansion.", "role": "BENEFICIARY", "rationale": "Gold ETF is the cleanest direct expression of dollar debasement thesis.", "isFeedbackIndicator": True, "feedbackWeight": 0.10},
            {"ticker": "MSTR", "companyName": "MicroStrategy", "companyDescription": "Enterprise software company that converted its balance sheet into a Bitcoin treasury. Largest corporate holder of Bitcoin globally.", "role": "BENEFICIARY", "rationale": "Bitcoin proxy with leverage — amplified expression of hard money flight.", "isFeedbackIndicator": True, "feedbackWeight": 0.08},
            {"ticker": "NEM", "companyName": "Newmont Corporation", "companyDescription": "World's largest gold mining company operating mines across five continents. Revenue and margins expand with rising gold prices.", "role": "BENEFICIARY", "rationale": "Gold miner with operating leverage — outperforms gold itself in a bull run.", "isFeedbackIndicator": False}
        ],
        "startupOpportunities": [
            {"name": "AurusPay", "oneLiner": "B2B payment rails denominated in tokenized gold for SMBs in high-inflation countries.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "HardVault", "oneLiner": "Self-custody hard asset platform — fractional gold, silver, and Bitcoin in one account.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "DeficitWatch", "oneLiner": "Real-time fiscal tracker that converts government spending data into portfolio hedging signals.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"}
        ],
        "effects": [
            {
                "id": "effect_usd_crypto_adoption",
                "order": 2,
                "title": "Crypto Becomes Mainstream Store of Value",
                "description": "As dollar trust erodes, Bitcoin graduates from speculation to legitimate reserve asset.",
                "initialTHI": 68,
                "equityBets": [
                    {"ticker": "IBIT", "companyName": "iShares Bitcoin Trust", "companyDescription": "BlackRock's spot Bitcoin ETF providing institutional-grade access to Bitcoin.", "role": "BENEFICIARY", "rationale": "BlackRock's Bitcoin ETF — institutional on-ramp"},
                    {"ticker": "COIN", "companyName": "Coinbase Global", "companyDescription": "Largest US cryptocurrency exchange and custodian. Revenue scales directly with crypto trading volume and adoption.", "role": "BENEFICIARY", "rationale": "Crypto exchange revenue scales with adoption"},
                    {"ticker": "JPM", "companyName": "JPMorgan Chase", "companyDescription": "Largest US bank by assets. Has been building blockchain and tokenization infrastructure for institutional clients.", "role": "CANARY", "rationale": "When JPM starts aggressively tokenizing assets, adoption has crossed the chasm"}
                ]
            },
            {
                "id": "effect_usd_real_estate",
                "order": 2,
                "title": "Real Assets Become Inflation Shelter",
                "description": "Real estate, farmland, and commodity-producing infrastructure become the go-to stores of value.",
                "initialTHI": 71,
                "equityBets": [
                    {"ticker": "O", "companyName": "Realty Income", "companyDescription": "Monthly-dividend REIT owning 13,000+ commercial properties with inflation-linked lease escalators.", "role": "BENEFICIARY", "rationale": "REIT with pricing power in inflation"},
                    {"ticker": "LAND", "companyName": "Gladstone Land", "companyDescription": "Farmland REIT owning and leasing agricultural land across the US. Farmland is a finite hard asset.", "role": "BENEFICIARY", "rationale": "Farmland REIT — hardest of hard assets"},
                    {"ticker": "TIP", "companyName": "iShares TIPS Bond ETF", "companyDescription": "ETF tracking Treasury Inflation-Protected Securities. Demand for TIPS reflects market inflation expectations.", "role": "CANARY", "rationale": "TIPS demand signals inflation expectations"}
                ]
            }
        ]
    },
    {
        "id": "thesis_glp1_revolution",
        "title": "GLP-1 Revolution & Health Optimization",
        "subtitle": "GLP-1 drugs like Ozempic are rewiring America's relationship with food and health.",
        "description": "Millions are losing weight, eating less, and demanding better healthcare outcomes. This creates massive winners and losers across every sector from food to fashion to pharma.",
        "timeHorizon": "3-7yr",
        "tags": ["healthcare", "consumer", "pharma", "food"],
        "initialTHI": 80,
        "initialUserConviction": 8,
        "feeds": [
            {"id": "gtrends_ozempic", "source": "GTRENDS", "keyword": "ozempic", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_glp1_weightloss", "source": "GTRENDS", "keyword": "GLP-1 weight loss", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_obesity_spending", "source": "FRED", "seriesId": "HLTHSCPCHCSA", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_protein_food", "source": "GTRENDS", "keyword": "high protein food", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_calorie_deficit", "source": "GTRENDS", "keyword": "calorie deficit meal prep", "sourceType": "adoption", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "NVO", "companyName": "Novo Nordisk", "companyDescription": "Danish pharma giant that makes Ozempic and Wegovy. Controls ~50% of the global GLP-1 market.", "role": "BENEFICIARY", "rationale": "Makes Ozempic/Wegovy — direct revenue proxy for GLP-1 adoption rate.", "isFeedbackIndicator": True, "feedbackWeight": 0.12},
            {"ticker": "PEP", "companyName": "PepsiCo", "companyDescription": "Global snack and beverage company. Frito-Lay division generates ~$23B in annual snack food revenue.", "role": "HEADWIND", "rationale": "Frito-Lay snack volumes are a direct readout of processed food demand destruction.", "isFeedbackIndicator": True, "feedbackWeight": 0.10},
            {"ticker": "HCA", "companyName": "HCA Healthcare", "companyDescription": "Largest for-profit hospital operator in the US with 180+ hospitals. High-margin surgical procedures drive revenue.", "role": "CANARY", "rationale": "High-margin procedure volumes signal whether obesity-related admissions are declining.", "isFeedbackIndicator": True, "feedbackWeight": 0.08}
        ],
        "startupOpportunities": [
            {"name": "ShelfSense", "oneLiner": "AI that helps grocery chains reoptimize shelf space using local GLP-1 prescription density data.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "PortionOS", "oneLiner": "Meal kit service calibrated exactly to GLP-1 user appetite.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "SlimFit Tailor", "oneLiner": "On-demand clothing alteration subscription for the GLP-1 weight loss journey.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"}
        ],
        "effects": [
            {
                "id": "effect_glp1_food_giants",
                "order": 2,
                "title": "Food Giants Get Murdered",
                "description": "People on GLP-1s literally can't finish a bag of Doritos anymore. Processed food consumption craters.",
                "initialTHI": 72,
                "equityBets": [
                    {"ticker": "PEP", "companyName": "PepsiCo", "companyDescription": "Global snack and beverage company. Frito-Lay division generates ~$23B in annual snack food revenue.", "role": "HEADWIND", "rationale": "Frito-Lay is the canary — snack volume = GLP-1 adoption rate"},
                    {"ticker": "UNFI", "companyName": "United Natural Foods", "companyDescription": "Largest wholesale distributor of natural, organic, and specialty foods in North America.", "role": "BENEFICIARY", "rationale": "Distributes organic/natural foods"},
                    {"ticker": "VITL", "companyName": "Vital Farms", "companyDescription": "Ethical food company producing pasture-raised eggs and butter. Premium protein products for health-conscious consumers.", "role": "BENEFICIARY", "rationale": "Vital Farms premium eggs and butter — perfect for high-protein GLP-1 diet"}
                ]
            },
            {
                "id": "effect_glp1_hospitals",
                "order": 2,
                "title": "Hospitals Lose Their Cash Cows",
                "description": "Cardiac procedures, knee replacements, and diabetes complications generate massive hospital revenues. As these become preventable, hospitals face revenue crisis.",
                "initialTHI": 55,
                "equityBets": [
                    {"ticker": "HCA", "companyName": "HCA Healthcare", "companyDescription": "Largest for-profit hospital operator in the US with 180+ hospitals.", "role": "HEADWIND", "rationale": "Fewer high-margin procedures = margin compression"},
                    {"ticker": "TDOC", "companyName": "Teladoc Health", "companyDescription": "Leading telehealth platform including BetterHelp mental health services. Enables remote preventive care.", "role": "BENEFICIARY", "rationale": "Teladoc benefits as healthcare shifts to prevention"},
                    {"ticker": "CVS", "companyName": "CVS Health", "companyDescription": "Integrated pharmacy, health insurance (Aetna), and MinuteClinic walk-in care provider.", "role": "BENEFICIARY", "rationale": "MinuteClinics capture more healthcare as hospitals lose patients"}
                ]
            },
            {
                "id": "effect_glp1_fashion",
                "order": 2,
                "title": "Fashion Retail Inventory Apocalypse",
                "description": "When 40% of Americans lose 15-50 pounds, every clothing size chart becomes obsolete overnight.",
                "initialTHI": 48,
                "equityBets": [
                    {"ticker": "LULU", "companyName": "Lululemon Athletica", "companyDescription": "Premium athletic apparel brand with cult following. Core customer skews health-conscious and affluent.", "role": "BENEFICIARY", "rationale": "Newly thin people splurge on premium athletic wear"},
                    {"ticker": "GPS", "companyName": "Gap Inc.", "companyDescription": "Multi-brand retailer (Gap, Old Navy, Banana Republic, Athleta). Inventory planned around current size distributions.", "role": "HEADWIND", "rationale": "Gap struggles with inventory of larger sizes"},
                    {"ticker": "TJX", "companyName": "TJX Companies", "companyDescription": "Off-price retailer operating TJ Maxx, Marshalls, and HomeGoods. Captures consumers trading down on apparel.", "role": "BENEFICIARY", "rationale": "TJ Maxx benefits as people need entirely new wardrobes cheaply"}
                ]
            }
        ]
    },
    {
        "id": "thesis_ai_infrastructure",
        "title": "AI Infrastructure Supercycle",
        "subtitle": "AI demand is creating the biggest infrastructure buildout since the internet.",
        "description": "Data centers are getting rebuilt from scratch, power grids are maxing out, and cooling systems can't keep up. This is a physical infrastructure cycle measured in concrete, copper, and electricity.",
        "timeHorizon": "3-7yr",
        "tags": ["AI", "infrastructure", "energy", "semiconductors"],
        "initialTHI": 73,
        "initialUserConviction": 7,
        "feeds": [
            {"id": "gtrends_ai_datacenter", "source": "GTRENDS", "keyword": "AI data center", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_electricity_industrial", "source": "FRED", "seriesId": "IPG2211A2N", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "fred_nonresidential_construction", "source": "FRED", "seriesId": "TLNRESCONS", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_gpu_shortage", "source": "GTRENDS", "keyword": "GPU shortage availability", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_semiconductor_production", "source": "FRED", "seriesId": "IPG3344S", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_hyperscaler_capex", "source": "GTRENDS", "keyword": "Microsoft Azure AWS Google Cloud infrastructure spending", "sourceType": "flow", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "NEE", "companyName": "NextEra Energy", "companyDescription": "Largest US electric utility and world's largest generator of wind and solar energy. Powers major datacenter corridors.", "role": "BENEFICIARY", "rationale": "Power infrastructure — AI datacenters need massive baseload electricity.", "isFeedbackIndicator": True, "feedbackWeight": 0.09},
            {"ticker": "SO", "companyName": "Southern Company", "companyDescription": "Major US utility with nuclear, gas, and renewable generation. Serves the Southeast datacenter corridor.", "role": "BENEFICIARY", "rationale": "Southern Company — nuclear and gas power for Southeast datacenter corridor.", "isFeedbackIndicator": False},
            {"ticker": "DUK", "companyName": "Duke Energy", "companyDescription": "One of America's largest electric utilities serving the Carolinas and Midwest. Major grid infrastructure operator.", "role": "BENEFICIARY", "rationale": "Duke Energy — another major power utility in prime datacenter geography.", "isFeedbackIndicator": False}
        ],
        "startupOpportunities": [
            {"name": "CoolCore", "oneLiner": "Liquid cooling-as-a-service for retrofitting existing datacenters to AI workloads.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "GridBid", "oneLiner": "Power procurement marketplace that helps datacenters lock in long-term electricity contracts.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "InferenceEdge", "oneLiner": "Deploys small inference clusters at telecom towers to reduce latency and datacenter load.", "timing": "TOO_EARLY", "timeHorizon": "1-3yr"}
        ],
        "effects": [
            {
                "id": "effect_ai_power_grid",
                "order": 2,
                "title": "Power Grid Hits Breaking Point",
                "description": "AI datacenters consume as much power as mid-sized cities. The grid wasn't built for this.",
                "initialTHI": 70,
                "equityBets": [
                    {"ticker": "VST", "companyName": "Vistra Corp", "companyDescription": "Largest competitive power generator in the US with nuclear, gas, and solar assets.", "role": "BENEFICIARY", "rationale": "Vistra Energy — merchant power with datacenter contracts"},
                    {"ticker": "CEG", "companyName": "Constellation Energy", "companyDescription": "Largest US nuclear power operator with 13 nuclear plants. Provides carbon-free baseload power.", "role": "BENEFICIARY", "rationale": "Constellation Energy — nuclear power for always-on AI demand"},
                    {"ticker": "ETR", "companyName": "Entergy Corporation", "companyDescription": "Electric utility serving the Gulf South region with nuclear and gas generation.", "role": "CANARY", "rationale": "Entergy's grid upgrade capex signals how serious utilities are taking AI demand"}
                ]
            },
            {
                "id": "effect_ai_cooling_crisis",
                "order": 2,
                "title": "Cooling Becomes the Bottleneck",
                "description": "Air cooling maxes out at certain power densities. Liquid cooling becomes mandatory for next-gen AI chips.",
                "initialTHI": 61,
                "equityBets": [
                    {"ticker": "VRT", "companyName": "Vertiv Holdings", "companyDescription": "Critical digital infrastructure company providing power, cooling, and IT management for datacenters.", "role": "BENEFICIARY", "rationale": "Vertiv — datacenter cooling and power infrastructure"},
                    {"ticker": "CARR", "companyName": "Carrier Global", "companyDescription": "Global leader in HVAC, refrigeration, and fire/security systems. Provides large-scale cooling solutions.", "role": "BENEFICIARY", "rationale": "Carrier Global — HVAC for large-scale cooling systems"},
                    {"ticker": "NVDA", "companyName": "NVIDIA Corporation", "companyDescription": "Dominant AI chip designer controlling ~80%+ of the GPU market for AI training and inference.", "role": "CANARY", "rationale": "NVDA gross margins signal chip demand that drives downstream cooling needs"}
                ]
            }
        ]
    },
    {
        "id": "thesis_reskilling_economy",
        "title": "Reskilling Economy & Career Chapters",
        "subtitle": "The economy is restructuring around multi-chapter careers where people reinvent every 7-10 years.",
        "description": "AI makes some jobs obsolete while creating new ones, forcing mass reskilling. The old model of one career, one company, one skill set is dead.",
        "timeHorizon": "3-7yr",
        "tags": ["education", "labor", "AI", "workforce"],
        "initialTHI": 67,
        "initialUserConviction": 7,
        "feeds": [
            {"id": "fred_job_openings", "source": "FRED", "seriesId": "JTSJOL", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "fred_layoffs", "source": "FRED", "seriesId": "JTSLAY", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_career_change", "source": "GTRENDS", "keyword": "career change how to", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_online_certification", "source": "GTRENDS", "keyword": "online certification course", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_temp_workers", "source": "FRED", "seriesId": "TEMPHELPS", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_ai_taking_jobs", "source": "GTRENDS", "keyword": "AI replacing jobs", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_labor_productivity", "source": "FRED", "seriesId": "PRS85006092", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_bootcamp", "source": "GTRENDS", "keyword": "coding bootcamp trade school", "sourceType": "adoption", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "CHGG", "companyName": "Chegg", "companyDescription": "Education technology company pivoting from homework help to AI-powered adult learning and reskilling platform.", "role": "BENEFICIARY", "rationale": "Chegg pivoting to adult reskilling — direct bet on career chapter thesis.", "isFeedbackIndicator": True, "feedbackWeight": 0.08},
            {"ticker": "STRA", "companyName": "Strategic Education", "companyDescription": "Operates Strayer University and Capella University focused on working adult education and vocational training.", "role": "BENEFICIARY", "rationale": "Strategic Education — vocational and workforce training focus.", "isFeedbackIndicator": False}
        ],
        "startupOpportunities": [
            {"name": "ChapterAI", "oneLiner": "AI career coach that maps your current skills to the highest-paying adjacent roles.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "SkillBridge", "oneLiner": "Employer-sponsored reskilling platform where companies pay to retrain displaced workers.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "CareerVault", "oneLiner": "Portable skills credential wallet that travels with you across employers and industries.", "timing": "TOO_EARLY", "timeHorizon": "3-7yr"}
        ],
        "effects": [
            {
                "id": "effect_reskill_credential_inflation",
                "order": 2,
                "title": "Credential Inflation Kills the Degree Premium",
                "description": "When everyone has micro-credentials and bootcamp certs, traditional 4-year degrees lose their signaling value. Universities face enrollment crises.",
                "initialTHI": 58,
                "equityBets": [
                    {"ticker": "LOPE", "companyName": "Grand Canyon Education", "companyDescription": "Provides education services to Grand Canyon University, a large private university focused on online degrees.", "role": "HEADWIND", "rationale": "Grand Canyon Education faces enrollment pressure as alternatives proliferate"},
                    {"ticker": "COUR", "companyName": "Coursera", "companyDescription": "Online learning platform offering university courses, professional certificates, and degree programs from 300+ partners.", "role": "BENEFICIARY", "rationale": "Coursera captures demand for stackable, employer-recognized credentials"},
                    {"ticker": "LRN", "companyName": "Stride Inc.", "companyDescription": "K-12 online education provider operating virtual schools and career learning programs across the US.", "role": "BENEFICIARY", "rationale": "Stride Inc benefits as K-12 families embrace alternative education pathways"}
                ]
            },
            {
                "id": "effect_reskill_staffing_boom",
                "order": 2,
                "title": "Staffing Agencies Become Talent Brokers",
                "description": "As careers fragment into chapters, staffing and talent marketplace companies become the new career infrastructure — matching reskilled workers to short-tenure roles.",
                "initialTHI": 62,
                "equityBets": [
                    {"ticker": "RHI", "companyName": "Robert Half International", "companyDescription": "Largest specialized staffing firm in the US placing finance, tech, legal, and creative professionals.", "role": "BENEFICIARY", "rationale": "Robert Half benefits from a world of constant job transitions"},
                    {"ticker": "UPWK", "companyName": "Upwork", "companyDescription": "World's largest freelance marketplace connecting businesses with independent professionals across 180+ countries.", "role": "BENEFICIARY", "rationale": "Upwork captures freelance demand from career-chapter workers"},
                    {"ticker": "HUBS", "companyName": "HubSpot", "companyDescription": "CRM and marketing automation platform serving mid-market companies. Hiring patterns signal SMB growth trends.", "role": "CANARY", "rationale": "HubSpot hiring trends signal whether mid-market companies embrace non-traditional talent"}
                ]
            },
            {
                "id": "effect_reskill_mental_health_surge",
                "order": 2,
                "title": "Career Anxiety Fuels Mental Health Demand",
                "description": "Constant reinvention and job insecurity drive a massive spike in anxiety and demand for mental health services, especially among 30-50 year olds.",
                "initialTHI": 55,
                "equityBets": [
                    {"ticker": "TDOC", "companyName": "Teladoc Health", "companyDescription": "Leading telehealth platform including BetterHelp mental health services.", "role": "BENEFICIARY", "rationale": "Teladoc's BetterHelp captures therapy demand from career-stressed workers"},
                    {"ticker": "HIMS", "companyName": "Hims & Hers Health", "companyDescription": "Telehealth platform offering prescription treatments for hair loss, skincare, mental health, and sexual wellness.", "role": "BENEFICIARY", "rationale": "Hims & Hers expands into anxiety and mental wellness prescriptions"}
                ]
            }
        ]
    },
    {
        "id": "thesis_electricity_bottleneck",
        "title": "Electricity Bottleneck & Power Infrastructure",
        "subtitle": "America's power grid is choking while nobody built new transmission for decades.",
        "description": "AI datacenters, crypto mining, and electrification are simultaneously hammering a grid that hasn't had serious investment since the 1980s.",
        "timeHorizon": "3-7yr",
        "tags": ["energy", "infrastructure", "utilities", "AI"],
        "initialTHI": 70,
        "initialUserConviction": 7,
        "feeds": [
            {"id": "fred_utility_capex", "source": "FRED", "seriesId": "PNFIA", "sourceType": "flow", "confirmingDirection": "higher"},
            {"id": "gtrends_power_outage", "source": "GTRENDS", "keyword": "power outage grid", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_natural_gas_price", "source": "FRED", "seriesId": "DHHNGSP", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_energy_crisis", "source": "GTRENDS", "keyword": "energy crisis electricity prices", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_grid_investment", "source": "FRED", "seriesId": "IPG2211A2N", "sourceType": "structural", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "NEE", "companyName": "NextEra Energy", "companyDescription": "Largest US electric utility and world's largest generator of wind and solar energy.", "role": "BENEFICIARY", "rationale": "NextEra — largest US utility with massive renewables pipeline.", "isFeedbackIndicator": True, "feedbackWeight": 0.10},
            {"ticker": "SO", "companyName": "Southern Company", "companyDescription": "Major US utility with nuclear, gas, and renewable generation serving the Southeast.", "role": "BENEFICIARY", "rationale": "Southern Company — nuclear and gas in prime AI datacenter geography.", "isFeedbackIndicator": False},
            {"ticker": "ETR", "companyName": "Entergy Corporation", "companyDescription": "Electric utility serving the Gulf South region with nuclear and gas generation.", "role": "CANARY", "rationale": "Entergy transmission capex signals how urgently utilities are upgrading.", "isFeedbackIndicator": False}
        ],
        "startupOpportunities": [
            {"name": "GridOS", "oneLiner": "Software layer for utility demand forecasting that accounts for AI datacenter load profiles.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "PermitFast", "oneLiner": "Automates the transmission line permitting process — currently takes 7-10 years manually.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "MicroGridCo", "oneLiner": "On-site microgrid infrastructure for datacenters that can't wait for utility connections.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"}
        ],
        "effects": [
            {
                "id": "effect_electricity_nuclear_renaissance",
                "order": 2,
                "title": "Nuclear Power Gets a Second Life",
                "description": "Grid bottlenecks make nuclear the only viable option for baseload power at datacenter scale. Shuttered plants get reopened and SMR projects accelerate.",
                "initialTHI": 65,
                "equityBets": [
                    {"ticker": "CEG", "companyName": "Constellation Energy", "companyDescription": "Largest US nuclear power operator with 13 nuclear plants providing carbon-free baseload.", "role": "BENEFICIARY", "rationale": "Constellation Energy owns the largest US nuclear fleet — direct beneficiary of reopenings"},
                    {"ticker": "CCJ", "companyName": "Cameco Corporation", "companyDescription": "World's largest publicly traded uranium producer controlling ~18% of global production.", "role": "BENEFICIARY", "rationale": "Cameco uranium supply becomes critical as nuclear demand surges"},
                    {"ticker": "SMR", "companyName": "NuScale Power", "companyDescription": "Developer of small modular nuclear reactors (SMRs) — next-gen nuclear technology company.", "role": "CANARY", "rationale": "NuScale Power's SMR order book signals whether next-gen nuclear is real"}
                ]
            },
            {
                "id": "effect_electricity_industrial_reshoring_stall",
                "order": 2,
                "title": "Reshoring Stalls on Power Constraints",
                "description": "Factories trying to reshore to the US discover there's no electricity available. Manufacturing buildout gets delayed by 3-5 years while utilities catch up.",
                "initialTHI": 52,
                "equityBets": [
                    {"ticker": "EATON", "companyName": "Eaton Corporation", "companyDescription": "Power management company making electrical components, switchgear, and grid infrastructure equipment.", "role": "BENEFICIARY", "rationale": "Eaton's electrical equipment is essential for every grid upgrade and factory connection"},
                    {"ticker": "GE", "companyName": "GE Vernova", "companyDescription": "GE's energy spin-off making gas turbines, wind turbines, and grid modernization equipment.", "role": "BENEFICIARY", "rationale": "GE Vernova turbines and grid equipment needed for capacity buildout"},
                    {"ticker": "X", "companyName": "United States Steel", "companyDescription": "Integrated steel producer with blast furnace and mini-mill operations across the US and Europe.", "role": "HEADWIND", "rationale": "US Steel reshoring demand gets delayed when factories can't get power hookups"}
                ]
            }
        ]
    },
    {
        "id": "thesis_ai_slop_human_premium",
        "title": "AI Slop Makes Human-Made Premium",
        "subtitle": "AI floods the internet with garbage, making anything genuinely human-created suddenly scarce and valuable.",
        "description": "When everyone can generate infinite slop, authentic human work becomes the new luxury good.",
        "timeHorizon": "1-3yr",
        "tags": ["AI", "media", "culture", "consumer"],
        "initialTHI": 62,
        "initialUserConviction": 7,
        "feeds": [
            {"id": "gtrends_ai_generated_content", "source": "GTRENDS", "keyword": "AI generated content fake", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_human_made", "source": "GTRENDS", "keyword": "handmade human made authentic", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_newsletter_subscription", "source": "GTRENDS", "keyword": "substack newsletter subscribe", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_ai_detector", "source": "GTRENDS", "keyword": "AI content detector", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_trust_media", "source": "GTRENDS", "keyword": "trust media news authenticity", "sourceType": "adoption", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "NFLX", "companyName": "Netflix", "companyDescription": "World's largest streaming platform with 260M+ subscribers. Invests $17B+/year in original human-created content.", "role": "BENEFICIARY", "rationale": "Premium human-curated content becomes more valuable vs. AI slop.", "isFeedbackIndicator": False},
            {"ticker": "SPOT", "companyName": "Spotify Technology", "companyDescription": "Leading audio streaming platform with 600M+ users. Curates human-created music, podcasts, and audiobooks.", "role": "BENEFICIARY", "rationale": "Human artist discovery and curation becomes a competitive moat.", "isFeedbackIndicator": False},
            {"ticker": "NYT", "companyName": "The New York Times", "companyDescription": "Premier subscription journalism brand with 10M+ digital subscribers. Gold standard for verified human reporting.", "role": "BENEFICIARY", "rationale": "Trusted human journalism becomes scarce and subscription-worthy.", "isFeedbackIndicator": True, "feedbackWeight": 0.08}
        ],
        "startupOpportunities": [
            {"name": "ProveMade", "oneLiner": "Blockchain-anchored provenance certificates for human-created creative work.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "HumanLayer", "oneLiner": "Verified human-only content platform — no AI generated posts allowed.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "RealInk", "oneLiner": "Premium newsletter platform that verifies all content is human-written.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"}
        ],
        "effects": [
            {
                "id": "effect_slop_live_events_premium",
                "order": 2,
                "title": "Live Events Become the Only Trustworthy Content",
                "description": "When all recorded media is suspect, live and in-person experiences become the only content you can trust. Concert, sports, and conference tickets skyrocket.",
                "initialTHI": 60,
                "equityBets": [
                    {"ticker": "LYV", "companyName": "Live Nation Entertainment", "companyDescription": "World's largest live entertainment company operating venues, ticketing (Ticketmaster), and concert promotion.", "role": "BENEFICIARY", "rationale": "Live Nation controls live event infrastructure — irreplaceable in an AI-slop world"},
                    {"ticker": "MSGS", "companyName": "Madison Square Garden Sports", "companyDescription": "Owns the NY Knicks, NY Rangers, and Madison Square Garden — iconic live sports and entertainment venue.", "role": "BENEFICIARY", "rationale": "Madison Square Garden Sports owns scarce live venue inventory"},
                    {"ticker": "DKNG", "companyName": "DraftKings", "companyDescription": "Leading US sports betting and daily fantasy sports platform with growing user engagement.", "role": "CANARY", "rationale": "DraftKings live sports engagement signals whether fans are fleeing digital for live"}
                ]
            },
            {
                "id": "effect_slop_artisan_ecommerce",
                "order": 2,
                "title": "Etsy-fication of Everything",
                "description": "Human-made provenance becomes a premium label across all consumer categories. Handcrafted goods command 3-5x markups over AI-designed alternatives.",
                "initialTHI": 55,
                "equityBets": [
                    {"ticker": "ETSY", "companyName": "Etsy", "companyDescription": "Online marketplace for handmade, vintage, and unique goods. 90M+ active buyers seeking human-crafted products.", "role": "BENEFICIARY", "rationale": "Etsy is the canonical marketplace for human-made goods — direct beneficiary"},
                    {"ticker": "AMZN", "companyName": "Amazon.com", "companyDescription": "World's largest e-commerce platform and cloud computing provider. Marketplace listings vulnerable to AI-generated spam.", "role": "HEADWIND", "rationale": "Amazon marketplace drowns in AI-generated product listings, eroding trust"}
                ]
            },
            {
                "id": "effect_slop_education_crisis",
                "order": 2,
                "title": "Education System Can't Grade Anything",
                "description": "AI-generated essays and homework become undetectable, forcing schools to abandon written assessments entirely and shift to oral exams and in-person demonstrations.",
                "initialTHI": 68,
                "equityBets": [
                    {"ticker": "PRCT", "companyName": "PROCEPT BioRobotics", "companyDescription": "Surgical robotics company. Used here as proxy for proctoring/assessment tech becoming critical for schools.", "role": "BENEFICIARY", "rationale": "Procept — proctoring and assessment tools become mission-critical for schools"},
                    {"ticker": "CHGG", "companyName": "Chegg", "companyDescription": "Education technology company offering homework help, textbook solutions, and tutoring services.", "role": "HEADWIND", "rationale": "Chegg's homework help model collapses when AI does all homework for free"},
                    {"ticker": "TWOU", "companyName": "2U Inc.", "companyDescription": "Online education platform partnering with universities to offer degree programs and boot camps.", "role": "HEADWIND", "rationale": "2U online education faces credibility crisis if degrees can be AI-gamed"}
                ]
            }
        ]
    },
    {
        "id": "thesis_senior_living_boom",
        "title": "Baby Boomers Turn 90 → Senior Living Boom",
        "subtitle": "80 million Boomers are hitting their final decade where they need serious care.",
        "description": "The biggest wealth transfer in history demanding the most expensive housing in America. Supply of senior care is catastrophically behind.",
        "timeHorizon": "3-7yr",
        "tags": ["demographics", "healthcare", "real estate", "macro"],
        "initialTHI": 75,
        "initialUserConviction": 7,
        "feeds": [
            {"id": "fred_population_65plus", "source": "FRED", "seriesId": "SPPOP65UPTOZSUSA", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "fred_healthcare_spend", "source": "FRED", "seriesId": "HLTHSCPCHCSA", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_senior_living", "source": "GTRENDS", "keyword": "senior living assisted living", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_memory_care", "source": "GTRENDS", "keyword": "memory care dementia facility", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_nursing_home_employment", "source": "FRED", "seriesId": "CES6562200001", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_aging_parents", "source": "GTRENDS", "keyword": "aging parents care options", "sourceType": "adoption", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "WELL", "companyName": "Welltower", "companyDescription": "Largest healthcare REIT specializing in senior housing and post-acute care facilities across US, UK, and Canada.", "role": "BENEFICIARY", "rationale": "Welltower — largest senior housing REIT, direct demographic play.", "isFeedbackIndicator": True, "feedbackWeight": 0.10},
            {"ticker": "VTR", "companyName": "Ventas", "companyDescription": "Diversified healthcare REIT owning senior housing, medical office buildings, and life science properties.", "role": "BENEFICIARY", "rationale": "Ventas — diversified healthcare REIT with senior housing focus.", "isFeedbackIndicator": False},
            {"ticker": "UNH", "companyName": "UnitedHealth Group", "companyDescription": "Largest US health insurer and healthcare services company. Medicare Advantage is its fastest-growing segment.", "role": "BENEFICIARY", "rationale": "UnitedHealth Medicare Advantage benefits from aging population.", "isFeedbackIndicator": False}
        ],
        "startupOpportunities": [
            {"name": "AgeCo", "oneLiner": "On-demand care coordination platform for families navigating senior care transitions.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "VillageStack", "oneLiner": "Software OS for independent senior living communities.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "CareCredits", "oneLiner": "Reverse mortgage alternative that converts home equity into senior care payments.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"}
        ],
        "effects": [
            {
                "id": "effect_senior_caregiver_shortage",
                "order": 2,
                "title": "Caregiver Wage Explosion",
                "description": "Demand for home health aides and nursing staff far outstrips supply, driving wages up 40-60% and creating a labor crisis that forces automation and immigration reform.",
                "initialTHI": 72,
                "equityBets": [
                    {"ticker": "AMED", "companyName": "Amedisys", "companyDescription": "Leading home health and hospice care provider operating across 37 states.", "role": "BENEFICIARY", "rationale": "Amedisys home health services capture surging demand for in-home elder care"},
                    {"ticker": "ENSG", "companyName": "The Ensign Group", "companyDescription": "Largest independent operator of skilled nursing and assisted living facilities in the US.", "role": "BENEFICIARY", "rationale": "Ensign Group skilled nursing facilities benefit from demographic inevitability"},
                    {"ticker": "ISRG", "companyName": "Intuitive Surgical", "companyDescription": "Pioneer of robotic-assisted surgery with the da Vinci system used in 10M+ procedures.", "role": "CANARY", "rationale": "Intuitive Surgical robot-assisted procedures signal whether automation fills the care gap"}
                ]
            },
            {
                "id": "effect_senior_wealth_transfer",
                "order": 2,
                "title": "The $80T Wealth Transfer Reshapes Finance",
                "description": "Boomers passing wealth to Gen X and Millennials triggers the largest intergenerational asset transfer in history, flooding wealth management and estate planning with demand.",
                "initialTHI": 70,
                "equityBets": [
                    {"ticker": "SCHW", "companyName": "Charles Schwab", "companyDescription": "Largest US brokerage firm with $8T+ in client assets. Captures wealth transfers into investment accounts.", "role": "BENEFICIARY", "rationale": "Schwab captures inherited assets flowing into brokerage accounts"},
                    {"ticker": "RJF", "companyName": "Raymond James Financial", "companyDescription": "Full-service wealth management firm with 8,000+ financial advisors specializing in high-net-worth clients.", "role": "BENEFICIARY", "rationale": "Raymond James advisors positioned for high-net-worth estate planning"},
                    {"ticker": "COIN", "companyName": "Coinbase Global", "companyDescription": "Largest US cryptocurrency exchange and custodian.", "role": "CANARY", "rationale": "Coinbase signals whether younger heirs allocate inherited wealth into crypto"}
                ]
            }
        ]
    },
    {
        "id": "thesis_genz_micro_luxury",
        "title": "Gen Z Affordable Affluence → Micro-Luxuries",
        "subtitle": "Gen Z has no money but still wants nice stuff — trading down on big purchases, trading up on tiny luxuries.",
        "description": "$40 face masks instead of $4,000 handbags. The micro-luxury market is exploding.",
        "timeHorizon": "1-3yr",
        "tags": ["consumer", "GenZ", "luxury", "retail"],
        "initialTHI": 65,
        "initialUserConviction": 6,
        "feeds": [
            {"id": "gtrends_affordable_luxury", "source": "GTRENDS", "keyword": "affordable luxury dupe", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_skincare_routine", "source": "GTRENDS", "keyword": "skincare routine affordable", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_consumer_spending_young", "source": "FRED", "seriesId": "PCE", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_dupe_luxury", "source": "GTRENDS", "keyword": "luxury dupe product", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_stanley_cup", "source": "GTRENDS", "keyword": "stanley cup water bottle viral", "sourceType": "adoption", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "ELF", "companyName": "e.l.f. Beauty", "companyDescription": "Fast-growing affordable cosmetics brand. $8 lip gloss that performs like $40 luxury — poster child of the micro-luxury trend.", "role": "BENEFICIARY", "rationale": "e.l.f. Beauty is the canonical micro-luxury brand.", "isFeedbackIndicator": True, "feedbackWeight": 0.12},
            {"ticker": "ULTA", "companyName": "Ulta Beauty", "companyDescription": "Largest US beauty retailer with 1,300+ stores carrying both prestige and mass-market brands.", "role": "BENEFICIARY", "rationale": "Ulta democratizes beauty across price points.", "isFeedbackIndicator": False}
        ],
        "startupOpportunities": [
            {"name": "CrateJoy 2.0", "oneLiner": "Micro-luxury subscription boxes curated around specific identities.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "StatusStack", "oneLiner": "App that tracks and gamifies your micro-luxury collection.", "timing": "TOO_EARLY", "timeHorizon": "1-3yr"},
            {"name": "DupeLab", "oneLiner": "AI that finds the highest-quality affordable version of any luxury product.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"}
        ],
        "effects": [
            {
                "id": "effect_microlux_legacy_brands_die",
                "order": 2,
                "title": "Legacy Luxury Brands Lose Gen Z Forever",
                "description": "Traditional luxury houses like Gucci and Burberry can't reach Gen Z who'd rather buy 50 small dopamine hits than one big flex. Entry-level luxury gets gutted.",
                "initialTHI": 58,
                "equityBets": [
                    {"ticker": "CPRI", "companyName": "Capri Holdings", "companyDescription": "Luxury fashion group owning Versace, Jimmy Choo, and Michael Kors brands.", "role": "HEADWIND", "rationale": "Capri Holdings (Versace, Michael Kors) stuck in mid-luxury no-man's-land"},
                    {"ticker": "TPR", "companyName": "Tapestry", "companyDescription": "Fashion holding company owning Coach, Kate Spade, and Stuart Weitzman brands.", "role": "HEADWIND", "rationale": "Tapestry (Coach, Kate Spade) faces pressure as Gen Z redefines affordable luxury"},
                    {"ticker": "ELF", "companyName": "e.l.f. Beauty", "companyDescription": "Fast-growing affordable cosmetics brand loved by Gen Z for luxury-quality products at drugstore prices.", "role": "BENEFICIARY", "rationale": "e.l.f. Beauty is the poster child — $8 lip gloss beats $40 Dior"}
                ]
            },
            {
                "id": "effect_microlux_subscription_fatigue",
                "order": 2,
                "title": "Micro-Luxury Subscription Fatigue Hits",
                "description": "Gen Z signs up for dozens of small subscriptions chasing micro-luxuries, then gets crushed by the aggregate cost. Subscription management and cancellation tools boom.",
                "initialTHI": 48,
                "equityBets": [
                    {"ticker": "AAPL", "companyName": "Apple", "companyDescription": "World's most valuable company making iPhones, Macs, and services. App Store captures 30% of all subscription revenue.", "role": "CANARY", "rationale": "Apple's App Store subscription revenue signals whether micro-subscription spend is peaking"},
                    {"ticker": "BMBL", "companyName": "Bumble", "companyDescription": "Dating app where women make the first move. Revenue depends on premium subscription tiers.", "role": "HEADWIND", "rationale": "Bumble premium subscriptions get cut when Gen Z trims micro-luxury spending"},
                    {"ticker": "SOFI", "companyName": "SoFi Technologies", "companyDescription": "Digital financial services platform offering banking, investing, and student loan refinancing for young adults.", "role": "BENEFICIARY", "rationale": "SoFi's budgeting tools capture demand from Gen Z trying to manage subscription sprawl"}
                ]
            }
        ]
    },
    {
        "id": "thesis_sleep_status",
        "title": "Sleep Is the New Status Symbol",
        "subtitle": "Rich people are obsessed with perfect sleep as the ultimate luxury and performance signal.",
        "description": "Eight-hour sleep tracking, $5k mattresses, and bedroom optimization are replacing cars and watches as status symbols.",
        "timeHorizon": "1-3yr",
        "tags": ["consumer", "health", "luxury", "wellness"],
        "initialTHI": 58,
        "initialUserConviction": 6,
        "feeds": [
            {"id": "gtrends_sleep_tracker", "source": "GTRENDS", "keyword": "sleep tracker whoop oura", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_sleep_optimization", "source": "GTRENDS", "keyword": "sleep optimization biohacking", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_consumer_durables", "source": "FRED", "seriesId": "PCDG", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_mattress_luxury", "source": "GTRENDS", "keyword": "luxury mattress sleep pod", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_magnesium_sleep", "source": "GTRENDS", "keyword": "magnesium supplement sleep", "sourceType": "adoption", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "AAPL", "companyName": "Apple", "companyDescription": "World's most valuable company. Apple Watch has become the leading consumer sleep tracker with health monitoring.", "role": "BENEFICIARY", "rationale": "Apple Watch sleep tracking integration accelerates mainstream adoption.", "isFeedbackIndicator": False},
            {"ticker": "TPX", "companyName": "Tempur Sealy International", "companyDescription": "World's largest mattress company owning Tempur-Pedic, Sealy, and Stearns & Foster premium sleep brands.", "role": "BENEFICIARY", "rationale": "Tempur-Sealy is the premium mattress brand that benefits most.", "isFeedbackIndicator": True, "feedbackWeight": 0.10}
        ],
        "startupOpportunities": [
            {"name": "SleepScore Pro", "oneLiner": "Professional sleep assessment service — think dentist for your sleep.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "DreamOS", "oneLiner": "Smart bedroom hub that integrates mattress, lighting, temperature, and sound.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "RecoveryStack", "oneLiner": "B2B sleep and recovery program sold to employers as a productivity benefit.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"}
        ],
        "effects": [
            {
                "id": "effect_sleep_caffeine_decline",
                "order": 2,
                "title": "Caffeine Becomes the New Cigarette",
                "description": "Sleep-obsessed culture reframes coffee and energy drinks as performance-destroying substances. Decaf and adaptogen beverages surge while caffeine gets vilified.",
                "initialTHI": 42,
                "equityBets": [
                    {"ticker": "MNST", "companyName": "Monster Beverage", "companyDescription": "Leading energy drink maker with Monster, Reign, and Bang brands. Revenue tied to caffeine consumption trends.", "role": "HEADWIND", "rationale": "Monster Beverage faces headwinds as sleep culture demonizes energy drinks"},
                    {"ticker": "CELH", "companyName": "Celsius Holdings", "companyDescription": "Fast-growing fitness energy drink brand marketed as a healthy, thermogenic beverage.", "role": "HEADWIND", "rationale": "Celsius energy drink growth stalls if caffeine becomes stigmatized"},
                    {"ticker": "SBUX", "companyName": "Starbucks", "companyDescription": "Global coffeehouse chain with 35,000+ stores. Decaf and non-coffee menu mix signals cultural shifts.", "role": "CANARY", "rationale": "Starbucks decaf and non-coffee menu mix signals the cultural shift"}
                ]
            },
            {
                "id": "effect_sleep_employer_mandates",
                "order": 2,
                "title": "Employers Start Mandating Rest",
                "description": "Companies discover that well-rested employees are 30% more productive. Sleep tracking becomes an employee benefit, and always-on culture gets regulated.",
                "initialTHI": 45,
                "equityBets": [
                    {"ticker": "AAPL", "companyName": "Apple", "companyDescription": "Apple Watch health platform tracks sleep stages, blood oxygen, and heart rate during sleep.", "role": "BENEFICIARY", "rationale": "Apple Watch sleep data becomes the backbone of corporate wellness programs"},
                    {"ticker": "CRM", "companyName": "Salesforce", "companyDescription": "Leading CRM platform known for hustle culture. Adoption of sleep policies would signal mainstream shift.", "role": "CANARY", "rationale": "Salesforce-style hustle culture companies adopting sleep policies signals the tipping point"},
                    {"ticker": "WDAY", "companyName": "Workday", "companyDescription": "Enterprise HR and finance cloud platform used by 10,000+ organizations for workforce management.", "role": "BENEFICIARY", "rationale": "Workday integrates wellness and rest metrics into HR platforms"}
                ]
            },
            {
                "id": "effect_sleep_bedroom_real_estate",
                "order": 2,
                "title": "The Master Bedroom Becomes a $50K Room",
                "description": "Soundproofing, blackout systems, climate control, and air filtration turn bedrooms into sleep laboratories. Home renovation spending shifts dramatically.",
                "initialTHI": 50,
                "equityBets": [
                    {"ticker": "HD", "companyName": "Home Depot", "companyDescription": "Largest home improvement retailer in the US with $150B+ annual revenue. Captures DIY and pro renovation spending.", "role": "BENEFICIARY", "rationale": "Home Depot captures DIY and pro bedroom renovation spend"},
                    {"ticker": "CARR", "companyName": "Carrier Global", "companyDescription": "Global leader in HVAC, refrigeration, and air quality systems for residential and commercial buildings.", "role": "BENEFICIARY", "rationale": "Carrier HVAC and air quality systems become bedroom essentials"}
                ]
            }
        ]
    },
    {
        "id": "thesis_yield_curve_resteepening",
        "title": "Yield Curve Re-steepening",
        "subtitle": "The yield curve is finally un-inverting — long rates rising faster than short rates.",
        "description": "Banks can actually make money again and the recession fear trade is unwinding.",
        "timeHorizon": "0-6mo",
        "tags": ["macro", "rates", "banks", "fixed income"],
        "initialTHI": 61,
        "initialUserConviction": 6,
        "feeds": [
            {"id": "fred_10y_2y_spread", "source": "FRED", "seriesId": "T10Y2Y", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "fred_10y_rate", "source": "FRED", "seriesId": "DGS10", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "fred_2y_rate", "source": "FRED", "seriesId": "DGS2", "sourceType": "structural", "confirmingDirection": "lower"},
            {"id": "fred_ffr", "source": "FRED", "seriesId": "FEDFUNDS", "sourceType": "policy", "confirmingDirection": "lower"},
            {"id": "fred_bank_net_interest_margin", "source": "FRED", "seriesId": "USNIM", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "fred_credit_spreads", "source": "FRED", "seriesId": "BAMLH0A0HYM2", "sourceType": "structural", "confirmingDirection": "lower"}
        ],
        "equityBets": [
            {"ticker": "KRE", "companyName": "SPDR S&P Regional Banking ETF", "companyDescription": "ETF tracking US regional bank stocks. Regional banks profit most from steep yield curves via borrow-short-lend-long.", "role": "BENEFICIARY", "rationale": "Regional bank ETF — most direct beneficiary of steepening yield curve.", "isFeedbackIndicator": True, "feedbackWeight": 0.12},
            {"ticker": "JPM", "companyName": "JPMorgan Chase", "companyDescription": "Largest US bank by assets with massive lending book. Net interest margin expands in steepening rate environments.", "role": "BENEFICIARY", "rationale": "JPMorgan NIM expands in steepening environment.", "isFeedbackIndicator": True, "feedbackWeight": 0.10},
            {"ticker": "TLT", "companyName": "iShares 20+ Year Treasury Bond ETF", "companyDescription": "ETF holding long-duration US Treasury bonds. Price moves inversely with long-term interest rates.", "role": "CANARY", "rationale": "Long-duration Treasury ETF — price action confirms/refutes steepening.", "isFeedbackIndicator": True, "feedbackWeight": 0.08}
        ],
        "startupOpportunities": [
            {"name": "BankYield", "oneLiner": "Platform that helps community banks optimize their loan books for steepening rates.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "SteepAlpha", "oneLiner": "Yield curve trade signal service for retail investors.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"}
        ],
        "effects": [
            {
                "id": "effect_yield_cre_refinancing_crisis",
                "order": 2,
                "title": "Commercial Real Estate Refinancing Wave Hits",
                "description": "Rising long rates make CRE refinancing punitive. Office buildings with 2021 low-rate debt face 200-400bps higher refinancing costs, triggering defaults.",
                "initialTHI": 63,
                "equityBets": [
                    {"ticker": "VNO", "companyName": "Vornado Realty Trust", "companyDescription": "Office-focused REIT concentrated in NYC and DC. Heavy debt load makes it sensitive to refinancing rates.", "role": "HEADWIND", "rationale": "Vornado's office-heavy portfolio faces refinancing pressure from steeper curves"},
                    {"ticker": "STWD", "companyName": "Starwood Property Trust", "companyDescription": "Largest commercial mortgage REIT in the US. Its loan book is a canary for CRE credit stress.", "role": "CANARY", "rationale": "Starwood Property Trust's CRE loan book signals where defaults are emerging"},
                    {"ticker": "CBRE", "companyName": "CBRE Group", "companyDescription": "World's largest commercial real estate services firm. Earns fees from transactions, management, and workouts.", "role": "BENEFICIARY", "rationale": "CBRE captures advisory fees from distressed CRE workouts and restructurings"}
                ]
            },
            {
                "id": "effect_yield_community_bank_revival",
                "order": 2,
                "title": "Community Banks Make a Comeback",
                "description": "Steeper curves restore the traditional borrow-short-lend-long business model. Small banks that survived the inversion suddenly have thriving margins again.",
                "initialTHI": 58,
                "equityBets": [
                    {"ticker": "KRE", "companyName": "SPDR S&P Regional Banking ETF", "companyDescription": "ETF tracking US regional bank stocks. Purest expression of steepening yield curve benefits.", "role": "BENEFICIARY", "rationale": "Regional bank ETF is the purest play on steepening-driven NIM expansion"},
                    {"ticker": "EWBC", "companyName": "East West Bancorp", "companyDescription": "Largest publicly traded bank focused on US-China cross-border banking. Strong growth market positioning.", "role": "BENEFICIARY", "rationale": "East West Bancorp benefits from restored lending margins in growth markets"},
                    {"ticker": "NYCB", "companyName": "New York Community Bancorp", "companyDescription": "Regional bank with large CRE loan portfolio. Recovery from recent stress tests bank health thesis.", "role": "CANARY", "rationale": "New York Community Bank's recovery signals whether steepening can heal damaged banks"}
                ]
            }
        ]
    },
    {
        "id": "thesis_anti_addiction",
        "title": "Attention Economy Oversaturation → Anti-Addiction",
        "subtitle": "People are getting sick of being constantly manipulated for their attention.",
        "description": "Anti-addiction becomes the new wellness trend — profitable, scalable, and culturally inevitable.",
        "timeHorizon": "1-3yr",
        "tags": ["tech", "consumer", "wellness", "culture"],
        "initialTHI": 55,
        "initialUserConviction": 7,
        "feeds": [
            {"id": "gtrends_digital_detox", "source": "GTRENDS", "keyword": "digital detox screen time limit", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_delete_social_media", "source": "GTRENDS", "keyword": "delete instagram social media addiction", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_screen_time_app", "source": "GTRENDS", "keyword": "app to limit screen time", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_consumer_sentiment", "source": "FRED", "seriesId": "UMCSENT", "sourceType": "structural", "confirmingDirection": "lower"},
            {"id": "gtrends_phone_free_schools", "source": "GTRENDS", "keyword": "phone free school policy", "sourceType": "policy", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "META", "companyName": "Meta Platforms", "companyDescription": "Parent of Facebook, Instagram, and WhatsApp. Revenue depends on user engagement and time-on-platform metrics.", "role": "HEADWIND", "rationale": "Meta engagement metrics are the canary — declining time-on-platform confirms thesis.", "isFeedbackIndicator": True, "feedbackWeight": 0.10},
            {"ticker": "SNAP", "companyName": "Snap Inc.", "companyDescription": "Parent of Snapchat, the ephemeral messaging app popular with teens and young adults.", "role": "HEADWIND", "rationale": "Most vulnerable to anti-addiction backlash among young users.", "isFeedbackIndicator": False},
            {"ticker": "GOOGL", "companyName": "Alphabet", "companyDescription": "Parent of Google, YouTube, and DeepMind. 80%+ of revenue from advertising tied to user attention.", "role": "CANARY", "rationale": "Google search volume decline signals attention shift.", "isFeedbackIndicator": False}
        ],
        "startupOpportunities": [
            {"name": "ClearMind", "oneLiner": "Subscription service that coaches families through digital minimalism.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "FocusOS", "oneLiner": "Employer productivity platform that replaces notification overload with intentional work windows.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "OfflineClub", "oneLiner": "Physical community spaces designed for analog connection — no phones, no screens.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"}
        ],
        "effects": [
            {
                "id": "effect_antiaddiction_regulation_wave",
                "order": 2,
                "title": "Social Media Gets Regulated Like Tobacco",
                "description": "Surgeon General warnings, age restrictions, and usage caps get mandated for social platforms. Compliance costs crater margins for engagement-maximizing companies.",
                "initialTHI": 52,
                "equityBets": [
                    {"ticker": "SNAP", "companyName": "Snap Inc.", "companyDescription": "Parent of Snapchat, popular with teens. Most exposed to youth-protection regulation.", "role": "HEADWIND", "rationale": "Snapchat is most exposed to youth-focused social media regulation"},
                    {"ticker": "META", "companyName": "Meta Platforms", "companyDescription": "Parent of Instagram and Facebook. Instagram faces intense scrutiny over teen mental health impacts.", "role": "HEADWIND", "rationale": "Meta's Instagram faces the strongest regulatory pressure from concerned parents"},
                    {"ticker": "MGNI", "companyName": "Magnite", "companyDescription": "Largest independent sell-side programmatic ad platform. Revenue tied to digital ad marketplace health.", "role": "CANARY", "rationale": "Magnite ad exchange volumes signal whether regulated platforms lose advertiser interest"}
                ]
            },
            {
                "id": "effect_antiaddiction_dumbphone_boom",
                "order": 2,
                "title": "Dumbphones Become a Status Symbol",
                "description": "Wealthy, high-status people publicly switch to feature phones as a flex. The anti-smartphone movement goes from niche to aspirational.",
                "initialTHI": 44,
                "equityBets": [
                    {"ticker": "NOK", "companyName": "Nokia", "companyDescription": "Finnish telecom company still producing feature phones alongside network infrastructure equipment.", "role": "BENEFICIARY", "rationale": "Nokia feature phones see unexpected demand from anti-smartphone movement"},
                    {"ticker": "AAPL", "companyName": "Apple", "companyDescription": "iPhone maker with 1.2B+ active devices. Upgrade cycle patterns signal consumer sentiment shifts.", "role": "CANARY", "rationale": "Apple iPhone upgrade cycle lengthening signals growing anti-smartphone sentiment"},
                    {"ticker": "GRMN", "companyName": "Garmin", "companyDescription": "GPS and wearable technology company making fitness watches, outdoor navigation, and aviation instruments.", "role": "BENEFICIARY", "rationale": "Garmin watches replace phones for fitness and navigation among digital minimalists"}
                ]
            },
            {
                "id": "effect_antiaddiction_attention_premium",
                "order": 2,
                "title": "Deep Focus Becomes a Paid Service",
                "description": "The ability to concentrate for hours becomes so rare that companies pay premium prices for deep-focus workers. Attention training becomes a professional skill.",
                "initialTHI": 47,
                "equityBets": [
                    {"ticker": "CALM", "companyName": "Calm", "companyDescription": "Leading meditation and mental wellness app with sleep stories, breathing exercises, and focus content.", "role": "BENEFICIARY", "rationale": "Calm meditation app captures demand for focus and attention training"},
                    {"ticker": "DUOL", "companyName": "Duolingo", "companyDescription": "World's most popular language learning app with 100M+ monthly users. Gamified model proves sustained attention is possible.", "role": "BENEFICIARY", "rationale": "Duolingo's gamified focus model proves attention can be retrained"}
                ]
            }
        ]
    },
    {
        "id": "thesis_analogue_revival",
        "title": "Screentime Backlash Drives Analogue Goods Revival",
        "subtitle": "Gen Z spends 6+ hours on screens, triggering a massive counter-trend toward physical, tactile experiences.",
        "description": "Vinyl records, film cameras, board games — anything that forces you to slow down and touch real things.",
        "timeHorizon": "1-3yr",
        "tags": ["consumer", "culture", "GenZ", "retail"],
        "initialTHI": 63,
        "initialUserConviction": 7,
        "feeds": [
            {"id": "gtrends_vinyl_records", "source": "GTRENDS", "keyword": "vinyl record player buy", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_film_camera", "source": "GTRENDS", "keyword": "film camera 35mm photography", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_board_games", "source": "GTRENDS", "keyword": "board games adults", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_journaling", "source": "GTRENDS", "keyword": "journaling paper notebook", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_arts_entertainment_spend", "source": "FRED", "seriesId": "PCRSA", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_thrift_store", "source": "GTRENDS", "keyword": "thrift store vintage shopping", "sourceType": "adoption", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "SONO", "companyName": "Sonos", "companyDescription": "Premium wireless speaker company. Products designed for intentional, high-fidelity listening experiences at home.", "role": "BENEFICIARY", "rationale": "Sonos high-quality audio for vinyl and intentional listening experience.", "isFeedbackIndicator": False},
            {"ticker": "FNKO", "companyName": "Funko", "companyDescription": "Pop culture consumer products company making vinyl figures, board games, and physical collectibles.", "role": "BENEFICIARY", "rationale": "Physical collectibles boom as people want things to hold.", "isFeedbackIndicator": False},
            {"ticker": "REAL", "companyName": "The RealReal", "companyDescription": "Largest online marketplace for authenticated luxury consignment. Sells pre-owned designer goods.", "role": "BENEFICIARY", "rationale": "Luxury resale benefits from analog, quality-over-quantity mindset.", "isFeedbackIndicator": True, "feedbackWeight": 0.08}
        ],
        "startupOpportunities": [
            {"name": "FrameShop", "oneLiner": "Film photo subscription — drop your disposable cameras in the mail, get prints back.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "TableSet", "oneLiner": "Board game bar franchise model — monthly membership, curated game library, no phones.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "PenPalPro", "oneLiner": "Handwritten letter subscription — you type it, they print it beautifully and mail it.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"}
        ],
        "effects": [
            {
                "id": "effect_analogue_paper_shortage",
                "order": 2,
                "title": "Paper and Film Supply Can't Keep Up",
                "description": "Kodak film, Moleskine notebooks, and vinyl pressing plants were scaled down for decades. Sudden demand spikes create supply shortages and price premiums.",
                "initialTHI": 57,
                "equityBets": [
                    {"ticker": "KODK", "companyName": "Eastman Kodak", "companyDescription": "Iconic photography company that still manufactures 35mm and medium format film. Supply can't meet revived demand.", "role": "BENEFICIARY", "rationale": "Kodak film production can't meet surging demand from analog photography revival"},
                    {"ticker": "IP", "companyName": "International Paper", "companyDescription": "One of the world's largest paper and packaging companies producing premium paper products.", "role": "BENEFICIARY", "rationale": "International Paper benefits from increased demand for premium paper products"},
                    {"ticker": "WMG", "companyName": "Warner Music Group", "companyDescription": "Major record label group (Atlantic, Warner, Elektra) with growing vinyl pressing and distribution business.", "role": "CANARY", "rationale": "Warner Music vinyl sales data signals the depth of the analog audio comeback"}
                ]
            },
            {
                "id": "effect_analogue_third_places",
                "order": 2,
                "title": "Third Places Make a Physical Comeback",
                "description": "Bookstores, record shops, and game cafes become the new social infrastructure as people seek screen-free gathering spaces. Physical retail gets a surprising second act.",
                "initialTHI": 60,
                "equityBets": [
                    {"ticker": "HAS", "companyName": "Hasbro", "companyDescription": "Major toy and game company owning Monopoly, Dungeons & Dragons, and Magic: The Gathering brands.", "role": "BENEFICIARY", "rationale": "Hasbro board game and tabletop division benefits from analog social gatherings"},
                    {"ticker": "BNED", "companyName": "Barnes & Noble Education", "companyDescription": "Operates campus bookstores at 1,400+ colleges. Physical retail model gains relevance in screen-free culture.", "role": "BENEFICIARY", "rationale": "Barnes & Noble Education's physical bookstore model finds new cultural relevance"},
                    {"ticker": "SBUX", "companyName": "Starbucks", "companyDescription": "Global coffeehouse chain with 35,000+ stores. Third-place gathering model uniquely positioned for analog revival.", "role": "CANARY", "rationale": "Starbucks dwell time trends signal whether physical third places are reviving"}
                ]
            }
        ]
    },
    {
        "id": "thesis_verification_crisis",
        "title": "AI Content Explosion → Verification Crisis",
        "subtitle": "AI generates so much content that nobody knows what's real anymore.",
        "description": "Every photo, video, article, and voice recording is suspect. This creates a massive market for verification tools.",
        "timeHorizon": "1-3yr",
        "tags": ["AI", "media", "trust", "infrastructure"],
        "initialTHI": 66,
        "initialUserConviction": 8,
        "feeds": [
            {"id": "gtrends_deepfake", "source": "GTRENDS", "keyword": "deepfake detection fake video", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_ai_fake_news", "source": "GTRENDS", "keyword": "AI fake news misinformation", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_content_authenticity", "source": "GTRENDS", "keyword": "content authenticity verification", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_trust_media", "source": "FRED", "seriesId": "UMCSENT", "sourceType": "structural", "confirmingDirection": "lower"},
            {"id": "gtrends_watermark_ai", "source": "GTRENDS", "keyword": "AI watermark detection tool", "sourceType": "adoption", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "ORCL", "companyName": "Oracle Corporation", "companyDescription": "Enterprise database and cloud infrastructure company. Building identity and provenance verification infrastructure.", "role": "BENEFICIARY", "rationale": "Oracle provenance and identity infrastructure for content verification.", "isFeedbackIndicator": False},
            {"ticker": "PANW", "companyName": "Palo Alto Networks", "companyDescription": "Leading cybersecurity platform company. Expanding from network security into content authentication and trust.", "role": "BENEFICIARY", "rationale": "Cybersecurity expands to content authentication.", "isFeedbackIndicator": False},
            {"ticker": "META", "companyName": "Meta Platforms", "companyDescription": "Parent of Facebook and Instagram. Content moderation costs are a direct readout of the fake content crisis.", "role": "CANARY", "rationale": "Meta's content moderation costs signal how bad the fake content problem has gotten.", "isFeedbackIndicator": False}
        ],
        "startupOpportunities": [
            {"name": "TrueSign", "oneLiner": "Cryptographic content signing tool that lets creators prove provenance.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "VerifyLayer", "oneLiner": "Browser plugin that checks authenticity scores on any content you encounter.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "TrustChain", "oneLiner": "Enterprise content provenance platform for media companies.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"}
        ],
        "effects": [
            {
                "id": "effect_verification_identity_layer",
                "order": 2,
                "title": "Digital Identity Becomes Mandatory Infrastructure",
                "description": "Governments and platforms mandate verified human identity for posting content. Anonymous internet dies, replaced by identity-first platforms.",
                "initialTHI": 56,
                "equityBets": [
                    {"ticker": "OKTA", "companyName": "Okta", "companyDescription": "Leading cloud identity and access management platform serving 18,000+ organizations.", "role": "BENEFICIARY", "rationale": "Okta identity verification becomes the backbone of authenticated content platforms"},
                    {"ticker": "TWLO", "companyName": "Twilio", "companyDescription": "Cloud communications platform providing SMS, voice, and identity verification APIs to developers.", "role": "BENEFICIARY", "rationale": "Twilio Verify handles phone-based identity confirmation at scale"},
                    {"ticker": "RDDT", "companyName": "Reddit", "companyDescription": "Social media platform built on anonymous discussion forums and communities (subreddits).", "role": "HEADWIND", "rationale": "Reddit's anonymous culture faces existential pressure from identity mandates"}
                ]
            },
            {
                "id": "effect_verification_insurance_chaos",
                "order": 2,
                "title": "Insurance Claims Become Unverifiable",
                "description": "AI-generated photos and videos of fake damage make insurance fraud trivial. Carriers scramble for new verification tools, and premiums spike for everyone.",
                "initialTHI": 62,
                "equityBets": [
                    {"ticker": "LMND", "companyName": "Lemonade", "companyDescription": "AI-powered insurance company for renters, homeowners, and pet insurance. Claims processing relies on digital evidence.", "role": "HEADWIND", "rationale": "Lemonade's AI claims processing is vulnerable to AI-generated fraudulent evidence"},
                    {"ticker": "VRSK", "companyName": "Verisk Analytics", "companyDescription": "Data analytics provider for insurance, energy, and financial services. Fraud detection is a core capability.", "role": "BENEFICIARY", "rationale": "Verisk's data analytics becomes critical for detecting AI-generated insurance fraud"},
                    {"ticker": "ALL", "companyName": "Allstate", "companyDescription": "One of the largest US personal auto and homeowners insurers. Claims expense ratios signal fraud trends.", "role": "CANARY", "rationale": "Allstate's claims expense ratio signals whether AI fraud is materially impacting carriers"}
                ]
            },
            {
                "id": "effect_verification_legal_evidence_crisis",
                "order": 2,
                "title": "Courts Can't Trust Digital Evidence",
                "description": "Photos, videos, and audio recordings become inadmissible without cryptographic provenance chains. The legal system scrambles to adapt evidentiary standards.",
                "initialTHI": 49,
                "equityBets": [
                    {"ticker": "AXON", "companyName": "Axon Enterprise", "companyDescription": "Makes body cameras, Tasers, and digital evidence management software for law enforcement.", "role": "BENEFICIARY", "rationale": "Axon body cameras with tamper-proof chains of custody become the gold standard"},
                    {"ticker": "ONTO", "companyName": "Onto Innovation", "companyDescription": "Semiconductor process control and inspection technology company. Verification tech applies to evidence authentication.", "role": "BENEFICIARY", "rationale": "Onto Innovation's inspection tech applies to document and evidence verification"}
                ]
            }
        ]
    },
    {
        "id": "thesis_cognitive_decline",
        "title": "AI-Induced Cognitive Decline",
        "subtitle": "As AI handles more cognitive tasks, people's brains atrophy from disuse.",
        "description": "Memory, critical thinking, and problem-solving skills decline. This creates demand for cognitive enhancement tools.",
        "timeHorizon": "3-7yr",
        "tags": ["AI", "health", "education", "neuroscience"],
        "initialTHI": 42,
        "initialUserConviction": 6,
        "feeds": [
            {"id": "gtrends_brain_training", "source": "GTRENDS", "keyword": "brain training cognitive improvement", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_memory_decline", "source": "GTRENDS", "keyword": "memory loss decline young people", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_nootropics", "source": "GTRENDS", "keyword": "nootropics brain supplements", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_ai_dependency", "source": "GTRENDS", "keyword": "too dependent on AI ChatGPT", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_education_spend", "source": "FRED", "seriesId": "HLTHSCPCHCSA", "sourceType": "structural", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "DUOL", "companyName": "Duolingo", "companyDescription": "World's most popular language learning app with 100M+ monthly users. Gamified cognitive exercise platform.", "role": "BENEFICIARY", "rationale": "Duolingo — cognitive exercise through language learning.", "isFeedbackIndicator": True, "feedbackWeight": 0.10},
            {"ticker": "ABBV", "companyName": "AbbVie", "companyDescription": "Major biopharmaceutical company with pipeline in neuroscience, including Alzheimer's and cognitive decline treatments.", "role": "BENEFICIARY", "rationale": "AbbVie Alzheimer's/cognitive decline pipeline.", "isFeedbackIndicator": False},
            {"ticker": "GOOGL", "companyName": "Alphabet", "companyDescription": "Parent of Google. Declining search query complexity signals people outsourcing thinking to AI.", "role": "CANARY", "rationale": "Declining Google search complexity signals people outsourcing thinking to AI.", "isFeedbackIndicator": False}
        ],
        "startupOpportunities": [
            {"name": "MindGym", "oneLiner": "Daily cognitive exercise app designed to counteract AI dependency atrophy.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "ThinkWithout", "oneLiner": "Productivity tool that blocks AI assistance for certain tasks.", "timing": "TOO_EARLY", "timeHorizon": "1-3yr"},
            {"name": "CognitiveRx", "oneLiner": "Corporate wellness program measuring and improving employee cognitive performance.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"}
        ],
        "effects": [
            {
                "id": "effect_cognitive_human_premium_hiring",
                "order": 2,
                "title": "Critical Thinkers Command 3x Salaries",
                "description": "As most workers become AI-dependent button-pushers, people who can actually think independently become extraordinarily scarce and valuable. A cognitive elite emerges.",
                "initialTHI": 45,
                "equityBets": [
                    {"ticker": "HIMS", "companyName": "Hims & Hers Health", "companyDescription": "Telehealth platform expanding into nootropics and cognitive supplements.", "role": "BENEFICIARY", "rationale": "Hims nootropics and cognitive supplements capture demand from workers trying to stay sharp"},
                    {"ticker": "DUOL", "companyName": "Duolingo", "companyDescription": "Gamified learning app that proves sustained attention and cognitive exercise can be engaging.", "role": "BENEFICIARY", "rationale": "Duolingo-style brain exercise apps become professional necessities"},
                    {"ticker": "LULU", "companyName": "Lululemon Athletica", "companyDescription": "Premium athletic brand expanding into mindfulness, meditation, and holistic wellness.", "role": "CANARY", "rationale": "Lululemon's mindfulness and wellness positioning signals mainstream cognitive health awareness"}
                ]
            },
            {
                "id": "effect_cognitive_education_overhaul",
                "order": 2,
                "title": "Schools Ban AI and Go Back to Basics",
                "description": "Alarmed by declining student cognition, school districts mandate pen-and-paper learning, memorization drills, and AI-free classrooms. EdTech faces a reckoning.",
                "initialTHI": 50,
                "equityBets": [
                    {"ticker": "STRA", "companyName": "Strategic Education", "companyDescription": "Operates Strayer and Capella Universities with vocational, hands-on training focus.", "role": "BENEFICIARY", "rationale": "Strategic Education's vocational hands-on training model thrives in an AI-skeptic education environment"},
                    {"ticker": "TWOU", "companyName": "2U Inc.", "companyDescription": "Online education platform partnering with universities for degree programs.", "role": "HEADWIND", "rationale": "2U's online-first education model faces backlash from anti-screen, anti-AI sentiment"},
                    {"ticker": "MSFT", "companyName": "Microsoft", "companyDescription": "Tech giant with Copilot AI integrated across Office, Teams, and education products.", "role": "CANARY", "rationale": "Microsoft Copilot adoption in schools signals whether education embraces or rejects AI tools"}
                ]
            }
        ]
    },
    {
        "id": "thesis_taiwan_chip_risk",
        "title": "Betting on Chips Crashing When China Moves",
        "subtitle": "China invades Taiwan and 90% of advanced semiconductors disappear overnight.",
        "description": "Every iPhone, datacenter, and AI chip gets stuck in geopolitical limbo. A tail risk thesis — low probability but civilization-scale consequences.",
        "timeHorizon": "3-7yr",
        "tags": ["geopolitics", "semiconductors", "tail risk", "China"],
        "initialTHI": 38,
        "initialUserConviction": 5,
        "feeds": [
            {"id": "gtrends_taiwan_china_conflict", "source": "GTRENDS", "keyword": "Taiwan China invasion conflict", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_chip_reshoring", "source": "GTRENDS", "keyword": "semiconductor reshoring CHIPS Act", "sourceType": "policy", "confirmingDirection": "higher"},
            {"id": "fred_semiconductor_imports", "source": "FRED", "seriesId": "IR", "sourceType": "structural", "confirmingDirection": "higher"},
            {"id": "gtrends_chips_act", "source": "GTRENDS", "keyword": "CHIPS Act semiconductor factory US", "sourceType": "policy", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "INTC", "companyName": "Intel Corporation", "companyDescription": "American chipmaker building domestic fab capacity under CHIPS Act. Only US company with leading-edge manufacturing ambitions.", "role": "BENEFICIARY", "rationale": "Intel's US manufacturing becomes critical infrastructure.", "isFeedbackIndicator": False},
            {"ticker": "WOLF", "companyName": "Wolfspeed", "companyDescription": "US-based silicon carbide semiconductor manufacturer for EV and industrial power applications.", "role": "BENEFICIARY", "rationale": "Wolfspeed — US-made silicon carbide chips.", "isFeedbackIndicator": False},
            {"ticker": "TSM", "companyName": "Taiwan Semiconductor", "companyDescription": "World's largest chip foundry manufacturing 90%+ of advanced semiconductors. All fabs concentrated in Taiwan.", "role": "CANARY", "rationale": "TSMC's US fab progress signals geopolitical risk pricing.", "isFeedbackIndicator": True, "feedbackWeight": 0.12}
        ],
        "startupOpportunities": [
            {"name": "ChipMapper", "oneLiner": "Supply chain mapping tool that shows companies their Taiwan chip exposure.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"},
            {"name": "ReShoreAI", "oneLiner": "Procurement platform that finds US alternatives for Taiwan-dependent components.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"}
        ],
        "effects": [
            {
                "id": "effect_chips_defense_stocks_surge",
                "order": 2,
                "title": "Defense Primes Get a Blank Check",
                "description": "A Taiwan crisis turns into the largest defense mobilization since the Cold War. Missile systems, naval assets, and cyber capabilities get emergency funding.",
                "initialTHI": 55,
                "equityBets": [
                    {"ticker": "LMT", "companyName": "Lockheed Martin", "companyDescription": "World's largest defense contractor making F-35 fighters, missiles, and naval combat systems.", "role": "BENEFICIARY", "rationale": "Lockheed Martin missile and naval systems get emergency procurement orders"},
                    {"ticker": "RTX", "companyName": "RTX Corporation", "companyDescription": "Defense and aerospace conglomerate (Raytheon + Pratt & Whitney) making missiles, engines, and radar systems.", "role": "BENEFICIARY", "rationale": "RTX Patriot missile systems and Pratt & Whitney engines surge on Pacific theater demand"},
                    {"ticker": "PLTR", "companyName": "Palantir Technologies", "companyDescription": "Data analytics and AI platform serving defense and intelligence agencies for battlefield decision-making.", "role": "BENEFICIARY", "rationale": "Palantir's intelligence platform becomes critical for Pacific theater operations"}
                ]
            },
            {
                "id": "effect_chips_consumer_electronics_shock",
                "order": 2,
                "title": "iPhone Prices Double Overnight",
                "description": "With TSMC fabs offline, advanced chip supply drops 90%. Consumer electronics prices skyrocket and waitlists stretch to months. Used devices become liquid assets.",
                "initialTHI": 48,
                "equityBets": [
                    {"ticker": "AAPL", "companyName": "Apple", "companyDescription": "Relies entirely on TSMC for A-series and M-series chips. iPhone production halts without Taiwan fabs.", "role": "HEADWIND", "rationale": "Apple can't build iPhones without TSMC — production halts devastate revenue"},
                    {"ticker": "SWAV", "companyName": "Shockwave Medical", "companyDescription": "Medical device company with intravascular lithotripsy technology using non-Taiwan chip supply chains.", "role": "BENEFICIARY", "rationale": "Shockwave medical devices with non-Taiwan chip supply chains gain competitive advantage"},
                    {"ticker": "GFS", "companyName": "GlobalFoundries", "companyDescription": "Third-largest chip foundry globally with US, EU, and Singapore fabs. Only major non-Taiwan/China alternative.", "role": "BENEFICIARY", "rationale": "GlobalFoundries US-based fabs become the only game in town for mature-node chips"}
                ]
            },
            {
                "id": "effect_chips_tech_cold_war",
                "order": 2,
                "title": "US-China Tech Decoupling Goes Total",
                "description": "A Taiwan crisis forces complete bifurcation of global tech supply chains. Every company must choose a side, creating two parallel technology ecosystems.",
                "initialTHI": 43,
                "equityBets": [
                    {"ticker": "AMAT", "companyName": "Applied Materials", "companyDescription": "Largest semiconductor equipment company providing deposition, etch, and inspection tools for chip fabs.", "role": "BENEFICIARY", "rationale": "Applied Materials chip equipment becomes strategic infrastructure for US fab buildout"},
                    {"ticker": "KLAC", "companyName": "KLA Corporation", "companyDescription": "Semiconductor process control and yield management equipment maker. Essential for every new fab.", "role": "BENEFICIARY", "rationale": "KLA Corp's inspection tools are essential for every new domestic fab"},
                    {"ticker": "BABA", "companyName": "Alibaba Group", "companyDescription": "China's largest e-commerce and cloud computing company. Core holding for China exposure.", "role": "HEADWIND", "rationale": "Alibaba becomes uninvestable for Western capital in a full decoupling scenario"}
                ]
            }
        ]
    },
    {
        "id": "thesis_dead_internet",
        "title": "Dead Internet Theory → Bot Economy Collapse",
        "subtitle": "The internet is mostly bots talking to bots, and when everyone realizes it, digital advertising collapses.",
        "description": "Real human attention becomes the scarcest commodity on earth. The valuation of attention-based businesses gets repriced.",
        "timeHorizon": "1-3yr",
        "tags": ["tech", "advertising", "AI", "media"],
        "initialTHI": 44,
        "initialUserConviction": 6,
        "feeds": [
            {"id": "gtrends_bot_traffic", "source": "GTRENDS", "keyword": "bot traffic fake engagement", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "gtrends_ad_fraud", "source": "GTRENDS", "keyword": "digital advertising fraud", "sourceType": "adoption", "confirmingDirection": "higher"},
            {"id": "fred_digital_ad_spend", "source": "FRED", "seriesId": "PCE", "sourceType": "structural", "confirmingDirection": "lower"},
            {"id": "gtrends_dead_internet", "source": "GTRENDS", "keyword": "dead internet theory bots everywhere", "sourceType": "adoption", "confirmingDirection": "higher"}
        ],
        "equityBets": [
            {"ticker": "TTD", "companyName": "The Trade Desk", "companyDescription": "Demand-side ad platform enabling brands to buy targeted digital ads. Benefits from shift to verified human impressions.", "role": "BENEFICIARY", "rationale": "The Trade Desk benefits from shift to verified human impressions.", "isFeedbackIndicator": False},
            {"ticker": "META", "companyName": "Meta Platforms", "companyDescription": "Parent of Facebook and Instagram. Ad revenue model most exposed to bot traffic discovery.", "role": "HEADWIND", "rationale": "Meta's ad business is most exposed to bot traffic repricing.", "isFeedbackIndicator": True, "feedbackWeight": 0.12},
            {"ticker": "GOOGL", "companyName": "Alphabet", "companyDescription": "Parent of Google and YouTube. 80%+ revenue from ads that may be served to bots.", "role": "HEADWIND", "rationale": "Google's search ad moat weakens if AI chatbots reduce search-as-discovery.", "isFeedbackIndicator": True, "feedbackWeight": 0.10}
        ],
        "startupOpportunities": [
            {"name": "HumanFirst Ads", "oneLiner": "Ad network that exclusively serves verified human audiences — charges 10x CPM premium.", "timing": "RIGHT_TIMING", "timeHorizon": "1-3yr"},
            {"name": "BotAudit", "oneLiner": "Third-party ad traffic verification service for CMOs.", "timing": "RIGHT_TIMING", "timeHorizon": "0-6mo"}
        ],
        "effects": [
            {
                "id": "effect_deadinternet_influencer_collapse",
                "order": 2,
                "title": "Influencer Marketing Implodes",
                "description": "Brands discover that 60-80% of influencer followers are bots. The $20B influencer industry faces a reckoning as CPMs get repriced to real human eyeballs.",
                "initialTHI": 56,
                "equityBets": [
                    {"ticker": "SNAP", "companyName": "Snap Inc.", "companyDescription": "Parent of Snapchat. Creator economy revenue dependent on follower counts vulnerable to bot exposure.", "role": "HEADWIND", "rationale": "Snapchat's creator economy is most exposed to bot-follower repricing"},
                    {"ticker": "PINS", "companyName": "Pinterest", "companyDescription": "Visual discovery and shopping platform. Intent-based model tied to real purchase behavior, not follower counts.", "role": "BENEFICIARY", "rationale": "Pinterest's intent-based model is less vulnerable to fake engagement than follower-based platforms"},
                    {"ticker": "DV", "companyName": "DoubleVerify", "companyDescription": "Digital media measurement and verification platform ensuring ad quality and brand safety.", "role": "BENEFICIARY", "rationale": "DoubleVerify's ad verification tools become essential as brands demand proof of human audiences"}
                ]
            },
            {
                "id": "effect_deadinternet_tv_revival",
                "order": 2,
                "title": "Traditional TV Gets a Second Wind",
                "description": "Advertisers flee digital channels they can't trust and return to TV where human audiences are measurable. Linear TV ad rates stabilize after years of decline.",
                "initialTHI": 44,
                "equityBets": [
                    {"ticker": "PARA", "companyName": "Paramount Global", "companyDescription": "Media conglomerate owning CBS, Paramount+, MTV, and Nickelodeon. Broadcast reaches verified human audiences.", "role": "BENEFICIARY", "rationale": "Paramount's broadcast and cable assets become trusted human-audience inventory"},
                    {"ticker": "CMCSA", "companyName": "Comcast", "companyDescription": "Largest US cable company and parent of NBCUniversal and Peacock streaming. Controls verified audience infrastructure.", "role": "BENEFICIARY", "rationale": "Comcast's NBC and Peacock benefit from advertisers seeking verified human attention"},
                    {"ticker": "IAS", "companyName": "Integral Ad Science", "companyDescription": "Digital ad verification and brand safety platform measuring viewability, fraud, and brand suitability.", "role": "BENEFICIARY", "rationale": "Integral Ad Science verification tools become mandatory for every digital ad buy"}
                ]
            },
            {
                "id": "effect_deadinternet_seo_death",
                "order": 2,
                "title": "SEO Dies and Google Search Degrades",
                "description": "AI-generated content farms flood search results with optimized garbage. Google's search quality collapses, accelerating the shift to AI chatbots and curated platforms.",
                "initialTHI": 65,
                "equityBets": [
                    {"ticker": "GOOGL", "companyName": "Alphabet", "companyDescription": "Google's search quality degradation from AI content farms directly threatens its core business.", "role": "HEADWIND", "rationale": "Google search quality degradation directly threatens their core ad business"},
                    {"ticker": "RDDT", "companyName": "Reddit", "companyDescription": "Forum-based social platform. Users increasingly append 'reddit' to searches for authentic human answers.", "role": "BENEFICIARY", "rationale": "Reddit becomes the de facto search engine as people append 'reddit' to every query"},
                    {"ticker": "MSFT", "companyName": "Microsoft", "companyDescription": "Bing search engine with integrated Copilot AI. Positioned to capture share as Google trust erodes.", "role": "BENEFICIARY", "rationale": "Microsoft Bing with Copilot captures share as Google search trust erodes"}
                ]
            }
        ]
    }
]


def seed_database(db: Session):
    """Seed database if empty."""
    existing = db.query(Thesis).count()
    if existing > 0:
        print(f"Database already has {existing} theses. Skipping seed.")
        return

    print("Seeding database with 16 theses...")

    for i, td in enumerate(SEED_DATA):
        thesis = Thesis(
            id=td["id"],
            title=td["title"],
            subtitle=td["subtitle"],
            description=td["description"],
            time_horizon=td["timeHorizon"],
            tags=td["tags"],
            thi_score=td["initialTHI"],
            thi_direction="confirming" if td["initialTHI"] >= 60 else ("refuting" if td["initialTHI"] <= 40 else "neutral"),
            user_conviction_score=td["initialUserConviction"],
            display_order=i,
            evidence_score=td["initialTHI"],
            momentum_score=50.0,
            conviction_data_score=50.0,
        )
        db.add(thesis)
        db.flush()

        # THI snapshot
        db.add(THISnapshot(
            thesis_id=thesis.id,
            score=td["initialTHI"],
            evidence_score=td["initialTHI"],
            momentum_score=50.0,
            conviction_score=50.0,
        ))

        # Conviction snapshot
        db.add(ConvictionSnapshot(
            thesis_id=thesis.id,
            score=td["initialUserConviction"],
        ))

        # Feeds
        for fd in td.get("feeds", []):
            name = fd["id"].replace("_", " ").title()
            feed = DataFeed(
                id=fd["id"],
                thesis_id=thesis.id,
                name=name,
                source=fd["source"],
                source_type=fd["sourceType"],
                series_id=fd.get("seriesId"),
                keyword=fd.get("keyword"),
                ticker=fd.get("ticker"),
                confirming_direction=fd["confirmingDirection"],
                status="stale",
            )
            db.add(feed)

        # Equity bets
        for eb in td.get("equityBets", []):
            bet = EquityBet(
                thesis_id=thesis.id,
                ticker=eb["ticker"],
                company_name=eb.get("companyName", ""),
                company_description=eb.get("companyDescription", ""),
                role=eb["role"],
                rationale=eb["rationale"],
                is_feedback_indicator=eb.get("isFeedbackIndicator", False),
                feedback_weight=eb.get("feedbackWeight", 0.0),
            )
            db.add(bet)

        # Startup opportunities
        for so in td.get("startupOpportunities", []):
            opp = StartupOpportunity(
                thesis_id=thesis.id,
                name=so["name"],
                one_liner=so["oneLiner"],
                timing=so["timing"],
                time_horizon=so["timeHorizon"],
            )
            db.add(opp)

        # Effects
        for ef in td.get("effects", []):
            effect = Effect(
                id=ef["id"],
                thesis_id=thesis.id,
                order=ef["order"],
                title=ef["title"],
                description=ef["description"],
                thi_score=ef["initialTHI"],
                thi_direction="confirming" if ef["initialTHI"] >= 60 else ("refuting" if ef["initialTHI"] <= 40 else "neutral"),
            )
            db.add(effect)
            db.flush()

            for eb in ef.get("equityBets", []):
                bet = EquityBet(
                    effect_id=effect.id,
                    ticker=eb["ticker"],
                    company_name=eb.get("companyName", ""),
                    company_description=eb.get("companyDescription", ""),
                    role=eb["role"],
                    rationale=eb["rationale"],
                )
                db.add(bet)

    # Seed macro header with defaults
    db.add(MacroHeader(
        regime="NEUTRAL",
        ffr=None,
        ten_year_two_year_spread=None,
        vix=None,
    ))

    db.commit()
    print(f"Seeded {len(SEED_DATA)} theses successfully.")
