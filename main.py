import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conciliação de Pagamentos", layout="wide")
st.title("🤖 Conciliador de Títulos: Tesouraria vs. VAN Bancária")
st.markdown("Faça o upload dos relatórios para conciliar os dados.")

# --- BARRA LATERAL COM MODO DE DEPURAÇÃO ---
st.sidebar.header("⚙️ Ferramentas")
debug_mode = st.sidebar.toggle("Ativar Modo de Depuração", value=True)
st.sidebar.info("Ative este modo para analisar a estrutura dos arquivos enviados.")

# --- 2. UPLOAD DOS ARQUIVOS ---
st.header("📤 1. Faça o Upload dos Relatórios")
col1, col2 = st.columns(2)
with col1:
    arquivo_tesouraria = st.file_uploader("Relatório da Tesouraria (.xlsx)", type=["xlsx"])
with col2:
    arquivo_nexxera = st.file_uploader("Relatório da VAN (Nexxera) (.xlsx)", type=["xlsx"])

# --- 3. LÓGICA PRINCIPAL ---
if debug_mode:
    st.subheader("🕵️‍♀️ MODO DE DEPURAÇÃO ATIVADO 🕵️‍♀️")
    st.warning("O aplicativo irá apenas analisar e exibir a estrutura dos arquivos.")

    if arquivo_tesouraria:
        with st.expander("Análise do 'Relatório da Tesouraria'", expanded=True):
            try:
                df_test = pd.read_excel(arquivo_tesouraria)
                st.success("Arquivo lido com sucesso!")
                st.write("**Colunas encontradas neste arquivo:**")
                st.code(df_test.columns.tolist())
                st.write("**Pré-visualização dos dados:**")
                st.dataframe(df_test.head(3))
            except Exception as e:
                st.error(f"Falha ao ler o arquivo: {e}")

    if arquivo_nexxera:
        with st.expander("Análise do 'Relatório da VAN (Nexxera)'", expanded=True):
            try:
                df_test = pd.read_excel(arquivo_nexxera, header=None) # Lê sem cabeçalho
                st.success("Arquivo lido com sucesso! (sem cabeçalho)")
                st.write("**Pré-visualização das primeiras linhas (sem nomes de coluna):**")
                st.dataframe(df_test.head(3))
            except Exception as e:
                st.error(f"Falha ao ler o arquivo: {e}")
else:
    # --- MODO DE PRODUÇÃO (CÓDIGO DE CONCILIAÇÃO) ---
    if arquivo_tesouraria and arquivo_nexxera:
        st.header("▶️ 2. Inicie a Conciliação")
        # (Aqui entraria o código de conciliação completo, mas vamos focar na depuração primeiro)
        st.info("Desative o 'Modo de Depuração' na barra lateral para habilitar o botão de conciliação.")
