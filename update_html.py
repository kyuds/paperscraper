import datetime

HTML = """\
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url='{url}'" />
  </head>
  <body>
    <a href="{url}">Click if not redirected</a>
  </body>
</html>
"""

if __name__ == "__main__":
    curr = datetime.datetime.now()
    path = "paperscraper/pdf/" + curr.strftime("%Y%m%d") + ".pdf"
    with open("index.html", "w") as file:
        file.write(HTML.format(url=path))
