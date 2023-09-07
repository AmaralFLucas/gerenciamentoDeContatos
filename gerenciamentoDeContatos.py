import sys
import sqlite3
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QListWidget, QMessageBox

class CadastroContatos(QMainWindow):
    def __init__(self):
        super().__init__()

        #Configurações de janela principal
        self.setWindowTitle('Cadastro de contatos')
        self.setGeometry(100, 100, 400, 600)

        #Widget central da janela para receber os elementos de layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        #Widgets do layout referente aos dados do contato
        self.lbl_nome = QLabel('Nome')
        self.txt_nome = QLineEdit()
        self.lbl_sobrenome = QLabel('Sobrenome')
        self.txt_sobrenome = QLineEdit()
        self.lbl_email = QLabel('Email')
        self.txt_email = QLineEdit()
        self.lbl_telefone = QLabel('Telefone')
        self.txt_telefone = QLineEdit()

        #Widgets do layout referente ás interações com os contatos da lista
        self.btn_salvar = QPushButton('Adicionar Contato')
        self.btn_editar = QPushButton('Editar Contato')
        self.btn_limpar_campos = QPushButton('Limpar Campos')
        self.btn_remover = QPushButton('Remover Contato')

        #Define as cores dos botões
        self.btn_salvar.setStyleSheet("background-color: lightgreen;"
                                      "border-radius: 5px;"
                                      "border: 2px solid green;")
        self.btn_editar.setStyleSheet("background-color: #F1EB9C;"
                                      "border-radius: 5px;"
                                      "border: 2px solid orange;")
        self.btn_remover.setStyleSheet("background-color: #FFA8A8;"
                                      "border-radius: 5px;"
                                      "border: 2px solid red;")
        self.btn_limpar_campos.setStyleSheet("background-color: #ADD8E6;"
                                             "border-radius: 5px;"
                                             "border: 2px solid blue;")

        #Widget de lista para demonstrar os contatos já cadastrados
        self.lsl_contato = QListWidget()
        self.lsl_contato.itemClicked.connect(self.selecionar_contato)

        #Adiciona os widgets ao layout
        self.layout.addWidget(self.lbl_nome)
        self.layout.addWidget(self.txt_nome)
        self.layout.addWidget(self.lbl_sobrenome)
        self.layout.addWidget(self.txt_sobrenome)
        self.layout.addWidget(self.lbl_email)
        self.layout.addWidget(self.txt_email)
        self.layout.addWidget(self.lbl_telefone)
        self.layout.addWidget(self.txt_telefone)
        self.layout.addWidget(self.lsl_contato)
        self.layout.addWidget(self.btn_salvar)
        self.layout.addWidget(self.btn_editar)
        self.layout.addWidget(self.btn_limpar_campos)
        self.layout.addWidget(self.btn_remover)

        #Criar o banco de dados
        self.criar_banco()

        #Carregar a lista de contatos
        self.carregar_contatos()

        #Validar Contato selecionado
        self.contato_selecionado = None

        #Ações para interação com banco de dados
        self.btn_salvar.clicked.connect(self.salvar_contato)
        self.btn_editar.clicked.connect(self.editar_contato)
        self.btn_limpar_campos.clicked.connect(self.limpar_campos)
        self.btn_remover.clicked.connect(self.remover_contato)

    def criar_banco(self):
        conexao = sqlite3.connect('cadastro_contatos.db')
        cursor = conexao.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS contatos(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    sobrenome TEXT,
                    email TEXT,
                    telefone TEXT
                )
            ''')
        conexao.close()

    def salvar_contato(self):
        nome = self.txt_nome.text()
        sobrenome = self.txt_sobrenome.text()
        email = self.txt_email.text()
        telefone = self.txt_telefone.text()  # Obtenha o número de telefone do campo de entrada

        if nome and sobrenome and email and telefone:  # Verifique se todos os campos estão preenchidos
            conexao = sqlite3.connect('cadastro_contatos.db')
            cursor = conexao.cursor()
            if self.contato_selecionado is None:
                cursor.execute('''
                    INSERT INTO contatos(nome, sobrenome, email, telefone)
                    VALUES (?, ?, ?, ?)
                ''', (nome, sobrenome, email, telefone))
            else:
                cursor.execute('''
                    UPDATE contatos
                    SET nome = ?, sobrenome = ?, email = ?, telefone = ?
                    WHERE ID = ?
                ''', (nome, sobrenome, email, telefone, self.contato_selecionado['id']))

            conexao.commit()
            conexao.close()

            self.txt_nome.clear()
            self.txt_sobrenome.clear()
            self.txt_email.clear()
            self.txt_telefone.clear()
            self.contato_selecionado = None
            self.carregar_contatos()

            if self.btn_salvar.text() == 'Atualizar Contato':
                self.btn_salvar.setText('Adicionar Contato')
                if self.btn_editar.text() == 'Cancelar':
                    self.btn_editar.setText('Editar Contato')
        else:
            QMessageBox.warning(self, 'Aviso', 'Preencha todos os dados')

    def carregar_contatos(self):
        self.lsl_contato.clear()
        conexao = sqlite3.connect('cadastro_contatos.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT id, nome, sobrenome, email, telefone FROM contatos')
        contatos = cursor.fetchall()
        conexao.close()

        for contato in contatos:
            id_contato, nome, sobrenome, email, telefone = contato
            self.lsl_contato.addItem(f'{id_contato} | {nome} {sobrenome} | {email} | {telefone}')

    def selecionar_contato(self, item):
        self.contato_selecionado = {
            'id': item.text().split()[0],
            'nome': self.txt_nome.text(),
            'sobrenome': self.txt_sobrenome.text(),
            'email': self.txt_email.text(),
            'telefone': self.txt_telefone.text()  # Obtenha o número de telefone do campo de entrada
        }

    def editar_contato(self):
        if self.btn_editar.text() == 'Editar Contato':
            if self.contato_selecionado is not None:
                conexao = sqlite3.connect('cadastro_contatos.db')
                cursor = conexao.cursor()
                cursor.execute('SELECT nome, sobrenome, email, telefone FROM contatos '
                               'WHERE id = ?', (self.contato_selecionado['id'],))
                contato = cursor.fetchone()
                conexao.close()

                if contato:
                    nome, sobrenome, email, telefone = contato
                    self.txt_nome.setText(nome)
                    self.txt_sobrenome.setText(sobrenome)
                    self.txt_email.setText(email)
                    self.txt_telefone.setText(telefone)  # Defina o número de telefone no campo de entrada
                    self.btn_salvar.setText('Atualizar Contato')
                    self.btn_editar.setText('Cancelar')
        else:
            self.txt_nome.clear()
            self.txt_sobrenome.clear()
            self.txt_email.clear()
            self.txt_telefone.clear()
            self.btn_salvar.setText('Adicionar Contato')
            self.btn_editar.setText('Editar Contato')

    def validar_remocao(self):
        if self.contato_selecionado is not None:
            mensagem = QMessageBox()
            mensagem.setWindowTitle('Confirmação')
            mensagem.setText('Tem certeza que deseja remover o contato?')
            #Define o texto dos botões de confirmação para sim e não
            botao_sim = mensagem.addButton('Sim', QMessageBox.YesRole)
            botao_nao = mensagem.addButton('Não', QMessageBox.NoRole)
            #Define o icone como questionamento
            mensagem.setIcon(QMessageBox.Question)
            mensagem.exec()

            if mensagem.clickedButton() == botao_sim:
                return True


    def remover_contato(self):
        if self.contato_selecionado is not None:
            if self.validar_remocao():
                conexao = sqlite3.connect('cadastro_contatos.db')
                cursor = conexao.cursor()
                cursor.execute('DELETE FROM contatos '
                               'WHERE id = ?', (self.contato_selecionado['id']))
                conexao.commit()
                conexao.close()
                self.carregar_contatos()
                self.txt_nome.clear()
                self.txt_sobrenome.clear()
                self.txt_email.clear()
                self.contato_selecionado = None

    def limpar_campos(self):
        self.txt_nome.clear()
        self.txt_sobrenome.clear()
        self.txt_email.clear()
        self.txt_telefone.clear()
        self.contato_selecionado = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CadastroContatos()
    window.show()
    sys.exit(app.exec())