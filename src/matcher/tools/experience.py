import os
from datetime import datetime, timedelta

from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from matcher.models.company import CompanyInfo

tavily_tool = TavilySearchResults(max_results=3)
tools = [tavily_tool]


class CompanyDatabase:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.collection_name = "companies"
        self.vector_store = PGVector(
            connection=self.connection_string,
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            use_jsonb=True,
        )

        self.vector_store.create_tables_if_not_exists()
        self.vector_store.create_collection()

    def _create_company_document(self, company_info: CompanyInfo) -> Document:
        content = company_info.description
        return Document(
            page_content=content,
            metadata={
                "linkedin_url": company_info.linkedin_url,
                "name": company_info.name,
                "sectors": company_info.sectors,
                "company_stage": company_info.company_stage,
                "last_updated": datetime.now().isoformat(),
            },
        )

    def get_company_info(self, name: str, linkedin_url: str):
        results = self.vector_store.similarity_search(
            name, k=1, filter={"linkedin_url": {"$eq": linkedin_url}}
        )

        if results:
            doc = results[0]
            last_updated = doc.metadata.get("last_updated")
            if last_updated:
                last_updated = datetime.fromisoformat(last_updated)
                if datetime.now() - last_updated < timedelta(days=90):
                    company_info = CompanyInfo(
                        name=doc.metadata.get("name"),
                        linkedin_url=doc.metadata.get("linkedin_url"),
                        sectors=doc.metadata.get("sectors"),
                        company_stage=doc.metadata.get("company_stage"),
                        description=doc.page_content,
                    )
                    return company_info
        return None

    def update_company_info(self, company_info: CompanyInfo):
        self.vector_store.delete(
            filter={"linkedin_url": {"$eq": company_info.linkedin_url}}
        )
        document = self._create_company_document(company_info)
        self.vector_store.add_documents([document])


# Initialize database
db = CompanyDatabase()


# Define functions
def get_company(name: str, linkedin_url: str) -> CompanyInfo:
    """Query the company database for information about a specific company."""

    result = db.get_company_info(name, linkedin_url)
    if result:
        return result
    return None


def update_company(company_info: CompanyInfo) -> str:
    """Update the company database with new information about a specific company.
    Don't call this tool if the data is already up-to-date from the database."""

    if not company_info.linkedin_url:
        return

    db.update_company_info(company_info)
    return f"Updated database entry for {company_info.name}"
