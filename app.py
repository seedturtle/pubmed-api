from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

NCBI_EMAIL = "agenthung849@gmail.com"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

@app.route("/search", methods=["GET"])
@app.route("/search/", methods=["GET"])
def search_pubmed():
    query = request.args.get("q") or request.args.get("term") or ""
    num = request.args.get("num", "10")
    
    if not query:
        return jsonify({"error": "Please provide q parameter"})
    
    # 搜尋
    search_url = f"{BASE_URL}/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": num,
        "retmode": "json",
        "email": NCBI_EMAIL
    }
    
    try:
        resp = requests.get(search_url, params=params, timeout=30)
        data = resp.json()
        
        idlist = data.get("esearchresult", {}).get("idlist", [])
        
        if idlist:
            # 取得詳細資料
            fetch_url = f"{BASE_URL}/esummary.fcgi"
            params2 = {
                "db": "pubmed",
                "id": ",".join(idlist[:10]),
                "retmode": "json",
                "email": NCBI_EMAIL
            }
            resp2 = requests.get(fetch_url, params=params2, timeout=30)
            summaries = resp2.json()
            
            results = []
            for uid, info in summaries.get("result", {}).items():
                if uid == "uids":
                    continue
                authors = info.get("authors", [])
                author_names = [a.get("name", "") for a in authors[:3]] if authors else []
                results.append({
                    "uid": uid,
                    "title": info.get("title", ""),
                    "authors": author_names,
                    "source": info.get("source", ""),
                    "pubdate": info.get("pubdate", ""),
                })
            
            return jsonify({"query": query, "count": len(results), "results": results})
        
        return jsonify({"query": query, "count": 0, "results": [], "message": "No results found"})
    
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
