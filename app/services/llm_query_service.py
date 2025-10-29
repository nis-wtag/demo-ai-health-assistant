from datetime import datetime

from core.config import settings
from core.database import DbSession
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from schemas.ai_response_schema import StructuredAIResponse
from schemas.chat_schema import ChatResponse
from schemas.doctor_schema import DoctorSearch
from middleware import logger
from services.doctor_service import formatted_search_doctors


class QueryService:
    def __init__(self, db: DbSession):
        self.db = db
        # Initialize the LLM and the output parser
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.5,
        )
        self.parser = JsonOutputParser(pydantic_object=StructuredAIResponse)
        self.prompt = self._create_prompt_template()
        # Create the full processing chain
        self.chain = self.prompt | self.llm | self.parser

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Creates the detailed prompt template for the LLM chain."""
        prompt_str = """
        You are an expert medical assistant in Bangladesh. Your task is to analyze a user's health query
        and provide a structured response in JSON format. The user's query will be in English, Bangla, or a mix (Banglish).

        Current Date: {current_date}

        Analyze the following user query:
        <query>
        {query}
        </query>

        Based on the query, perform two tasks:
        1.  **Generate a Remedy:** Provide a safe, non-diagnostic home remedy. Do not diagnose diseases or prescribe medicine. The remedy must be educational, safe, and generally applicable.
        2.  **Extract Search Parameters:** Extract all relevant criteria for finding a doctor. If a specific piece of information (like a day, time, or location) is not mentioned, you MUST leave the corresponding field as null. Do not invent or assume information.

        Your output MUST be a JSON object that follows this exact format:
        {format_instructions}
        """
        return ChatPromptTemplate.from_template(
            prompt_str,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

    def process_user_query(self, user_query: str) -> ChatResponse:
        """
        Processes a user's natural language query to provide remedies and doctor recommendations.
        """
        # 2. Invoke the LangChain to get structured data
        current_date_str = datetime.now().strftime("%A, %Y-%m-%d")

        try:
            llm_response = self.chain.invoke(
                {"query": user_query, "current_date": current_date_str}
            )
            search_params = DoctorSearch(**llm_response.get("search_parameters", {}))
            remedy = llm_response.get(
                "remedy",
                "Could not determine a specific remedy. Please consult a doctor.",
            )
        except Exception as e:
            # Fallback if the LLM fails to generate valid JSON
            logger.debug(f"LLM parsing failed: {e}")
            search_params = DoctorSearch(specialization="General")
            remedy = "I had trouble understanding the specifics of your query. It's always best to consult with a General Practitioner for any health concerns."

        # 3. Use the structured data to find doctors
        recommended_doctors = formatted_search_doctors(
            self.db, search_params=search_params, limit=6
        )

        # 4. Assemble the final response
        return ChatResponse(
            disclaimer="This is AI-generated advice and not a substitute for professional medical consultation. Please see a certified doctor for any health concerns.",
            remedy=remedy,
            recommended_doctors=recommended_doctors,
        )
