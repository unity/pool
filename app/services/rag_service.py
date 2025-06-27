import os
from google.cloud import storage
from google import genai
import vertexai
from vertexai import rag
from google.genai.types import GenerateContentConfig, Retrieval, Tool, VertexRagStore

PROJECT_ID = "oa-bta-learning-dv"
LOCATION = "europe-west4"
EMBEDDING_MODEL = "publishers/google/models/text-embedding-005"
MODEL_ID = "gemini-2.0-flash-001"
INPUT_GCS_BUCKET = "gs://hackathon-team-9-rag-data/"

class RAGService:
    def __init__(self):
        vertexai.init(project=PROJECT_ID, location="us-central1")
        self.client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        print("corpus creation started")
        
        self.rag_corpus = rag.create_corpus(
            display_name="team9-rag-corpus-final",
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=rag.RagEmbeddingModelConfig(
                    vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                        publisher_model=EMBEDDING_MODEL
                    )
                )
            ),
        )
        print("corpus creation done: ")
        print("corpus files import started: " + INPUT_GCS_BUCKET)
        rag.import_files(
            corpus_name=self.rag_corpus.name,
            paths=[INPUT_GCS_BUCKET],
            transformation_config=rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(chunk_size=1024, chunk_overlap=100)
            ),
            max_embedding_requests_per_min=900,
        )
        print("corpus files import done")
        self.rag_retrieval_tool = Tool(
            retrieval=Retrieval(
                vertex_rag_store=VertexRagStore(
                    rag_corpora=[self.rag_corpus.name],
                    similarity_top_k=10,
                    vector_distance_threshold=0.5,
                )
            )
        )

    def ask_agent(self, question: str) -> str:
        response = self.client.models.generate_content(
            model=MODEL_ID,
            contents=question,
            config=GenerateContentConfig(tools=[self.rag_retrieval_tool],
                                         system_instruction='talk like a beauty advisor in a firendly way recommending products',),
        )
        return response.text 