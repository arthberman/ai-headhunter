import os
from datetime import datetime, timedelta

from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector

from matcher.models.school import SchoolInfo

tavily_tool = TavilySearchResults(max_results=3)
tools = [tavily_tool]


class SchoolDatabase:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.collection_name = "schools2"
        self.vector_store = PGVector(
            connection=self.connection_string,
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            use_jsonb=True,
        )

        self.vector_store.create_tables_if_not_exists()
        self.vector_store.create_collection()

    def _create_school_document(self, school_info: SchoolInfo) -> Document:
        content = school_info.description
        return Document(
            page_content=content,
            metadata={
                "linkedin_url": school_info.linkedin_url,
                "name": school_info.name,
                "description": school_info.description,
                "ranking": school_info.ranking,
                "fields": school_info.fields,
                "last_updated": datetime.now().isoformat(),
            },
        )

    def get_school_info(self, name: str, linkedin_url: str):
        results = self.vector_store.similarity_search(
            query=name,
            k=1,
            filter={"linkedin_url": {"$eq": linkedin_url}, "name": {"$eq": name}},
        )
        if results:
            doc = results[0]
            last_updated = doc.metadata.get("last_updated")
            if last_updated:
                last_updated = datetime.fromisoformat(last_updated)
                if datetime.now() - last_updated < timedelta(days=90):
                    school_info = SchoolInfo(
                        name=doc.metadata.get("name"),
                        description=doc.metadata.get("description"),
                        ranking=doc.metadata.get("ranking"),
                        fields=doc.metadata.get("fields"),
                        linkedin_url=doc.metadata.get("linkedin_url"),
                    )
                    return school_info
        return None

    def update_school_info(self, school_info: SchoolInfo):
        self.vector_store.delete(
            filter={
                "linkedin_url": {"$eq": school_info.linkedin_url},
                "name": {"$eq": school_info.name},
            }
        )
        document = self._create_school_document(school_info)
        self.vector_store.add_documents([document])


# Initialize database
db = SchoolDatabase()


# Define functions
def get_school(name: str, linkedin_url: str) -> SchoolInfo:
    """Query the school database for information about a specific school."""
    return None
    result = db.get_school_info(name, linkedin_url)
    if result:
        return result
    return None


def update_school(school_info: SchoolInfo) -> str:
    """Update the school database with new information about a specific school.
    Don't call this tool if the data is already up-to-date from the database."""

    if not school_info.linkedin_url:
        return

    db.update_school_info(school_info)
    return f"Updated database entry for {school_info.name}"
