
from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3, os, csv, json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "etapa7_secret"

DB_FILE = "notas.db"
USUARIOS_FILE = "usuarios.json"
alunos = ['Alan Joaquim Vidal', 'Alison Okuhira Tartari', 'Amani Mendonça Yassin', 'Ana Carolina Marangon Vieira', 'Ana Clara Vieira Nascimento Matos', 'Ana Flávia Ramos do Amaral', 'Anna Carolina de Araújo', 'Arthur Ribeiro Covezzi', 'Brenda Ferreira da Silva', 'Bruna Melo Medeiros', 'Carlos Antonio Haddad Junior', 'Carlos Roberto Calil Anunciação', 'Caroline dos Santos Brunetto', 'Clara Prates Fonsêca de Camargo', 'Eduardo Francescon Barroso', 'Eglis Arantes Mendonça Magalhães', 'Élisson Souza Abreu', 'Elnatã Pereira Alves', 'Emanuele Emili Bernardes Santos', 'Enide Neiva Santos Martins Veloso', 'Fernanda Santos Garcia', 'Filipe Leão Neitzke', 'Gabriel Dallarmi Thomé', 'Gabriela Barszcz Parisotto', 'Gabriela Laurindo', 'Gabriela Santos Vieira Marques', 'Gelson Felisberto Miranda Júnior', 'Giovanna Luiza Susin', 'Giseli da Silveira', 'Guilherme João Nadin', 'Helena Luiza Bez Batti Teles', 'Henrique Avila de Azevedo Nunes', 'Irlan Zeitoun', 'Isabelle Cadore Galli', 'João Lucas Pio da Silva', 'João Matheus Carvalho Lopes', 'João Paulo Pinto de Arruda Abdalla', 'João Vitor Gabrine Mamede', 'Jonathan Monteiro Martins de Mello', 'José Eduardo Cesário Lindote', 'José Eduardo Almeida Araújo', 'Julia Salvatori Piovesan Pereira', 'Juliana Vidotti de Jesus', 'Letícia de Paula Simoni', 'Loise Benites Pinheiro', 'Luana Spagnol Mazzardo', 'Luisa Fontes Cury Roder', 'Maria Eduarda Barroso Assis Silva', 'Maria Eduarda Rech', 'Maria Luiza Cadore', 'Mariah Marques Andrade', 'Mariana de Paula Simoni', 'Mariana Marangon Vieira', 'Mateus Vilacian de Souza Martins', 'Matheus Dallarmi Thomé', 'Matheus de Souza Souto', 'Natália Ferronato', 'Pedro Thomazo Furlanetti Gouvêa Rotta Medeiros', 'Priscila Analú da Silva Previato', 'Rafaela Abdala Rodrigues da Silva', 'Raul José do Nascimento Moreira', 'Renata Fraga de Melo Souza', 'Rodrigo Celestino Nascimento Pazetto', 'Ruan Silva Barros', 'Thaina Gabriely Santiago', 'Valdeci Bernardes Ribeiro Neto', 'Valkmira Izabel de Oliveira Silva', 'Victor Nahuel Carruesco', 'Victoria Bortolo Lucas', 'Vinícius da Costa Marques', 'Vitor Hugo Bressan Marcon', 'Vitor Rogério Menezes Fassbinder', 'Vitória Ellen de Oliveira', 'Vitória Mosa Pulchério', 'Wilson Fernandes da Silva Neto']

def carregar_usuarios():
    with open(USUARIOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_usuarios(data):
    with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

usuarios = carregar_usuarios()
professores = list(usuarios.keys())

def init_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notas (
                    id INTEGER PRIMARY KEY,
                    aluno TEXT,
                    professor TEXT,
                    nota REAL,
                    datahora TEXT
                )
            ''')

init_db()

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        nome = request.form.get("professor")
        senha = request.form.get("senha")
        usuarios = carregar_usuarios()
        if nome in usuarios and senha == usuarios[nome]["senha"]:
            session["usuario"] = nome
            return redirect("/")
        else:
            erro = "Nome ou senha inválidos."
    return render_template("login.html", professores=professores, erro=erro)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/alterar-senha", methods=["GET", "POST"])
def alterar_senha():
    if "usuario" not in session:
        return redirect("/login")
    erro = sucesso = None
    if request.method == "POST":
        atual = request.form["senha_atual"]
        nova = request.form["nova_senha"]
        confirma = request.form["confirmar_senha"]
        usuario = session["usuario"]
        usuarios = carregar_usuarios()
        if atual != usuarios[usuario]["senha"]:
            erro = "Senha atual incorreta."
        elif nova != confirma:
            erro = "Nova senha e confirmação não coincidem."
        else:
            usuarios[usuario]["senha"] = nova
            salvar_usuarios(usuarios)
            sucesso = "Senha alterada com sucesso!"
    return render_template("alterar_senha.html", titulo="Alterar Senha", erro=erro, sucesso=sucesso)

@app.route("/", methods=["GET", "POST"])
def index():
    if "usuario" not in session:
        return redirect("/login")
    usuarios = carregar_usuarios()
    usuario = session["usuario"]
    resultado = None
    if request.method == "POST":
        aluno = request.form.get("aluno")
        nota = request.form.get("nota")
        try:
            nota = float(nota)
            if 0 <= nota <= 10:
                with sqlite3.connect(DB_FILE) as conn:
                    conn.execute("INSERT INTO notas (aluno, professor, nota, datahora) VALUES (?, ?, ?, ?)",
                                 (aluno, usuario, nota, datetime.now().isoformat()))
                resultado = f"Nota registrada com sucesso: {aluno} - {nota}"
            else:
                resultado = "A nota deve estar entre 0 e 10."
        except:
            resultado = "Nota inválida."
    return render_template("index.html", titulo="GERENCIADOR DE NOTAS ETAPA 7 CLÍNICA CIRÚRGICA",
                           alunos=alunos, usuario=usuario,
                           acesso=usuarios[usuario]["acesso_relatorio"], resultado=resultado)

@app.route("/relatorio", methods=["GET", "POST"])
def relatorio():
    if "usuario" not in session:
        return redirect("/login")
    usuarios = carregar_usuarios()
    if not usuarios[session["usuario"]]["acesso_relatorio"]:
        return redirect("/")
    registros = []
    if request.method == "POST":
        aluno = request.form.get("aluno")
        professor = request.form.get("professor")
        data_ini = request.form.get("data_ini")
        data_fim = request.form.get("data_fim")
        query = "SELECT id, aluno, professor, nota, datahora FROM notas WHERE 1=1"
        params = []
        if aluno:
            query += " AND aluno = ?"
            params.append(aluno)
        if professor:
            query += " AND professor = ?"
            params.append(professor)
        if data_ini:
            query += " AND datahora >= ?"
            params.append(data_ini)
        if data_fim:
            query += " AND datahora <= ?"
            params.append(data_fim + 'T23:59:59')
        with sqlite3.connect(DB_FILE) as conn:
            registros = conn.execute(query, params).fetchall()
            with open("export_notas.csv", "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows([["Aluno", "Professor", "Nota", "DataHora"]] + registros)
    return render_template("relatorio.html", titulo="GERENCIADOR DE NOTAS ETAPA 7 CLÍNICA CIRÚRGICA",
                           alunos=alunos, professores=professores, registros=registros)

@app.route("/exportar")
def exportar():
    return send_file("export_notas.csv", as_attachment=True)
