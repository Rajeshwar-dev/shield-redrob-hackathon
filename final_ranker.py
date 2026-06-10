import json
import csv
import heapq

TITLE_KEYWORDS = {
    "senior ai engineer": 25,
    "senior machine learning engineer": 25,
    "lead ai engineer": 22,
    "staff machine learning engineer": 22,
    "applied ml engineer": 20,
    "machine learning engineer": 18,
    "ml engineer": 18,
    "ai engineer": 18,
}

SKILL_KEYWORDS = {
    "bm25": 20,
    "information retrieval": 20,
    "learning to rank": 20,
    "retrieval": 18,
    "ranking": 18,
    "embeddings": 18,
    "vector search": 16,
    "semantic search": 16,

    "faiss": 15,
    "pinecone": 15,
    "qdrant": 15,
    "weaviate": 15,
    "milvus": 15,
    "opensearch": 15,
    "elasticsearch": 15,
    "pgvector": 15,

    "recommendation systems": 15,
    "sentence transformers": 15,
    "rag": 12,

    "llms": 5,
    "langchain": 3,
    "llamaindex": 3,
}

PRODUCT_COMPANIES = {
    "apple","meta","amazon","google","netflix",
    "zomato","flipkart","swiggy","phonepe",
    "razorpay","microsoft","uber"
}
BAD_TITLES = [
"marketing",
"sales",
"accountant",
"customer support",
"operations",
"hr",
"recruiter"
]


def score_candidate(c):
    score = 0

    profile = c.get("profile", {})
    signals = c.get("redrob_signals", {})

    title = profile.get("current_title", "").lower()
    summary = profile.get("summary", "").lower()

    # title score
    for k, v in TITLE_KEYWORDS.items():
        if k in title:
            score += v
    for bad in BAD_TITLES:
        if bad in title:
            score -= 100

    # experience score
    exp = profile.get("years_of_experience", 0)

    if 5 <= exp <= 9:
        score += 20
    elif 4 <= exp < 5:
        score += 10
    elif 9 < exp <= 12:
        score += 8

    # company bonus
    company = profile.get("current_company", "").lower()
    if company in PRODUCT_COMPANIES:
        score += 10

    # skills
    skills_text = " ".join(
        s.get("name", "") for s in c.get("skills", [])
    ).lower()

    combined_text = summary + " " + skills_text

    for job in c.get("career_history", []):
        combined_text += " "
        combined_text += job.get("description", "").lower()

    for k, v in SKILL_KEYWORDS.items():
        if k in combined_text:
            score += v

    # behavioral signals
    if signals.get("open_to_work_flag"):
        score += 5

    score += min(
        signals.get("github_activity_score", 0) / 20,
        5
    )

    score += (
        signals.get("recruiter_response_rate", 0) * 5
    )

    score += (
        signals.get("interview_completion_rate", 0) * 5
    )

    notice = signals.get("notice_period_days", 90)

    if notice <= 30:
        score += 5
    elif notice <= 60:
        score += 2

    return round(score, 2)


print("Scoring candidates...")

top = []

with open("candidates.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)

        score = score_candidate(c)

        item = (
            score,
            c["candidate_id"],
            c
        )

        if len(top) < 100:
            heapq.heappush(top, item)
        else:
            if score > top[0][0]:
                heapq.heapreplace(top, item)

top.sort(key=lambda x: (-x[0], x[1]))
print("Generating submission.csv")

with open(
    "submission.csv",
    "w",
    newline="",
    encoding="utf-8"
) as out:

    writer = csv.writer(out)

    writer.writerow(
        ["candidate_id", "rank", "score", "reasoning"]
    )

    for rank, (score, cid, c) in enumerate(top, start=1):

        reasoning = (
            "Strong AI/ML profile with retrieval, ranking "
            "and production machine learning experience."
        )

        writer.writerow(
            [cid, rank, score, reasoning]
        )

print("Done.")
print("submission.csv created")