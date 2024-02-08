import arxiv
import json
import sys

from datetime import datetime, date, timedelta
from update_html import update_html_file
from pdf_converter import save_to_pdf_file

def search_query(utctime):
    s = "submittedDate:[{} TO {}]"
    t = date.today()
    d2 = (t - timedelta(days = 1)).strftime("%Y%m%d") + utctime + "00"
    d1 = (t - timedelta(days = 2)).strftime("%Y%m%d") + utctime + "00"
    return s.format(d1, d2)

def get_arxiv_papers(conf):
    client = arxiv.Client()
    search = arxiv.Search(
        query = search_query(conf["update-time"]),
        max_results = float("inf"),
    )

    total_count, relevant_count = 0, 0
    initial_filtered = []

    for r in client.results(search):
        for ct in r.categories:
            if ct in conf["category-filter"]:
                initial_filtered.append(r)
                relevant_count += 1
                break
        total_count += 1

    print("Total Documents:", total_count)
    print("Relevant Documents:", relevant_count)

    return initial_filtered

def get_pdf_file_name():
    c = datetime.now()
    return "pdf/" + c.strftime("%Y%m%d") + ".pdf"

if __name__ == "__main__":
    config_file = sys.argv[1]
    with open(config_file) as json_file:
        conf = json.load(json_file)
        papers = get_arxiv_papers(conf)
        # need filtering with GPT
        pdf_name = get_pdf_file_name()
        save_to_pdf_file(papers, pdf_name)
        update_html_file(conf["html-file-name"], pdf_name)
