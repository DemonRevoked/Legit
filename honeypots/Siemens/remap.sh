sudo docker run -d \
  --name sim-plc \
  -p 502:502 \
  --privileged \
  --mac-address="3C:5A:B4:12:34:56" \
  plc-honeypot
