import datetime

HTML = """\
<!DOCTYPE html>
<html>
  <head>
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Amiko', sans-serif;
        letter-spacing: 8px;
      }
      html, body {
          width: 100vw;
          background-color: #030a15;
      }
      a {
          color: white;
          text-decoration: none;
          font-size: 1rem;
          padding: 2rem;
          border: solid white;
          text-align: center;
      }
      div {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
      }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Amiko&display=swap" rel="stylesheet">
    <meta http-equiv="refresh" content="0; url='{url}'" />
  </head>
  <body>
    <div>
      <a href="{url}">
        <span>click here</span>
      </a>
    </div>
  </body>
</html>
"""

if __name__ == "__main__":
    curr = datetime.datetime.now()
    path = "pdf/" + curr.strftime("%Y%m%d") + ".pdf"
    with open("index.html", "w") as file:
        file.write(HTML.format(url=path))
