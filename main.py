import arxiv
import json
import sys
import glob
import os
import concurrent.futures
import openai
import time

from datetime import datetime, date, timedelta
from redirect import update_html
from prompt import SUMMARIZER_PROMPT

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
                initial_filtered.append(ArxivQuery.__paper_info(r))
            total_count += 1

        print("Total Documents:", total_count)
        print("Relevant Documents:", relevant_count)

        return initial_filtered

    @staticmethod
    def __search_query(utctime):
        s = "submittedDate:[{} TO {}]"
        t = date.today()
        d2 = (t - timedelta(days = 2)).strftime("%Y%m%d") + utctime + "00"
        d1 = (t - timedelta(days = 3)).strftime("%Y%m%d") + utctime + "00"
        query = s.format(d1, d2)
        print("Query:", query) # for logging purposes. 
        return query

    @staticmethod
    def __paper_info(paper):
        info = {}
        info["authors"] = paper.authors
        info["title"] = paper.title
        info["links"] = paper.links
        info["abstract"] = paper.summary
        return info

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
            if len(paper["summary"]) > 0:
                self.__create_section(paper, build)
        self.file.build(build)

    def __create_header(self, build):
        build.append(Paragraph(
            self.date.strftime("%a %Y.%m.%d"), 
            self.title_style
        ))
        build.append(Spacer(1, 20))

    def __create_section(self, paper, build):
        authors = ", ".join([a.name for a in paper["authors"]])
        build.append(Paragraph(paper["title"], style=self.subtitle_style))
        build.append(Spacer(1, 2))
        build.append(Paragraph(authors, style=self.author_style))
        build.append(Spacer(1, 5))
        
        build.append(Paragraph(
            f'<b>What\'s New:</b> {paper["summary"].get("whats new", "")}', 
            style=self.summary_style))
        build.append(Spacer(1, 5))
        build.append(Paragraph(
            f'<b>Technical Details:</b> {paper["summary"].get("technical details", "")}', 
            style=self.summary_style))
        build.append(Spacer(1, 5))
        build.append(Paragraph(
            f'<b>Results:</b> {paper["summary"].get("results", "")}', 
            style=self.summary_style))

        if len(paper["links"]) > 0:
            build.append(Spacer(1, 5))
            link = "<a href='{}'>link: {}</a>".format(paper["links"][0], paper["links"][0])
            build.append(Paragraph(link, self.link_style))

        build.append(Spacer(1, 15))

class GPTSummarizer:
    def __init__(self, key, retry, model, max_tokens, prompt):
        self.client = openai.OpenAI(api_key=key)
        self.retry = retry
        self.model = model
        self.max_tokens = max_tokens
        self.prompt = prompt
    
    def __summarize(self, abstract):
        for i in range(self.retry):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt},
                        {"role": "user", "content": abstract},
                    ],
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"}
                )
                return resp.choices[0].message.content.strip()
            except Exception as e:
                print(e)
                # exponential backoff; no need to sleep for last attempt
                if i != self.retry - 1:
                    time.sleep(min(60, 10 + 5 ** i))
        return ""

    def summarize(self, papers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()*2) as executor:
            futures, result = {}, []
            for pi in papers:
                futures[
                    executor.submit(
                        lambda abstract: self.__summarize(abstract), 
                        pi["abstract"]
                    )
                ] = pi
            for f in concurrent.futures.as_completed(futures):
                result.append(futures[f])
                result[-1]["summary"] = json.loads(f.result())
        return result

def remove_stale_pdf(n):
    # sanity check
    assert n > 0, "Number of pdfs to be kept should be positive."
    pdfs = glob.glob(os.path.join("pdf", "*.pdf"))

    if len(pdfs) > n:
        pdfs.sort()
        os.system("rm {}".format(" ".join(pdfs[:len(pdfs) - n])))

if __name__ == "__main__":
    config_file = sys.argv[1]
    with open(config_file) as json_file:
        conf = json.load(json_file)
        query = ArxivQuery(conf)
        papers = query.get_papers()
        if len(papers) > 0:
            gpt = GPTSummarizer(
                sys.argv[2],
                int(conf["openai-retry"]),
                conf["openai-model"],
                int(conf["openai-max-tokens"]),
                SUMMARIZER_PROMPT
            )
            papers = gpt.summarize(papers)
            report = Report(papers)
            report.generate()
            update_html(conf["html-file-name"], Report.filename())
            remove_stale_pdf(int(conf["archived-pdf-count"]))
