ROUTER_TEMPLATE = """
You are the router to classify the question as being about financial reports or information in the handbook.

If the question is about year revenue reports:
Identify year and product name, and format as: year_product_name (example: 2024_GoPro_Hero_12_Black)

Follow this example return format:
{{
    "revenue_report": [
        "2024_GoPro_Hero_12_Black"
    ]
}}

If the question is in quarter reports:
Identify: month, year, quarter (example: May_2023_Q2, Jun_2019_Q1).  
If the question refers to multiple years or months, return all values.

Follow this example format:
{{
    "quarter_report": [
        "Jun_2019_Q1",
        "May_2023_Q2"
    ]
}}

If the question is in handbook, classify based on the list below:
[
    "basic_data",
    "policy_general_regulation",
    "policy_recruitment",
    "policy_probation",
    "policy_introduction"
]

Follow this example format:
{{
    "handbook": [
        "policy_probation",
        "policy_introduction"
    ]
}}

Question: {question}

Only return JSON in the formats above.
"""

SUMMARY_GREMLIN_TEMPLATE = """
Please summarize the JSON data below based on the question in plain text:
Question: {question}
Data: {data}

Only return the summarized content.
"""

SUMMARY_QUESTION = """
Given a user’s original question, infer the intended meaning and rewrite the question so that it becomes clear, complete, and aligned with one of the following three categories:

1. Company Handbook & Policies
   - Must specify which policy type the user is asking about.
   - Valid types: "basic_data", "policy_general_regulation", "policy_recruitment", "policy_probation", "policy_introduction".

2. Quarter Report Information
   - The rewritten question must explicitly include year, month, and quarter (Q1–Q4).

3. Revenue Report Information
   - The rewritten question must explicitly include both product name and year.

Instructions:
1. Infer what the user intends from the original question.
2. Rewrite it so that it contains all required fields for the correct category.
3. The rewritten question must be unambiguous, specific, and fully compliant with data requirements.

Question: {question}

Output Format:
Only provide the rewritten, clarified question in English.
"""
