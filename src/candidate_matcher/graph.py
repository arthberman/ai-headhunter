from typing import Set

from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from candidate_matcher.analysis.graph import get_analysis_graph
from candidate_matcher.configuration import Configuration
from candidate_matcher.enrichment.education import node_education_enrichment
from candidate_matcher.enrichment.experience import node_experience_enrichment
from candidate_matcher.enrichment.language import node_language_enrichment
from candidate_matcher.models.profile import Profile
from candidate_matcher.state import InputGraphState, MainGraphState
from candidate_matcher.synthesis.node import node_synthesis
from scorecard_generator.models.scorecard import Scorecard
from utils.parse_profile import parse_profile


def continue_to_school_enrichment(state: MainGraphState):
    """Continue to school enrichment."""
    if state.profile.educations:
        # Use a set to keep track of unique (school, linkedin_url) pairs
        unique_schools: Set[tuple] = set()
        enrichment_tasks = []

        for e in state.profile.educations:
            school_key = (e.school, e.linkedin_url)
            if school_key not in unique_schools:
                unique_schools.add(school_key)
                enrichment_tasks.append(
                    Send(
                        "node_education_enrichment",
                        {"education": e},
                    )
                )

        return enrichment_tasks if enrichment_tasks else "init_analysis"
    else:
        return "init_analysis"


def continue_to_company_enrichment(state: MainGraphState):
    """Continue to company enrichment."""
    if state.profile.experiences:
        # Use a set to keep track of unique (company, linkedin_url) pairs
        unique_companies: Set[tuple] = set()
        enrichment_tasks = []

        for e in state.profile.experiences:
            company_key = (e.company, e.linkedin_url)
            if company_key not in unique_companies:
                unique_companies.add(company_key)
                enrichment_tasks.append(
                    Send(
                        "node_experience_enrichment",
                        {"experience": e},
                    )
                )

        return enrichment_tasks if enrichment_tasks else "init_analysis"
    else:
        return "init_analysis"


