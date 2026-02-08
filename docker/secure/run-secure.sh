
docker run \
  --name opencngsm-secure \
  --network=none \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --cap-drop=ALL \
  --security-opt=no-new-privileges:true \
  --security-opt=seccomp=default \
  --security-opt=apparmor=docker-default \
  --memory=256m \
  --cpus=0.5 \
  --pids-limit=50 \
  --user=1000:1000 \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/skills:/app/skills:ro \
  -e OPENCNGSM_SECURE_MODE=true \
  opencngsm:v3.3-secure
