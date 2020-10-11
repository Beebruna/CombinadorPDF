import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
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
    def __init__(self, fitz_doc):
        # juntando informações do pdf
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

    def download(self, filename):
        # faz download do pdf
        self.nome = filename

        # validacao do nome
        if not self.nome:
            return
        if not self.nome.endswith('.pdf'):
            self.nome += '.pdf'

        self.fitz_doc.save(self.nome)

    def excluir_pagina(self, pagina):
        # exclui pagina e atualiza atributos
        self.fitz_doc.deletePage(pagina)
        self.pdf.tamanho = self.pdf.tamanho - 1


class MenuBarMain(tk.Menu):
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

        # download
        self.menu_download = tk.Menu(self)
        self.add_cascade(label='Download',
                         menu=self.menu_download)

        self.menu_download.add_cascade(label='Combinar e baixar',
                                       command=self.combinar_pdfs)
        self.menu_download.add_command(label='Baixar como imagem')

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
        self.combinadorPDF.combinar()

        top = tk.Toplevel()
        FrameVisualizadorPDF(top,
                             self.combinadorPDF.fitz_doc_combinado)


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
                                         command=lambda: self.adicionar_arquivos(
                                             filedialog.askopenfilenames()),
                                         width=10)
        self.botao_excluir = tk.Button(self.frame_botoes,
                                       text='Excluir',
                                       command=lambda: self.excluir_arquivos(
                                           self.treeview.selection()),
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
#         top.title(nome_arquivo)

        FrameVisualizadorPDF(top,
                             self.combinadorPDF.pdf_dict[nome_arquivo],
                             nome_arquivo,
                             self.treeview,
                             self.treeview.selection()[0],
                             self.combinadorPDF)


class MenuVisualizadorPDF(tk.Menu):
    def __init__(self, frame_pdf):
        self.parent = frame_pdf.parent
        tk.Menu.__init__(self, self.parent)
        self.parent.config(menu=self)
        self.pdf = frame_pdf.pdf
        self.separator = frame_pdf.separator
        self.treeview = frame_pdf.treeview
        self.frame_pdf = frame_pdf
        self.metadados_visiveis = False

        self.frame_metadados = FrameMetadados(frame_pdf.parent, self.pdf)

        self.add_command(label='Excluir página',
                         command=lambda: self.excluir_pagina(self.frame_pdf.scale.get() - 1))
        self.add_command(label='Selecionar páginas',
                         command=self.selecionar_paginas)
        self.add_command(label='Editar metadados',
                         command=self.mostrar_metadados)
        self.add_command(label='Baixar',
                         command=self.salvar)

    def excluir_pagina(self, pagina):
        # exclui a pagina do pdf sendo exibida

        # removendo referencias a pagina
        self.pdf.lista_imagens.remove(self.pdf.lista_imagens[pagina])
        self.pdf.excluir_pagina(pagina)

        # mudando pagina exibida
        if self.pdf.tamanho == 0:
            # try caso nao tenha id
            # chamado pelo metodo combinar_pdfs
            try:
                self.treeview.delete(self.id_arquivo)
                self.combinadorPDF.excluir_arquivos([self.nome_arquivo])
            finally:
                self.parent.destroy()
                return

        if pagina == 0:
            self.atualizar_pagina(pagina)
        else:
            self.atualizar_pagina(pagina - 1)

    def selecionar_paginas(self):
        # seleciona páginas específicas do pdf e exclui o resto

        paginas_selecionadas = simpledialog.askstring(title='Páginas selecionadas',
                                                      prompt='Intervalo de 1 a 5 e 7 a 9 como 1-5,7-9',
                                                      parent=self.frame_pdf)

        if not paginas_selecionadas:
            return

        # interpretando string e excluindo
        fitz_doc = fitz.open()
        intervalos = paginas_selecionadas.split(',')
        for intervalo in intervalos:
            paginas = intervalo.split('-')
            fitz_doc.insertPDF(self.pdf.fitz_doc, 
                               from_page=int(paginas[0]), to_page=int(paginas[1]))

        # atualizando widgets
        self.frame_pdf.pdf = PdfFile(fitz_doc)
        self.frame_pdf.scale.configure(to=self.frame_pdf.pdf.tamanho)
        self.frame_pdf.atualizar_pagina(0)

    def mostrar_metadados(self):
        # mostra/esconde frame com opção de editar metadados
        if self.metadados_visiveis:
            self.metadados_visiveis = False
            self.separator.grid_forget()
            self.frame_metadados.grid_forget()
        else:
            self.metadados_visiveis = True
            self.separator.grid(row=0, column=1, sticky='ns', padx=15)
            self.frame_metadados.grid(row=0, column=2)

    def salvar(self):
        # salva as modificações no pdf em outro arquivo
        filename = filedialog.asksaveasfilename()
        self.pdf.download(filename)

    def excluir_pagina(self, pagina):
        # exclui a pagina do pdf sendo exibida

        # removendo referencias a pagina
        self.pdf.lista_imagens.remove(self.pdf.lista_imagens[pagina])
        self.pdf.fitz_doc.deletePage(pagina)
        self.pdf.tamanho = self.pdf.tamanho - 1
        self.frame_pdf.scale.config(to=self.pdf.tamanho)

        # mudando pagina exibida
        if self.pdf.tamanho == 0:
            # try caso nao tenha id
            # chamado pelo metodo combinar_pdfs
            try:
                self.treeview.delete(self.id_arquivo)
                self.combinadorPDF.excluir_arquivos([self.nome_arquivo])
            finally:
                self.parent.destroy()
                return

        if pagina == 0:
            self.frame_pdf.atualizar_pagina(pagina)
        else:
            self.frame_pdf.atualizar_pagina(pagina - 1)


class FrameVisualizadorPDF(tk.Frame):
    def __init__(self, parent, fitz_doc, nome_arquivo=None, treeview=None, id_arquivo=None, combinadorPDF=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.id_arquivo = id_arquivo
        self.treeview = treeview
        self.combinadorPDF = combinadorPDF
        self.pdf = PdfFile(fitz_doc)

        # widgets
        self.separator = ttk.Separator(parent,
                                       orient=tk.VERTICAL)
        self.menu = MenuVisualizadorPDF(self)

        self.label_imagem = tk.Label(self,
                                     image=self.pdf.lista_imagens[0])
        # manter segunda referencia
        self.label_imagem.imagem = self.pdf.lista_imagens[0]

        self.scale = tk.Scale(
            self,
            from_=1, to=self.pdf.tamanho,
            orient=tk.HORIZONTAL,
            command=lambda pagina: self.atualizar_pagina(pagina, 'scale'),
            showvalue=0)

        self.label_pagina = tk.Label(
            self,
            text='Página 1 de {}'.format(self.pdf.tamanho))

        self.botao_avancar = tk.Button(
            self,
            text='>',
            command=lambda: self.atualizar_pagina(self.scale.get()))
        self.botao_voltar = tk.Button(
            self,
            text='<',
            command=lambda: self.atualizar_pagina(self.scale.get() - 2),
            state=tk.DISABLED)
        self.botao_excluir = tk.Button(
            self,
            text='Excluir pagina',
            command=lambda: self.excluir_pagina(self.scale.get() - 1))

        # layout
        self.grid(row=0, column=0)

        self.botao_voltar.grid(row=0, column=0)
        self.label_imagem.grid(row=0, column=1)
        self.botao_avancar.grid(row=0, column=2)
        self.label_pagina.grid(row=1, column=1)
        self.scale.grid(row=2, column=0, columnspan=3, sticky='ew')

    def atualizar_pagina(self, pagina, widget='botao'):
        # atualiza a pagina, mudando a imagem exibida

        # verificando de qual widget vem o comando
        if widget == 'scale':
            pagina = int(pagina) - 1
        else:
            self.scale.set(pagina + 1)

        # atualizando imagem e mantendo segunda referencia
        self.label_imagem.configure(image=self.pdf.lista_imagens[pagina])
        self.label_imagem.imagem = self.pdf.lista_imagens[pagina]

        self.label_pagina.configure(text='Página {} de {}'.format(
            self.scale.get(), len(self.pdf.fitz_doc)))
        # atualizando estado dos botoes
        if pagina == 0:
            self.botao_voltar.configure(state=tk.DISABLED)
        else:
            self.botao_voltar.configure(state=tk.NORMAL)

        if pagina == self.pdf.tamanho - 1:
            self.botao_avancar.configure(state=tk.DISABLED)
        else:
            self.botao_avancar.configure(state=tk.NORMAL)


class FrameMetadados(tk.Frame):
    def __init__(self, parent, pdf):
        tk.Frame.__init__(self, parent)
        self.parent=parent
        self.pdf=pdf

        # blocos com label e entry dentro de um frame com pady para distancia-los uns dos outros
        self.frame_format=tk.Frame(self)
        self.label_format=tk.Label(self.frame_format, text='Formato')
        self.entry_format=tk.Entry(self.frame_format, width=50)
        self.insert('format', self.entry_format)
        self.frame_format.pack(pady=15)
        self.label_format.pack()
        self.entry_format.pack()

        self.frame_title=tk.Frame(self)
        self.label_title=tk.Label(self.frame_title, text='Titulo')
        self.entry_title=tk.Entry(self.frame_title, width=50)
        self.insert('title', self.entry_title)
        self.frame_title.pack(pady=15)
        self.label_title.pack()
        self.entry_title.pack()

        self.frame_author=tk.Frame(self)
        self.label_author=tk.Label(self.frame_author, text='Autor')
        self.entry_author=tk.Entry(self.frame_author, width=50)
        self.insert('author', self.entry_author)
        self.frame_author.pack(pady=15)
        self.label_author.pack()
        self.entry_author.pack()

        self.frame_subject=tk.Frame(self)
        self.label_subject=tk.Label(self.frame_subject, text='Assunto')
        self.entry_subject=tk.Entry(self.frame_subject, width=50)
        self.insert('subject', self.entry_subject)
        self.frame_subject.pack(pady=15)
        self.label_subject.pack()
        self.entry_subject.pack()

        self.frame_keywords=tk.Frame(self)
        self.label_keywords=tk.Label(
            self.frame_keywords, text='Palavras-chave')
        self.entry_keywords=tk.Entry(self.frame_keywords, width=50)
        self.insert('keywords', self.entry_keywords)
        self.frame_keywords.pack(pady=15)
        self.label_keywords.pack()
        self.entry_keywords.pack()

        self.frame_creator=tk.Frame(self)
        self.label_creator=tk.Label(self.frame_creator, text='Criador')
        self.entry_creator=tk.Entry(self.frame_creator, width=50)
        self.insert('creator', self.entry_creator)
        self.frame_creator.pack(pady=15)
        self.label_creator.pack()
        self.entry_creator.pack()

        self.frame_producer=tk.Frame(self)
        self.label_producer=tk.Label(self.frame_producer, text='Produtor')
        self.entry_producer=tk.Entry(self.frame_producer, width=50)
        self.insert('producer', self.entry_producer)
        self.frame_producer.pack(pady=15)
        self.label_producer.pack()
        self.entry_producer.pack()

        self.frame_creation_date=tk.Frame(self)
        self.label_creation_date=tk.Label(
            self.frame_creation_date,
            text='Data de criação')
        self.entry_creation_date=tk.Entry(
            self.frame_creation_date,
            width=50)
        self.insert('creationDate', self.entry_creation_date)
        self.frame_creation_date.pack(pady=15)
        self.label_creation_date.pack()
        self.entry_creation_date.pack()

        self.frame_mod_date=tk.Frame(self)
        self.label_mod_date=tk.Label(
            self.frame_mod_date, text='Data de modificação')
        self.entry_mod_date=tk.Entry(self.frame_mod_date, width=50)
        self.insert('modDate', self.entry_mod_date)
        self.frame_mod_date.pack(pady=15)
        self.label_mod_date.pack()
        self.entry_mod_date.pack()

        self.frame_encryption=tk.Frame(self)
        self.label_encryption=tk.Label(
            self.frame_encryption, text='Criptografia')
        self.entry_encryption=tk.Entry(self.frame_encryption, width=50)
        self.insert('encryption', self.entry_encryption)
        self.frame_encryption.pack(pady=15)
        self.label_encryption.pack()
        self.entry_encryption.pack()

        self.botao_salvar_metadados=tk.Button(self,
                                                text='Salvar',
                                                command=self.salvar_metadados)
        self.botao_salvar_metadados.pack()

    def insert(self, metadata, entry):
        # insere os metadados na entrada se for diferente de None
        if self.pdf.fitz_doc.metadata[metadata]:
            entry.insert(0, self.pdf.fitz_doc.metadata[metadata])

    def salvar_metadados(self):
        if self.entry_format.get() != '':
            self.pdf.fitz_doc.metadata['format']=self.entry_format.get()
        if self.entry_title.get() != '':
            self.pdf.fitz_doc.metadata['title']=self.entry_title.get()
        if self.entry_author.get() != '':
            self.pdf.fitz_doc.metadata['author']=self.entry_author.get()
        if self.entry_subject.get() != '':
            self.pdf.fitz_doc.metadata['subject']=self.entry_subject.get()
        if self.entry_keywords.get() != '':
            self.pdf.fitz_doc.metadata['keywords']=self.entry_keywords.get()
        if self.entry_creator.get() != '':
            self.pdf.fitz_doc.metadata['creator']=self.entry_creator.get()
        if self.entry_producer.get() != '':
            self.pdf.fitz_doc.metadata['producer']=self.entry_producer.get()
        if self.entry_creation_date != '':
            self.pdf.fitz_doc.metadata['creationDate']=self.entry_creation_date.get(
            )
        if self.entry_mod_date.get() != '':
            self.pdf.fitz_doc.metadata['modDate']=self.entry_mod_date.get()
        if self.entry_encryption.get() != '':
            self.pdf.fitz_doc.metadata['encryption']=self.entry_encryption.get(
            )

        self.pdf.fitz_doc.setMetadata(self.pdf.fitz_doc.metadata)


class MainApplication(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        parent.title('CombinadorPDF')
        parent.geometry('330x270')
        self.parent=parent

        # objeto para manter os pdfs
        self.combinadorPDF=CombinadorPDF()

        # widgets
        self.frame_treeview=FrameTreeview(self)
        self.menu_bar=MenuBarMain(self)

        self.pack(fill=tk.BOTH, expand=1)
        self.frame_treeview.pack(fill=tk.BOTH, expand=1)


if __name__ == '__main__':
    root=tk.Tk()
    MainApplication(root)
    root.mainloop()
