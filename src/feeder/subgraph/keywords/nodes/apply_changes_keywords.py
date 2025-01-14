from trustcall import create_extractor

from feeder.models.raw_query import RawQuery
from feeder.utils.init_model import init_model
from feeder.subgraph.keywords.state import KeywordsState


def apply_changes_keywords(state: KeywordsState) -> KeywordsState:
    """Apply changes to the keywords based on the feedback of the judge."""
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    extractor = create_extractor(llm, tools=[RawQuery])
    trustcall_result = extractor.invoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": """
                    You are a Human Resources expert tasked with sourcing candidates using Boolean queries on Linkedin Sales Navigator. Your specific task is to update the "keywords" list from the provided JSON object based on feedback previously given by a judge.

                    <instructions>
                    1. Review all the feedbacks given by the judge. 
                    2. Review the job offer description in order to understand the main role and skills required for the job.
                    3. Update the "keywords" list based on the feedbacks of the judge.
                    </instructions>

                    <guidelines>
                    1. Only the keywords concerned by a feedback should be removed from the "keywords" list. 
                    2. If a feedback is not related to an existing keyword, ignore it.
                    3. Never add or modify something that is not mentioned in the feedbacks.

                    </guidelines>
                    <few_shot_examples>
                    <few_shot_1>
                    INPUT: 
                    - feedback_judge: "- Role Alignment Issue: "Flutter Specialist for ninja minigames" - Detected role focused on a niche area (ninja minigames) that does not align with the broader app development and leadership responsibilities described in the job summary."
                    - include: ["Senior Software Engineer", "Senior Mobile Engineer", "Senior Flutter Developer", "Mobile Engineer", "Flutter Specialist for ninja minigames"]
                    <bad>
                    BAD OUTPUT:
                    ["Senior Mobile Engineer", "Senior Flutter Developer", "Mobile Engineer"]
                    EXPLANATION: 
                    This output doesn't respect the guideline #1 and is problematic because it: 
                    - Removes a job title that is not concerned by the feedback ("Senior Software Engineer" have been removed without being mentioned in the feedback of the judge)
                    </bad>
                    <good>
                    GOOD OUTPUT:
                    ["Senior Software Engineer", "Senior Mobile Engineer", "Senior Flutter Developer", "Mobile Engineer"]
                    EXPLANATION:
                    This output respects the guideline #1 and is correct because it ONLY removes the job title "Flutter Specialist for ninja minigames" which is concerned by the feedback of the judge while preserving all the other job titles.
                    </good>
                    </few_shot_1>

                    <few_shot_2>
                    INPUT: 
                    - feedback_judge: "- Role Alignment Issue: "Junior Developer" are too junior for this senior position that requires 5+ years of experience. - Role Alignment Issue: "Entry Level Engineer" are too junior for this senior position that requires 5+ years of experience."
                    - include: ["Senior Software Engineer", "Lead Developer", "Software Architect"]

                    <bad>
                    BAD OUTPUT: 
                    ["Senior Software Engineer", "Lead Developer", "Software Architect", "Junior Developer", "Entry Level Engineer"]
                    EXPLANATION: 
                    This output doesn't respect the guideline #2 and is problematic because it: 
                    - Adds job titles mentioned in the feedback of the judge ("Junior Developer", "Entry Level Engineer") that are not in the existing "in job titles" list
                    </bad>
                    <good>
                    GOOD OUTPUT:
                    - include: ["Senior Software Engineer", "Lead Developer", "Software Architect"]
                    EXPLANATION:
                    This output respects the guideline #2 and is correct because job titles mentioned in the feedback of the judge ("Junior Developer", "Entry Level Engineer") that are not in the existing "in job titles" list are ignored. 
                    </good>
                    </few_shot_2>

                    <few_shot_3>
                    INPUT:
                    - feedback_judge: "- Role Alignment Issue: 'Social Media Guru' and 'Content Wizard' use informal language that doesn't fit common linkedin job titles.
                    - include: ["Digital Marketing Manager", "Social Media Manager", "Social Media Guru", "Content Wizard", "SEO Specialist", "Marketing Strategist"]
        
                    <bad>
                    BAD OUTPUT:
                    ["Digital Marketing Manager", "Social Media Manager", "SEO Specialist", "Marketing Strategist", "Content Creator"]
                    EXPLANATION:
                    This output doesn't respect the guideline #3 and is problematic because it:
                    - Adds a job title ("Content Creator") that is not mentioned in the feedback of the judge
                    </bad>
                    <good>
                    GOOD OUTPUT: 
                    ["Digital Marketing Manager", "Social Media Manager", "SEO Specialist", "Marketing Strategist"]
                    This output respects the guideline #3 and is correct because no other job titles are added or removed from the "in job titles" list except ones from the feedbacks.
                    </few_shot_examples>
                    """,
                },
                {
                    "role": "user",
                    "content": f"""
                    Begin! 

                    <json_object>
                    {state.json_object.keywords}
                    </json_object>

                    <feedback_judge>
                    {state.feedback_judge}
                    </feedback_judge>
                    """,
                },
            ],
            "existing": {"RawQuery": state.json_object.model_dump()},
        }
    )
    out = RawQuery.model_validate(trustcall_result["responses"][0].model_dump())
    state.json_object.keywords = out.keywords
    return state
