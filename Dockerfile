FROM python:3.9 as deps
ENV POETRY_VIRTUALENVS_IN_PROJECT true
WORKDIR /opt
RUN pip install poetry
COPY pyproject.toml ./
COPY poetry.lock ./
RUN poetry install --no-dev

FROM python:3.9
RUN useradd appuser
USER appuser
VOLUME "/data"
COPY --from=deps /opt/.venv /opt/venv
ENV PATH "/opt/venv/bin:$PATH"
COPY feedback_bot feedback_bot
CMD python -m feedback_bot

EXPOSE 8080/tcp
