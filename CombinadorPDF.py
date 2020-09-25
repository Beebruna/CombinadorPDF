from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from fitz import *
from PIL import ImageTk, Image

class CombinadorPDF:
    def __init__(self, pdf_filename):
        # abre o pdf e cria uma lista com as imagens de cada pagina
        self.pdf = fitz.open(pdf_filename)
        self.update_image_list()

    def update_image_list(self):
        "pega uma lista de objetos PhotoImage para utilizaçao no gui tkinter"

        self.image_list = []

        for page_number in range(len(self.pdf)):
            # criando um objeto da classe PhotoImage que pode ser utilizado no tkinter
            pix = self.pdf.getPagePixmap(page_number)
            mode = 'RGBA' if pix.alpha else 'RGB'
            image = Image.frombytes(
                mode, [pix.width, pix.height], pix.samples)
            photo_image = ImageTk.PhotoImage(image)

            self.image_list.append(photo_image)

    def combinar(self, pdf_filename):
        "combina outro pdf e atualiza as imagens"

        pdf2 = fitz.open(pdf_filename)
        self.pdf.insertPDF(pdf2)
        self.update_image_list()

    def download(self):
        "faz download do pdf no estado atual"
        # ainda nao testado/implementado
        self.pdf.save(asksavefilename())


class Application:
    def __init__(self, master):
        "inicia a aplicaçao chamando a frame com o botao de selecionar arquivos"

        self.master = master
        master.title('CombinadorPDF')

        self.define_options_frame()

    def define_options_frame(self):
        "define o frame com o botao de selecao"

        # criando o frame que sera visualizado na inicialização do programa
        self.options_frame = Frame(self.master)
        self.options_frame.pack()

        select_button = Button(
            self.options_frame, text='Selecionar arquivo', command=self.abre_pdfs)
        select_button.pack()

    def define_editor_frame(self):
        "cria frame de exibiçao e ediçao do pdf"

        # criando novo frame de exibiçao e ediçao do pdf
        self.editor_frame = Frame(self.master)
        self.editor_frame.pack()

        # definindo widgets no frame
        pagina_atual = 0
        self.redefine_layout(pagina_atual)

    def redefine_layout(self, pagina_atual):
        "atualiza e arruma os widgets"

        # excluir se ja tiver uma imagem
        if hasattr(self, 'label_imagem'):
            self.label_imagem.grid_forget()

        # redefinindo widgets
        self.label_imagem = Label(
            self.editor_frame, image=self.combinador_pdf.image_list[pagina_atual])
        # manter outra referencia da imagem para evitar garbage collection
        self.label_imagem.imagem = self.combinador_pdf.image_list[pagina_atual]

        self.botao_avancar = Button(
            self.editor_frame, text='>', command=lambda: self.update_pagina(pagina_atual, 'avancar'))
        self.botao_voltar = Button(
            self.editor_frame, text='<', command=lambda: self.update_pagina(pagina_atual, 'voltar'))
        self.delete_button = Button(
            self.editor_frame, text='Deletar página', command=lambda: self.deletar_pagina(pagina_atual))
        self.botao_combinar = Button(
            self.editor_frame, text='Adicionar pdf', command=lambda: self.combinador_pdf.combinar(askopenfilename()))

        # desabilita botao voltar na primeira pagina
        if pagina_atual == 0:
            self.botao_voltar = Button(
                self.editor_frame, text='<', state=DISABLED)
        # desabilita botao avancar na ultima pagina
        elif pagina_atual == len(self.combinador_pdf.image_list) - 1:
            self.botao_avancar = Button(
                self.editor_frame, text='>', state=DISABLED)

        # arrumando layout
        self.botao_voltar.grid(row=0, column=0)
        self.label_imagem.grid(row=0, column=1, columnspan=2)
        self.botao_avancar.grid(row=0, column=3)

        self.delete_button.grid(row=1, column=1)
        self.botao_combinar.grid(row=1, column=2)

    def abre_pdfs(self):
        "inicializa o CombinadorPDF e muda frames"

        # abre tela para selecionar arquivo pdf
        pdf_list = askopenfilename()

        # se nenhum arquivo for selecionado nao faz nada
        if len(pdf_list) == 0:
            return

        # cria objeto manipulador de pdf
        self.combinador_pdf = CombinadorPDF(pdf_list)

        # destroi options_frame e cria editor frame
        self.options_frame.destroy()
        self.define_editor_frame()

    def update_pagina(self, pagina_atual, update):
        "atualiza pagina atual e redefine o layout"

        if update == 'avancar':
            pagina_atual += 1
        else:
            pagina_atual -= 1

        self.redefine_layout(pagina_atual)

    def deletar_pagina(self, pagina_atual):
        "remove a pagina sendo exibida"

        # removendo pagina
        self.combinador_pdf.pdf.deletePage(pagina_atual)
        self.combinador_pdf.image_list.remove(
            self.combinador_pdf.image_list[pagina_atual])

        # alterando a pagina exibida
        if len(self.combinador_pdf.image_list) == 0:
            self.define_options_frame()
        elif pagina_atual == 0:
            pagina_atual += 1
            self.update_pagina(pagina_atual, 'voltar')
        elif pagina_atual == 1:
            self.update_pagina(pagina_atual, 'voltar')
        else:
            pagina_atual -= 2
            self.update_pagina(pagina_atual, 'avancar')

root = Tk()
Application(root)
root.mainloop()
