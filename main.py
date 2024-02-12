import arxiv
import json
import sys
import glob
import os

from datetime import datetime, date, timedelta
from redirect import update_html

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4

class ArxivQuery:
    def __init__(self, conf):
        self.conf = conf
    
    def get_papers(self):
        client = arxiv.Client()
        search = arxiv.Search(
            query = ArxivQuery.__search_query(self.conf["update-time"]),
            max_results = float("inf"),
        )

        total_count, relevant_count = 0, 0
        initial_filtered = []

        for r in client.results(search):
            for ct in r.categories:
                if ct in self.conf["category-filter"]:
                    initial_filtered.append(r)
                    relevant_count += 1
                    break
            total_count += 1

        print("Total Documents:", total_count)
        print("Relevant Documents:", relevant_count)

        return initial_filtered

    @staticmethod
    def __search_query(utctime):
        s = "submittedDate:[{} TO {}]"
        t = date.today()
        d2 = (t - timedelta(days = 1)).strftime("%Y%m%d") + utctime + "00"
        d1 = (t - timedelta(days = 2)).strftime("%Y%m%d") + utctime + "00"
        return s.format(d1, d2)

class Report:
    def __init__(self, papers):
        self.papers = papers
        self.file = Canvas(Report.filename(), pagesize=A4)

    @staticmethod
    def filename():
        c = datetime.now()
        return os.path.join("pdf", c.strftime("%Y%m%d") + ".pdf")

    def generate(self):
        self.__setup_file()
        self.__create_header()

        for paper in self.papers:
            self.__create_section(paper)

        self.file.save()

    def __setup_file(self):
        self.file.drawCentredString(290, 720, "test")

    def __create_header(self):
        pass

    def __create_section(self, paper):
        pass

def remove_stale_pdf(n):
    # sanity check
    assert n > 0, "Number of pdfs to be kept should be positive."
    pdfs = glob.glob(os.path.join("pdf", "*.pdf"))

    if len(pdfs) > n:
        pdfs.sort()
        os.system("rm {}".format(pdfs[0]))

if __name__ == "__main__":
    config_file = sys.argv[1]
    with open(config_file) as json_file:
        conf = json.load(json_file)
        query = ArxivQuery(conf)
        papers = query.get_papers()
        # need filtering with GPT
        report = Report(papers)
        report.generate()
        update_html(conf["html-file-name"], Report.filename())
        remove_stale_pdf(int(conf["archived-pdf-count"]))
