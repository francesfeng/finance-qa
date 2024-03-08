questions = [
    {
        "question": "How much capacity for hydrogen's application for each end use, display by years as 2020s, 2030s, 2040s",
        "title": "Hydrogen application by capacity: 2020's - 2040's",
        "SQL": """SELECT CASE WHEN EXTRACT(YEAR FROM "Date Online") < 2030 THEN '2020s' WHEN EXTRACT(YEAR FROM "Date Online") < 2040 THEN '2030s' ELSE '2040s' END AS "Decade", "End Use", ROUND(SUM("MWel")::NUMERIC,2) AS "Total Capacity" FROM "hydrogen_project" JOIN "hydrogen_project_enduse" ON "hydrogen_project"."Ref" = "hydrogen_project_enduse"."Ref" WHERE "MWel" IS NOT NULL GROUP BY "Decade", "End Use" ORDER BY "Decade", "End Use""",
        "explanation": {
            "data": "The data shows the total capacity for hydrogen's application for each end use, categorized by decades starting from the 2020s. The total capacity is measured in megawatts of electricity (MWel), which is a unit of power representing one million watts of electrical power. The data is grouped by the decade in which the hydrogen projects came online and by the specific end use of the hydrogen.",
            "assumption": "The assumption is that the capacity for hydrogen's application is represented by the 'MWel' data field. The decades are determined based on the year the project came online, and it is assumed that the projects are distributed into three decades: 2020s, 2030s, and 2040s. Projects coming online before 2030 are categorized as '2020s', those coming online before 2040 are categorized as '2030s', and all others are assumed to be '2040s'.",
            "improvement": "To provide more detailed insights, additional data fields such as the actual year the project came online, the projected lifespan of the project, and the geographic location could be included. This would allow for a more granular analysis of the capacity over time and by region.",
      },
    },
    {
        "question": "What is the capacity for each technology used for hydrogen projects that are in operational stage?",
        "title": "Hydrogen project capacities by technology - operational",
        "SQL": """SELECT "Technology", ROUND(SUM("MWel")::NUMERIC, 2) AS total_capacity FROM "hydrogen_project" WHERE "Status" = 'Operational' AND "MWel" IS NOT NULL GROUP BY "Technology""",
        "explanation": {
            "data": "The data focuses on the technology used in hydrogen projects and the total electrical capacity in megawatts for each technology. Only projects that are currently operational are considered, and any projects without a specified capacity are excluded from the sum.",
            "assumption": "The assumption is that 'capacity' refers to the electrical capacity, which is represented by the 'MWel' data field. If capacity could also refer to hydrogen production in normal cubic meters per hour or kilotons per year, these data fields are not included in the current data.",
            "improvement": "To provide a more comprehensive view of capacity, additional data fields such as hydrogen production rate and annual production could be included in the output. This would allow for a more detailed analysis of the operational capabilities of each technology.",
        }
    },
    {
        "question": "List the hydrogen capacity by status and countries, only provide the top 20 countries by capacity",
        "title": "Top countries by hydrogen capacity and status",
        "SQL": """WITH projects as (
              SELECT "project_location"."Country", "hydrogen_project"."Status", ROUND(SUM("hydrogen_project"."MWel")::NUMERIC, 2) AS total_capacity 
              FROM "hydrogen_project" JOIN "project_location" ON "hydrogen_project"."Ref" = "project_location"."Ref" 
              WHERE "hydrogen_project"."MWel" IS NOT NULL AND ("project_location"."Country" <> 'Mauritania' AND "project_location"."Country" <> 'Kazakhstan')
              GROUP BY "project_location"."Country", "hydrogen_project"."Status" ORDER BY total_capacity 
              )

              SELECT * FROM projects WHERE "Country" IN (SELECT "Country" FROM (
                SELECT "Country", SUM(total_capacity) AS "Total Capacity" 
                FROM projects GROUP BY 1 ORDER BY "Total Capacity" DESC LIMIT 20 ) AS countries)""",
        "explanation": {
            "data": "The data includes a list of countries and the status of hydrogen projects, along with the total hydrogen capacity measured in megawatts electrical (MWel) for each status and country. The total capacity is a sum of the individual capacities of hydrogen projects, and only the top 20 countries with the highest total capacity are provided.",
            "assumption": "The assumption is that the capacity of hydrogen projects is measured in megawatts electrical (MWel), and that the data is grouped by the status of the projects and the countries they are located in. The query does not differentiate between different types of statuses within a country; it sums up all capacities for each status and country combination.",
            "improvement": "To provide more detailed insights, additional data fields such as the year of commissioning, the specific technology used, or the hydrogen color could be included. This would allow for a more granular analysis of the hydrogen capacity by different factors, such as the evolution of capacity over time or the prevalence of certain technologies or hydrogen types in top countries.",
        }
    },
]