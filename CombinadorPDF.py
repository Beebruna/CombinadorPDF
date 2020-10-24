import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
import fitz


class CombinadorPDF:
    def __init__(self):
        self.fitz_docs = []
        self.nome_arquivos = []

    def adicionar_arquivo(self, pdfFile):
        # adiciona arquivo os atributos
        self.nome_arquivos.append(pdfFile.nome_arquivo)
        self.fitz_docs.append(pdfFile.fitz_doc)

    def combinar(self):
        # combina os pdfs armazenados em fitz_docs
        fitz_doc_combinado = fitz.open()
        for fitz_doc in self.fitz_docs:
            fitz_doc_combinado.insertPDF(fitz_doc)
        return fitz_doc_combinado


class PdfFile:
    def __init__(self, fitz_doc, nome_arquivo=None):
        self.nome_arquivo = nome_arquivo
        self.fitz_doc = fitz_doc
        self.lista_imagens = self.extrair_imagens()

    def extrair_imagens(self):
        # extrai paginas do pdf como imagens
        lista_imagens = []
        for pagina in range(len(self.fitz_doc)):
            pix = self.fitz_doc.getPagePixmap(pagina)
            mode = 'RGBA' if pix.alpha else 'RGB'
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            image = image.resize((250, 350))
            lista_imagens.append(ImageTk.PhotoImage(image))

        return lista_imagens

    def selecionar_paginas(self, paginas_selecionadas):
        # seleciona paginas especificas do pdf e exclui o resto

        if not paginas_selecionadas:
            return

        fitz_doc = fitz.open()
        intervalos = paginas_selecionadas.split('-')

        for intervalo in intervalos:
            paginas = intervalo.split(',')
            fitz_doc.insertPDF(self.fitz_doc,
                               from_page=int(paginas[0]) - 1, to_page=int(paginas[1]) - 1)

        self.fitz_doc = fitz_doc
        self.lista_imagens = self.extrair_imagens()


class FrameVisualizarPdf(tk.LabelFrame):
    def __init__(self, master, pdfFile=None, dimensao=(250, 350)):
        self.master = master
        tk.LabelFrame.__init__(self, master, text='Visualizar arquivo')
        
        self.pdfFile = pdfFile

        # ------------------------------------- widgets ----------------------------------------

        self.label_imagem = tk.Label(self)

        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)

        self.scale = ttk.Scale(self)

        self.botao_voltar = tk.Button(self, text='<')
        self.botao_avancar = tk.Button(self, text='>')
        self.label_pagina = tk.Label(self)

        if not pdfFile:
            # imagem em branco para ocupar espaço do label imagem
            image = Image.new('RGB', dimensao, (255, 255, 255))
            self.img = ImageTk.PhotoImage(image)
            self.widgets_padrao()
        else:
            self.visualizar()
            
        # ------------------------------------- layout ----------------------------------------

        self.label_imagem.grid(
            row=0, column=1,
            pady=10)

        self.separator.grid(
            row=1, column=0,
            columnspan=3, sticky='WE',
            pady=10)

        self.botao_voltar.grid(
            row=2, column=0,
            padx=10)

        self.scale.grid(
            row=2, column=1,
            padx=10, sticky='WE')

        self.botao_avancar.grid(
            row=2, column=2,
            padx=10)

        self.label_pagina.grid(
            row=3, column=1)

    def widgets_padrao(self):
        # volta os widgets para o padrao quando nao tem nenhum pdf a mostra
        self.scale.set(1)
        self.scale.configure(state=tk.DISABLED)

        self.botao_avancar.configure(state=tk.DISABLED)
        self.botao_voltar.configure(state=tk.DISABLED)

        self.label_pagina.configure(text='Página 1 de ?')

        self.label_imagem.configure(
            image=self.img)
        self.label_imagem.image = self.img

    def visualizar(self, nome_arquivo=None):
        # inicializa a visualizacao do pdf
        if not self.pdfFile:
            self.pdfFile = PdfFile(fitz.open(nome_arquivo))

        self.label_imagem.configure(image=self.pdfFile.lista_imagens[0])
        self.label_imagem.image = self.pdfFile.lista_imagens[0]

        self.label_pagina.configure(
            text='Página 1 de {}'.format(len(self.pdfFile.fitz_doc)))

        self.scale.configure(
            from_=1, to=len(self.pdfFile.fitz_doc),
            command=lambda pagina: self.atualizar_pagina(pagina, 'scale'))

        self.botao_voltar.configure(
            command=lambda: self.atualizar_pagina(self.scale.get() - 2),
            state=tk.DISABLED)

        self.scale.configure(state=tk.NORMAL)

        self.botao_avancar.configure(
            command=lambda: self.atualizar_pagina(self.scale.get()),
            state=tk.NORMAL)

    def atualizar_pagina(self, pagina, widget='botao'):
        # atualiza a pagina, mudando a imagem exibida e atualizando widgets

        # argumento pagina vem diferente dependendo do widget
        if widget == 'scale':
            pagina = int(pagina.split('.')[0])
            pagina = pagina - 1
        else:
            pagina = int(pagina)
            self.scale.set(pagina + 1)

        # atualizando imagem e mantendo segunda referencia
        self.label_imagem.configure(image=self.pdfFile.lista_imagens[pagina])
        self.label_imagem.image = self.pdfFile.lista_imagens[pagina]

        self.label_pagina.configure(text='Página {} de {}'.format(
            pagina + 1, len(self.pdfFile.fitz_doc)))

        # atualizando estado dos botoes
        if pagina == 0:
            self.botao_voltar.configure(state=tk.DISABLED)
        else:
            self.botao_voltar.configure(state=tk.NORMAL)

        if pagina == len(self.pdfFile.fitz_doc) - 1:
            self.botao_avancar.configure(state=tk.DISABLED)
        else:
            self.botao_avancar.configure(state=tk.NORMAL)


