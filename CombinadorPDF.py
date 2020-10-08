import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
from fitz import *
import copy
import os

class CombinadorPDF:
    def __init__(self):
        # dicionario com nome como chave e fitz.document como valor
        self.pdf_dict = {}
        # ordem dos pdfs com base na ordem da lista
        self.nome_arquivos = []

    def adicionar_arquivos(self, nome_arquivos):
        # insere nome na lista nome_arquivos
        # e fitz.document como value no pdf_dict

        for nome_arquivo in nome_arquivos:
            self.nome_arquivos.append(nome_arquivo)
            self.pdf_dict[nome_arquivo] = fitz.open(nome_arquivo)

    def excluir_arquivos(self, nome_arquivos):
        # remove itens da lista self.nome_arquivos
        # e values com essas chaves do dicionario pdf

        for nome_arquivo in nome_arquivos:
            self.nome_arquivos.remove(nome_arquivo)
            self.pdf_dict.pop(nome_arquivo)

    def reinserir_antes(self, nome_arquivo):
        # move o item na lista a uma posição anterior

        index = self.nome_arquivos.index(nome_arquivo)
        if index == 0:
            return

        self.nome_arquivos.remove(nome_arquivo)
        self.nome_arquivos.insert(index - 1, nome_arquivo)

    def reinserir_depois(self, nome_arquivo):
        # move o item na lista a uma posição posterior

        index = self.nome_arquivos.index(nome_arquivo)
        if index == len(self.nome_arquivos) - 1:
            return

        self.nome_arquivos.remove(nome_arquivo)
        self.nome_arquivos.insert(index + 1, nome_arquivo)

    def combinar(self):
        # combina os pdfs
        self.fitz_doc_combinado = fitz.open()
        for nome_arquivo in self.nome_arquivos:
            self.fitz_doc_combinado.insertPDF(self.pdf_dict[nome_arquivo])

