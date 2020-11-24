import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
import fitz

class CombinadorPDF:
    """
    Classe usada para combinar pdfs

    Atributos
    ---------
    docs : list
        lista de objetos fitz.fitz.Document
    nome_arquivos : list
        lista de nomes dos arquivos

    Métodos
    -------
    adicionar_arquivo(self, pdfFile)
        Adiciona nome do arquivo e objeto fitz.fitz.Document aos atributos
    combinar(self)
        Combina os pdfs da lista docs

    """

    def __init__(self):
        """"""

        self.docs = []
        self.nome_arquivos = []

    def adicionar_arquivo(self, pdfFile):
        """
        Adiciona nome do arquivo e objeto fitz.fitz.Document aos atributos

        Parâmetros
        ----------
        nome_arquivo : str
            nome do arquivo incluindo endereço absoluto
        doc : fitz.fitz.Document
            documento pdf
        """

        self.nome_arquivos.append(pdfFile.nome_arquivo)
        self.docs.append(pdfFile.doc)

    def combinar(self):
        """
        Combina os pdfs da lista docs

        Retorno
        -------
        fitz.fitz.Document
            um documento pdf com todos os pdfs da lista docs combinados
        """

        doc_combinado = fitz.open()
        for doc in self.docs:
            doc_combinado.insertPDF(doc)
        return doc_combinado

class PdfFile:
    """
    Classe usada para manipulação dos pdfs de forma individual

    Atributos
    ---------
    nome_arquivo : string
        nome do arquivo
    doc : fitz.fitz.Document
        documento pdf
    dimensao: tuple, opcional
        dimensao das pagina exibida na GUI
    imagens : list
        lista de objetos PIL.ImageTk.PhotoImage para serem exibidos na GUI

    Métodos
    -------
    extrair_imagens(self)
        Extrai as páginas do pdf como imagens.
    selecionar_paginas(self, intervalo):
        Exclui do pdf todas as páginas que não estão dentro do intervalo.
    """

    def __init__(self, doc, nome_arquivo=None, dimensao=(250, 350)):
        """
        Parâmetros
        ----------
        doc : fitz.fitz.Document
            documento pdf
        nome_arquivo : str
            nome do arquivo, caso tenha
        dimensao : tuple, opcional
            dimensao das imagens para a GUI
        """

        self.nome_arquivo = nome_arquivo
        self.doc = doc
        self.dimensao = dimensao
        self.imagens = self.extrair_imagens()

    def extrair_imagens(self):
        """
        Extrai as páginas do pdf como imagens.

        Usado para definir o atributo imagens.

        Retorno
        -------
        list
            lista das páginas do pdf como imagens (objetos ImageTk.PhotoImage)
        """

        imagens = []
        for pagina in range(len(self.doc)):
            pix = self.doc.getPagePixmap(pagina)
            mode = 'RGBA' if pix.alpha else 'RGB'
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            image = image.resize(self.dimensao)
            imagens.append(ImageTk.PhotoImage(image))

        return imagens

    def selecionar_paginas(self, intervalo):
        """
        Exclui do pdf todas as páginas que não estão dentro do intervalo.

        Parâmetros
        ----------
        intervalo : str
            string com determinado formato informando intervalo das páginas selecionadas
        """

        # melhorar testes para determinar o formato do intervalo
        if not intervalo:
            return

        doc2 = fitz.open()
        intervalos_paginas = intervalo.split(',')

        for intervalo_paginas in intervalos_paginas:
            paginas = intervalo_paginas.split('-')

            _from = int(paginas[0]) - 1

            if len(paginas) == 1:
                to = int(paginas[0]) - 1
            elif len(paginas) == 2:
                to = int(paginas[1]) - 1

            doc2.insertPDF(
                self.doc,
                from_page=_from, to_page=to)

        self.doc = doc2
        self.imagens = self.extrair_imagens()

