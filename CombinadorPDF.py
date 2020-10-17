import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
import fitz

class CombinadorPDF:
    def __init__(self):
        self.fitz_docs = []
        self.nome_arquivos = []
        
    def adicionar_arquivo(self, nome_arquivo, fitz_doc):
        # adiciona arquivo os atributos
        self.nome_arquivos.append(nome_arquivo)
        self.fitz_docs.append(fitz_doc)
        
    def baixar(self, filename):
        # combina os pdfs e baixa
        
        self.fitz_doc_combinado = fitz.open()
        
        for fitz_doc in self.fitz_docs:
            self.fitz_doc_combinado.insertPDF(fitz_doc)
            
        self.fitz_doc_combinado.save(filename)

class PdfFile:
    def __init__(self, fitz_doc):
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

class FrameArquivos(tk.LabelFrame):
    def __init__(self, master):
        self.master = master
        tk.LabelFrame.__init__(self, master, text='Seleção de arquivos')

        # ------------------------------------- widgets ----------------------------------------

        self.botao_procurar = tk.Button(
            self, text='Procurar arquivos',
            command=self.selecionar_arquivos)

        # ------------------------------------- layout ----------------------------------------

        self.grid_columnconfigure(0, weight=1)

        self.botao_procurar.grid(
            row=0, column=0,
            padx=10, pady=10,
            sticky='WE')
    
    def selecionar_arquivos(self):
        # adiciona nome dos arquivos selecionados ao menuoption e ao combinadorpdf
        
        nome_arquivos = filedialog.askopenfilenames(
            filetypes=[('Arquivos PDF', '*.pdf')])
        
        # atualizando objeto combinadorPdf
        for nome_arquivo in nome_arquivos:
            self.master.frame_inserir.opcoes.append(nome_arquivo)
                
        # atualizando menuoption
        self.master.frame_inserir.option_menu['menu'].delete(0, 'end')
        self.master.frame_inserir.opcoes.sort(key=str.lower)
        
        for opcao in self.master.frame_inserir.opcoes:
            self.master.frame_inserir.option_menu['menu'].add_command(
                label=opcao, command=lambda escolhido=opcao: self.master.frame_visualizar.visualizar(escolhido))
        
class FrameVisualizar(tk.LabelFrame):
    def __init__(self, master):
        self.master = master
        tk.LabelFrame.__init__(self, master, text='Visualizar')

        # imagem em branco para ocupar espaço do label_imagem
        image = Image.new('RGB', (250, 350), (255, 255, 255))
        self.img = ImageTk.PhotoImage(image)

        # ------------------------------------- widgets ----------------------------------------

        self.label_imagem = tk.Label(self, image=self.img)
        self.label_imagem.image = self.img

        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)

        self.scale = ttk.Scale(self)

        self.botao_voltar = tk.Button(self, text='<')
        self.botao_avancar = tk.Button(self, text='>')
        self.label_pagina = tk.Label(self, text='Página 1 de ?')

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
            padx=10,
            sticky='WE')

        self.botao_avancar.grid(
            row=2, column=2,
            padx=10)

        self.label_pagina.grid(
            row=3, column=1)

    def visualizar(self, escolhido):
        # coloca pagina no pdf no label_imagem e atualiza widgets
        # inicializacao na primeira pagina
        
        self.master.frame_inserir.selecionado.set(escolhido)
        
        self.nome_escolhido = escolhido
        self.pdfFile = PdfFile(fitz.open(escolhido))
        
        self.label_imagem.configure(image=self.pdfFile.lista_imagens[0])
        self.label_imagem.image = self.pdfFile.lista_imagens[0]
        
        self.label_pagina.configure(text='Página 1 de {}'.format(len(self.pdfFile.fitz_doc)))
        
        self.scale.configure(
            from_=1, to=len(self.pdfFile.fitz_doc),
            command=lambda pagina: self.atualizar_pagina(pagina, 'scale'))
        
        self.botao_voltar.configure(
            command=lambda: self.atualizar_pagina(self.scale.get() - 2),
            state=tk.DISABLED)
        
        self.botao_avancar.configure(
            command=lambda: self.atualizar_pagina(self.scale.get()))
        
    def atualizar_pagina(self, pagina, widget='botao'):
        # atualiza a pagina, mudando a imagem exibida e atualizando widgets
        
    
        # verificando de qual widget vem o comando
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
        
