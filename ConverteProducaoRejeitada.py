import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
import os
from datetime import datetime

def processar_linha(linha):
    """Processa uma linha do arquivo e extrai as informações solicitadas"""
    
    # Verifica se a linha tem o comprimento mínimo necessário
    if len(linha) < 200:
        return None
    
    try:
        mes_referencia = linha[10:16]  
        data_atendimento = linha[36:44]  
        codigo_sus = linha[49:59]  
        cns = linha[59:74].strip()  
        os_codigo = linha[100:109]  
        nome = linha[112:142].strip() 
        data_nascimento = linha[142:150] 
        cpf = linha[339:349].strip() 
        
        # DEBUG - Mostrar o que está sendo extraído
        print(f"DEBUG - Extração:")
        print(f"Mês Referencia (10-16): '{mes_referencia}'")
        print(f"Data de Atendimento (36-44): '{data_atendimento}'")
        print(f"Codigo SUS (49-59): '{codigo_sus}'")
        print(f"CNS (59-74): '{cns}'")
        print(f"OS (100-109): '{os_codigo}'")
        print(f"Nome (112-142): '{nome}'")
        print(f"Data de Nascimento (142-150): '{data_nascimento}'")
        print(f"CPF (339-349): '{cpf}'")
        print("-" * 50)
        
        # Convertendo datas - CORRIGINDO O FORMATO
        try:
            data_atendimento_formatada = datetime.strptime(data_atendimento, '%Y%m%d').strftime('%d/%m/%Y')
        except Exception as e:
            print(f"Erro na data atendimento: {data_atendimento} - {e}")
            data_atendimento_formatada = "Data inválida"
        
        try:
            data_nascimento_formatada = datetime.strptime(data_nascimento, '%Y%m%d').strftime('%d/%m/%Y')
        except Exception as e:
            print(f"Erro na data nascimento: {data_nascimento} - {e}")
            data_nascimento_formatada = "Data inválida"
        
        # Tratando CNS
        if not cns or cns.isspace() or len(cns) == 0:
            cns_tratado = "Não possui CNS no arquivo"
        else:
            cns_tratado = cns
        
        # Tratando CPF
        if not cpf or cpf.isspace() or len(cpf) == 0:
            cpf_tratado = "Não possui CPF no arquivo"
        else:
            # Verificar se é um CPF válido
            if cpf.isdigit() and len(cpf) == 11:
                cpf_tratado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
            else:
                cpf_tratado = cpf
        
        return {
            'MesReferencia': mes_referencia,
            'DataAtendimento': data_atendimento_formatada,
            'CodigoSus': codigo_sus,
            'CNS': cns_tratado,
            'OS': os_codigo,
            'Nome': nome,
            'DataNascimento': data_nascimento_formatada,
            'CPF': cpf_tratado
        }
        
    except Exception as e:
        print(f"Erro ao processar linha: {e}")
        print(f"Linha problemática: {linha}")
        return None

