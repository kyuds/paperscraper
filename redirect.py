HTML = """\
<!DOCTYPE html>
<html>
  <head>
    <style>
      * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Amiko', sans-serif;
        letter-spacing: 5px;
      }}
      html, body {{
          width: 100vw;
          background-color: white;
      }}
      a {{
          color: #030a15;
          text-decoration: none;
          font-size: 1rem;
          padding: 2rem;
          text-align: center;
      }}
      div {{
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
      }}
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

def update_html(filename, pdf_name):
    with open(filename, "w") as file:
        file.write(HTML.format(url=pdf_name))
