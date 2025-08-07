FROM docker.m.daocloud.io/library/python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Use Chinese mirrors for apt
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    git \
    gcc \
    g++ \
    make \
    # PostgreSQL client and development headers
    postgresql-client \
    libpq-dev \
    python3-dev \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libgtk-3-0 \
    # Chinese language support
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    locales \
    # System monitoring
    procps \
    htop \
    # Timezone data
    tzdata \
    # Network utilities
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set timezone to China
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Generate Chinese locale
RUN locale-gen zh_CN.UTF-8
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN.UTF-8
ENV LC_ALL=zh_CN.UTF-8

# Use Chinese pip mirror
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Create directories
RUN mkdir -p /app/logs /app/data /app/models /app/backups

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command - run on port 8080
CMD ["python", "run_server.py"]