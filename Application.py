from tkinter import *
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from tkinter import ttk
from CombinadorPDF import *
import os

class Application:
    def __init__(self, master):
        "cria widgets na tela inicial"

        self.master = master
        self.master.title('CombinadorPDF')
        self.master.geometry('330x330')

        # frame em que serao colocados os widgets
        self.frame_tabela = Frame(self.master)
        self.frame_tabela.pack(fill=BOTH, expand=1)

        # menu
        self.menu = Menu(self.frame_tabela)
        self.master.config(menu=self.menu)

        self.menu_arquivos = Menu(self.menu)
        self.menu.add_cascade(label='Arquivos', menu=self.menu_arquivos)

        self.menu_arquivos.add_command(
            label='Adicionar arquivos', command=lambda: self.adicionar_arquivos(askopenfilenames()))
        self.menu_arquivos.add_command(label='Excluir arquivo selecionado',
                                       command=lambda: self.excluir_arquivos(self.tabela.selection()))
        self.menu_arquivos.add_command(
            label='Editar arquivo selecionado', command=lambda: self.editar_arquivo(self.tabela.selection()))
        self.menu_arquivos.add_command(
            label='Excluir todos registros', command=lambda: self.excluir_arquivos(self.tabela.get_children()))

        self.menu_ordenacao = Menu(self.menu)
        self.menu.add_cascade(label='Opções de ordenação',
                              menu=self.menu_ordenacao)

        self.menu_ordenacao.add_command(
            label='Nome', command=lambda: self.ordenar_tabela('nome'))
        self.menu_ordenacao.add_command(
            label='Nome com diretório', command=lambda: self.ordenar_tabela('diretorio'))
        self.menu_ordenacao.add_command(
            label='Data de modificação mais recente', command=lambda: self.ordenar_tabela('data'))
        self.menu_ordenacao.add_command(
            label='Data de modificação mais antiga', command=lambda: self.ordenar_tabela('antigo'))

        # tabela utilizando treeview
        self.tabela = ttk.Treeview(self.frame_tabela)

        self.tabela.heading('#0', text='Arquivos')
        self.tabela.column('#0', stretch=True)

        # botoes
        # frame para colocar os botoes abaixo da tabela com grid layout
        self.frame_botoes = Frame(self.frame_tabela)
        self.botao_adicionar = Button(
            self.frame_botoes, text='Adicionar', command=lambda: self.adicionar_arquivos(askopenfilenames()))
        self.botao_excluir = Button(self.frame_botoes, text='Excluir',
                                    command=lambda: self.excluir_arquivos(self.tabela.selection()))
        self.botao_editar = Button(
            self.frame_botoes, text='Editar', command=lambda: self.editar_arquivo(self.tabela.selection()))
        self.botao_mover_cima = Button(
            self.frame_tabela, text='↑', command=lambda: self.mover_cima(self.tabela.selection()[0]))
        self.botao_mover_baixo = Button(
            self.frame_tabela, text='↓', command=lambda: self.mover_baixo(self.tabela.selection()[0]))

        self.botao_mover_cima.pack(side=LEFT)
        self.botao_mover_baixo.pack(side=RIGHT)
        self.tabela.pack(fill=X, expand=1, pady=10)
        self.frame_botoes.pack()
        self.botao_adicionar.grid(row=0, column=0)
        self.botao_excluir.grid(row=0, column=1)
        self.botao_editar.grid(row=0, column=2)

    def mover_cima(self, arquivo_selecionado):
        "troca a posição de dois arquivos na tabela, colocando o arquivo selecionado uma posição a frente"
        self.tabela.move(arquivo_selecionado, self.tabela.parent(
            arquivo_selecionado), self.tabela.index(arquivo_selecionado)-1)

    def mover_baixo(self, arquivo_selecionado):
        "similar ao mover_cima(), mas move o arquivo para baixo"
        self.tabela.move(arquivo_selecionado, self.tabela.parent(
            arquivo_selecionado), self.tabela.index(arquivo_selecionado)+1)

    def adicionar_arquivos(self, arquivos_selecionados):
        "adiciona os arquivos em formato pdf selecionados"
        for a in arquivos_selecionados:
            if a.endswith('.pdf'):
                self.tabela.insert(parent='', index='end', text=a)

    def excluir_arquivos(self, arquivos_selecionados):
        "exclui os arquivos selecionados da tabela"
        for a in arquivos_selecionados:
            self.tabela.delete(a)

    def get_itens_tabela(self):
        "retorna diretamente o texto dos itens da tabela em vez do id com o metodo get_children()"
        ids = self.tabela.get_children()
        itens = []
        for id in ids:
            itens.append(self.tabela.item(id, 'text'))

        return itens

    def ordenar_tabela(self, ordenacao):
        "ordena os itens da tabela de acordo o parametro passado para ordenacao"

        ids = self.tabela.get_children()
        itens = self.get_itens_tabela()

        if ordenacao == 'nome':
            # pega o nome ignorando o diretorio
            lista_nomes = []
            for item in itens:
                lista_nomes.append(item.split('/')[-1])

            # utilizando trecho de codigo de bubble sort em vez de .sort(str.lower)
            # para fazer as mesmas alterações feitas na lista_nomes em itens
            sorted = False
            while not sorted:
                sorted = True
                for i in range(len(lista_nomes) - 1):
                    if lista_nomes[i+1].lower() < lista_nomes[i].lower():
                        sorted = False
                        lista_nomes[i+1], lista_nomes[i] = lista_nomes[i], lista_nomes[i+1]
                        itens[i+1], itens[i] = itens[i], itens[i+1]

        elif ordenacao == 'diretorio':
            itens.sort(key=str.lower)

        elif ordenacao == 'data':
            itens.sort(key=os.path.getmtime)
            itens = reversed(itens)
            
        elif ordenacao == 'antigo':
            itens.sort(key=os.path.getmtime)

        self.excluir_arquivos(ids)
        self.adicionar_arquivos(itens)

    def editar_arquivo(self, id_item_selecionado):
        '''
        cria nova janela com opções de ediçao
        inicializa widgets que serão usados
        '''

        # pegando informaçao necessaria
        arquivo_selecionado = self.tabela.item(id_item_selecionado, 'text')
        self.combinadorPDF = CombinadorPDF(arquivo_selecionado)
        self.combinadorPDF.extrair_dados()

        # abrindo nova janela e inicializando widgets
        self.window = Toplevel()
        self.window.title(arquivo_selecionado)

        self.frame_imagem = Frame(self.window)
        self.frame_imagem.grid(row=0, column=0)

        self.label_imagem = Label(
            self.frame_imagem, image=self.combinadorPDF.lista_imagens[0])
        self.label_imagem.imagem = self.combinadorPDF.lista_imagens[0]
        self.label_pagina_atual = Label(
            self.frame_imagem, text='Pagina 1 de {}'.format(self.combinadorPDF.tamanho_arquivo))
        self.botao_avancar = Button(self.frame_imagem, text='>')
        self.botao_voltar = Button(self.frame_imagem, text='<', state=DISABLED)
        self.botao_deletar = Button(self.frame_imagem, text='Deletar página')
        self.botao_metadados = Button(
            self.frame_imagem, text='Editar metadados', command=self.editar_metadados)

        self.botao_voltar.grid(row=0, column=0)
        self.label_imagem.grid(row=0, column=1, columnspan=2)
        self.botao_avancar.grid(row=0, column=3)
        self.label_pagina_atual.grid(row=1, column=1, columnspan=2)
        self.botao_deletar.grid(row=2, column=1)
        self.botao_metadados.grid(row=2, column=2)

        # visualizaçao do frame contendo metadados
        self.metadados_visiveis = False

    def editar_metadados(self):
        '''
        quando nao está visivel inicializa os widgets com os metadados do arquivo ja preenchidos
        caso contrario destroi o frame para deixa-lo invisivel
        '''

        if self.metadados_visiveis:
            self.metadados_visiveis = False
            self.separator.destroy()
            self.frame_metadados.destroy()
        else:
            # definindo frame e separator
            self.metadados_visiveis = True
            self.frame_metadados = Frame(self.window)
            self.separator = ttk.Separator(self.window, orient=VERTICAL)
            self.separator.grid(row=0, column=1, sticky='ns', padx=15)
            self.frame_metadados.grid(row=0, column=2)

            # blocos com label e entry dentro de um frame com pady para distancia-los uns dos outros
            self.frame_format = Frame(self.frame_metadados)
            self.label_format = Label(self.frame_format, text='Format')
            self.entry_format = Entry(self.frame_format, width=50)
            self.frame_format.pack(pady=15)
            self.label_format.pack()
            self.entry_format.pack()

            self.frame_title = Frame(self.frame_metadados)
            self.label_title = Label(self.frame_title, text='Title')
            self.entry_title = Entry(self.frame_title, width=50)
            self.frame_title.pack(pady=15)
            self.label_title.pack()
            self.entry_title.pack()

            self.frame_author = Frame(self.frame_metadados)
            self.label_author = Label(self.frame_author, text='Author')
            self.entry_author = Entry(self.frame_author, width=50)
            self.frame_author.pack(pady=15)
            self.label_author.pack()
            self.entry_author.pack()

            self.frame_subject = Frame(self.frame_metadados)
            self.label_subject = Label(self.frame_subject, text='Subject')
            self.entry_subject = Entry(self.frame_subject, width=50)
            self.frame_subject.pack(pady=15)
            self.label_subject.pack()
            self.entry_subject.pack()

            self.frame_keywords = Frame(self.frame_metadados)
            self.label_keywords = Label(self.frame_keywords, text='Keywords')
            self.entry_keywords = Entry(self.frame_keywords, width=50)
            self.frame_keywords.pack(pady=15)
            self.label_keywords.pack()
            self.entry_keywords.pack()

            self.frame_creator = Frame(self.frame_metadados)
            self.label_creator = Label(self.frame_creator, text='Creator')
            self.entry_creator = Entry(self.frame_creator, width=50)
            self.frame_creator.pack(pady=15)
            self.label_creator.pack()
            self.entry_creator.pack()

            self.frame_producer = Frame(self.frame_metadados)
            self.label_producer = Label(self.frame_producer, text='Producer')
            self.entry_producer = Entry(self.frame_producer, width=50)
            self.frame_producer.pack(pady=15)
            self.label_producer.pack()
            self.entry_producer.pack()

            self.frame_creation_date = Frame(self.frame_metadados)
            self.label_creation_date = Label(
                self.frame_creation_date, text='Creation Date')
            self.entry_creation_date = Entry(
                self.frame_creation_date, width=50)
            self.frame_creation_date.pack(pady=15)
            self.label_creation_date.pack()
            self.entry_creation_date.pack()

            self.frame_mod_date = Frame(self.frame_metadados)
            self.label_mod_date = Label(self.frame_mod_date, text='Mod Date')
            self.entry_mod_date = Entry(self.frame_mod_date, width=50)
            self.frame_mod_date.pack(pady=15)
            self.label_mod_date.pack()
            self.entry_mod_date.pack()

            self.frame_encryption = Frame(self.frame_metadados)
            self.label_encryption = Label(
                self.frame_encryption, text='Encryption')
            self.entry_encryption = Entry(self.frame_encryption, width=50)
            self.frame_encryption.pack(pady=15)
            self.label_encryption.pack()
            self.entry_encryption.pack()

            self.botao_salvar_metadados = Button(
                self.frame_metadados, text='Salvar')
            self.botao_salvar_metadados.pack()

            # evitar erros quando certo atributo for None
            if self.combinadorPDF.pdf.metadata['format']:
                self.entry_format.insert(
                    0, self.combinadorPDF.pdf.metadata['format'])
            if self.combinadorPDF.pdf.metadata['title']:
                self.entry_title.insert(
                    0, self.combinadorPDF.pdf.metadata['title'])
            if self.combinadorPDF.pdf.metadata['author']:
                self.entry_author.insert(
                    0, self.combinadorPDF.pdf.metadata['author'])
            if self.combinadorPDF.pdf.metadata['subject']:
                self.entry_subject.insert(
                    0, self.combinadorPDF.pdf.metadata['subject'])
            if self.combinadorPDF.pdf.metadata['keywords']:
                self.entry_keywords.insert(
                    0, self.combinadorPDF.pdf.metadata['keywords'])
            if self.combinadorPDF.pdf.metadata['creator']:
                self.entry_creator.insert(
                    0, self.combinadorPDF.pdf.metadata['creator'])
            if self.combinadorPDF.pdf.metadata['producer']:
                self.entry_producer.insert(
                    0, self.combinadorPDF.pdf.metadata['producer'])
            if self.combinadorPDF.pdf.metadata['creationDate']:
                self.entry_creation_date.insert(
                    0, self.combinadorPDF.pdf.metadata['creationDate'])
            if self.combinadorPDF.pdf.metadata['modDate']:
                self.entry_mod_date.insert(
                    0, self.combinadorPDF.pdf.metadata['modDate'])
            if self.combinadorPDF.pdf.metadata['encryption']:
                self.entry_encryption.insert(
                    0, self.combinadorPDF.pdf.metadata['encryption'])

if __name__ == '__main__':
    root = Tk()
    Application(root)
    root.mainloop()