class WindowBaixar(tk.Toplevel):
    def __init__(self, pdfFile=None):
        tk.Toplevel.__init__(self)

        self.pdfFile = pdfFile

        # ------------------------------------- widgets ----------------------------------------

        self.frame_visualizar_pdf = FrameVisualizarPdf(
            self, pdfFile, dimensao=(400, 560))

        self.frame_metadados = tk.LabelFrame(
            self, text='Editar metadados')

        self.init_metadados_widgets()

        self.botao_concluir = tk.Button(
            self, text='Escolher diretório e baixar', command=self.salvar)

        # ------------------------------------- layout ----------------------------------------

        self.frame_visualizar_pdf.grid(
            row=0, column=0,
            sticky='N', padx=5, pady=10)

        self.frame_metadados.grid(
            row=0, column=1,
            rowspan=2, padx=5, pady=5)

        self.botao_concluir.grid(
            row=1, column=0,
            sticky='EW', padx=5, pady=5)

    def init_metadados_widgets(self):
        # loop pelo dicionario metadata e cria widgets de acordo
        self.entries = {}

        for key, value in self.pdfFile.fitz_doc.metadata.items():
            frame = tk.Frame(self.frame_metadados)
            label = tk.Label(frame, text=key.capitalize())
            entry = tk.Entry(frame, width=50)

            if self.pdfFile.fitz_doc.metadata[key]:
                entry.insert(0, self.pdfFile.fitz_doc.metadata[key])

            frame.pack(pady=15)
            label.pack()
            entry.pack()

            self.entries[key] = entry

    def salvar(self):
        pass


