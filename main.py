import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🕵️ Ferramenta de Diagnóstico de Arquivo CSV")
st.info("Faça o upload do arquivo CSV que está apresentando o ParserError para inspecionar seu conteúdo.")

# 1. Upload do arquivo problemático
uploaded_file = st.file_uploader(
    "Faça o upload do seu 'Rel Tesouraria Pagamentos.csv'",
    type=['csv']
)

if uploaded_file:
    # 2. Mostra as primeiras linhas do arquivo como texto puro
    st.subheader("Conteúdo Bruto do Arquivo (Primeiras 20 linhas)")
    
    # Lê as primeiras linhas para inspeção visual
    file_content_bytes = uploaded_file.getvalue()
    
    # Tenta decodificar com diferentes encodings comuns
    try:
        st.write("Tentando decodificar com 'latin1'...")
        file_content_str = file_content_bytes.decode('latin1')
        st.code(file_content_str, language='text')
    except UnicodeDecodeError:
        st.write("Falhou com 'latin1'. Tentando decodificar com 'utf-8'...")
        try:
            file_content_str = file_content_bytes.decode('utf-8')
            st.code(file_content_str, language='text')
        except Exception as e:
            st.error(f"Não foi possível decodificar o arquivo. Erro: {e}")
    
    st.markdown("---")
    st.warning(
        "**O que procurar no texto acima:**\n\n"
        "- **Linhas no topo:** Existem linhas de título ou em branco antes dos nomes das colunas?\n"
        "- **Separador:** O caractere que separa as colunas é realmente um ponto e vírgula (`;`)?\n"
        "- **Aspas:** Você vê algum campo de texto com aspas (`\"`) que pareçam fora do lugar?"
    )
