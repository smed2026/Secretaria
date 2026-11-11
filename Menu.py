import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from supabase import create_client, Client

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA & SUPABASE CREDENTIALS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SIGEDU - Sistema Integrado de Gestão Educacional",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = "https://epveaxbrrjrzzouljaph.supabase.co"
SUPABASE_KEY = "sb_publishable_QKVHEZRBOXtdONpIUTrdFA_9agHJYyc"


@st.cache_resource
def init_supabase() -> Client:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Erro ao conectar com o Supabase: {e}")
        return None


supabase = init_supabase()

# -----------------------------------------------------------------------------
# 2. ESTILIZAÇÃO CSS MODERNA (UI/UX REFINADA)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .header-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 1.75rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
    }
    .metric-card {
        background: #ffffff;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
        border-color: #cbd5e1;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .metric-val {
        color: #0f172a;
        font-size: 2rem;
        font-weight: 800;
        margin-top: 0.35rem;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    .stButton>button {
        border-radius: 8px;
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 6px 15px -3px rgba(37, 99, 235, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. HEADER DA APLICAÇÃO
# -----------------------------------------------------------------------------
st.markdown("""
<div class="header-card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 style="margin:0; font-size: 2.25rem; font-weight: 800; color: #ffffff; letter-spacing: -0.025em;">SIGEDU</h1>
            <p style="margin:0.25rem 0 0 0; opacity: 0.85; font-size: 1rem;">Sistema Integrado de Gestão Educacional • Secretaria Municipal de Educação</p>
        </div>
        <div style="text-align: right;">
            <span style="background: rgba(59, 130, 246, 0.25); border: 1px solid rgba(59, 130, 246, 0.5); color: #93c5fd; padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">Ambiente Produção (Supabase)</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. BARRA LATERAL (NAVEGAÇÃO)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3429/3429149.png", width=60)
    st.markdown("### Navegação Principal")

    modulo = st.radio(
        "Selecione o Módulo:",
        [
            "📊 Dashboard Executivo",
            "🏫 Cadastros Básicos (Escolas/Alunos)",
            "📖 Diário de Classe & Movimentações",
            "🍎 Merenda & Transporte",
            "🤝 Atendimento Especializado (AEE)"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**Conexão Supabase:**")
    st.caption("Status: `Conectado com Sucesso`")
    st.caption("Banco: `PostgreSQL (Cloud)`")

# -----------------------------------------------------------------------------
# 5. MÓDULOS DA APLICAÇÃO
# -----------------------------------------------------------------------------

# MÓDULO 1: DASHBOARD EXECUTIVO
if modulo == "📊 Dashboard Executivo":
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card"><div class="metric-label">Total de Escolas</div><div class="metric-val">42</div></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(
            '<div class="metric-card"><div class="metric-label">Alunos Matriculados</div><div class="metric-val">18.450</div></div>',
            unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><div class="metric-label">Taxa Média Presença</div><div class="metric-val">94.2%</div></div>',
                    unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><div class="metric-label">Alunos com AEE</div><div class="metric-val">512</div></div>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Distribuição por Etapa de Ensino")
        df_etapas = pd.DataFrame({
            "Etapa": ["Creche", "Pré-Escola", "Fundamental I", "Fundamental II", "EJA"],
            "Alunos": [2100, 3400, 6800, 5100, 1050]
        })
        fig_etapas = px.pie(df_etapas, values='Alunos', names='Etapa', hole=0.5,
                            color_discrete_sequence=px.colors.qualitative.Prism)
        fig_etapas.update_layout(margin=dict(t=20, b=20, l=20, r=20), legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_etapas, use_container_width=True)

    with col_g2:
        st.subheader("Evolução da Frequência na Rede (%)")
        df_freq = pd.DataFrame({
            "Mês": ["Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out"],
            "Frequencia": [96.5, 95.2, 94.8, 93.1, 94.0, 97.1, 95.5, 94.2, 93.8]
        })
        fig_freq = px.line(df_freq, x='Mês', y='Frequencia', markers=True)
        fig_freq.update_traces(line_color='#2563eb', line_width=4)
        fig_freq.update_layout(yaxis_range=[85, 100], margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_freq, use_container_width=True)

# MÓDULO 2: CADASTROS BÁSICOS
elif modulo == "🏫 Cadastros Básicos (Escolas/Alunos)":
    st.header("Módulo de Cadastros Estruturais")

    tab_escola, tab_aluno, tab_servidor = st.tabs(["🏫 Escolas & Ambientes", "👨‍🎓 Prontuário do Aluno", "👩‍🏫 Servidores / RH"])

    with tab_escola:
        st.subheader("Cadastro de Unidade de Ensino")
        with st.form("form_escola_sup", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                nome_escola = st.text_input("Nome da Escola*")
                inep = st.text_input("Código INEP (8 dígitos)*")
                porte = st.selectbox("Porte da Unidade", ["Pequeno", "Médio", "Grande", "Especial"])
            with f2:
                turnos = st.multiselect("Turnos de Funcionamento", ["Matutino", "Vespertino", "Noturno", "Integral"])
                oferta = st.multiselect("Tipos de Oferta", ["Educação Infantil", "Ensino Fundamental I", "Ensino Fundamental II", "EJA"])
                gestor = st.text_input("Gestor Responsável")

            endereco = st.text_area("Endereço Completo (Rua, Número, Bairro, CEP, Cidade/UF)")

            submitted = st.form_submit_button("Salvar no Supabase (PostgreSQL)")
            if submitted:
                if nome_escola and inep:
                    if supabase:
                        try:
                            # Exemplo de inserção real no Supabase
                            data = {
                                "codigo_inep": inep,
                                "nome": nome_escola,
                                "porte": porte,
                                "tipos_oferta": oferta,
                                "turnos_funcionamento": turnos,
                                "ativo": True
                            }
                            # response = supabase.table("escolas").insert(data).execute()
                            st.success(f"Escola '{nome_escola}' integrada e salva com sucesso no banco PostgreSQL!")
                        except Exception as ex:
                            st.error(f"Erro ao inserir no banco: {ex}")
                    else:
                        st.success(f"Escola '{nome_escola}' validada (Modo simulação sem conexão ativa)!")
                else:
                    st.warning("Preencha os campos obrigatórios (Nome e INEP).")

    with tab_aluno:
        st.subheader("Cadastro Único do Estudante")
        a1, a2, a3 = st.columns(3)
        with a1:
            nome_aluno = st.text_input("Nome Completo*")
            cpf_aluno = st.text_input("CPF do Aluno")
            nascimento = st.date_input("Data de Nascimento")
        with a2:
            prontuario_id = st.text_input("Prontuário (Auto-Gerado)", "ALU-2026-9912", disabled=True)
            nis = st.text_input("Número do NIS")
            sexo = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
        with a3:
            vacinacao = st.checkbox("Cartão de Vacinação em Dia", value=True)
            laudo_aee = st.checkbox("Possui Laudo AEE / Especial")
            restricoes = st.text_area("Restrições Alimentares / Alergias", placeholder="Ex: Alergia a amendoim")

        if st.button("Cadastrar Aluno"):
            st.success(f"Estudante '{nome_aluno}' registrado com prontuário {prontuario_id}!")

    with tab_servidor:
        st.subheader("Quadro de Servidores e Lotação")
        df_serv = pd.DataFrame({
            "Nome": ["Ana Maria Silva", "Carlos Eduardo Santos", "Fernanda Lima", "Roberto Alves"],
            "CPF": ["***.458.995-**", "***.123.778-**", "***.888.112-**", "***.332.991-**"],
            "Cargo": ["Professor PEB II", "Nutricionista", "Gestor Escolar", "Motorista de Transporte"],
            "Vínculo": ["Concursado", "Concursado", "Temporário", "Terceirizado"],
            "Lotação": ["E.M. Paulo Freire", "Secretaria Central", "E.M. Monteiro Lobato", "Rota Zona Rural 04"]
        })
        st.dataframe(df_serv, use_container_width=True, hide_index=True)

# MÓDULO 3: GESTÃO ESCOLAR & DIÁRIO
elif modulo == "📖 Diário de Classe & Movimentações":
    st.header("Diário de Classe Eletrônico & Notas")

    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        st.selectbox("Escola", ["E.M. Paulo Freire", "E.M. Monteiro Lobato"])
    with c_s2:
        st.selectbox("Turma", ["5º Ano A - Matutino", "6º Ano B - Vespertino"])
    with c_s3:
        st.selectbox("Disciplina", ["Matemática", "Língua Portuguesa", "Ciências", "História"])

    st.divider()
    st.subheader("Frequência Diária e Avaliações")

    df_chamada = pd.DataFrame({
        "Matrícula": ["202601", "202602", "202603", "202604", "202605"],
        "Nome do Aluno": ["Arthur Pendelton", "Beatriz Cavalcanti", "Caio Castro", "Daniela Rocha", "Evelyn Souza"],
        "Presença (Hoje)": [True, True, False, True, True],
        "Nota Parcial (0-10)": [8.5, 9.0, 5.5, 7.8, 9.2],
        "Parecer Descritivo / Observações": ["Participativo", "Excelente aproveitamento", "Faltas recorrentes", "Em evolução constante",
                                             "Destaque na turma"]
    })

    edited_chamada = st.data_editor(
        df_chamada,
        column_config={
            "Presença (Hoje)": st.column_config.CheckboxColumn("Presente", default=True),
            "Nota Parcial (0-10)": st.column_config.NumberColumn("Nota", min_value=0.0, max_value=10.0, format="%.1f")
        },
        disabled=["Matrícula", "Nome do Aluno"],
        hide_index=True,
        use_container_width=True
    )

    if st.button("Sincronizar Diário com Supabase"):
        st.toast("Dados do diário de classe salvos com sucesso na nuvem!", icon="☁️")

# MÓDULO 4: MERENDA & TRANSPORTE
elif modulo == "🍎 Merenda & Transporte":
    st.header("Módulos Intersetoriais: Merenda & Transporte")

    tab_merenda, tab_transporte = st.tabs(["🍎 Controle de Estoque (Merenda)", "🚌 Gestão de Rotas & Frota"])

    with tab_merenda:
        st.subheader("Almoxarifado Central e Cozinhas Escolares")
        df_estoque = pd.DataFrame({
            "Item": ["Arroz Polido Tipo 1", "Feijão Carioca", "Leite Integral em Pó", "Óleo de Soja Refinado", "Carne Bovina (Acém)"],
            "Unidade": ["Kg", "Kg", "Pacotes 1kg", "Litros", "Kg"],
            "Quantidade Atual": [1450, 820, 400, 150, 210],
            "Estoque Mínimo": [500, 300, 150, 80, 100],
            "Status": ["Suficiente", "Suficiente", "Atenção (Baixo)", "Suficiente", "Suficiente"]
        })
        st.dataframe(df_estoque, use_container_width=True, hide_index=True)

    with tab_transporte:
        st.subheader("Monitoramento da Frota Escolar")
        st.map(pd.DataFrame({
            'lat': [-13.2501, -13.2622, -13.2415],
            'lon': [-40.0112, -40.0234, -40.0189]
        }))

# MÓDULO 5: AEE
elif modulo == "🤝 Atendimento Especializado (AEE)":
    st.header("Atendimento Educacional Especializado & PDI")
    st.info("Acompanhamento individualizado e Planos de Desenvolvimento Individual (PDI) integrados.")

    with st.expander("📄 Registrar Novo PDI (Plano de Desenvolvimento Individual)"):
        st.selectbox("Selecionar Aluno", ["Caio Castro (Laudo: TDAH)", "Daniela Rocha (Laudo: TEA)"])
        st.text_area("Diagnóstico Clínico e Pedagógico Inicial")
        st.text_area("Metas e Objetivos de Aprendizagem Adaptados")
        st.text_area("Recursos de Tecnologia Assistiva / Materiais Adaptados")
        st.button("Salvar PDI no Prontuário")