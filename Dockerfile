ARG PYTHON_VERSION=3.11-slim-bookworm

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POSTGIS_MAJOR 3
ENV PG_MAJOR 13

# Set the working directory
WORKDIR /code

# Add the necessary repository to get PostGIS:
RUN apt-get update \
    && apt-get install -y wget gnupg \
    && echo "Repository tools installed successfully!" \
    
    && echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "PostgreSQL repository added successfully!" \
    
    && apt-get update \
    
  #  && apt-get install -y postgresql-13 \
  #  && echo "PostgreSQL installed successfully!" \
  #  
  #  && apt-get install -y postgresql-13-postgis-3 \
  #  && echo "PostGIS for PostgreSQL installed successfully!" \
  #  
  #  && apt-get install -y postgresql-13-postgis-3-scripts \
  #  && echo "PostGIS scripts for PostgreSQL installed successfully!" \
    
    && apt-get install -y libpq-dev \
    && echo "libpq-dev installed successfully!" \
    
    && apt-get install -y gcc \
    && echo "GCC installed successfully!" \
    
    && apt-get install -y binutils \
    && echo "Binutils installed successfully!" \
    
    && apt-get install -y libproj-dev \
    && echo "libproj-dev installed successfully!" \
    
    && apt-get install -y gdal-bin \
    && echo "GDAL binaries installed successfully!" \
    
    && rm -rf /var/lib/apt/lists/* \
    && echo "APT lists cleared!"

# Copy the requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/

# Copy the current directory content into the container
COPY . /code

# Make the entrypoint script executable
RUN ["chmod", "+x", "./entrypoint.sh"]

EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "core.wsgi"]