from tkinter import *
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from tkinter import ttk
from CombinadorPDF import *

class Application:
    def __init__(self, master):
        "cria widgets na tela inicial"
        
        self.master = master
        self.master.title('CombinadorPDF')
        self.master.geometry('350x350')

        # frame em que serao colocados os widgets
        self.frame_tabela = Frame(self.master)
        self.frame_tabela.pack(fill=BOTH, expand=1)

        # menu
        self.menu = Menu(self.frame_tabela)
        self.master.config(menu=self.menu)

        self.menu_arquivos = Menu(self.menu)
        self.menu.add_cascade(label='Arquivos', menu=self.menu_arquivos)

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
            label='Data de modificação', command=lambda: self.ordenar_tabela('data'))

        # tabela utilizando treeview
        self.tabela = ttk.Treeview(self.frame_tabela)

        self.tabela.heading('#0', text='Arquivos selecionados')
        self.tabela.column('#0', stretch=True)

        self.tabela.pack(fill=X, expand=1, pady=10)

        # botoes
        self.botao_adicionar = Button(
            self.frame_tabela, text='Adicionar', command=lambda: self.adicionar_arquivos(askopenfilenames()))
        self.botao_excluir = Button(self.frame_tabela, text='Excluir',
                                    command=lambda: self.excluir_arquivos(self.tabela.selection()[0]))
        self.botao_editar = Button(
            self.frame_tabela, text='Editar', command=lambda: self.editar_arquivo(self.tabela.selection()))

        self.botao_adicionar.pack()
        self.botao_excluir.pack()
        self.botao_editar.pack()

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
            pass  # necessario extrair dados do pdf

        self.excluir_arquivos(ids)
        self.adicionar_arquivos(itens)

    def editar_arquivo(self, id_item_selecionado):
        '''
        cria nova janela com opções de ediçao
        inicializa widgets que serão usados
        '''
        
        # pegando informaçao necessaria
        arquivo_selecionado = self.tabela.item(id_item_selecionado, 'text')
        lista_imagens, tamanho_arquivo = CombinadorPDF.get_images(arquivo_selecionado)
        
        # abrindo nova janela e inicializando widgets
        self.window = Toplevel()
        self.window.title(arquivo_selecionado)
        
        self.frame_imagem = Frame(self.window)
        self.frame_imagem.grid(row=0, column=0)
        
        self.label_imagem = Label(self.frame_imagem, image=lista_imagens[0])
        self.label_imagem.imagem = lista_imagens[0]
        self.botao_avancar = Button(self.frame_imagem, text='>')
        self.botao_voltar = Button(self.frame_imagem, text='<', state=DISABLED)
        self.botao_deletar = Button(self.frame_imagem, text='Deletar página')
        self.botao_metadados = Button(self.frame_imagem, text='Editar metadados')
        self.label_pagina_atual = Label(self.frame_imagem, text='Pagina 0 de {}'.format(tamanho_arquivo))
        
        self.botao_voltar.grid(row=0, column=0)
        self.label_imagem.grid(row=0, column=1, columnspan=2)
        self.botao_avancar.grid(row=0, column=3)
        self.label_pagina_atual.grid(row=1, column=1, columnspan=2)
        self.botao_deletar.grid(row=2, column=1)
        self.botao_metadados.grid(row=2, column=2)



if __name__ == '__main__':
    root = Tk()
    Application(root)
    root.mainloop()
