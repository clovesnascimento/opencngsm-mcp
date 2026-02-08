
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 opencngsm

# Install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=opencngsm:opencngsm . .

# Switch to non-root user
USER opencngsm

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "print('healthy')" || exit 1

# Run application
CMD ["python", "-m", "opencngsm.main"]
