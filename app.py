from flask import Flask, Response, request
import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column("nome", db.String(150))
    senha = db.Column("senha", db.String(150))

    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha
        
    def to_dict(self, columns=[]):
        # Verifica se foram informadas colunas para filtrar o retorno

        if not columns:
            return {
                "id": self.id,
                "nome": self.nome,
                "senha": self.senha
            }
        else:
            return {col: getattr(self, col) for col in columns}


app = Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.sqlite3"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://usuarios_kjjr_user:VHefx8aIdMDHE4LF12BdEXXEHlKeZk0I@dpg-cmniuqla73kc73auknh0-a/usuarios_kjjr"
db.init_app(app=app)
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_RECORD_QUERIES"] = True

# It's important to use session
app.secret_key = "$$$581489*@Abscaracha"


@app.route("/")
def index():
    # Is returned an iterator with
    #  all users
    try:
        usuarios = Usuario.query.all()

        # Cast every object into dict
        result = [u.to_dict() for u in usuarios]
        return Response(response=json.dumps({"status": "success", "data": result}), status=200, content_type="application/json")
    except Exception as e:
        return Response(response=json.dumps({"status": "success", "data": {f"{type(e).__name__}": f">>{e}"}}), status=200, content_type="application/json")


@app.route("/add", methods=["POST"])
def add():
    data = request.get_json(force=True)
    usuario = Usuario(
        data["nome"], 
        data["senha"],
        )
    db.session.add(usuario)
    db.session.commit()
    # Retorna a resposta em json
    return Response(response=json.dumps({"status": "success", "data": usuario.to_dict()}), status=200, content_type="application/json")

@app.route("/edit/<userid>", methods=["PUT", "POST"])
def edit(userid):
    # Localiza o usuário no banco pelo email
    usuario = Usuario.query.where(Usuario.id == userid).first()
    data = request.get_json(force=True)
    usuario.nome = data["nome"]
    usuario.senha = data["senha"]
    db.session.commit()
    return Response(response=json.dumps({"status": "success", "data": usuario.to_dict()}), status=200, content_type="application/json")


@app.route("/delete/<userid>", methods=["DELETE"])
def delete(userid):
    usuario = Usuario.query.where(Usuario.id == userid).first()
    db.session.delete(usuario)
    db.session.commit()
    return Response(response=json.dumps({"status": "success", "data": usuario.to_dict()}), status=200, content_type="application/json")

if __name__ == "__main__":
    # Inicia e configura o banco de dados
    # db.init_app(app=app)
    # Crea as tabelas apenas se a aplicação estiver pronta
    with app.test_request_context():
        db.create_all()
    app.run(debug=True)