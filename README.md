# paperscraper

Automatically scrape recent (two days old due to API update issues) papers from arXiv and summarize them through gpt 3. Github workflows automatically summarize and push summaries to github pages.

### How To Use
1. Fork the repo
2. In `.github/workflows/update.yml`, uncomment workflow dispatch
```
#schedule:                  <-- this part
#  - cron: '0 15 * * *'
```
3. Configure actions and setup Github Pages.
4. Configure OpenAI API Keys through Github Secrets: `OpenAI_API_KEY`. (refer to `update.yml`)
5. View daily summaries through `<your github username>.github.io/paperscraper`.

Please note that there are some days when arXiv is not updated. In that case, paperscraper is not going to update itself.

## TODO
Currently, about 700+ papers are uploaded to arXiv everyday. I don't think anybody is going to read 700+ abstract summaries everyday. Therefore, some next steps is to add LLM support to determine which abstracts would be most interesting for a given user, which will also be defined in the prompt and JSON file.
