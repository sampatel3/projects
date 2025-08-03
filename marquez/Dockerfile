FROM python:3.9-slim

# Create the /app/.dbt directory where the profiles.yml will be stored
# RUN mkdir -p /app/dbt/.dbt

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Marquez client for DBT integration
RUN pip install marquez-python

# Set environment variables for DBT and Marquez
ENV DBT_PROFILES_DIR=/app/dbt/.dbt/
ENV MARQUEZ_API_URL=http://localhost:5000  
ENV MARQUEZ_NAMESPACE=marquez_local  
ENV MARQUEZ_DATASET_NAME=marquezdb  

# Check DBT version (to ensure it's installed correctly)
RUN dbt --version

# Set environment variables for DBT (ensure profiles dir exists)
ENV DBT_PROFILES_DIR=/app/dbt/.dbt

# Expose the PostgreSQL port (for connection)
EXPOSE 9876

# Default command to keep the container running interactively
CMD ["tail", "-f", "/dev/null"]

# run DBT
RUN