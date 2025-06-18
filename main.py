from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import json
import uvicorn

# Load discourse data
with open("discourse_data.json", "r", encoding="utf-8") as f:
    discourse_raw = json.load(f)

# Load course data
with open("course_data.json", "r", encoding="utf-8") as f:
    course_data = json.load(f)

# Safely clean discourse data
discourse_data = []
for item in discourse_raw:
    if all(k in item for k in ("title", "body", "url")):
        discourse_data.append({
            "source": "discourse",
            "title": item["title"],
            "body": item["body"],
            "url": item["url"]
        })

# Combine all cleaned data
combined_data = discourse_data + [
    {"source": "course", "title": item.get("title", ""), "body": item.get("body", ""), "url": None}
    for item in course_data if "body" in item
]


# Load sentence embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Embed all bodies
corpus = [item["body"] for item in combined_data]
corpus_embeddings = model.encode(corpus, convert_to_tensor=True)

# FastAPI app
app = FastAPI()

# Request model
class QuestionRequest(BaseModel):
    question: str

@app.post("/api/")
async def answer_question(data: QuestionRequest):
    query = data.question
    query_embedding = model.encode(query, convert_to_tensor=True)
    scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = scores.argsort(descending=True)[:3]

    answer = combined_data[int(top_results[0])]["body"]
    links = []

    for idx in top_results:
        entry = combined_data[int(idx)]
        if entry.get("url"):
            links.append({
                "url": entry["url"],
                "text": entry.get("title", "View post")
            })

    return {
        "answer": answer,
        "links": links
    }

# Uncomment to run directly
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