class PdfFile:
    def __init__(self, nome_arquivo, fitz_doc):
        # juntando informações do pdf
        self.nome = nome_arquivo
        self.fitz_doc = fitz_doc
        self.tamanho = len(self.fitz_doc)
        self.extrair_imagens()

    def extrair_imagens(self):
        # retorna lista de objetos PhotoImage para serem usados com tkinter
        self.lista_imagens = []
        for pagina in range(self.tamanho):
            pix = self.fitz_doc.getPagePixmap(pagina)
            mode = 'RGBA' if pix.alpha else 'RGB'
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            image = image.resize((round(680/pix.height*pix.width), round(680)))
            self.lista_imagens.append(ImageTk.PhotoImage(image))

    def download(self):
        # faz download do pdf
        self.fitz_doc.save(self.nome)

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        # não é possivel colocar menu diretamente no frame
        parent.parent.config(menu=self)

        self.combinadorPDF = parent.combinadorPDF
        self.parent = parent
        self.frame_treeview = parent.frame_treeview
        self.treeview = parent.frame_treeview.treeview

        # arquivos
        self.menu_arquivos = tk.Menu(self)
        self.add_cascade(label='Arquivos',
                         menu=self.menu_arquivos)

        self.menu_arquivos.add_command(
            label='Adicionar arquivos',
            command=lambda: self.frame_treeview.adicionar_arquivos(filedialog.askopenfilenames()))
        self.menu_arquivos.add_command(
            label='Excluir arquivos',
            command=lambda: self.frame_treeview.excluir_arquivos(self.frame_treeview.treeview.selection()))
        self.menu_arquivos.add_command(
            label='Excluir todos os arquivos',
            command=lambda: self.frame_treeview.excluir_arquivos(self.frame_treeview.treeview.get_children()))
        self.menu_arquivos.add_command(
            label='Editar arquivo selecionado',
            command=self.frame_treeview.editar_arquivo)
        self.menu_arquivos.add_command(
            label='Combinar pdfs e fazer download',
            command=self.combinar_pdfs)

        # ordenacao
        self.menu_ordenacao = tk.Menu(self)
        self.add_cascade(label='Ordenação',
                         menu=self.menu_ordenacao)

        self.menu_ordenacao.add_command(
            label='Nome',
            command=lambda: self.ordenar('nome'))
        self.menu_ordenacao.add_command(
            label='Nome com diretório',
            command=lambda: self.ordenar('diretorio'))
        self.menu_ordenacao.add_command(
            label='Data de modificação mais recente',
            command=lambda: self.ordenar('data'))
        self.menu_ordenacao.add_command(
            label='Data de modificação mais antiga',
            command=lambda: self.ordenar('antigo'))

    def adicionar_arquivos(self, nome_arquivos):
        # valida os nomes antes da adiciona-los
        for nome_arquivo in nome_arquivos:
            if nome_arquivo.endswith('.pdf') and nome_arquivo not in self.parent.combinadorPDF.nome_arquivos:
                self.parent.combinadorPDF.adicionar_arquivos([nome_arquivo])
                self.frame_treeview.treeview.insert(
                    parent='', index='end', text=nome_arquivo)

    def excluir_arquivos(self, id_arquivos):
        # exclui arquivos selecionados da treeview

        nome_arquivos = []
        for id_arquivo in id_arquivos:
            nome_arquivos.append(
                self.frame_treeview.treeview.item(id_arquivo, 'text'))
            self.frame_treeview.treeview.delete(id_arquivo)

        self.parent.combinadorPDF.excluir_arquivos(nome_arquivos)

    def ordenar(self, ordenacao):
        # ordena os itens da tabela de acordo com a opçao escolhida

        id_arquivos = self.frame_treeview.treeview.get_children()
        # evitar que apontem para o mesmo objeto
        nome_arquivos = list(self.parent.combinadorPDF.nome_arquivos)

        if ordenacao == 'nome':
            # ordena de acordo com o nome do arquivo ignorando o diretorio
            lista_nomes = []
            for nome_arquivo in nome_arquivos:
                lista_nomes.append(nome_arquivo.split('/')[-1])

            # ordenando a lista nome_arquivos de acordo com a lista_nomes
            sorted = False
            while not sorted:
                sorted = True
                for i in range(len(lista_nomes) - 1):
                    if lista_nomes[i].lower() > lista_nomes[i+1].lower():
                        sorted = False
                        lista_nomes[i], lista_nomes[i +
                                                    1] = lista_nomes[i+1], lista_nomes[i]
                        nome_arquivos[i], nome_arquivos[i +
                                                        1] = nome_arquivos[i+1], nome_arquivos[i]

        elif ordenacao == 'diretorio':
            nome_arquivos.sort(key=str.lower)

        elif ordenacao == 'data':
            nome_arquivos.sort(key=os.path.getmtime)
            nome_arquivos = reversed(nome_arquivos)

        elif ordenacao == 'antigo':
            nome_arquivos.sort(key=os.path.getmtime)

        self.excluir_arquivos(id_arquivos)
        self.adicionar_arquivos(nome_arquivos)

    def combinar_pdfs(self):
        # combina os pdfs e abre janela de exibição
#         filename = filedialog.asksaveasfilename()
        
#         # validacao do nome
#         if not filename:
#             return
#         if not filename.endswith('.pdf'):
#             filename += '.pdf'   
        filename = 'CombinadorPDF'
        self.combinadorPDF.combinar()
        
        top = tk.Toplevel()
        FrameVisualizadorPDF(top,
                            self.combinadorPDF.fitz_doc_combinado,
                            filename)