def processar_arquivo():
    """Função principal para processar o arquivo"""
    # Abrir diálogo para selecionar arquivo
    arquivo_origem = filedialog.askopenfilename(
        title="Selecione o arquivo TXT",
        filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
    )
    
    if not arquivo_origem:
        return
    
    # Atualizar status
    status_label.config(text="Processando arquivo...")
    root.update()
    
    try:
        dados = []
        total_linhas = 0
        linhas_processadas = 0
        
        # Contar linhas para a barra de progresso
        with open(arquivo_origem, 'r', encoding='utf-8') as file:
            total_linhas = sum(1 for _ in file)
        
        # Configurar barra de progresso
        progress_bar['maximum'] = total_linhas
        
        # Ler e processar o arquivo
        with open(arquivo_origem, 'r', encoding='utf-8') as file:
            for i, linha in enumerate(file):
                # Pular linhas muito curtas (cabeçalhos ou linhas inválidas)
                linha = linha.rstrip('\n\r')  # Remover quebras de linha
                if len(linha.strip()) < 100:
                    continue
                    
                resultado = processar_linha(linha)
                if resultado:
                    dados.append(resultado)
                linhas_processadas += 1
                progress_bar['value'] = linhas_processadas
                
                # Atualizar a cada 10 linhas para ver o debug
                if linhas_processadas % 10 == 0:
                    status_label.config(text=f"Processando... {linhas_processadas}/{total_linhas} linhas")
                    root.update()
        
        if not dados:
            messagebox.showerror("Erro", "Nenhum dado válido foi encontrado no arquivo.")
            status_label.config(text="Nenhum dado válido encontrado")
            progress_bar['value'] = 0
            return
        
        # Criar DataFrame
        df = pd.DataFrame(dados)
        
        # Perguntar onde salvar
        arquivo_destino = filedialog.asksaveasfilename(
            title="Salvar arquivo Excel",
            defaultextension=".xlsx",
            filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")],
            initialfile="dados_processados.xlsx"
        )
        
        if not arquivo_destino:
            status_label.config(text="Processamento cancelado")
            progress_bar['value'] = 0
            return
        
        # Salvar como Excel
        with pd.ExcelWriter(arquivo_destino, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados Processados')
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Dados Processados']
            for i, column in enumerate(df.columns):
                max_length = max(df[column].astype(str).map(len).max(), len(column))
                worksheet.column_dimensions[chr(65 + i)].width = max_length + 2
        
        # Atualizar status
        status_label.config(text=f"Processamento concluído! {len(dados)} registros processados.")
        
        # Mostrar preview no terminal
        print(f"\n✅ PROCESSAMENTO CONCLUÍDO!")
        print(f"📊 Total de registros: {len(dados)}")
        print(f"💾 Salvo em: {arquivo_destino}")
        print(f"\n📋 Preview dos primeiros 2 registros:")
        print(df.head(2).to_string(index=False))
        
        messagebox.showinfo("Sucesso", f"Arquivo processado com sucesso!\n{len(dados)} registros salvos em:\n{arquivo_destino}")
        
        # Reseta barra de progresso
        progress_bar['value'] = 0
        
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante o processamento:\n{str(e)}")
        status_label.config(text="Erro no processamento")
        progress_bar['value'] = 0
        import traceback
        traceback.print_exc()

def debug_linha_detalhado():
    """Função para debug detalhado"""
    arquivo_origem = filedialog.askopenfilename(
        title="Selecione o arquivo TXT para debug",
        filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
    )
    
    if not arquivo_origem:
        return
    
    try:
        with open(arquivo_origem, 'r', encoding='utf-8') as file:
            for i, linha in enumerate(file):
                linha = linha.rstrip('\n\r')
                if len(linha.strip()) > 100:  # Pega a primeira linha válida
                    print(f"=== 🎯 DEBUG DETALHADO - LINHA {i+1} ===")
                    print(f"📏 Comprimento total: {len(linha)} caracteres")
                    print(f"📝 Conteúdo completo:\n{linha}")
                    print(f"\n🔍 Posições específicas:")
                    print(f"10-16 (MesReferencia): '{linha[10:16]}'")
                    print(f"36-44 (DataAtendimento): '{linha[36:44]}'")
                    print(f"44-54 (CodigoSus): '{linha[44:54]}'")
                    print(f"69-84 (CNS): '{linha[69:84]}'")
                    print(f"108-117 (OS): '{linha[108:117]}'")
                    print(f"117-147 (Nome): '{linha[117:147]}'")
                    print(f"147-155 (DataNascimento): '{linha[147:155]}'")
                    print(f"155-166 (CPF): '{linha[155:166]}'")
                    
                    # Mostrar contexto around das posições
                    print(f"\n🔎 Contexto around:")
                    print(f"Around MesReferencia (5-25): '{linha[5:25]}'")
                    print(f"Around DataAtendimento (30-50): '{linha[30:50]}'")
                    print(f"Around CNS (60-90): '{linha[60:90]}'")
                    print(f"Around OS (100-120): '{linha[100:120]}'")
                    print(f"Around Nome (110-150): '{linha[110:150]}'")
                    print("=" * 70)
                    break
                    
    except Exception as e:
        messagebox.showerror("Erro Debug", f"Erro durante debug:\n{str(e)}")
        import traceback
        traceback.print_exc()

def criar_interface():
    """Cria a interface gráfica do aplicativo"""
    global root, status_label, progress_bar
    
    root = tk.Tk()
    root.title("Conversor de produção Rejeitada TXT para Excel - PMU")
    root.geometry("800x450")
    root.resizable(False, False)
    
    # Centralizar na tela
    root.eval('tk::PlaceWindow . center')
    
    # Estilo
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 10))
    style.configure('TLabel', font=('Arial', 9))
    
    # Frame principal
    main_frame = ttk.Frame(root, padding="20")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Título
    titulo_label = ttk.Label(main_frame, text="🔧 Conversor de Produção Rejeitada TXT - Para EXCEL", font=('Arial', 20, 'bold'))
    titulo_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
    
    # Botão para processar
    processar_btn = ttk.Button(main_frame, text="📁 Selecionar e Processar Arquivo TXT", command=processar_arquivo)
    processar_btn.grid(row=1, column=0, columnspan=2, pady=10, padx=20, sticky='ew')
    
    # Botão para debug detalhado
    debug_btn = ttk.Button(main_frame, text="🔍 Debug Detalhado - Verificar Posições", command=debug_linha_detalhado)
    debug_btn.grid(row=2, column=0, columnspan=2, pady=5, padx=20, sticky='ew')
    
    # Barra de progresso
    progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate')
    progress_bar.grid(row=3, column=0, columnspan=2, pady=15, padx=20, sticky='ew')
    
    # Label de status
    status_label = ttk.Label(main_frame, text="✅ Pronto para processar arquivo", font=('Arial', 10))
    status_label.grid(row=4, column=0, columnspan=2, pady=5)
    
    # Informações
    info_text = """📋 Dados extraídos:
    
• Mês Referência (10-16) • Data de atendimento (36-44) • Codigo SUS (44-54)
• CNS (69-84) • OS (108-117) • Nome (117-147)
• Data de nascimento (147-155) • CPF (155-166)

🔔 OBSERVAÇÕES:

• Copyright: Darley Silva - 2025
• Versão: 1.0.0
• Contato: (34) 9 9187 - 8703
"""
    
    info_label = ttk.Label(main_frame, text=info_text, font=('Courier', 9))
    info_label.grid(row=5, column=0, columnspan=2, pady=(15, 0))
    
    # Configurar expansão
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    
    return root

def main():
    """Função principal"""
    global root
    root = criar_interface()
    root.mainloop()

if __name__ == "__main__":
    main()