from gensim.models import Word2Vec
import numpy as np
import json

def load_token_corpus(json_file):
    with open(json_file, 'r') as f:
        lines = f.readlines()
    docs = [json.loads(line) for i, line in enumerate(lines) if i % 2 == 1]
    return [doc["tokens"].split() for doc in docs if "tokens" in doc]

def load_fp_interval_corpus(json_file):
    """
    Load the fingerprint interval corpus from the bulk JSON file.
    """
    with open(json_file, 'r') as f:
        lines = f.readlines()
    docs = [json.loads(line) for i, line in enumerate(lines) if i % 2 == 1]
    return [doc["interval_fp"].split() for doc in docs if "interval_fp" in doc]

def train_music2vec(corpus, vector_size=128, window=5, min_count=1):
    model = Word2Vec(
        sentences=corpus,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        sg=1,
        workers=4
    )
    return model

def get_doc_embedding(fp_intervals, model):
    vectors = [model.wv[fp] for fp in fp_intervals if fp in model.wv]
    if not vectors:
        return np.zeros(model.vector_size)
    return np.mean(vectors, axis=0)

def add_embeddings_to_bulk(bulk_path, out_path, model):
    with open(bulk_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    for i, line in enumerate(lines):
        if i % 2 == 0:
            index_metadata = json.loads(line)
            index_metadata["index"]["_index"] = "musicxml_token_embeddings"  # Change index name
            new_lines.append(json.dumps(index_metadata))
        else:
            doc = json.loads(line)
            fp_intervals = doc.get("interval_fp", "").split()
            vec = get_doc_embedding(fp_intervals, model)
            doc["embedding"] = list(map(float, vec))
            new_lines.append(json.dumps(doc))

    with open(out_path, 'w') as f:
        for line in new_lines:
            f.write(line + "\n")

if __name__ == "__main__":
    fp_interval_corpus = load_fp_interval_corpus("bulk_index.json")
    music2vec_model = train_music2vec(fp_interval_corpus)
    music2vec_model.save("music2vecFP.model")
    add_embeddings_to_bulk("bulk_index.json", "bulk_with_FPembeddings.json", music2vec_model)
    print("✅ Training complete. Embeddings saved to bulk_with_FPembeddings.json.")
