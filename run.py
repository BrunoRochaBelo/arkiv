from arkiv_app import create_app

app = create_app()

if __name__ == "__main__":
    # Habilitar CORS para rotas da API
    from flask_cors import CORS
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"].split(",")}})
    app.run(host="0.0.0.0", port=5000)