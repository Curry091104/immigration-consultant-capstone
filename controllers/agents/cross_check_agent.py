import warnings
warnings.filterwarnings("ignore")
from llama_index.core.evaluation import SemanticSimilarityEvaluator
from llama_index.core.embeddings import SimilarityMode, resolve_embed_model

class CrossCheckAgent:
    