questions = [
  {
    "question": "What is the total investment amount in USD for hydrogen projects by technology type, excluding any projects with unknown investment amounts?",
    "title": "Total Investment by Technology",
    "SQL": "SELECT \"Technology\", SUM(\"Total Investment in USD\") AS total_investment_usd FROM hydrogen_project WHERE \"Total Investment in USD\" IS NOT NULL GROUP BY \"Technology\"",
    "explanation": {
      "data": "The focus is on aggregating the total investment amounts for different technology types used in hydrogen projects. Only projects with specified investment amounts are considered, ensuring data quality and relevance.",
      "assumption": "It's assumed that the investment amount is accurately recorded and updated. Projects with unspecified investment amounts are excluded, which may omit some technology types from the analysis.",
      "improvement": "Including fields that detail the project phase or progress could provide insights into how investment amounts correlate with project maturity."
    }
  },
  {
    "question": "Which country has the highest number of operational hydrogen fuel stations, and what is the total storage capacity?",
    "title": "Top Country by Hydrogen Fuel Stations",
    "SQL": "SELECT pl.\"Country\", COUNT(*) AS station_count, SUM(CAST(isf.\"Storage Capacity (kg)\" AS INTEGER)) AS total_storage_capacity FROM international_fuelling_stations isf JOIN project_location pl ON isf.\"Ref\" = pl.\"Ref\" WHERE isf.\"Status\" = 'active' GROUP BY pl.\"Country\" ORDER BY station_count DESC, total_storage_capacity DESC LIMIT 1",
    "explanation": {
      "data": "This analysis identifies the country with the most operational hydrogen fuel stations, combining the number of stations and their total hydrogen storage capacity to provide a comprehensive view of infrastructure readiness.",
      "assumption": "It assumes that the storage capacity data is available and accurately recorded for all operational stations, which might not be the case.",
      "improvement": "Adding data fields related to station usage, such as average daily refuelings or customer visits, could offer deeper insights into station performance and demand."
    }
  },
  {
    "question": "What is the average fleet size for hydrogen-fueled vehicles by vehicle type, excluding prototypes?",
    "title": "Average Fleet Size by Vehicle Type",
    "SQL": "SELECT \"Vehicle Type\", AVG(\"Fleet Size\") AS average_fleet_size FROM hydrogen_fueled_vehicles WHERE \"Status\" != 'Planned' GROUP BY \"Vehicle Type\"",
    "explanation": {
      "data": "The query calculates the average number of vehicles for different types of hydrogen-fueled vehicles in active use, excluding those still in the planning stage to focus on currently operational vehicles.",
      "assumption": "This assumes that all vehicles counted in the fleet sizes are operational and not awaiting deployment, which might not always be the case.",
      "improvement": "Incorporating data on the operational status of each vehicle in the fleet could refine the accuracy of the average fleet size calculation."
    }
  },
  {
    "question": "How much funding in USD has been allocated to hydrogen projects by funding scheme, excluding projects without specified funding amounts?",
    "title": "Funding by Scheme",
    "SQL": "SELECT \"Scheme Name\", SUM(\"Funding Amount in USD\") AS total_funding_usd FROM hydrogen_project_finance_schemes WHERE \"Funding Amount in USD\" IS NOT NULL GROUP BY \"Scheme Name\"",
    "explanation": {
      "data": "This query aggregates funding amounts allocated to hydrogen projects for each funding scheme, focusing only on projects with specified funding amounts to ensure data accuracy.",
      "assumption": "Assumes that all funding amounts are current and reflect actual disbursements, which may not account for future funding commitments or adjustments.",
      "improvement": "Adding fields that detail the disbursement schedule or funding conditions could provide a more nuanced understanding of funding flows."
    }
  },
  {
    "question": "Which hydrogen projects have captured the most CO2 annually, and what are their associated technologies?",
    "title": "Top CO2 Capturing Projects",
    "SQL": "SELECT \"Project Name\", \"Technology\", \"t CO2 captured/y\" FROM hydrogen_project WHERE \"t CO2 captured/y\" IS NOT NULL ORDER BY \"t CO2 captured/y\" DESC LIMIT 5",
    "explanation": {
      "data": "The query highlights the top hydrogen projects in terms of annual CO2 capture, along with the technologies used, focusing on projects that have specified their CO2 capture amounts.",
      "assumption": "It assumes the CO2 capture data is accurately measured and reported, which may not include all forms of carbon capture or offsets associated with the project.",
      "improvement": "Integrating data on the lifecycle emissions of the projects, including upstream and downstream impacts, would offer a fuller picture of their environmental performance."
    }
  },
  {
    "question": "What is the total nominal power output at sites equipped with fuel cells in the US, categorized by fuel cell type?",
    "title": "Total Power by Fuel Cell Type",
    "SQL": "SELECT \"Fuel Cell Type\", SUM(\"Total Nominal Power at Site (kW)\") AS total_power_output FROM us_stationary_fuel_cells WHERE \"Total Nominal Power at Site (kW)\" IS NOT NULL GROUP BY \"Fuel Cell Type\"",
    "explanation": {
      "data": "The data is centered on summing up the power output capabilities of fuel cell sites in the United States, differentiated by the type of fuel cell technology they utilize. It only includes sites with specified power output data to ensure accuracy.",
      "assumption": "The assumption here is that the total nominal power output data is up-to-date and correctly attributed to the respective fuel cell types, potentially overlooking the dynamic nature of operational capabilities.",
      "improvement": "Enhancing the dataset with fields that capture operational efficiency, downtime, and maintenance schedules could offer a more detailed view of power output reliability and sustainability."
    }
  },
  {
    "question": "How many hydrogen projects per country are in the operational phase, and what's their average investment in USD?",
    "title": "Operational Projects and Investment by Country",
    "SQL": "SELECT pl.\"Country\", COUNT(*) AS project_count, AVG(hp.\"Total Investment in USD\") AS average_investment_usd FROM hydrogen_project hp JOIN project_location pl ON hp.\"Ref\" = pl.\"Ref\" WHERE hp.\"Status\" = 'Operational' GROUP BY pl.\"Country\"",
    "explanation": {
      "data": "This query identifies the number of hydrogen projects in the operational phase within each country, alongside the average investment poured into these projects, measured in USD. It specifically targets operational projects to gauge active engagement and investment landscape.",
      "assumption": "The underlying assumption is that the investment data is comprehensive and reflects the total investment until the operational phase, which may not account for ongoing or additional expenses post-commissioning.",
      "improvement": "Incorporating data on operational performance, such as production volumes, efficiency rates, or profitability, could further elucidate the return on investment for these projects."
    }
  },
  {
    "question": "What is the distribution of hydrogen project colors, and how do they compare in terms of average MWel capacity?",
    "title": "Hydrogen Color and MWel Capacity",
    "SQL": "SELECT \"Hydrogen Color\", COUNT(*) AS project_count, AVG(\"MWel\") AS average_mwel FROM hydrogen_project WHERE \"MWel\" IS NOT NULL GROUP BY \"Hydrogen Color\"",
    "explanation": {
      "data": "This query examines the distribution of hydrogen projects based on their color categorization, which signifies the production method and environmental impact, and compares these categories in terms of their average electrical output capacity measured in MWel. It filters out projects without MWel data to maintain data integrity.",
      "assumption": "It presumes that the MWel capacity is a reliable indicator of a project's scale and output potential, which may not fully account for the variability in operational efficiency or the actual environmental impact.",
      "improvement": "Augmenting the dataset with more granular data on carbon emissions, water usage, and land impact could offer a more comprehensive assessment of each project's environmental footprint."
    }
  },
  {
    "question": "Which hydrogen policies have the highest budgets, and what sectors do they target?",
    "title": "Top Policies by Budget",
    "SQL": "SELECT \"Policy Name\", \"Total Budget in USD\", \"Sectors\" FROM hydrogen_policy WHERE \"Total Budget in USD\" IS NOT NULL ORDER BY \"Total Budget in USD\" DESC LIMIT 5",
    "explanation": {
      "data": "This query ranks hydrogen-related policies based on their total allocated budgets in USD and identifies the sectors they aim to impact. It focuses on policies with specified budget amounts to ensure an accurate depiction of financial commitment.",
      "assumption": "The analysis assumes that the listed budget figures accurately reflect the funds allocated or spent, which may not consider future budget revisions or the actual disbursement of funds over time.",
      "improvement": "Enriching the dataset with additional fields that detail the policy outcomes, such as projects funded, technologies developed, or emissions reduced, could provide insights into the effectiveness of the budget expenditure."
    }
  },
  {
    "question": "What are the most common end uses for hydrogen projects, and what is their average funding amount in USD?",
    "title": "Common End Uses and Funding",
    "SQL": "SELECT \"End Use\", COUNT(*) AS project_count, AVG(hpfs.\"Funding Amount in USD\") AS average_funding_usd FROM hydrogen_project_enduse hpe JOIN hydrogen_project_finance_schemes hpfs ON hpe.\"Ref\" = hpfs.\"Ref\" GROUP BY \"End Use\"",
    "explanation": {
      "data": "The focus here is on identifying the most frequently cited end uses for hydrogen projects and analyzing them in the context of the average funding amount allocated, in USD terms. This approach aims to shed light on the priority areas within hydrogen applications and their financial backing.",
      "assumption": "Assumes that the funding amount data is accurately linked to the respective projects and their end uses, which may not capture the full scope of investment if multiple funding rounds or sources are involved.",
      "improvement": "Expanding the data to include the impact or outcomes achieved for each end-use category, such as emissions reduction, energy produced, or jobs created, could enhance the understanding of investment effectiveness."
    }
  },
  {
    "question": "Which investors have contributed the most funding to hydrogen projects, and in which countries are these projects located?",
    "title": "Top Investors and Project Countries",
    "SQL": "SELECT pi.\"Investor Name\", SUM(pi.\"Investment Amount in USD\") AS total_investment, pl.\"Country\" FROM project_investor pi JOIN project_location pl ON pi.\"Ref\" = pl.\"Ref\" GROUP BY pi.\"Investor Name\", pl.\"Country\" ORDER BY total_investment DESC LIMIT 5",
    "explanation": {
      "data": "This analysis identifies the investors contributing the most significant funding amounts to hydrogen projects and highlights the countries where these heavily funded projects are situated. It aims to reveal the geographical focus and financial commitment of leading investors in the hydrogen sector.",
      "assumption": "It's assumed that all investments are correctly recorded and attributed to the investors and countries, which might not account for indirect investments or investments in multinational projects.",
      "improvement": "Adding details about the type of investment (equity, debt, grants) and the specific project phases these investments support could provide insights into investment strategies and risk appetites."
    }
  },
  {
    "question": "How does the average investment in hydrogen projects vary between different hydrogen colors?",
    "title": "Investment Variation by Hydrogen Color",
    "SQL": "SELECT \"Hydrogen Color\", AVG(\"Total Investment in USD\") AS average_investment FROM hydrogen_project GROUP BY \"Hydrogen Color\"",
    "explanation": {
      "data": "This query examines how average financial investment in hydrogen projects varies across different 'colors' of hydrogen, which indicate the method of hydrogen production and its environmental impact. It seeks to understand if certain production methods attract more investment than others.",
      "assumption": "Assumes that the investment data is complete and accurately reflects the funds allocated to projects of different hydrogen colors, which may overlook unreported or misclassified investments.",
      "improvement": "Incorporating data on the return on investment (ROI) or economic performance of projects by hydrogen color could further elucidate the financial viability of different hydrogen production methods."
    }
  },
  {
    "question": "What is the total number of hydrogen fuel cell vehicles by vehicle type and their operational status?",
    "title": "Hydrogen Vehicles by Type and Status",
    "SQL": "SELECT \"Vehicle Type\", \"Status\", COUNT(*) AS vehicle_count FROM hydrogen_fueled_vehicles GROUP BY \"Vehicle Type\", \"Status\"",
    "explanation": {
      "data": "This query categorizes hydrogen fuel cell vehicles by their type and operational status, providing a comprehensive overview of the deployment and readiness of hydrogen vehicles in different categories. It aims to illustrate the current landscape of hydrogen mobility.",
      "assumption": "The assumption here is that the vehicle type and status are accurately recorded, which may not capture recent changes or the full complexity of operational readiness (e.g., vehicles undergoing testing).",
      "improvement": "Enhancing the dataset with fields related to vehicle performance, usage data (e.g., mileage, refueling frequency), and owner feedback could offer deeper insights into the practical aspects of hydrogen vehicle adoption."
    }
  },
  {
    "question": "What are the average and total capacities of hydrogen production (in Nm3 H2/h) across projects, broken down by hydrogen color?",
    "title": "Hydrogen Production Capacity by Color",
    "SQL": "SELECT \"Hydrogen Color\", AVG(\"Nm3 H2/h\") AS average_production_capacity, SUM(\"Nm3 H2/h\") AS total_production_capacity FROM hydrogen_project GROUP BY \"Hydrogen Color\"",
    "explanation": {
      "data": "This analysis focuses on the capacity for hydrogen production, measured in normal cubic meters per hour (Nm3 H2/h), across different hydrogen project colors. It aims to assess both the average and total production capacities, providing insight into the scale and efficiency of hydrogen production methods.",
      "assumption": "It is assumed that the production capacity data is accurately measured and reported, which might not reflect variations in operational efficiency or downtime that could affect actual production volumes.",
      "improvement": "Adding data on the utilization rate of production capacity and the cost of hydrogen production by project could help evaluate the economic efficiency and environmental benefits of different hydrogen colors."
    }
  },
  {
    "question": "How many hydrogen projects are utilizing carbon capture and storage (CCS) technology, and what is their average CO2 capture capacity?",
    "title": "Hydrogen Projects with CCS",
    "SQL": "SELECT COUNT(*) AS project_count, AVG(\"t CO2 captured/y\") AS average_co2_captured FROM hydrogen_project WHERE \"Technology\" LIKE '%CCUS%'",
    "explanation": {
      "data": "This query identifies the number of hydrogen projects incorporating Carbon Capture, Utilization, and Storage (CCUS) technologies and calculates the average annual CO2 capture capacity. It highlights the integration of carbon management strategies in hydrogen production.",
      "assumption": "The analysis presumes that all projects listed with CCUS technologies are actively utilizing them for CO2 capture, which may not consider the full lifecycle of the project or the operational efficiency of the capture technology.",
      "improvement": "To refine the dataset, including details on the specific type of CCUS technology used (e.g., pre-combustion, post-combustion, oxy-fuel combustion) and data on the fate of the captured CO2 (e.g., storage, utilization) could provide a more nuanced view of the projects' environmental impact."
    }
  },
  {
    "question": "What is the distribution of hydrogen projects by feedstock type, and how does the average investment in USD vary among them?",
    "title": "Hydrogen Projects by Feedstock and Investment",
    "SQL": "SELECT \"Feedstock\", COUNT(*) AS project_count, AVG(\"Total Investment in USD\") AS average_investment FROM hydrogen_project GROUP BY \"Feedstock\"",
    "explanation": {
      "data": "The query investigates hydrogen projects based on the type of feedstock used for hydrogen production, providing insights into the prevalence of different feedstock types and the average financial investment associated with each. It aims to understand the economic considerations and priorities in feedstock selection for hydrogen production.",
      "assumption": "It assumes that the classification of projects by feedstock and the reported investment figures are accurate, not accounting for potential discrepancies in reporting or classification.",
      "improvement": "Enhancing the dataset with information on the efficiency and sustainability of different feedstock types could offer a more comprehensive perspective on the trade-offs involved in feedstock selection."
    }
  },
  {
    "question": "Which countries have implemented the most hydrogen policies, and what is the focus of these policies?",
    "title": "Hydrogen Policies by Country and Focus",
    "SQL": "SELECT \"Country\", COUNT(*) AS policy_count, STRING_AGG(DISTINCT \"Sectors\", ', ') AS sectors_focused FROM hydrogen_policy GROUP BY \"Country\" ORDER BY policy_count DESC LIMIT 5",
    "explanation": {
      "data": "This analysis ranks countries by the number of hydrogen-related policies they have implemented and summarizes the sectors these policies primarily focus on. It aims to highlight the policy landscape for hydrogen across different nations and identify key areas of policy emphasis.",
      "assumption": "Assumes that the policy count and sector focus are comprehensively recorded, potentially overlooking nuanced policy objectives or emerging policy areas not yet categorized.",
      "improvement": "Incorporating outcome measures or effectiveness assessments of these policies could provide insights into their impact and guide future policy development."
    }
  },
  {
    "question": "How has the total investment in hydrogen projects evolved over the last decade?",
    "title": "Investment Trend in Hydrogen Projects",
    "SQL": "SELECT EXTRACT(YEAR FROM \"Date Online\") AS year, SUM(\"Total Investment in USD\") AS total_investment FROM hydrogen_project WHERE \"Date Online\" >= (CURRENT_DATE - INTERVAL '10 years') GROUP BY year ORDER BY year",
    "explanation": {
      "data": "This query tracks the annual total investment in USD for hydrogen projects over the past decade, aiming to identify trends in investment levels over time. It provides insights into how the hydrogen sector's attractiveness to investors has changed.",
      "assumption": "The analysis assumes that all relevant projects have accurately reported both their investment figures and the dates they came online, which may not include delayed or unreported investments.",
      "improvement": "Adding granularity to the investment data, such as distinguishing between public and private sector investments or highlighting significant investment spikes due to policy changes, could enhance the understanding of investment dynamics."
    }
  },
  {
    "question": "What are the common characteristics of hydrogen projects that have secured the highest amounts of funding?",
    "title": "Characteristics of Highly Funded Hydrogen Projects",
    "SQL": "SELECT \"Technology\", \"Feedstock\", \"Hydrogen Color\", AVG(\"Total Investment in USD\") AS average_investment FROM hydrogen_project GROUP BY \"Technology\", \"Feedstock\", \"Hydrogen Color\" ORDER BY average_investment DESC LIMIT 5",
    "explanation": {
      "data": "This query examines hydrogen projects by technology, feedstock, and hydrogen color to identify common characteristics among those that have received the highest average investments. It aims to uncover patterns or preferences in funding allocation within the hydrogen sector.",
      "assumption": "It assumes that the reported investment figures accurately reflect the financial backing for the projects, which may not capture all forms of financial support or in-kind contributions.",
      "improvement": "Enriching the dataset with details on the projects' geographic locations, stages of development, or specific environmental impacts could provide deeper insights into the factors influencing investment decisions."
    }
  },
  ]