class MainApplication(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        master.title('CombinadorPDF')

        self.combinadorPdf = CombinadorPDF()
        self.inicializacao_widgets()

    def inicializacao_widgets(self):

        # --- frame arquivos --------------------------------------

        self.frame_arquivos = tk.LabelFrame(
            self, text='Seleção de arquivos')

        self.botao_procurar = tk.Button(
            self.frame_arquivos, text='Procurar arquivos',
            command=self.botao_procurar_command)

        self.frame_arquivos.grid_columnconfigure(0, weight=1)
        self.botao_procurar.grid(
            row=0, column=0,
            padx=10, pady=10,
            sticky='WE')

        self.frame_arquivos.grid(
            row=0, column=0,
            padx=10, pady=5, sticky='we')

        # --- frame inserir --------------------------------------

        self.frame_inserir = tk.LabelFrame(
            self, text='Edição de arquivos')

        self.opcoes = []
        self.selecionado_menu = tk.StringVar()
        self.selecionado_menu.set('Adicione um arquivo para editar')

        self.selecionado_radio = tk.StringVar()
        self.selecionado_radio.set('TODAS')

        self.option_menu = tk.OptionMenu(
            self.frame_inserir, self.selecionado_menu, self.opcoes)

        self.label_opcoes = tk.Label(
            self.frame_inserir, text='Páginas a serem inseridas:')

        self.botao_radio_todas = tk.Radiobutton(
            self.frame_inserir, text='Todas as páginas',
            variable=self.selecionado_radio, value='TODAS')

        self.frame_botao_intervalo = tk.Frame(self.frame_inserir)

        self.botao_radio_intervalo = tk.Radiobutton(
            self.frame_botao_intervalo, text='Páginas:',
            variable=self.selecionado_radio, value='SELECIONADAS')

        self.entry_paginas = tk.Entry(
            self.frame_botao_intervalo, width=25)

        self.label_exemplo = tk.Label(
            self.frame_botao_intervalo, text='Exemplo: 1,5-9,12')

        self.botao_inserir = tk.Button(
            self.frame_inserir, text='Inserir', command=self.botao_inserir_command)

        self.option_menu.grid(
            row=0, column=0,
            sticky='W', padx=10, pady=5)

        self.label_opcoes.grid(
            row=1, column=0,
            sticky='W', pady=5)

        self.botao_radio_todas.grid(
            row=2, column=0,
            sticky='W')

        self.frame_botao_intervalo.grid(
            row=3, column=0,
            sticky='W')

        self.botao_radio_intervalo.grid(
            row=0, column=0)

        self.entry_paginas.grid(
            row=0, column=1)

        self.label_exemplo.grid(
            row=1, column=1,
            sticky='W')

        self.botao_inserir.grid(
            row=4, column=0,
            sticky='W', padx=20)

        self.frame_inserir.grid(
            row=0, column=1,
            rowspan=3, padx=10, pady=5, ipadx=10, ipady=10)

        # --- frame visualizar --------------------------------------

        self.frame_visualizar_pdf = FrameVisualizarPdf(self)
        self.frame_visualizar_pdf.grid(
            row=1, column=0,
            rowspan=7, padx=10, pady=5, ipadx=10, ipady=10)

        # --- frame combinar --------------------------------------

        self.frame_combinar = tk.LabelFrame(
            self, text='Arquivos a serem combinados')

        self.lista_arquivos = tk.Listbox(
            self.frame_combinar, selectmode=tk.SINGLE)

        self.botao_baixar = tk.Button(
            self.frame_combinar, text='Baixar',
            command=self.botao_baixar_command)

        self.lista_arquivos.pack(
            padx=10, pady=5,
            fill=tk.BOTH, expand=True)

        self.botao_baixar.pack(pady=10)

        self.frame_combinar.grid(
            row=3, column=1,
            rowspan=5, sticky='NSEW', padx=10, pady=5)

    def botao_procurar_command(self):
        # adiciona nome dos arquivos selecionados ao menuoption e ao combinadorpdf

        nome_arquivos = filedialog.askopenfilenames(
            filetypes=[('Arquivos PDF', '*.pdf')])

        # atualizando option menu
        for nome_arquivo in nome_arquivos:
            self.opcoes.append(nome_arquivo)
        self.opcoes.sort(key=str.lower)

        self.option_menu['menu'].delete(0, 'end')
        for opcao in self.opcoes:
            self.option_menu['menu'].add_command(
                label=opcao, command=lambda: self.option_menu_command(opcao))

    def option_menu_command(self, nome_arquivo):
        # seta opcao mostrada e começa o visualizador do pdf
        self.selecionado_menu.set(nome_arquivo)
        self.frame_visualizar_pdf.visualizar(nome_arquivo)

    def botao_inserir_command(self):
        # modificando pdf e inserindo na listbox

        if self.selecionado_menu.get() == 'Adicione um arquivo para editar':
            return
        
        doc = fitz.open(self.selecionado_menu.get())
        pdfFile = PdfFile(doc, self.selecionado_menu.get())
        
        if self.selecionado_radio.get() != 'TODAS':
            pdfFile.selecionar_paginas(self.entry_paginas.get())
            
        self.combinadorPdf.adicionar_arquivo(pdfFile)
        
        self.lista_arquivos.insert(tk.END, self.selecionado_menu.get())
        index = self.option_menu['menu'].index(self.selecionado_menu.get())
        self.option_menu['menu'].delete(index)
        self.opcoes.remove(self.selecionado_menu.get())

        if len(self.opcoes) == 0:
            self.selecionado_menu.set('Adicione um arquivo para editar')
        else:
            self.selecionado_menu.set(self.opcoes[0])
        
        self.frame_visualizar_pdf.widgets_padrao()
        
    def botao_baixar_command(self):
        WindowBaixar(PdfFile(self.combinadorPdf.combinar()))


if __name__ == '__main__':
    root = tk.Tk()
    MainApplication(root).pack(side=tk.TOP)
    root.mainloop()
