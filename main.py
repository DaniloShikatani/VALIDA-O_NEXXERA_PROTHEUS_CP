import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Conciliação de Pagamentos", layout="wide")
st.title("🤖 Conciliador de Títulos: Tesouraria vs. VAN Bancária")
st.markdown("Faça o upload dos relatórios da Tesouraria e da Nexxera (em formato Excel) para verificar os pagamentos processados.")

# --- 2. FUNÇÕES DE AJUDA (Não precisamos mais da limpeza de valor aqui) ---
@st.cache_data
def converter_df_para_csv(df):
    """Converte um DataFrame para CSV em memória, pronto para download."""
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig', decimal=',').encode('utf-8')


# --- 3. UPLOAD DOS ARQUIVOS ---
st.header("📤 1. Faça o Upload dos Relatórios")
col1, col2 = st.columns(2)

with col1:
    arquivo_tesouraria = st.file_uploader("Relatório da Tesouraria (.xlsx)", type=["xlsx"])

with col2:
    arquivo_nexxera = st.file_uploader("Relatório da VAN (Nexxera) (.xlsx)", type=["xlsx"])


# --- 4. LÓGICA DE PROCESSAMENTO E CONCILIAÇÃO ---
if arquivo_tesouraria and arquivo_nexxera:
    st.header("▶️ 2. Inicie a Conciliação")
    if st.button("Conciliar Relatórios"):
        with st.spinner("Mágica acontecendo... Lendo, padronizando e cruzando os dados..."):
            
            try:
                # --- Leitura dos Arquivos ---
                df_tesouraria = pd.read_excel(arquivo_tesouraria)
                
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
                df_nexxera = pd.read_excel(arquivo_nexxera, header=None, names=cabecalho_nexxera)
            except Exception as e:
                st.error(f"Erro ao ler um dos arquivos Excel. Verifique se eles não estão corrompidos. Erro: {e}")
                st.stop()

            # --- CORREÇÃO PRINCIPAL: Padronização das Chaves ---
            
            # Padroniza a chave da Tesouraria (converte para texto e remove espaços)
            if 'Id. Cnab' in df_tesouraria.columns:
                df_tesouraria['Id. Cnab'] = df_tesouraria['Id. Cnab'].astype(str).str.strip()
            else:
                st.error("ERRO: A coluna 'Id. Cnab' não foi encontrada no Relatório da Tesouraria.")
                st.stop()

            # Padroniza a chave da Nexxera
            if 'Seu Número' in df_nexxera.columns:
                df_nexxera['Seu Número'] = df_nexxera['Seu Número'].astype(str).str.strip()
                df_nexxera['StatusVAN'] = 'Processado na VAN' # Adiciona uma flag para o merge
            else:
                st.error("ERRO: A coluna 'Seu Número' não foi encontrada no Relatório da Nexxera.")
                st.stop()
            # --- FIM DA CORREÇÃO ---
            
            st.success("Arquivos lidos e chaves padronizadas com sucesso!")

            # --- A Conciliação (Merge) com a nova lógica ---
            # Otimização: Usamos apenas as colunas necessárias da Nexxera para o merge
            df_nexxera_para_merge = df_nexxera[['Seu Número', 'StatusVAN']].drop_duplicates()

            df_resultado = pd.merge(
                df_tesouraria,
                df_nexxera_para_merge,
                left_on='Id. Cnab',     # Chave da tabela da esquerda (Tesouraria)
                right_on='Seu Número',  # Chave da tabela da direita (Nexxera)
                how='left'              # Mantém todos os registros da Tesouraria
            )
            
            # Separa os resultados
            df_conciliados = df_resultado[df_resultado['StatusVAN'].notna()]
            df_nao_encontrados = df_resultado[df_resultado['StatusVAN'].isna()]
            
            # Salva os resultados na memória do app
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
