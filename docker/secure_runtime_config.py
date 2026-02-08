"""
Runtime Isolation Configuration
Configuração segura para Docker com isolamento total

Features:
- Network isolation (--network=none)
- Read-only filesystem
- Tmpfs com noexec
- Resource limits
- Security options
"""

# Docker Compose configuration for secure runtime
DOCKER_COMPOSE_SECURE = """
version: '3.8'

services:
  opencngsm-secure:
    image: opencngsm:v3.3-secure
    container_name: opencngsm-secure
    
    # NETWORK ISOLATION - Sem acesso à rede
    network_mode: none
    
    # FILESYSTEM - Read-only com tmpfs para /tmp
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=100m
    
    # RESOURCE LIMITS
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M
    
    # SECURITY OPTIONS
    security_opt:
      - no-new-privileges:true
      - seccomp=default
      - apparmor=docker-default
    
    # CAPABILITIES - Drop all
    cap_drop:
      - ALL
    
    # USER - Run as non-root
    user: "1000:1000"
    
    # PIDS LIMIT
    pids_limit: 50
    
    # ENVIRONMENT
    environment:
      - PYTHONUNBUFFERED=1
      - OPENCNGSM_SECURE_MODE=true
    
    # VOLUMES - Apenas read-only
    volumes:
      - ./config:/app/config:ro
      - ./skills:/app/skills:ro
    
    # RESTART POLICY
    restart: unless-stopped
"""

# Dockerfile for secure image
DOCKERFILE_SECURE = """
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
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD python -c "print('healthy')" || exit 1

# Run application
CMD ["python", "-m", "opencngsm.main"]
"""

# Docker run command for manual execution
DOCKER_RUN_SECURE = """
docker run \\
  --name opencngsm-secure \\
  --network=none \\
  --read-only \\
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \\
  --cap-drop=ALL \\
  --security-opt=no-new-privileges:true \\
  --security-opt=seccomp=default \\
  --security-opt=apparmor=docker-default \\
  --memory=256m \\
  --cpus=0.5 \\
  --pids-limit=50 \\
  --user=1000:1000 \\
  -v $(pwd)/config:/app/config:ro \\
  -v $(pwd)/skills:/app/skills:ro \\
  -e OPENCNGSM_SECURE_MODE=true \\
  opencngsm:v3.3-secure
"""

# AppArmor profile for additional security
APPARMOR_PROFILE = """
#include <tunables/global>

profile opencngsm-secure flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/python>

  # Deny network access
  deny network,

  # Allow read access to application files
  /app/** r,
  /app/config/** r,
  /app/skills/** r,

  # Allow write only to /tmp
  /tmp/** rw,

  # Deny everything else
  deny /** w,
  deny /proc/** w,
  deny /sys/** w,
  deny /dev/** w,
}
"""

if __name__ == "__main__":
    from pathlib import Path
    
    # Create configuration files
    output_dir = Path("docker/secure")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write docker-compose.yml
    (output_dir / "docker-compose.yml").write_text(DOCKER_COMPOSE_SECURE)
    print(f"✅ Created: {output_dir}/docker-compose.yml")
    
    # Write Dockerfile
    (output_dir / "Dockerfile").write_text(DOCKERFILE_SECURE)
    print(f"✅ Created: {output_dir}/Dockerfile")
    
    # Write run script
    (output_dir / "run-secure.sh").write_text(DOCKER_RUN_SECURE)
    print(f"✅ Created: {output_dir}/run-secure.sh")
    
    # Write AppArmor profile
    (output_dir / "apparmor-profile").write_text(APPARMOR_PROFILE)
    print(f"✅ Created: {output_dir}/apparmor-profile")
    
    print()
    print("=" * 80)
    print("🛡️ Secure Runtime Configuration Created")
    print("=" * 80)
    print()
    print("To use:")
    print("1. Build image: docker build -t opencngsm:v3.3-secure -f docker/secure/Dockerfile .")
    print("2. Run with compose: docker-compose -f docker/secure/docker-compose.yml up")
    print("3. Or run manually: bash docker/secure/run-secure.sh")
    print()
