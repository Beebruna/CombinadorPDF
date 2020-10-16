import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
import fitz

class CombinadorPDF:
    def __init__(self):
        self.pdf_dict = {}
        self.nome_arquivos = []
        

class PdfFile:
    def __init__(self, fitz_doc):
        self.fitz_doc = fitz_doc
        self.extrair_imagens()

    def extrair_imagens(self):
        # extrai paginas do pdf como imagens
        self.lista_imagens = []
        
        for pagina in range(len(self.fitz_doc)):
            pix = self.fitz_doc.getPagePixmap(pagina)
            mode = 'RGBA' if pix.alpha else 'RGB'
            image = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            image = image.resize((250, 350))
            self.lista_imagens.append(ImageTk.PhotoImage(image))

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
        
        for nome_arquivo in nome_arquivos:
            if nome_arquivo not in self.master.combinadorPdf.nome_arquivos:
                self.master.combinadorPdf.nome_arquivos.append(nome_arquivo)
                self.master.combinadorPdf.pdf_dict[nome_arquivo] = fitz.open(nome_arquivo)                
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
        
        self.pdfFile = PdfFile(self.master.combinadorPdf.pdf_dict[escolhido])
        
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
        self.selecionado = tk.StringVar(self)
        self.selecionado.set('Escolha um arquivo para editar')

        # ------------------------------------- widgets ----------------------------------------

        self.option_menu = tk.OptionMenu(
            self, self.selecionado, [])

        self.label_opcoes = tk.Label(
            self, text='Páginas a serem inseridas:')

        self.botao_radio_todas = tk.Radiobutton(
            self, text='Todas as páginas',
            variable=self.selecionado, value=1)

        self.frame_entry = tk.Frame(self)

        self.botao_radio_intervalo = tk.Radiobutton(
            self.frame_entry, text='Páginas:',
            variable=self.selecionado, value=2)

        self.entry_paginas = tk.Entry(
            self.frame_entry, width=25)

        self.label_exemplo = tk.Label(
            self.frame_entry, text='Exemplo: 1,5-9,12')

        self.botao_inserir = tk.Button(
            self, text='Inserir')

        # ------------------------------------- layout ----------------------------------------

        self.option_menu.grid(
            row=0, column=0,
            sticky='WE',
            padx=10, pady=5)

        self.label_opcoes.grid(
            row=1, column=0,
            sticky='W',
            pady=5)

        self.botao_radio_todas.grid(
            row=2, column=0,
            sticky='W')

        self.frame_entry.grid(
            row=3, column=0)

        self.botao_radio_intervalo.grid(row=0, column=0)

        self.entry_paginas.grid(row=0, column=1)

        self.label_exemplo.grid(
            row=1, column=1,
            sticky='W')

        self.botao_inserir.grid(
            row=4, column=0,
            sticky='W', padx=20)


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
            self, text='Baixar')

        # ------------------------------------- layout ----------------------------------------

        self.lista_arquivos.configure(
            width=40, height=13)

        self.lista_arquivos.grid(
            row=0, column=0,
            padx=10, pady=10,
            sticky='NSEW')

        self.botao_baixar.grid(
            row=1, column=0)

class MainApplication(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        master.title('CombinadorPDF')

        self.combinadorPdf = CombinadorPDF()
        
        # ------------------------------------- widgets ----------------------------------------
        
        self.frame_inserir = FrameInserir(self)   
        self.frame_visualizar = FrameVisualizar(self)
        self.frame_arquivos = FrameArquivos(self)
        self.frame_combinacao = FrameCombinacao(self)

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
