from flask import Flask, render_template, request, jsonify, send_file
import requests
import os
import zipfile
import io

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "Je n'ai rien reçu."})

    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "Tu es KoïtaAI, une intelligence artificielle qui répond à toutes les questions avec clarté."},
            {"role": "user", "content": user_input}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
    if response.status_code == 200:
        answer = response.json()["choices"][0]["message"]["content"]
        with open("reponse.txt", "w", encoding="utf-8") as f:
            f.write(answer)
        return jsonify({"response": answer})
    else:
        return jsonify({"response": "Erreur lors de la communication avec l'IA."})

@app.route("/download-zip")
def download_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        if os.path.exists("reponse.txt"):
            zf.write("reponse.txt")
    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name="koitaai_reponse.zip")

@app.route("/upload-zip", methods=["POST"])
def upload_zip():
    uploaded_file = request.files["file"]
    if uploaded_file and uploaded_file.filename.endswith(".zip"):
        zip_path = os.path.join("uploads", uploaded_file.filename)
        os.makedirs("uploads", exist_ok=True)
        uploaded_file.save(zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall("uploads/unzipped")
        content = ""
        for fname in os.listdir("uploads/unzipped"):
            with open(os.path.join("uploads/unzipped", fname), "r", encoding="utf-8") as f:
                content += f.read() + "\n"
        return jsonify({"response": f"Contenu du ZIP :\n{content}"})
    return jsonify({"response": "Fichier invalide."})

if __name__ == "__main__":
    app.run(debug=True)