class FrameVisualizarPdf(tk.LabelFrame):
    """
    Frame que mostra o pdf.

    Atributos
    ---------
    master : tkinter.Frame
        elemento da GUI 'pai' dessa classe
    pdfFile : PdfFile
        pdf a ser visualizado nesse frame
        inicializado como None na inicialização do programa quando ainda não há pdfs a serem visualizados
    img : ImageTk.PhotoImage
        imagem mostrada quando não há pdfs sendo visualizados
    label_imagem : tkinter.Label
        label que recebe imagem da página para visualização
    separator : ttk.Separator
        elemento da GUI para separação
    scale : ttk.Scale
        escala para transitar entre as páginas do pdf mostradas no label_imagem
    botao_voltar : tkinter.Button
        botão para voltar a página
    botao_avancar : tkinter.Button
        botão para avançar a página
    label_pagina : tkinter.Label
        label que mostra a página sendo visualizada    

    Métodos
    -------
    widgets_padrao(self)
        Retorna a GUI para o estado padrão de incialização, não tendo nenhum pdf à mostra.
    visualizar(self, nome_arquivo=None)
        Reconfigura os widgets para visualizar o pdf.
    atualizar_pagina(self, pagina, widget='botao')
        Atualiza os widgets para mudar a página.
    """

    def __init__(self, master, pdfFile=None):
        """
        Parâmetros
        ----------
        master : tkinter.Frame
            elemento da GUI 'pai' dessa classe
        pdfFile : PdfFile
            pdf a ser visualizado nesse frame
            inicializado como None na inicialização do programa quando ainda não há pdfs a serem visualizados
        """

        self.master = master
        tk.LabelFrame.__init__(self, master, text='Visualizar arquivo')

        # ------------------------------------- widgets ----------------------------------------

        self.label_imagem = tk.Label(self)

        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)

        self.scale = ttk.Scale(self)

        self.botao_voltar = tk.Button(self, text='<')
        self.botao_avancar = tk.Button(self, text='>')
        self.label_pagina = tk.Label(self)

        self.pdfFile = pdfFile
        if not pdfFile:
            # gera imagem em branco para ocupar espaço no label imagem
            image = Image.new('RGB', (250, 350), (255, 255, 255))
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
            columnspan=3, sticky='WE', pady=10)

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
        """
        Retorna a GUI para o estado padrão de incialização, não tendo nenhum pdf à mostra.
        """

        self.scale.set(1)
        self.label_pagina.configure(text='Página 1 de ?')

        self.label_imagem.configure(
            image=self.img)
        self.label_imagem.image = self.img

        self.scale.configure(state=tk.DISABLED)
        self.botao_avancar.configure(state=tk.DISABLED)
        self.botao_voltar.configure(state=tk.DISABLED)
        
        self.pdfFile = None
        

    def visualizar(self, nome_arquivo=None):
        """
        Reconfigura os widgets para visualizar o pdf.

        Parâmetros
        ----------
        nome_arquivo : str, opcional
            nome do arquivo para inicializar ou mudar o documento pdf
        """

        if nome_arquivo:
            self.pdfFile = PdfFile(fitz.open(nome_arquivo), nome_arquivo)
        
        # manter segunda referencia
        self.label_imagem.configure(image=self.pdfFile.imagens[0])
        self.label_imagem.image = self.pdfFile.imagens[0]

        self.label_pagina.configure(
            text='Página 1 de {}'.format(len(self.pdfFile.doc)))

        self.scale.configure(
            from_=1, to=len(self.pdfFile.doc),
            command=lambda pagina: self.atualizar_pagina(pagina, 'scale'))

        self.botao_voltar.configure(
            command=lambda: self.atualizar_pagina(self.scale.get() - 2),
            state=tk.DISABLED)

        self.scale.configure(state=tk.NORMAL)

        self.botao_avancar.configure(
            command=lambda: self.atualizar_pagina(self.scale.get()),
            state=tk.NORMAL)

    def atualizar_pagina(self, pagina, widget='botao'):
        """
        Atualiza os widgets para mudar a página.

        Parâmetros
        ----------
        pagina : str
            página atual do pdf que chega de outro widget como string
        widget : str
            widget que está chamando essa função, podendo ser botao (tk.Button) ou scale (ttk.Scale)
        """

        # argumento pagina chega diferente dependendo do widget
        if widget == 'scale':
            pagina = int(pagina.split('.')[0])
            pagina = pagina - 1
        else:
            pagina = int(pagina)
            self.scale.set(pagina + 1)

        # manter segunda referencia da imagem
        self.label_imagem.configure(image=self.pdfFile.imagens[pagina])
        self.label_imagem.image = self.pdfFile.imagens[pagina]

        self.label_pagina.configure(text='Página {} de {}'.format(
            pagina + 1, len(self.pdfFile.doc)))

        if pagina == 0:
            self.botao_voltar.configure(state=tk.DISABLED)
        else:
            self.botao_voltar.configure(state=tk.NORMAL)

        if pagina == len(self.pdfFile.doc) - 1:
            self.botao_avancar.configure(state=tk.DISABLED)
        else:
            self.botao_avancar.configure(state=tk.NORMAL)

