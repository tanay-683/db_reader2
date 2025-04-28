FROM db_reader2_updated:latest
COPY . .
RUN uv pip install -r pyproject.toml --system
RUN uv pip install -e . --system
CMD [ "python3", "main.py" ]