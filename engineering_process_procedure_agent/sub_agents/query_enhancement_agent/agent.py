import os
from typing import Dict, Any
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Import model factory for multi-model support
from common.model_factory import create_model_for_agent

# Load environment variables
load_dotenv()

# Get Azure OpenAI configuration from environment
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Set LiteLLM environment variables for Azure OpenAI
os.environ["AZURE_API_KEY"] = AZURE_OPENAI_API_KEY
os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_API_VERSION"] = AZURE_OPENAI_API_VERSION


class AviationQueryClassifier:
    """Classifies aviation maintenance queries into categories."""
    
    MAINTENANCE_KEYWORDS = [
        'maintenance', 'repair', 'overhaul', 'inspection', 'service', 'check',
        'component', 'part', 'replacement', 'installation', 'removal',
        'robbing', 'cannibalization', 'swap', 'exchange'
    ]
    
    TROUBLESHOOTING_KEYWORDS = [
        'troubleshoot', 'diagnose', 'fault', 'failure', 'malfunction',
        'problem', 'issue', 'defect', 'error', 'symptom'
    ]
    
    REGULATORY_KEYWORDS = [
        'regulation', 'compliance', 'faa', 'easa', 'part 145', 'part 43',
        'airworthiness', 'certification', 'approval', 'documentation',
        'regulatory', 'standard', 'requirement'
    ]
    
    SAFETY_KEYWORDS = [
        'safety', 'hazard', 'risk', 'sms', 'safety management',
        'incident', 'accident', 'precaution', 'warning', 'caution'
    ]

    @classmethod
    def classify_query(cls, query: str) -> str:
        """Classify a query into aviation maintenance categories.
        
        Args:
            query: The user's query string
            
        Returns:
            str: The classified category ('maintenance', 'troubleshooting', 'regulatory', 'safety', 'general')
        """
        query_lower = query.lower()

        # Count keyword matches for each category
        maintenance_score = sum(1 for keyword in cls.MAINTENANCE_KEYWORDS if keyword in query_lower)
        troubleshooting_score = sum(1 for keyword in cls.TROUBLESHOOTING_KEYWORDS if keyword in query_lower)
        regulatory_score = sum(1 for keyword in cls.REGULATORY_KEYWORDS if keyword in query_lower)
        safety_score = sum(1 for keyword in cls.SAFETY_KEYWORDS if keyword in query_lower)

        # Determine the category with the highest score
        scores = {
            'maintenance': maintenance_score,
            'troubleshooting': troubleshooting_score,
            'regulatory': regulatory_score,
            'safety': safety_score
        }

        max_score = max(scores.values())
        if max_score == 0:
            return 'general'

        # Return the category with the highest score
        for category, score in scores.items():
            if score == max_score:
                return category

        return 'general'