class WindowBaixar(tk.Toplevel):
    """
    Elemento da GUI para concluir as edições do pdf e baixá-lo

    Atributos
    ---------
    pdfFile : PdfFile
        pdf sendo editado
    frame_visualizar_pdf : FrameVisualizarPdf
        frame para mostrar o pdf
    frame_metadados : tk.LabelFrame
        frame que mostra e permite edição dos metadados do pdf
    entries : dictionary
        dicionario com os metadados do pdf
    botao_concluir : tk.Button
        botão que chama comando de salvar o pdf no estado atual

    Métodos
    -------
    botao_concluir_command(self)
        Abre diálogo para escolher nome e diretório para salvar o arquivo
    """

    def __init__(self, pdfFile):
        """
        Parâmetros
        ----------
        pdfFile : PdfFile
            documento pdf sendo editado
        """

        tk.Toplevel.__init__(self)

        self.pdfFile = pdfFile

        # ------------------------------------- widgets ----------------------------------------

        self.frame_visualizar_pdf = FrameVisualizarPdf(
            self, pdfFile)

        self.botao_concluir = tk.Button(
            self, text='Escolher diretório e baixar', command=self.botao_concluir_command)

        self.frame_metadados = tk.LabelFrame(
            self, text='Editar metadados')

        # loop pelo dicionario metadata do pdf e criando widgets de acordo
        self.entries = {}

        for key, value in self.pdfFile.doc.metadata.items():
            frame = tk.Frame(self.frame_metadados)
            label = tk.Label(frame, text=key.capitalize())
            entry = tk.Entry(frame, width=50)

            if self.pdfFile.doc.metadata[key]:
                entry.insert(0, self.pdfFile.doc.metadata[key])

            frame.pack(pady=15)
            label.pack()
            entry.pack()

            self.entries[key] = entry

        # ------------------------------------- layout ----------------------------------------

        self.botao_concluir.grid(
            row=0, column=0,
            sticky='EW', padx=5, pady=5)

        self.frame_visualizar_pdf.grid(
            row=1, column=0,
            sticky='NS', padx=5, pady=10)

        self.frame_metadados.grid(
            row=0, column=1,
            rowspan=2, padx=5, pady=5)

    def botao_concluir_command(self):
        """
        Abre diálogo para escolher nome e diretório para salvar o arquivo
        """

        filename = filedialog.asksaveasfilename()

        if not filename.endswith('.pdf'):
            filename += '.pdf'

        self.pdfFile.doc.save(filename)

