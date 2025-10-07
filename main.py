import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conciliação de Pagamentos", layout="wide")
st.title("🤖 Conciliador de Títulos: Tesouraria vs. VAN Bancária")
st.markdown("Faça o upload dos relatórios da Tesouraria e da Nexxera para verificar os pagamentos processados.")

# --- 2. FUNÇÕES DE AJUDA ---
def limpar_valor(valor):
    """Converte uma coluna de valor (texto, com vírgula) para número (float)."""
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        try:
            return float(valor.replace('R$', '').strip().replace('.', '').replace(',', '.'))
        except (ValueError, TypeError):
            return 0.0
    return 0.0

@st.cache_data
def converter_df_para_csv(df):
    """Converte um DataFrame para CSV em memória, pronto para download."""
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig', decimal=',').encode('utf-8')


# --- 3. UPLOAD DOS ARQUIVOS ---
st.header("📤 1. Faça o Upload dos Relatórios")
col1, col2 = st.columns(2)

with col1:
    arquivo_tesouraria = st.file_uploader("Relatório da Tesouraria", type=["csv", "xlsx"])

with col2:
    arquivo_nexxera = st.file_uploader("Relatório da VAN (Nexxera)", type=["csv", "xlsx"])


# --- 4. LÓGICA DE PROCESSAMENTO E CONCILIAÇÃO ---
if arquivo_tesouraria and arquivo_nexxera:
    st.header("▶️ 2. Inicie a Conciliação")
    if st.button("Conciliar Relatórios"):
        with st.spinner("Mágica acontecendo... Lendo, padronizando e cruzando os dados..."):
            
            # --- Leitura e Pré-Processamento ---
            df_tesouraria = pd.read_csv(arquivo_tesouraria, sep=';', encoding='latin1', engine='python')
            
            # --- CORREÇÃO APLICADA AQUI: Leitura do arquivo Nexxera ---
            
            # 1. Definimos o cabeçalho que você forneceu
            cabecalho_nexxera = [
                'Status', 'Nome Favorecido/Contribuinte', 'Inscrição', 'Banco', 'Agência', 'Conta', 
                'DAC', 'Operação', 'Seu Número', 'Data Vencimento', 'Data Pagamento', 'Valor', 'Lançamento', 
                'Banco_2', 'Agência_2', 'Conta_2', 'DAC_2', 'Nosso Número', 'Código de Barras', 
                'Data/Hora de Geração', 'Ocorrência 1', 'Ocorrência 2', 'Ocorrência 3', 'Ocorrência 4', 
                'Ocorrência 5', 'Autenticação Bancária', 'Autenticação Legislativa', 'Observação', 
                'Período de Apuração', 'Competência', 'Código da Receita', 'UF', 'Placa', 'Autorizadores', 
                'Número NSA Retorno', 'Autorização 1', 'Autorização 2', 'Autorização 3', 'Autorização 4', 
                'Autorização 5', 'Finalidade / Compl. do Tipo de Serviço', 'Tipo Chave Pix', 'Chave Pix'
            ]
            
            # 2. Lemos o arquivo sem cabeçalho e aplicamos os nomes da nossa lista
            df_nexxera = pd.read_csv(
                arquivo_nexxera, 
                sep=';', 
                encoding='latin1', 
                engine='python',
                header=None, # Informa que o arquivo não tem cabeçalho
                names=cabecalho_nexxera # Aplica os nomes da nossa lista
            )
            # --- FIM DA CORREÇÃO ---

            # Padroniza nomes das colunas e limpa os dados
            # Tabela da Tesouraria
            df_tesouraria.rename(columns={'NOSSO NÚMERO': 'ChaveTitulo', 'VALOR DO TÍTULO': 'Valor'}, inplace=True)
            df_tesouraria['Valor'] = df_tesouraria['Valor'].apply(limpar_valor)
            df_tesouraria['ChaveConciliacao'] = df_tesouraria['ChaveTitulo'].astype(str) + '_' + df_tesouraria['Valor'].astype(str)
            
            # Tabela da Nexxera (Ajuste no rename para usar o nome de coluna que definimos no cabeçalho)
            df_nexxera.rename(columns={'Seu Número': 'ChaveTitulo'}, inplace=True)
            df_nexxera['Valor'] = df_nexxera['Valor'].apply(limpar_valor)
            df_nexxera['ChaveConciliacao'] = df_nexxera['ChaveTitulo'].astype(str) + '_' + df_nexxera['Valor'].astype(str)
            df_nexxera['StatusVAN'] = 'Processado na VAN'
            
            st.success("Arquivos lidos e padronizados com sucesso!")

            # --- A Conciliação (Merge) ---
            df_resultado = pd.merge(
                df_tesouraria,
                df_nexxera[['ChaveConciliacao', 'StatusVAN']],
                on='ChaveConciliacao',
                how='left'
            )
            
            df_conciliados = df_resultado[df_resultado['StatusVAN'].notna()]
            df_nao_encontrados = df_resultado[df_resultado['StatusVAN'].isna()]
            
            st.session_state['df_conciliados'] = df_conciliados
            st.session_state['df_nao_encontrados'] = df_nao_encontrados
            
        st.balloons()
        st.success("Conciliação concluída!")


# --- 5. EXIBIÇÃO DOS RESULTADOS ---
if 'df_conciliados' in st.session_state:
    st.header("📊 3. Resultados da Conciliação")
    
    df_conciliados = st.session_state['df_conciliados']
    df_nao_encontrados = st.session_state['df_nao_encontrados']
    total_tesouraria = len(df_conciliados) + len(df_nao_encontrados)
    
    st.subheader("Resumo Geral")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Títulos na Tesouraria", value=f"{total_tesouraria}")
    kpi2.metric("✅ Conciliados na VAN", value=f"{len(df_conciliados)}")
    kpi3.metric("❌ Não Encontrados na VAN", value=f"{len(df_nao_encontrados)}")
    
    tab_conciliados, tab_nao_encontrados = st.tabs(["✅ Títulos Conciliados", "❌ Títulos Não Encontrados"])
    
    with tab_conciliados:
        st.write(f"Encontrados {len(df_conciliados)} títulos correspondentes no relatório da VAN.")
        st.dataframe(df_conciliados)
        st.download_button("📥 Baixar Lista de Conciliados (CSV)", converter_df_para_csv(df_conciliados), "conciliados.csv", "text/csv")
        
    with tab_nao_encontrados:
        st.write(f"Estes {len(df_nao_encontrados)} títulos da Tesouraria não foram encontrados no relatório da VAN.")
        st.dataframe(df_nao_encontrados)
        st.download_button("📥 Baixar Lista de Pendentes (CSV)", converter_df_para_csv(df_nao_encontrados), "pendentes_conciliacao.csv", "text/csv")