def init_node(state: MainGraphState) -> MainGraphState:
    """Initialize the node."""
    profile_json = {
        "id": "f2d18a3c-0229-4198-b108-7b184397d93c",
        "firstName": "Alexandre",
        "lastName": "Pages",
        "fullName": "Alexandre Pages",
        "country": "France",
        "city": "Greater Paris Metropolitan Region",
        "state": None,
        "headline": "Co-founder & CEO at explorz",
        "summary": "",
        "createdAt": "2024-08-16T13:49:04.611Z",
        "updatedAt": "2024-08-16T13:49:04.939Z",
        "scrapProvider": "RAPIDAPI",
        "connectionCount": None,
        "followersCount": None,
        "isCreator": None,
        "isHiring": None,
        "isOpenToWork": None,
        "linkedin_id": "alexandrepages42",
        "linkedin_urn": "ACoAABoYfUQB0yVR8xIBvKEzMZrD6d6iR2vtVEg",
        "skills": [
            "Unix",
            "C",
            "Git",
            "PHP",
            "MySQL",
            "JavaScript",
            "Node.js",
            "HTML",
            "AngularJS",
            "MVC",
        ],
        "avatarId": "3e470aa1-80fc-4880-9be4-055a92306865",
        "experiences": [
            {
                "id": "9bd13c98-23e3-44a4-a611-aae3cc91fa3f",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2015-01-30T23:00:00.000Z",
                "endsAt": "2015-02-27T23:00:00.000Z",
                "companyId": "66c89c54-ca82-4609-b4b8-e4fd71e7dbce",
                "title": "Developer Intern",
                "description": "I joined Pandacraft as an intern, acting as the CTO's right-hand man.\n\nMy main missions were the following:\n\n- Built an internal monitoring module using NodeJS \n- Created internal tools to improve our weekly emailing processes\n- Implemented various features in Magento (using PHP)",
                "location": "France",
                "company": {
                    "id": "66c89c54-ca82-4609-b4b8-e4fd71e7dbce",
                    "name": "Pandacraft",
                    "linkedinUrl": "https://www.linkedin.com/company/pandacraft/",
                    "linkedinId": None,
                    "logoId": "efa8f2de-2252-439e-9145-9b20cd3dbfe4",
                },
            },
            {
                "id": "cc35966b-3369-48ff-8041-1144fd44c429",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2016-02-28T23:00:00.000Z",
                "endsAt": "2016-07-30T22:00:00.000Z",
                "companyId": "8b317d37-f73c-4e50-90d5-3749e6cd4ce1",
                "title": "Lead Developer",
                "description": "Participated in the launch of a startup within the HEC launchpad program.\n\n- Refined our customer segmentation through detailed analysis.\n- Created Fresq's MVP (NodeJS, Angular)\n- In charge of setting up the tech infrastructure",
                "location": "Paris",
                "company": {
                    "id": "8b317d37-f73c-4e50-90d5-3749e6cd4ce1",
                    "name": "Fresq",
                    "linkedinUrl": "https://www.linkedin.com/company/fresq/",
                    "linkedinId": None,
                    "logoId": "152f3daa-d4d6-4b71-b64f-06b187448fe5",
                },
            },
            {
                "id": "ffe368a4-4d38-4145-8620-fcafc0a812de",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2016-08-30T22:00:00.000Z",
                "endsAt": "2018-12-30T23:00:00.000Z",
                "companyId": "6db3b1bf-ea14-478e-84cd-975ed529b53b",
                "title": "Lead Developer",
                "description": "- Created the intranet from scratch for Station F (billing, desk booking, users' profiles, visitor registration, event management, meeting rooms bookings, perks, KPI dashboard)\n- Managed building access control with over 10000 access cards per year\n- Handled STATION F servers (more than 50 virtual machines)",
                "location": "Paris Area, France",
                "company": {
                    "id": "6db3b1bf-ea14-478e-84cd-975ed529b53b",
                    "name": "STATION F / Halle Freyssinet",
                    "linkedinUrl": "https://www.linkedin.com/company/stationf/",
                    "linkedinId": None,
                    "logoId": "a49e747e-5379-48d7-bca2-f40e84083332",
                },
            },
            {
                "id": "ffa32fc5-37c1-4d5b-935a-70d037c3b2d1",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2018-12-30T23:00:00.000Z",
                "endsAt": "2021-09-29T22:00:00.000Z",
                "companyId": "6db3b1bf-ea14-478e-84cd-975ed529b53b",
                "title": "Head of Tech/IT (CTO)",
                "description": "Part of STATION F founding team & oversaw STATION F's entire tech team (~10 engineers)",
                "location": "Région de Paris, France",
                "company": {
                    "id": "6db3b1bf-ea14-478e-84cd-975ed529b53b",
                    "name": "STATION F / Halle Freyssinet",
                    "linkedinUrl": "https://www.linkedin.com/company/stationf/",
                    "linkedinId": None,
                    "logoId": "a49e747e-5379-48d7-bca2-f40e84083332",
                },
            },
            {
                "id": "7433a066-afdc-47f7-a754-2dde3299ad02",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2022-06-29T22:00:00.000Z",
                "endsAt": "2022-06-29T22:00:00.000Z",
                "companyId": "75165f63-22f1-4461-b611-ea16a11572f3",
                "title": "Investor",
                "description": "Empowering investors to achieve their dreams of financial independence",
                "location": "",
                "company": {
                    "id": "75165f63-22f1-4461-b611-ea16a11572f3",
                    "name": "Finary",
                    "linkedinUrl": "https://www.linkedin.com/company/finaryhq/",
                    "linkedinId": None,
                    "logoId": "e5e63eda-6fc0-49d0-a3bd-69e45e1eeee5",
                },
            },
            {
                "id": "ac6048d3-233a-40b9-9bbe-d661b254c813",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2023-06-29T22:00:00.000Z",
                "endsAt": "2023-06-29T22:00:00.000Z",
                "companyId": "9c813b2e-30ba-475e-8aa0-edc3f3736144",
                "title": "Investor",
                "description": "",
                "location": "",
                "company": {
                    "id": "9c813b2e-30ba-475e-8aa0-edc3f3736144",
                    "name": "Gens de Confiance",
                    "linkedinUrl": "https://www.linkedin.com/company/gensdeconfiance/",
                    "linkedinId": None,
                    "logoId": "29a9b7f0-a3c4-4b7f-8642-9a724735ca44",
                },
            },
            {
                "id": "055829c1-1984-4eed-b827-668869310776",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2023-01-30T23:00:00.000Z",
                "endsAt": "1899-12-30T23:50:39.000Z",
                "companyId": "49929cfa-6a2a-4eb6-a5da-8225449a8e3e",
                "title": "Co-founder & CEO",
                "description": "explorz is the app to stop scrolling and have fun outside with your friends 💜",
                "location": "",
                "company": {
                    "id": "49929cfa-6a2a-4eb6-a5da-8225449a8e3e",
                    "name": "explorz",
                    "linkedinUrl": "https://www.linkedin.com/company/explorz/",
                    "linkedinId": None,
                    "logoId": "3734cb5c-ea8d-499e-8699-d9c98cc5055d",
                },
            },
        ],
        "educations": [
            {
                "id": "bdf1fae4-3692-4fad-bd81-78b96cbd4cf8",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2018-12-30T23:00:00.000Z",
                "endsAt": "2018-12-30T23:00:00.000Z",
                "schoolId": "eda8c3b9-9dd9-44dd-a443-f4e85d6c7fe3",
                "description": "Full training to understand the start-up world & develop the key competencies to succeed. Hefty focus on the new jobs within this ecosystem (Product Management, Growth Hacking, Intrapreneur, etc.)",
                "fieldOfStudy": "",
                "grade": "",
                "degree": "",
                "school": {
                    "id": "eda8c3b9-9dd9-44dd-a443-f4e85d6c7fe3",
                    "name": "Join Lion",
                    "linkedinUrl": "https://www.linkedin.com/school/joinlion/",
                    "linkedinId": "10783802",
                    "logoId": None,
                },
            },
            {
                "id": "7171919f-8abb-4707-8fe6-67893671618a",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2014-12-30T23:00:00.000Z",
                "endsAt": "1899-12-30T23:50:39.000Z",
                "schoolId": "902b2406-9119-4e69-aae5-5343df5f9373",
                "description": "",
                "fieldOfStudy": "",
                "grade": "",
                "degree": "HEC launchpad",
                "school": {
                    "id": "902b2406-9119-4e69-aae5-5343df5f9373",
                    "name": "HEC Paris",
                    "linkedinUrl": "https://www.linkedin.com/school/hec-paris/",
                    "linkedinId": "235785",
                    "logoId": None,
                },
            },
            {
                "id": "195d1029-640f-485f-8d32-2d9e5c3bd479",
                "createdAt": "2024-08-16T13:49:04.611Z",
                "updatedAt": "2024-08-16T13:49:04.611Z",
                "ProfileId": "f2d18a3c-0229-4198-b108-7b184397d93c",
                "startsAt": "2014-12-30T23:00:00.000Z",
                "endsAt": "2015-12-30T23:00:00.000Z",
                "schoolId": "16adc77b-9842-4a56-9e4b-225e4d6926aa",
                "description": "42's pedagogy is based on peer-to-peer learning: a participatory approach, without courses or teachers, that allows students to unleash their creativity through project-based learning.\n\nDuring my time I led the total rebuild of 42's Food truck website that enabled all students to order food. The website handled more than 700 orders per day.",
                "fieldOfStudy": "",
                "grade": "Level 21",
                "degree": "Engineer's Degree",
                "school": {
                    "id": "16adc77b-9842-4a56-9e4b-225e4d6926aa",
                    "name": "42",
                    "linkedinUrl": "https://www.linkedin.com/school/42born2code/",
                    "linkedinId": "2354401",
                    "logoId": None,
                },
            },
        ],
    }
    profile: Profile = parse_profile(profile_json)

    scorecard_json = {
        "mustHaveCriteria": [
            {
                "id": None,
                "type": "EXPERIENCE",
                "context": "Given Ynstant's startup nature and focus on real-time carpooling, experience in a Consumer startup that raised more than $100k in funding is crucial. This criteria should be strictly followed",
                "description": "Minimum of 1 year of experience in a Consumer startup that raised more than $100k in funding.",
                "distribution_params": None,
                "scoring_distribution": "CONTINUOUS",
            }
        ],
        "importantCriteria": [
            {
                "id": None,
                "type": "HARD_SKILL",
                "context": "Automation skills are valuable for reducing manual workload and increasing efficiency in handling CEE files, aligning with Ynstant's innovative approach to operations.",
                "description": "Experience with automation tools or scripting to streamline processes.",
                "distribution_params": {
                    "Basic": 0.3,
                    "Advanced": 0.9,
                    "Intermediate": 0.6,
                },
                "scoring_distribution": "ORDINAL",
            }
        ],
        "niceToHaveCriteria": [
            {
                "id": None,
                "type": "INDUSTRY_KNOWLEDGE",
                "context": "Experience in the mobility sector, especially in a startup, provides valuable insights into the challenges and opportunities of developing innovative transportation solutions like Ynstant's carpooling app.",
                "description": "Experience in a startup environment, particularly in the mobility sector.",
                "distribution_params": None,
                "scoring_distribution": "GAUSSIAN",
            }
        ],
    }
    scorecard: Scorecard = Scorecard.model_validate(scorecard_json)

    return {"profile": profile, "scorecard": scorecard}


