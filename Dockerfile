
# Stage 1: Install Node.js dependencies
FROM node:18-slim as node

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

# Stage 2: Build the final Python image
FROM python:3.12-slim

WORKDIR /app

# Copy Node.js executable from the node stage
COPY --from=node /app/node_modules/ /app/node_modules/

# Set the PATH to include the mmdc executable
ENV PATH="/app/node_modules/.bin:${PATH}"

# Install system dependencies for Puppeteer
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-sandbox \
    fonts-liberation \
    libasound2 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    wget \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && \
    apt-get install -y chromium-browser
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "codee:app", "--host", "0.0.0.0", "--port", "8000"]
