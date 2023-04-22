
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from mysql.connector import errorcode

print("Conectando...")
try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='rato',
    )

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('Existe algo errado no nome de usuário ou senha')
    else:
        print(err)

cursor = conn.cursor()

cursor.execute("DROP DATABASE IF EXISTS `Integra1`;")

cursor.execute("CREATE DATABASE `Integra1`;")

cursor.execute("USE `Integra1`;")

# criando tabelas
TABLES = {}
TABLES['Integrantes'] = ('''
      CREATE TABLE `Integrantes` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `nome` varchar(50) NOT NULL,
      `altura` varchar(40) NOT NULL,
      `idade` varchar(20) NOT NULL,
      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['Usuarios'] = ('''
      CREATE TABLE `usuarios` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `nome`  varchar(20) NOT NULL,
      `senha` varchar(100) NOT NULL,
      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

for tabela_nome in TABLES:
    tabela_sql = TABLES[tabela_nome]
    try:
        print('Criando tabela {}:'.format(tabela_nome), end=' ')
        cursor.execute(tabela_sql)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print('Já existe')
        else:
            print(err.msg)
    else:
        print('OK')


class Integra:
    def __init__(self, nome, idade, altura):
        self.nome = nome
        self.idade = idade
        self.altura = altura

listaIntegrantes = [] 

class Usuario:
    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha

ListaUsuarios = []

app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/')
def index():
    return render_template('templates.html', titulo = 'Integrantes', integrantes=listaIntegrantes)

@app.route("/new")
def new():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Faça o login para adicionar um integrante')
        return redirect('/login')
    return render_template("newTemplate.html", titulo = 'Novo Integrante')

Integrantes_sql = 'INSERT INTO Integrantes (nome, idade, altura) VALUES (%s, %s, %s)'
Integrantes = [
    ('Trigoni', '60', '1,49'),
    ("Roberto", "78", '1,59')
]

@app.route("/criar", methods=['POST'])
def criar():
    nome = request.form['nome']
    altura = request.form['altura']
    idade = request.form['idade']
    integrante = Integra(nome, idade, altura)
    dados = (nome, altura, idade)
    listaIntegrantes.append(integrante)
    Integrantes.append(dados)
    return redirect('/')

cursor.executemany(Integrantes_sql, Integrantes)

cursor.execute('select * from Integra1.Integrantes')
print('\n Nome ---- Altura ---- Idade ----')
for i in cursor.fetchall():
    print(i[1],'    ', i[2],'    ', i[3])
print('\n')

@app.route("/login")
def login():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return render_template('login.html', titulo='Login')
    else:
        flash('Olá ' + session['usuario_logado'] + ' você já está logado')
        return redirect('/')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    for i in ListaUsuarios:
        if i.senha == request.form['senha'] and i.nome == request.form['usuario']:
            session['usuario_logado'] = request.form['usuario']
            flash('Olá ' + session['usuario_logado'] + ' bem vindo!')
            return redirect('/')
    flash('Senha ou usuario incorretos')
    return redirect('/login')

@app.route('/logout')
def logout():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        flash('Você ainda não efetuou o login')
        return redirect('/')
    else:
        session['usuario_logado'] = None
        flash('Logout efetuado com sucesso!')
        return redirect('/')

@app.route('/cadastro')
def cadastro():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return render_template("cadastro.html", titulo = 'Cadastro')
    else:
        flash('Você já está cadastrado')
        return redirect('/')
        

usuario_sql = 'INSERT INTO usuarios (nome, senha) VALUES (%s, %s)'
usuarios = [
    ("Trigoni", "senha"),
    ("Roberto", "pypy")
]

@app.route("/criarUsuario", methods=['POST'])
def criarUsuario():
    nome = request.form['nome1']
    senha = request.form['senha1']
    user = Usuario(nome, senha)
    ListaUsuarios.append(user)
    dadosUsuario = (nome, senha)
    usuarios.append(dadosUsuario)
    return redirect('/login')

cursor.executemany(usuario_sql, usuarios)

cursor.execute('select * from Integra1.usuarios')
print('\nUsuários ---- Senha ----')
for i in cursor.fetchall():
    print(i[1],'     ', i[2])

# commitando se não nada tem efeito
conn.commit()

cursor.close()
conn.close()

app.run(debug=True)