class FrameTreeview(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.combinadorPDF = parent.combinadorPDF
        
        # treeview
        self.treeview = ttk.Treeview(self)
        self.treeview.heading('#0', text='Arquivos')
        self.treeview.column('#0', stretch=True)
        
        # botoes
        self.botao_mover_cima = tk.Button(self,
                                          text='↑',
                                          command=self.up)
        self.botao_mover_baixo = tk.Button(self,
                                           text='↓',
                                           command=self.down)
        
        # organizando botoes abaixo da treeview em outro frame
        self.frame_botoes = tk.Frame(self)
        self.botao_adicionar = tk.Button(self.frame_botoes,
                                         text='Adicionar',
                                         command=lambda: self.adicionar_arquivos(filedialog.askopenfilenames()),
                                         width=10)
        self.botao_excluir = tk.Button(self.frame_botoes,
                                       text='Excluir',
                                       command=lambda: self.excluir_arquivos(self.treeview.selection()),
                                       width=10)
        self.botao_editar = tk.Button(self.frame_botoes,
                                      text='Editar',
                                      command=self.editar_arquivo,
                                      width=10)
        
        self.botao_mover_cima.grid(row=0, column=0)
        self.treeview.grid(row=0, column=1, sticky='ew')
        self.columnconfigure(1, weight=1)  # expandir treeview
        self.botao_mover_baixo.grid(row=0, column=2)

        self.frame_botoes.grid(row=1, column=0, columnspan=3)
        self.botao_adicionar.grid(row=0, column=0)
        self.botao_excluir.grid(row=0, column=1)
        self.botao_editar.grid(row=0, column=2)

    def adicionar_arquivos(self, nome_arquivos):
        # valida os nomes antes da adiciona-los
        for nome_arquivo in nome_arquivos:
            if nome_arquivo.endswith('.pdf') and nome_arquivo not in self.combinadorPDF.nome_arquivos:
                self.combinadorPDF.adicionar_arquivos([nome_arquivo])
                self.treeview.insert(
                    parent='', index='end', text=nome_arquivo)

    def excluir_arquivos(self, id_arquivos):
        # exclui arquivos selecionados da treeview
        nome_arquivos = []
        for id_arquivo in id_arquivos:
            nome_arquivos.append(self.treeview.item(id_arquivo, 'text'))
            self.treeview.delete(id_arquivo)

        self.combinadorPDF.excluir_arquivos(nome_arquivos)

    def up(self):
        # move a posição do item na treeview para cima
        id_arquivo = self.treeview.selection()[0]
        self.treeview.move(id_arquivo,
                           self.treeview.parent(id_arquivo),
                           self.treeview.index(id_arquivo) - 1)
        # move a posição do item na lista do objeto combinadorPDF
        nome_arquivo = self.treeview.item(id_arquivo, 'text')
        self.combinadorPDF.reinserir_antes(nome_arquivo)

    def down(self):
        # move a posição do item na treeview para baixo
        id_arquivo = self.treeview.selection()[0]
        self.treeview.move(id_arquivo,
                           self.treeview.parent(id_arquivo),
                           self.treeview.index(id_arquivo) + 1)
        # move a posição do item na lista do objeto combinadorPDF
        nome_arquivo = self.treeview.item(id_arquivo, 'text')
        self.combinadorPDF.reinserir_depois(nome_arquivo)

    def editar_arquivo(self):
        # abre o pdf em uma nova janela com opções de edição
        id_arquivo = self.treeview.selection()[0]
        nome_arquivo = self.treeview.item(id_arquivo, 'text')

        top = tk.Toplevel()
        top.title(nome_arquivo)

        FrameVisualizadorPDF(top,
                             self.combinadorPDF.pdf_dict[nome_arquivo],
                             nome_arquivo,
                             self.treeview,
                             self.treeview.selection()[0],
                             self.combinadorPDF)

class FrameVisualizadorPDF(tk.Frame):
    def __init__(self, parent, fitz_doc, nome_arquivo, treeview=None, id_arquivo=None, combinadorPDF=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.id_arquivo = id_arquivo
        self.treeview = treeview
        self.combinadorPDF = combinadorPDF
        self.pdf = PdfFile(nome_arquivo, fitz_doc)

        # widgets
        self.frame_metadados = FrameMetadados(self.parent, self.pdf)
        self.separator = ttk.Separator(parent, orient=tk.VERTICAL)

        self.label_imagem = tk.Label(self,
                                     image=self.pdf.lista_imagens[0])
        # manter segunda referencia
        self.label_imagem.imagem = self.pdf.lista_imagens[0]
        self.label_pagina = tk.Label(self,
                                     text='Pagina 1 de {}'.format(self.pdf.tamanho))
        self.botao_avancar = tk.Button(self,
                                       text='>',
                                       command=lambda: self.forward(1))
        self.botao_voltar = tk.Button(self,
                                      text='<',
                                      state=tk.DISABLED)
        self.botao_excluir = tk.Button(self,
                                       text='Excluir pagina',
                                       command=lambda: self.excluir_pagina(0))
        self.botao_metadados = tk.Button(self,
                                         text='Editar metadados',
                                         command=self.mostrar_metadados)

        # layout
        self.grid(row=0, column=0)

        self.botao_voltar.grid(row=0, column=0)
        self.label_imagem.grid(row=0, column=1, columnspan=2)
        self.botao_avancar.grid(row=0, column=3)
        self.label_pagina.grid(row=1, column=1, columnspan=2)
        self.botao_excluir.grid(row=2, column=1)
        self.botao_metadados.grid(row=2, column=2)

        self.metadados_visiveis = False

    def verifica_botoes(self, pagina):
        # desabilita botao voltar na primeira pagina e avancar na ultima
        if pagina == 0:
            self.botao_voltar = tk.Button(self,
                                          text='<',
                                          state=tk.DISABLED)
        if pagina == self.pdf.tamanho - 1:
            self.botao_avancar = tk.Button(self,
                                           text='>',
                                           state=tk.DISABLED)

    def forward(self, pagina):
        # avança para a proxima pagina no visualizador de pdfs
        self.label_imagem = tk.Label(self,
                                     image=self.pdf.lista_imagens[pagina])
        # manter segunda referencia
        self.label_imagem.imagem = self.pdf.lista_imagens[pagina]
        self.label_pagina = tk.Label(self,
                                     text='Pagina {} de {}'.format(pagina + 1, self.pdf.tamanho))
        self.botao_avancar = tk.Button(self,
                                       text='>',
                                       command=lambda: self.forward(pagina + 1))
        self.botao_voltar = tk.Button(self,
                                      text='<',
                                      command=lambda: self.back(pagina - 1))
        self.botao_excluir = tk.Button(self,
                                       text='Excluir pagina',
                                       command=lambda: self.excluir_pagina(pagina))
        self.botao_metadados = tk.Button(self,
                                         text='Editar metadados',
                                         command=self.mostrar_metadados)

        self.verifica_botoes(pagina)

        self.botao_voltar.grid(row=0, column=0)
        self.label_imagem.grid(row=0, column=1, columnspan=2)
        self.botao_avancar.grid(row=0, column=3)
        self.label_pagina.grid(row=1, column=1, columnspan=2)
        self.botao_excluir.grid(row=2, column=1)

    def back(self, pagina):
        # volta para a pagina anterior no visualizador de pdfs
        self.label_imagem = tk.Label(self,
                                     image=self.pdf.lista_imagens[pagina])
        # manter segunda referencia
        self.label_imagem.imagem = self.pdf.lista_imagens[pagina]
        self.label_pagina = tk.Label(self,
                                     text='Pagina {} de {}'.format(pagina + 1, self.pdf.tamanho))
        self.botao_avancar = tk.Button(self,
                                       text='>',
                                       command=lambda: self.forward(pagina + 1))
        self.botao_voltar = tk.Button(self,
                                      text='<',
                                      command=lambda: self.back(pagina - 1))
        self.botao_excluir = tk.Button(self,
                                       text='Excluir pagina',
                                       command=lambda: self.excluir_pagina(0))
        self.botao_metadados = tk.Button(self,
                                         text='Editar metadados',
                                         command=self.mostrar_metadados)

        self.verifica_botoes(pagina)

        self.botao_voltar.grid(row=0, column=0)
        self.label_imagem.grid(row=0, column=1, columnspan=2)
        self.botao_avancar.grid(row=0, column=3)
        self.label_pagina.grid(row=1, column=1, columnspan=2)
        self.botao_excluir.grid(row=2, column=1)

    def excluir_pagina(self, pagina):
        # exclui a pagina do pdf sendo exibida

        # removendo referencias a pagina
        self.pdf.lista_imagens.remove(self.pdf.lista_imagens[pagina])
        self.pdf.fitz_doc.deletePage(pagina)
        self.pdf.tamanho = self.pdf.tamanho - 1

        # mudando pagina exibida
        if self.pdf.tamanho == 0:
            # try caso nao tenha id
            # chamado pelo metodo combinar_pdfs
            try: 
                nome_arquivo = self.treeview.item(self.id_arquivo, 'text')
                self.treeview.delete(self.id_arquivo)
                self.combinadorPDF.excluir_arquivos([nome_arquivo])
            finally:
                self.parent.destroy()
                return

        if pagina == 0:
            self.back(pagina)
        elif pagina == 1:
            self.back(pagina - 1)
        else:
            self.forward(pagina - 1)

    def mostrar_metadados(self):
        if self.metadados_visiveis:
            self.metadados_visiveis = False
            self.separator.grid_forget()
            self.frame_metadados.grid_forget()
        else:
            self.metadados_visiveis = True
            self.separator.grid(row=0, column=1, sticky='ns', padx=15)
            self.frame_metadados.grid(row=0, column=2)

class FrameMetadados(tk.Frame):
    def __init__(self, parent, pdf):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.pdf = pdf

        # blocos com label e entry dentro de um frame com pady para distancia-los uns dos outros
        self.frame_format = tk.Frame(self)
        self.label_format = tk.Label(self.frame_format, text='Formato')
        self.entry_format = tk.Entry(self.frame_format, width=50)
        self.insert('format', self.entry_format)
        self.frame_format.pack(pady=15)
        self.label_format.pack()
        self.entry_format.pack()

        self.frame_title = tk.Frame(self)
        self.label_title = tk.Label(self.frame_title, text='Título')
        self.entry_title = tk.Entry(self.frame_title, width=50)
        self.insert('title', self.entry_title)
        self.frame_title.pack(pady=15)
        self.label_title.pack()
        self.entry_title.pack()

        self.frame_author = tk.Frame(self)
        self.label_author = tk.Label(self.frame_author, text='Autor')
        self.entry_author = tk.Entry(self.frame_author, width=50)
        self.insert('author', self.entry_author)
        self.frame_author.pack(pady=15)
        self.label_author.pack()
        self.entry_author.pack()

        self.frame_subject = tk.Frame(self)
        self.label_subject = tk.Label(self.frame_subject, text='Assunto')
        self.entry_subject = tk.Entry(self.frame_subject, width=50)
        self.insert('subject', self.entry_subject)
        self.frame_subject.pack(pady=15)
        self.label_subject.pack()
        self.entry_subject.pack()

        self.frame_keywords = tk.Frame(self)
        self.label_keywords = tk.Label(
            self.frame_keywords, text='Palavras-chave')
        self.entry_keywords = tk.Entry(self.frame_keywords, width=50)
        self.insert('keywords', self.entry_keywords)
        self.frame_keywords.pack(pady=15)
        self.label_keywords.pack()
        self.entry_keywords.pack()

        self.frame_creator = tk.Frame(self)
        self.label_creator = tk.Label(self.frame_creator, text='Criador')
        self.entry_creator = tk.Entry(self.frame_creator, width=50)
        self.insert('creator', self.entry_creator)
        self.frame_creator.pack(pady=15)
        self.label_creator.pack()
        self.entry_creator.pack()

        self.frame_producer = tk.Frame(self)
        self.label_producer = tk.Label(self.frame_producer, text='Produtor')
        self.entry_producer = tk.Entry(self.frame_producer, width=50)
        self.insert('producer', self.entry_producer)
        self.frame_producer.pack(pady=15)
        self.label_producer.pack()
        self.entry_producer.pack()

        self.frame_creation_date = tk.Frame(self)
        self.label_creation_date = tk.Label(
            self.frame_creation_date,
            text='Data de criação')
        self.entry_creation_date = tk.Entry(
            self.frame_creation_date,
            width=50)
        self.insert('creationDate', self.entry_creation_date)
        self.frame_creation_date.pack(pady=15)
        self.label_creation_date.pack()
        self.entry_creation_date.pack()

        self.frame_mod_date = tk.Frame(self)
        self.label_mod_date = tk.Label(
            self.frame_mod_date, text='Data de Modificação')
        self.entry_mod_date = tk.Entry(self.frame_mod_date, width=50)
        self.insert('modDate', self.entry_mod_date)
        self.frame_mod_date.pack(pady=15)
        self.label_mod_date.pack()
        self.entry_mod_date.pack()

        self.frame_encryption = tk.Frame(self)
        self.label_encryption = tk.Label(
            self.frame_encryption, text='Criptografia')
        self.entry_encryption = tk.Entry(self.frame_encryption, width=50)
        self.insert('encryption', self.entry_encryption)
        self.frame_encryption.pack(pady=15)
        self.label_encryption.pack()
        self.entry_encryption.pack()

        self.botao_salvar_metadados = tk.Button(self,
                                                text='Salvar',
                                                state=tk.DISABLED)
        self.botao_salvar_metadados.pack()

    def insert(self, metadata, entry):
        # insere o texto e desabilita o widget
        if self.pdf.fitz_doc.metadata[metadata]:
            entry.insert(0, self.pdf.fitz_doc.metadata[metadata])
        entry.configure(state=tk.DISABLED)

class MainApplication(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        parent.title('CombinadorPDF')
        parent.geometry('330x270')
        self.parent = parent

        # objeto para manter os pdfs
        self.combinadorPDF = CombinadorPDF()

        # widgets
        self.frame_treeview = FrameTreeview(self)
        self.menu_bar = MenuBar(self)

        self.pack(fill=tk.BOTH, expand=1)
        self.frame_treeview.pack(fill=tk.BOTH, expand=1)

if __name__ == '__main__':
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()