class MainApplication(tk.Frame):
    """
    Frame mostrado na janela inicial da aplicação.

    Atributos
    ---------
    master : tkinter.Tk
        Janela principal da aplicação.
    combinadorPdf : CombinadorPDF
        Objeto usado para combinar os pdfs.

    frame_arquivos : LabelFrame
        Frame com widgets de entrada de dados.
    botao_procurar : tk.Button
        Botão que abre diálogo para seleção dos arquivos.

    frame_inserir : LabelFrame
        Frame com widgets para algumas possibilidades de edição
    opcoes : list
        Lista com arquivos selecionados
    selecionado_menu : StringVar
        Opção escolhida no OptionMenu.
    option_menu : tk.OptionMenu
        Elemento da GUI para escolher entre os arquivos selecionados.
    selecionado_radio : StringVar
        Opção escolhida nos botões de rádio.
    botao_radio_todas : tk.Radiobutton
        Botão de rádio para inserir o pdf inteiro.
    botao_radio_intervalo : tk.Radiobutton
        Botão de rádio para escolher as páginas do pdf.
    entry_paginas : tk.Entry
        Widget de entrada para escolher o intervalo de páginas como uma string formatada.
    label_exemplo : tk.Label
        Label com exemplo de como deve ser formatada a string no widget de entrada entry_paginas.
    botao_inserir : tk.Button
        Botão para inserir 

    frame_visualizar : FrameVisualizarPdf
        Frame que mostra o pdf

    frame_combinar : LabelFrame
        Frame com widgets para mostrar os arquivos selecionados e botão baixar.
    listbox : tk.Listbox
        Elemento da GUI para selecionar o pdf para visualização e edição.
    botao_baixar : tk.Button
        Botão para gerar um pdf combinado e abrir outra janela para visualizar e salvar.

    Métodos
    -------
    botao_procurar_command(self)
    option_menu_command(self, nome_arquivo)
    botao_baixar_command(self)

    """

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        master.title('CombinadorPDF')

        self.combinadorPdf = CombinadorPDF()

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
            self.frame_botao_intervalo, text='Exemplo: 1-5,9-12')

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

        self.listbox = tk.Listbox(
            self.frame_combinar, selectmode=tk.SINGLE)

        self.botao_baixar = tk.Button(
            self.frame_combinar, text='Baixar',
            command=self.botao_baixar_command)

        self.listbox.pack(
            padx=10, pady=5,
            fill=tk.BOTH, expand=True)

        self.botao_baixar.pack(pady=10)

        self.frame_combinar.grid(
            row=3, column=1,
            rowspan=5, sticky='NSEW', padx=10, pady=5)

    def botao_procurar_command(self):
        """
        Abre diálogo de seleção de arquivos e adiciona os arquivos selecionados às opções.
        """

        nome_arquivos = filedialog.askopenfilenames(
            filetypes=[('Arquivos PDF', '*.pdf')])

        for nome_arquivo in nome_arquivos:
            self.opcoes.append(nome_arquivo)
        self.opcoes.sort(key=str.lower)

        # readicionando opçoes
        self.option_menu['menu'].delete(0, 'end')
        for opcao in self.opcoes:
            self.option_menu['menu'].add_command(
                label=opcao,
                command=lambda nome_arquivo=opcao: self.option_menu_command(nome_arquivo))

    def option_menu_command(self, nome_arquivo):
        """
        Ao selecionar uma opção do option menu, configura os widgets para visualizar aquela opção.

        Parâmetros
        ----------
        nome_arquivo : str
            nome do arquivo selecionado no option_menu
        """

        self.selecionado_menu.set(nome_arquivo)
        self.frame_visualizar_pdf.visualizar(nome_arquivo)

    def botao_inserir_command(self):
        """
        Salvando e inserindo pdf na listbox de acordo com os parâmetros passados no entry_paginas para combiná-lo
        """
        
        pdfFile = self.frame_visualizar_pdf.pdfFile
        
        if pdfFile.nome_arquivo == 'Adicione um arquivo para editar':
            return
        
        doc = pdfFile.doc
        
        if self.selecionado_radio.get() != 'TODAS':
            pdfFile.selecionar_paginas(self.entry_paginas.get())

        self.combinadorPdf.adicionar_arquivo(pdfFile)

        self.listbox.insert(tk.END, self.selecionado_menu.get())
        index = self.option_menu['menu'].index(self.selecionado_menu.get())
        self.option_menu['menu'].delete(index)
        self.opcoes.remove(self.selecionado_menu.get())

        if len(self.opcoes) == 0:
            self.selecionado_menu.set('Adicione um arquivo para editar')
        else:
            self.selecionado_menu.set(self.opcoes[0])

        self.frame_visualizar_pdf.widgets_padrao()

    def botao_baixar_command(self):
        """
        Combina os pdfs da listbox e abre janela para salvar o pdf gerado.
        """

        WindowBaixar(
            PdfFile(self.combinadorPdf.combinar(), dimensao=(400, 560)))

if __name__ == '__main__':
    root = tk.Tk()
    MainApplication(root).pack(side=tk.TOP)
    root.mainloop()