class AviationQueryEnhancer:
    """Enhances queries with aviation-specific context and terminology."""
    
    ENHANCEMENT_TEMPLATES = {
        'maintenance': {
            'prefix': "Aircraft Maintenance Procedure Query",
            'context': (
                "Please provide step-by-step maintenance procedures following industry standards. "
                "Reference applicable procedure manuals and exposition."
            )
        },
        'troubleshooting': {
            'prefix': "Aircraft Troubleshooting and Diagnostic Query",
            'context': (
                "Please provide systematic troubleshooting procedures and diagnostic approaches. "
                "Include fault isolation techniques, system interactions, common failure modes, "
                "required test equipment, safety precautions, and references to applicable troubleshooting manuals (TSM, FIM). "
                "Consider line maintenance vs. base maintenance contexts and operational impact."
            )
        },
        'regulatory': {
            'prefix': "Aviation Regulatory Compliance Query",
            'context': (
                "Please provide information on regulatory requirements and compliance procedures. "
                "Include references to applicable regulations (FAR, EASA regulations), certification requirements, "
                "documentation standards, approval processes, and industry compliance best practices. "
                "Consider both operator and maintenance organization perspectives."
            )
        },
        'safety': {
            'prefix': "Aviation Safety Management Query",
            'context': (
                "Please provide safety-focused information following SMS (Safety Management System) principles. "
                "Include hazard identification, risk assessment, safety protocols, incident prevention measures, "
                "and references to safety standards and best practices. Consider human factors, operational safety, "
                "and maintenance safety aspects."
            )
        },
        'general': {
            'prefix': "Aircraft Engineering and MRO Query",
            'context': (
                "Please provide comprehensive information relevant to aircraft maintenance, repair, and overhaul (MRO) operations. "
                "Include industry best practices, regulatory considerations, safety protocols, and references to "
                "applicable aviation standards and documentation. Consider both technical and operational aspects "
                "of aircraft engineering and maintenance."
            )
        }
    }

    @classmethod
    def enhance_query(cls, original_query: str, query_type: str) -> tuple[str, Dict[str, Any]]:
        """Enhance a query with aviation-specific context.
        
        Args:
            original_query: The original user query
            query_type: The classified query type
            
        Returns:
            Tuple[str, Dict[str, Any]]: Enhanced query and metadata about the enhancement
        """
        template = cls.ENHANCEMENT_TEMPLATES.get(query_type, cls.ENHANCEMENT_TEMPLATES['general'])

        # Build the enhanced query
        enhanced_query = f"{template['prefix']}: {original_query}\n\n{template['context']}"

        # Add relevant aviation keywords for better RAG retrieval
        relevant_keywords = cls._extract_relevant_keywords(original_query)
        if relevant_keywords:
            enhanced_query += f"\n\nRelevant aviation terms: {', '.join(relevant_keywords)}"

        # Metadata about the enhancement
        enhancement_metadata = {
            "original_query": original_query,
            "query_type": query_type,
            "enhancement_applied": True,
            "template_used": template['prefix'],
            "relevant_keywords": relevant_keywords
        }

        return enhanced_query, enhancement_metadata

    @classmethod
    def _extract_relevant_keywords(cls, query: str) -> list[str]:
        """Extract relevant aviation keywords from the query."""
        query_lower = query.lower()
        relevant_keywords = []

        # Combine all keyword lists from the classifier
        all_keywords = (AviationQueryClassifier.MAINTENANCE_KEYWORDS +
                       AviationQueryClassifier.TROUBLESHOOTING_KEYWORDS +
                       AviationQueryClassifier.REGULATORY_KEYWORDS +
                       AviationQueryClassifier.SAFETY_KEYWORDS)

        for keyword in all_keywords:
            if keyword in query_lower:
                relevant_keywords.append(keyword)

        return relevant_keywords


def enhance_aviation_query(query: str) -> Dict[str, Any]:
    """Tool function to enhance a query with aviation context.
    
    Args:
        query: The original user query to enhance
        
    Returns:
        dict: Enhanced query and metadata
    """
    try:
        # Classify the query
        query_type = AviationQueryClassifier.classify_query(query)
        
        # Enhance the query
        enhanced_query, metadata = AviationQueryEnhancer.enhance_query(query, query_type)
        
        return {
            "status": "success",
            "enhanced_query": enhanced_query,
            "original_query": query,
            "query_type": query_type,
            "metadata": metadata
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error enhancing query: {str(e)}",
            "enhanced_query": query,  # Fallback to original query
            "original_query": query
        }


# Create the Query Enhancement Agent
query_enhancement_agent = LlmAgent(
    name="QueryEnhancementAgent",
    model=create_model_for_agent("query_enhancement_agent"),  # Using GPT-4.1-nano for focused enhancement tasks
    description=(
        "Specialized agent that enhances user queries with aviation engineering and MRO-specific context. "
        "Transforms raw queries into aviation-domain enriched queries with relevant terminology, "
        "regulatory references, and industry best practices."
    ),
    instruction=(
        "You are a Query Enhancement Agent specialized in aircraft MRO (Maintenance, Repair, and Overhaul) "
        "and aviation engineering contexts. Your role is to take user queries and enhance them with "
        "aviation-specific terminology, regulatory context, and industry best practices. "
        "\n\n"
        "ENHANCEMENT PROCESS:\n"
        "1. Analyze the user's query to understand the aviation maintenance context\n"
        "2. Use the enhance_aviation_query tool to transform the query\n"
        "3. Output ONLY the enhanced query text - no additional commentary\n"
        "\n\n"
        "IMPORTANT: Your output will be used directly by the next agent in the pipeline. "
        "Return only the enhanced query text, not explanations or metadata."
    ),
    tools=[enhance_aviation_query],
    output_key="enhanced_query"  # This stores the output in state for the next agent
)
