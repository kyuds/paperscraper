import arxiv

# https://export.arxiv.org/api/query?search_query=submittedDate:[200901130630+TO+200901131645]

client = arxiv.Client()
search = arxiv.Search(
    query = "submittedDate:[200901130630+TO+200901131645]",
    max_results = 10,
    sort_by = arxiv.SortCriterion.SubmittedDate
)

results = client.results(search)

for r in results:
    print(r.title)

