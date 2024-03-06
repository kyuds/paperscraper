import arxiv
import json
import sys
import glob
import os

from datetime import datetime, date, timedelta
from redirect import update_html

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

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
            deny = False
            sati = False
            for ct in r.categories:
                for denial in self.conf["remove-filter"]:
                    if denial in ct:
                        deny = True
                        break
                if deny:
                    break
                if ct in self.conf["category-filter"]:
                    sati = True
            if not deny and sati:
                relevant_count += 1
                initial_filtered.append(r)
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
        query = s.format(d1, d2)
        print("Query:", query) # for logging purposes. 
        return query

class Report:
    def __init__(self, papers):
        self.date = datetime.now()
        self.papers = papers
        self.file = SimpleDocTemplate(
            Report.filename(), 
            pagesize=A4,
            title="Report: {}".format(self.date.strftime("%Y%m%d"))
        )
        default = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            name="TitleStyle",
            parent=default["Title"],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=18
        )
        self.subtitle_style = ParagraphStyle(
            name="SubtitleStyle",
            parent=default["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11
        )
        self.author_style = ParagraphStyle(
            name="AuthorStyle",
            parent=default["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=10
        )
        self.summary_style = ParagraphStyle(
            name="SummaryStyle",
            parent=default["Normal"],
            fontName="Helvetica",
            fontSize=10
        )
        self.link_style = ParagraphStyle(
            name="LinkStyle",
            parent=default["Normal"],
            fontName="Helvetica",
            fontSize=10,
            underline=True
        )

    @staticmethod
    def filename():
        c = datetime.now()
        return os.path.join("pdf", c.strftime("%Y%m%d") + ".pdf")

    def generate(self):
        build = []
        self.__create_header(build)
        for paper in self.papers:
            self.__create_section(paper, build)
        self.file.build(build)

    def __create_header(self, build):
        build.append(Paragraph(
            self.date.strftime("%a %Y.%m.%d"), 
            self.title_style
        ))
        build.append(Spacer(1, 20))

    def __create_section(self, paper, build):
        authors = ", ".join([a.name for a in paper.authors])
        build.append(Paragraph(paper.title, style=self.subtitle_style))
        build.append(Spacer(1, 2))
        build.append(Paragraph(authors, style=self.author_style))
        build.append(Spacer(1, 5))
        build.append(Paragraph(paper.summary, style=self.summary_style))

        if len(paper.links) > 0:
            build.append(Spacer(1, 5))
            link = "<a href='{}'>link: {}</a>".format(paper.links[0], paper.links[0])
            build.append(Paragraph(link, self.link_style))

        build.append(Spacer(1, 15))


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
        if len(papers) > 0:
            # need filtering with GPT
            # arbitrary for now until GPT filter
            report = Report(papers[:int(conf["num-reports"])])
            report.generate()
            update_html(conf["html-file-name"], Report.filename())
            remove_stale_pdf(int(conf["archived-pdf-count"]))