def continue_to_analysis(state: MainGraphState):
    """Continue to the analysis graph."""
    all_criteria = (
        state.scorecard.mustHaveCriteria
        + state.scorecard.importantCriteria
        + state.scorecard.niceToHaveCriteria
    )
    return [
        Send(
            "node_analysis",
            {"main_state": state, "messages": [], "criterion": criterion},
        )
        for criterion in all_criteria
    ]


def init_analysis(state: MainGraphState) -> MainGraphState:
    """BLANK : Initialize the analysis graph."""
    return state


def compile_candidate_matcher_graph() -> CompiledGraph:
    """Compile the candidate matcher graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node("init_node", init_node)
    workflow.add_node("node_language_enrichment", node_language_enrichment)
    workflow.add_node("node_education_enrichment", node_education_enrichment)
    workflow.add_node("node_experience_enrichment", node_experience_enrichment)
    workflow.add_node(
        "node_analysis",
        get_analysis_graph(),
    )
    workflow.add_node("init_analysis", init_analysis)
    workflow.add_node("node_synthesis", node_synthesis)

    workflow.add_edge(START, "init_node")

    workflow.add_conditional_edges(
        "init_node",
        continue_to_school_enrichment,
        ["node_education_enrichment", "init_analysis"],
    )
    workflow.add_conditional_edges(
        "init_node",
        continue_to_company_enrichment,
        ["node_experience_enrichment", "init_analysis"],
    )
    workflow.add_edge("init_node", "node_language_enrichment")
    workflow.add_edge(
        [
            "node_experience_enrichment",
            "node_education_enrichment",
            "node_language_enrichment",
        ],
        "init_analysis",
    )

    workflow.add_conditional_edges(
        "init_analysis", continue_to_analysis, ["node_analysis"]
    )
    workflow.add_edge("node_analysis", "node_synthesis")
    workflow.add_edge("node_synthesis", END)

    graph = workflow.compile()
    graph.name = "CandidateMatcherGraph"
    return graph
