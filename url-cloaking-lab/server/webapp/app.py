import os
from flask import Flask, request, redirect, url_for, render_template, jsonify

app = Flask(__name__)

# In the Labtainers topology, the scanner has this source IP.
# Change SCANNER_IPS if the address in config/start.config changes.
SCANNER_IPS = {
    item.strip()
    for item in os.environ.get("SCANNER_IPS", "192.168.1.50").split(",")
    if item.strip()
}


def is_scanner(ip):
    """Exact IP comparison; deliberately does not trust X-Forwarded-For."""
    return ip in SCANNER_IPS


@app.after_request
def add_safety_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/")
def index():
    client_ip = request.remote_addr or "unknown"
    scanner = is_scanner(client_ip)
    app.logger.info("URL_CLOAKING_REQUEST ip=%s decision=%s", client_ip,
                    "normal-page" if scanner else "302-training-simulation")
    if scanner:
        return render_template("normal.html", source_ip=client_ip, preview=False)
    return redirect(url_for("simulation_landing"), code=302)


@app.route("/training-simulation")
def simulation_landing():
    # This is an inert training page. It does not ask for or collect credentials.
    client_ip = request.remote_addr or "unknown"
    app.logger.info("URL_CLOAKING_SIMULATION_PAGE ip=%s", client_ip)
    return render_template("simulation.html", source_ip=client_ip, preview=False), 200


@app.route("/preview")
def preview_home():
    return render_template("preview.html"), 200


@app.route("/preview/scanner")
def preview_scanner():
    # Visual preview only: this route intentionally bypasses IP classification.
    return render_template("normal.html", source_ip="preview mode", preview=True), 200


@app.route("/preview/victim")
def preview_victim():
    # Visual preview only: this route intentionally bypasses IP classification.
    return render_template("simulation.html", source_ip="preview mode", preview=True), 200


@app.route("/training-complete", methods=["GET", "POST"])
def training_complete():
    # No form data is read or stored. The simulated call-to-action ends here.
    return render_template("training_complete.html"), 200


@app.route("/health")
def health():
    return jsonify(status="ok", service="url-cloaking-lab"), 200


if __name__ == "__main__":
    # Flask's built-in server is used only for this isolated training lab.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), debug=False)
