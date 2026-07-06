FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md requirements.txt ./
COPY npmai_agents ./npmai_agents

RUN pip install --no-cache-dir -e ".[full]"

RUN python -c "import npmai_agents.cli; print('We Imported Sucessfully')" #This is just to verify 
RUN npmai --help

ENTRYPOINT ["npmai"]
CMD ["--help"]
