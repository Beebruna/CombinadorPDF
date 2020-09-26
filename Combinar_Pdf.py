import PyPDF2  #biblioteca para manipulação de Pdfs

print('1 - Combinar Pdfs\n'
      '2 - Combinar páginas específicas  de um Pdf\n'
      '3-  Metadados do arquivo: ')
opcao = int(input())

if(opcao == 1):
    count=0
    arquivo= list()
    while True:
        arq = input('Digite o nome do {}° arquivo: '.format(count+1)) #inserir documento para combinar
        count +=1
        if arq not in arquivo:
            arquivo.append(arq+'.pdf') #forçar o arquivo estar no formato pdf
        else:
            print('Arquivo já inserido!')
        ler = str(input(('Quer continuar incluindo Pdfs? [S/N]: '))) #pergunta ao usuario se ele quer continuando adicionando pdfs
        if ler in 'Nn':
            break

    escrever = PyPDF2.PdfFileWriter()
    for i in arquivo:
        pdf= PyPDF2.PdfFileReader(i, 'rb') #Modo de leitura binário para não dar erro
        for pagina in range(pdf.getNumPages()):
            escrever.addPage(pdf.getPage(pagina))
    with open('Pdfcombinado.pdf', 'wb') as out:  #Nome do arquivo combinado
        escrever.write(out)
    print('Pdf combinado')
elif(opcao == 2):
    arquivo = input('Digite o nome do  arquivo: ')  # inserir documento
    arquivo= arquivo+'.pdf' #forçar o arquivo estar no formato pdf
    pdf= PyPDF2.PdfFileReader(arquivo, 'r') #Modo de leitura binário para não dar erro
    escrever= PyPDF2.PdfFileWriter()
    while True:
        pag= int(input('Digite o número da página: '))
        escrever.addPage(pdf.getPage(pag))
        ler = str(input(
            ('Quer continuar incluindo páginas desse arquivo? [S/N]: ')))  # pergunta ao usuario se ele quer continuando adicionando pdfs
        if ler in 'Nn':
            break
    with open('Pdf_combinado.pdf', 'wb') as out:
        escrever.write(out)
        print("Pdf combinado")

else:
    arquivo= input("Digite o nome do pdf: ")
    arquivo= arquivo+'.pdf' #forçar o arquivo estar no formato pdf
    '''Os tipos de metadados que a biblioteca consegue extrair é 
    autor, creator, produtor, assunto, título, número de páginas '''
    info=open(arquivo, 'rb')
    pdf= PyPDF2.PdfFileReader(info)
    informacao = pdf.getDocumentInfo()
    n_paginas= pdf.getNumPages()
    print('Título: ',informacao.title)
    print('Autores: ', informacao.author)
    print('Número de páginas: ', n_paginas)
    #print('Onde foi produzido: ', informacao.producer)
    #print('Assunto', informacao.subject)
