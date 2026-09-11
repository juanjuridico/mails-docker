#!/bin/sh
set -eu

# Solicita un túnel al servicio vpn-docker. Esto sólo cambia la ruta de salida;
# no intenta resolver desafíos de Cloudflare.
PROXY_URL="$(python - <<'PY2'
import os, time, urllib.request, json, sys

api = os.getenv("VPN_API_URL", "http://vpn_api:6004").rstrip("/")
country = os.getenv("VPN_COUNTRY", "JP").upper()
for attempt in range(1, 8):
    try:
        req = urllib.request.Request(
            api + "/tuneles",
            data=json.dumps({"pais": country}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.load(response)
        tunnel = payload.get("data", {})
        if payload.get("ok") and tunnel.get("proxy_host"):
            print("http://%s:%s" % (tunnel["proxy_host"], tunnel["proxy_port"]))
            sys.exit(0)
    except Exception as exc:
        print(f"[vpn] intento {attempt}/7: {exc}", file=sys.stderr)
        time.sleep(4)
sys.exit(1)
PY2
)" || PROXY_URL=""

if [ -n "$PROXY_URL" ]; then
  export PROXY="$PROXY_URL" HTTP_PROXY="$PROXY_URL" HTTPS_PROXY="$PROXY_URL"
  export NO_PROXY="localhost,127.0.0.1,vpn_api"
  echo "[vpn] salida tunelizada por $PROXY_URL"
else
  echo "[vpn] no se pudo obtener túnel; se continúa sin proxy"
fi

exec "$@"
