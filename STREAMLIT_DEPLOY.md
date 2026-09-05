# Deploy AgentInvest

This project is a Streamlit app. The public app entrypoint is:

```text
app.py
```

## Local Demo

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

The portfolio demo button currently points to this local URL.

## Public Deployment

1. Push this folder to GitHub.
2. Create a new app at Streamlit Community Cloud.
3. Set the main file path to `app.py`.
4. Add this in the app Secrets panel:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-5.6-luna"
```

5. Deploy the app.
6. Replace the portfolio button URL in `sherry-portfolio/index.html` with the deployed Streamlit URL.

Do not commit `.env` or `.streamlit/secrets.toml`.
