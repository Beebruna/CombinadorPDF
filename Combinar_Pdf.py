import fitz

print('1 - Combinar páginas específicas 2 Pdfs\n'
      '2 - Combinar páginas específicas  de um Pdf\n'
      '3 - Remover páginas de um Pdf\n'
      '4 - Metadados de um Pdf:')
opcao = int(input())

if(opcao == 1):
    arquivo1 = input("Digite o nome do 1° PDF: ")
    arquivo1 = arquivo1 + '.pdf' #forçando o arquivo estar em pdf
    doc1 = fitz.open(arquivo1)  # abrindo o pdf
    paginas= []
    while True:
        paginas.append((int(input("Digite o número da página: ")))-1) #pois o python começa a contagem no 0
        resp = str(input("Que continuar inserindo páginas? [S/N]: "))
        if resp in 'Nn':
            break
    doc1.select(paginas)
    arquivo2 = input("Digite o nome do 2° PDF: ")
    arquivo2 = arquivo2 + '.pdf'
    doc2 = fitz.open(arquivo2)  # abrindo o pdf
    paginas= []
    while True:
        paginas.append((int(input("Digite o número da página: ")))-1) #pois o python começa a contagem no 0
        resp = str(input("Que continuar inserindo páginas? [S/N]: "))
        if resp in 'Nn':
            break
    doc2.select(paginas)
    doc1.insertPDF(doc2)
    doc1.save("PDF_Combinado.pdf")
    print("PDFs combinados")
elif(opcao==2):
    arquivo1 = input("Digite o nome do PDF: ")
    arquivo1 = arquivo1 + '.pdf'
    doc1 = fitz.open(arquivo1)  # abrindo o pdf
    paginas= []
    while True:
        paginas.append(int(input("Digite o número da página: ")))
        resp = str(input("Que continuar inserindo páginas? [S/N]: "))
        if resp in 'Nn':
            break
    doc1.select(paginas)
    doc1.save("Pdf_Combinado.pdf")
    print("PDF combinado")
elif(opcao==3):
    arquivo1 = input("Digite o nome do PDF: ")
    arquivo1 = arquivo1 + '.pdf'
    doc1 = fitz.open(arquivo1)  # abrindo o pdf
    while True:
        i= int(input("Digite o número da página a ser removida: "))
        doc1.deletePage(i) #remove página selecionada
        resp = str(input("Que continuar removendo páginas? [S/N]: "))
        if resp in 'Nn':
            break
    doc1.save("PDF_Modificado.pdf") #salvando Pdf modificado
    print("PDF Modificado")
elif(opcao==4):
    arquivo1 = input("Digite o nome do PDF: ")
    arquivo1 = arquivo1 + '.pdf'
    doc1 = fitz.open(arquivo1)  # abrindo o pdf
    print("Metadados: {0}",doc1.metadata)
else:
    print("Opcao inválida")