class FrameInserir(tk.LabelFrame):
    def __init__(self, master):
        self.master = master
        tk.LabelFrame.__init__(self, master, text='Inserir arquivos')

        self.opcoes = []
        self.selecionado = tk.StringVar()
        self.selecionado.set('Adicione um arquivo para editar')
        
        self.selecionado_radio = tk.StringVar()
        self.selecionado_radio.set('TODAS')
        
        # ------------------------------------- widgets ----------------------------------------

        self.option_menu = tk.OptionMenu(
            self, self.selecionado, self.opcoes)

        self.label_opcoes = tk.Label(
            self, text='Páginas a serem inseridas:')

        self.botao_radio_todas = tk.Radiobutton(
            self, text='Todas as páginas',
            variable=self.selecionado_radio, value='TODAS')

        self.frame_entry = tk.Frame(self)

        self.botao_radio_intervalo = tk.Radiobutton(
            self.frame_entry, text='Páginas:',
            variable=self.selecionado_radio, value='SELECIONADAS')

        self.entry_paginas = tk.Entry(
            self.frame_entry, width=25)

        self.label_exemplo = tk.Label(
            self.frame_entry, text='Exemplo: 1,5-9,12')

        self.botao_inserir = tk.Button(
            self, text='Inserir', command=self.inserir)

        # ------------------------------------- layout ----------------------------------------
        
        self.option_menu.grid(
            row=0, column=0,
            sticky='W',
            padx=10, pady=5)

        self.label_opcoes.grid(
            row=1, column=0,
            sticky='W',
            pady=5)

        self.botao_radio_todas.grid(
            row=2, column=0,
            sticky='W')

        self.frame_entry.grid(
            row=3, column=0,
            sticky='W')

        self.botao_radio_intervalo.grid(row=0, column=0)

        self.entry_paginas.grid(row=0, column=1)

        self.label_exemplo.grid(
            row=1, column=1,
            sticky='W')

        self.botao_inserir.grid(
            row=4, column=0,
            sticky='W', padx=20)

    def inserir(self):
        # insere o pdf de acordo com a opçao selecionada
        
        opcao_selecionada = self.selecionado_radio.get()
        
        if opcao_selecionada == 'TODAS':
            self.master.combinadorPdf.adicionar_arquivo(
                self.master.frame_visualizar.nome_escolhido,
                self.master.frame_visualizar.pdfFile.fitz_doc)
        else:
            self.master.frame_visualizar.pdfFile.selecionar_paginas(
                self.entry_paginas.get())
            
            self.master.combinadorPdf.adicionar_arquivo(
                self.master.frame_visualizar.nome_escolhido,
                self.master.frame_visualizar.pdfFile.fitz_doc)
        
        # excluindo de optionmenu e adicionando a listbox
        index = self.option_menu['menu'].index(self.selecionado.get())
        self.option_menu['menu'].delete(index)
        
        self.master.frame_combinacao.lista_arquivos.insert(tk.END, self.selecionado.get())
        
        # voltando para o padrao
        self.master.frame_visualizar.label_imagem.configure(image=self.master.frame_visualizar.img)
        self.master.frame_visualizar.label_imagem.image = self.master.frame_visualizar.img
        
        self.opcoes.remove(self.selecionado.get())
        
        if len(self.opcoes) == 0:
            self.selecionado.set('Adicione um arquivo para editar')
        else:
            self.selecionado.set(self.opcoes[0])
        
class FrameCombinacao(tk.LabelFrame):
    def __init__(self, master):
        self.master = master
        tk.LabelFrame.__init__(self, master,
                               text='Arquivos combinados')

        # ------------------------------------- widgets ----------------------------------------

        self.lista_arquivos = tk.Listbox(
            self, selectmode=tk.SINGLE)  # talvez adicionar scrollbar à lista

        self.frame_botoes = tk.Frame(self)

        self.botao_baixar = tk.Button(
            self, text='Baixar',
            command=self.baixar)

        # ------------------------------------- layout ----------------------------------------
        
        self.lista_arquivos.pack(
            padx=10, pady=5,
            fill=tk.BOTH, expand=True)
        
        self.botao_baixar.pack(pady=10)

        
    def baixar(self):
        # abre dialogo para nome do arquivo e baixa o arquivo
        nome_arquivo = filedialog.asksaveasfilename()
        
        if not nome_arquivo:
            return
        
        if not nome_arquivo.endswith('.pdf'):
            nome_arquivo += '.pdf'
            
        self.master.combinadorPdf.baixar(nome_arquivo)
        
class MainApplication(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        master.title('CombinadorPDF')

        self.combinadorPdf = CombinadorPDF()
        
        # ------------------------------------- widgets ----------------------------------------
        
        self.frame_combinacao = FrameCombinacao(self)
        self.frame_visualizar = FrameVisualizar(self)     
        self.frame_inserir = FrameInserir(self)   
        self.frame_arquivos = FrameArquivos(self)

        # ------------------------------------- layout ----------------------------------------
        
        self.grid_columnconfigure(0, weight=1)
    
        self.frame_arquivos.grid(
            row=0, column=0,
            padx=10, pady=5,
            sticky='we')

        self.frame_visualizar.grid(
            row=1, column=0,
            rowspan=7,
            padx=10, pady=5,
            ipadx=10, ipady=10)

        self.frame_inserir.grid(
            row=0, column=1,
            rowspan=3,
            padx=10, pady=5,
            ipadx=10, ipady=10)

        self.frame_combinacao.grid(
            row=3, column=1,
            rowspan=5,
            sticky='NSEW',
            padx=10, pady=5)

if __name__ == '__main__':
    root = tk.Tk()
    MainApplication(root).pack(side=tk.TOP)
    root.mainloop()
