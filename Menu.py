import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from supabase import create_client, Client

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CONEXÃO SUPABASE
# ==============================================================================
st.set_page_config(
    page_title="SIGEM - Gestão Educacional Municipal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUPABASE_URL = "https://epveaxbrrjrzzouljaph.supabase.co"
SUPABASE_KEY = "sb_publishable_QKVHEZRBOXtdONpIUTrdFA_9agHJYyc"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ==============================================================================
# 2. ESTILIZAÇÃO CSS MODERNA
# ==============================================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .main-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.9;
        font-size: 0.95rem;
    }
    div[data-testid="metric-container"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNÇÕES AUXILIARES DE BANCO DE DADOS
# ==============================================================================
def carregar_tabela(nome_tabela: str, filtros: dict = None) -> pd.DataFrame:
    try:
        query = supabase.table(nome_tabela).select("*")
        if filtros:
            for col, val in filtros.items():
                if val is not None:
                    query = query.eq(col, val)
        res = query.execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.warning(f"Aviso ao consultar '{nome_tabela}': {e}")
        return pd.DataFrame()

# ==============================================================================
# 4. CONTROLE DE AUTENTICAÇÃO (LOGIN)
# ==============================================================================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

def tela_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class="main-header" style="text-align:center;">
            <h1>🎓 SIGEM</h1>
            <p>Sistema Integrado de Gestão Educacional Municipal</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            st.subheader("Acesso ao Sistema")
            login_input = st.text_input("Usuário / Login", placeholder="Ex: admin")
            senha_input = st.text_input("Senha", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary")

            if submit:
                if not login_input.strip() or not senha_input.strip():
                    st.warning("Informe o usuário e a senha.")
                    return

                try:
                    res = (
                        supabase.table("usuarios_sistema")
                        .select("*")
                        .eq("login", login_input.strip())
                        .eq("senha_hash", senha_input.strip())
                        .eq("ativo", True)
                        .execute()
                    )
                    if res.data:
                        st.session_state.usuario = res.data[0]
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas ou usuário inativo.")
                except Exception as e:
                    st.error("Erro de permissão ou conexão com o Supabase.")
                    st.info("Certifique-se de ter executado o script SQL de permissões (GRANT) no painel do Supabase.")
                    with st.expander("Detalhes técnicos do erro"):
                        st.code(str(e))

if st.session_state.usuario is None:
    tela_login()
    st.stop()

user = st.session_state.usuario
escola_vinculada = user.get("escola_id")  # None = Acesso global da SMED

# ==============================================================================
# 5. MENU LATERAL (NAVEGAÇÃO DINÂMICA POR PERMISSÃO)
# ==============================================================================
with st.sidebar:
    st.markdown(f"### 👤 {user['nome_exibicao']}")
    st.caption(f"Perfil: **{user['perfil']}**")
    st.divider()

    opcoes_menu = ["📊 Painel Executivo (BI)"]
    if user.get("perm_admin_rede"):
        opcoes_menu.append("🏫 Escolas e Turmas")
    if user.get("perm_gestao_servidores"):
        opcoes_menu.append("👩‍🏫 Servidores e Lotação")
    if user.get("perm_matriculas"):
        opcoes_menu.append("🎒 Alunos e Matrículas")
    if user.get("perm_diario_classe"):
        opcoes_menu.append("📖 Diário de Classe Digital")
    if user.get("perm_educacao_especial"):
        opcoes_menu.append("🧩 Educação Especial (AEE)")
    if user.get("perm_merenda_transporte"):
        opcoes_menu.append("🍎 Merenda e Transporte")
    if user.get("perm_admin_rede"):
        opcoes_menu.append("🔐 Usuários e Permissões")

    menu_selecionado = st.radio("Navegação", opcoes_menu, label_visibility="collapsed")

    st.divider()
    ano_letivo_atual = st.selectbox("Ano Letivo", [2026, 2025, 2027], index=0)
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state.usuario = None
        st.rerun()

# ==============================================================================
# 6. MÓDULO 1: PAINEL EXECUTIVO (BI)
# ==============================================================================
if menu_selecionado == "📊 Painel Executivo (BI)":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Painel de Indicadores da Rede Municipal</h1>
        <p>Visão consolidada de matrículas, unidades escolares, servidores e inclusão.</p>
    </div>
    """, unsafe_allow_html=True)

    df_escolas = carregar_tabela("escolas", {"id": escola_vinculada} if escola_vinculada else None)
    df_alunos = carregar_tabela("alunos")
    df_matriculas = carregar_tabela("matriculas", {"ano_letivo": ano_letivo_atual, "escola_id": escola_vinculada})
    df_servidores = carregar_tabela("servidores", {"ativo": True})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Unidades Escolares", len(df_escolas))
    c2.metric("Matrículas Ativas", len(df_matriculas[df_matriculas["situacao"] == "Ativa"]) if not df_matriculas.empty else 0)
    c3.metric("Servidores Ativos", len(df_servidores))
    qtd_aee = len(df_alunos[df_alunos["publico_aee"] == True]) if not df_alunos.empty else 0
    c4.metric("Estudantes Público AEE", qtd_aee)

    st.divider()
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Matrículas por Unidade Escolar")
        if not df_matriculas.empty and not df_escolas.empty:
            merged = df_matriculas.merge(df_escolas, left_on="escola_id", right_on="id", suffixes=("", "_esc"))
            contagem = merged.groupby("nome").size().reset_index(name="Total de Alunos")
            fig = px.bar(contagem, x="nome", y="Total de Alunos", color="nome", text_auto=True)
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Alunos")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cadastre escolas e matrículas para visualizar o gráfico.")

    with col_g2:
        st.subheader("Distribuição de Servidores por Cargo")
        if not df_servidores.empty:
            cargos = df_servidores.groupby("cargo").size().reset_index(name="Quantidade")
            fig2 = px.pie(cargos, names="cargo", values="Quantidade", hole=0.45)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Nenhum servidor cadastrado até o momento.")

# ==============================================================================
# 7. MÓDULO 2: ESCOLAS E TURMAS
# ==============================================================================
elif menu_selecionado == "🏫 Escolas e Turmas":
    st.title("🏫 Gestão de Unidades Escolares e Turmas")
    tab1, tab2 = st.tabs(["Unidades Escolares", "Turmas do Ano Letivo"])

    with tab1:
        with st.expander("➕ Cadastrar Nova Unidade Escolar", expanded=False):
            with st.form("form_escola"):
                c1, c2, c3 = st.columns([1, 2, 1])
                inep = c1.text_input("Código INEP *")
                nome_esc = c2.text_input("Nome da Escola *")
                zona = c3.selectbox("Zona *", ["Urbana", "Rural"])

                c4, c5, c6 = st.columns([2, 1, 1])
                tipologia = c4.text_input("Tipologia *", placeholder="Ex: Creche e Fundamental I")
                capacidade = c5.number_input("Capacidade Física", min_value=10, value=200)
                tel_esc = c6.text_input("Telefone")
                end_esc = st.text_input("Endereço Completo")

                if st.form_submit_button("Salvar Escola", type="primary"):
                    if inep and nome_esc:
                        try:
                            supabase.table("escolas").insert({
                                "codigo_inep": inep.strip(), "nome": nome_esc.strip(), "zona": zona,
                                "tipologia": tipologia.strip(), "capacidade_alunos": capacidade,
                                "telefone": tel_esc, "endereco": end_esc
                            }).execute()
                            st.success("Escola cadastrada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar escola: {e}")
                    else:
                        st.warning("Preencha os campos obrigatórios (*).")

        df_esc = carregar_tabela("escolas", {"id": escola_vinculada} if escola_vinculada else None)
        st.dataframe(df_esc, use_container_width=True, hide_index=True)

    with tab2:
        df_esc = carregar_tabela("escolas", {"id": escola_vinculada} if escola_vinculada else None)
        if df_esc.empty:
            st.warning("Cadastre ao menos uma escola antes de criar turmas.")
        else:
            with st.expander("➕ Criar Nova Turma", expanded=True):
                with st.form("form_turma"):
                    esc_map = dict(zip(df_esc["nome"], df_esc["id"]))
                    c1, c2 = st.columns(2)
                    esc_nome = c1.selectbox("Unidade Escolar *", list(esc_map.keys()))
                    nome_turma = c2.text_input("Nome da Turma *", placeholder="Ex: 3º Ano B")

                    c3, c4, c5 = st.columns(3)
                    etapa = c3.selectbox("Etapa", ["Educação Infantil", "Fundamental I", "Fundamental II", "EJA"])
                    turno = c4.selectbox("Turno", ["Matutino", "Vespertino", "Noturno", "Integral"])
                    vagas = c5.number_input("Total de Vagas", min_value=5, value=30)

                    if st.form_submit_button("Criar Turma", type="primary"):
                        if nome_turma:
                            try:
                                supabase.table("turmas").insert({
                                    "escola_id": esc_map[esc_nome], "ano_letivo": ano_letivo_atual,
                                    "nome": nome_turma.strip(), "etapa_ensino": etapa,
                                    "turno": turno, "vagas_totais": vagas
                                }).execute()
                                st.success("Turma criada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao criar turma: {e}")
                        else:
                            st.warning("Informe o nome da turma.")

            df_turmas = carregar_tabela("turmas", {"ano_letivo": ano_letivo_atual, "escola_id": escola_vinculada})
            if not df_turmas.empty:
                df_turmas_view = df_turmas.merge(df_esc[["id", "nome"]], left_on="escola_id", right_on="id", suffixes=("_turma", "_escola"))
                st.dataframe(df_turmas_view[["nome_escola", "nome_turma", "etapa_ensino", "turno", "vagas_totais"]], use_container_width=True, hide_index=True)

# ==============================================================================
# 8. MÓDULO 3: SERVIDORES E LOTAÇÃO
# ==============================================================================
elif menu_selecionado == "👩‍🏫 Servidores e Lotação":
    st.title("👩‍🏫 Gestão de Pessoas e Lotação")
    tab_cad, tab_lot = st.tabs(["Cadastro de Servidores", "Lotação nas Escolas"])

    with tab_cad:
        with st.expander("➕ Cadastrar Servidor", expanded=False):
            with st.form("form_servidor"):
                c1, c2, c3 = st.columns([2, 1, 1])
                nome_s = c1.text_input("Nome Completo *")
                cpf_s = c2.text_input("CPF *")
                tel_s = c3.text_input("Telefone")

                c4, c5, c6 = st.columns(3)
                cargo_s = c4.selectbox("Cargo *", [
                    "Professor(a)", "Diretor(a)", "Vice-Diretor(a)",
                    "Coordenador(a) Pedagógico(a)", "Secretário(a) Escolar",
                    "Monitor(a) AEE / Apoio", "Merendeira", "Serviços Gerais", "Motorista"
                ])
                vinculo_s = c5.selectbox("Vínculo *", ["Efetivo", "Temporário / REDA", "Comissionado", "Terceirizado"])
                formacao_s = c6.text_input("Formação / Titulação", placeholder="Ex: Pedagogia / Pós-graduação")

                if st.form_submit_button("Cadastrar Servidor", type="primary"):
                    if nome_s and cpf_s:
                        try:
                            supabase.table("servidores").insert({
                                "nome": nome_s.strip(), "cpf": cpf_s.strip(), "telefone": tel_s,
                                "cargo": cargo_s, "vinculo": vinculo_s, "formacao": formacao_s
                            }).execute()
                            st.success("Servidor cadastrado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar servidor: {e}")
                    else:
                        st.warning("Nome e CPF são obrigatórios.")

        st.dataframe(carregar_tabela("servidores"), use_container_width=True, hide_index=True)

    with tab_lot:
        df_serv = carregar_tabela("servidores", {"ativo": True})
        df_esc = carregar_tabela("escolas", {"id": escola_vinculada} if escola_vinculada else None)
        if not df_serv.empty and not df_esc.empty:
            with st.form("form_lotacao"):
                st.subheader("Vincular Servidor a uma Unidade Escolar")
                serv_map = dict(zip(df_serv["nome"] + " (" + df_serv["cargo"] + ")", df_serv["id"]))
                esc_map = dict(zip(df_esc["nome"], df_esc["id"]))

                c1, c2 = st.columns(2)
                s_sel = c1.selectbox("Servidor *", list(serv_map.keys()))
                e_sel = c2.selectbox("Escola de Lotação *", list(esc_map.keys()))

                c3, c4, c5 = st.columns(3)
                turno_l = c3.selectbox("Turno", ["Matutino", "Vespertino", "Noturno", "Integral"])
                ch_l = c4.number_input("Carga Horária Semanal (h)", min_value=10, max_value=60, value=20)
                func_l = c5.text_input("Atividade / Disciplina", placeholder="Ex: Regência 1º Ano")

                if st.form_submit_button("Confirmar Lotação", type="primary"):
                    try:
                        supabase.table("lotacoes").insert({
                            "servidor_id": serv_map[s_sel], "escola_id": esc_map[e_sel],
                            "ano_letivo": ano_letivo_atual, "turno": turno_l,
                            "carga_horaria_semanal": ch_l, "funcao_exercida": func_l
                        }).execute()
                        st.success("Lotação registrada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao registrar lotação: {e}")

        df_lot = carregar_tabela("lotacoes", {"ano_letivo": ano_letivo_atual, "escola_id": escola_vinculada})
        if not df_lot.empty and not df_serv.empty and not df_esc.empty:
            view_lot = df_lot.merge(df_serv[["id", "nome", "cargo"]], left_on="servidor_id", right_on="id")
            view_lot = view_lot.merge(df_esc[["id", "nome"]], left_on="escola_id", right_on="id", suffixes=("_servidor", "_escola"))
            st.dataframe(view_lot[["nome_servidor", "cargo", "nome_escola", "turno", "carga_horaria_semanal", "funcao_exercida"]], use_container_width=True, hide_index=True)

# ==============================================================================
# 9. MÓDULO 4: ALUNOS E MATRÍCULAS
# ==============================================================================
elif menu_selecionado == "🎒 Alunos e Matrículas":
    st.title("🎒 Secretaria Escolar: Alunos e Matrículas")
    tab_al, tab_mat = st.tabs(["Cadastro de Estudantes", "Efetivar Matrícula"])

    with tab_al:
        with st.expander("➕ Novo Cadastro de Estudante", expanded=True):
            with st.form("form_aluno"):
                c1, c2, c3 = st.columns([2, 1, 1])
                nome_al = c1.text_input("Nome Completo do Aluno *")
                nasc_al = c2.date_input("Data de Nascimento *", value=date(2015, 1, 1))
                cpf_al = c3.text_input("CPF do Aluno")

                c4, c5, c6 = st.columns([2, 1, 1])
                resp_al = c4.text_input("Nome do Responsável Legal *")
                tel_resp = c5.text_input("Telefone / WhatsApp")
                zona_al = c6.selectbox("Zona de Residência", ["Urbana", "Rural"])

                c7, c8 = st.columns([1, 2])
                pub_aee = c7.checkbox("Estudante Público-Alvo AEE / Inclusão?")
                det_aee = c8.text_input("Especificação AEE / Laudo / Monitor", placeholder="Ex: TEA - Necessita de monitor de apoio")
                rest_alim = st.text_input("Restrição Alimentar (Merenda)", placeholder="Ex: Intolerância à lactose")

                if st.form_submit_button("Salvar Cadastro do Aluno", type="primary"):
                    if nome_al and resp_al:
                        try:
                            supabase.table("alunos").insert({
                                "nome": nome_al.strip(), "data_nascimento": str(nasc_al),
                                "cpf": cpf_al.strip() if cpf_al.strip() else None,
                                "nome_responsavel": resp_al.strip(), "telefone_responsavel": tel_resp,
                                "zona_residencia": zona_al, "publico_aee": pub_aee,
                                "detalhes_aee": det_aee, "restricao_alimentar": rest_alim
                            }).execute()
                            st.success("Estudante cadastrado!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar estudante: {e}")
                    else:
                        st.warning("Nome do aluno e do responsável são obrigatórios.")

        st.dataframe(carregar_tabela("alunos"), use_container_width=True, hide_index=True)

    with tab_mat:
        df_al = carregar_tabela("alunos")
        df_esc = carregar_tabela("escolas", {"id": escola_vinculada} if escola_vinculada else None)
        df_tur = carregar_tabela("turmas", {"ano_letivo": ano_letivo_atual, "escola_id": escola_vinculada})

        if not df_al.empty and not df_esc.empty and not df_tur.empty:
            esc_map = dict(zip(df_esc["nome"], df_esc["id"]))
            esc_escolhida = st.selectbox("Selecione a Escola", list(esc_map.keys()))
            turmas_esc = df_tur[df_tur["escola_id"] == esc_map[esc_escolhida]]

            if turmas_esc.empty:
                st.warning("Esta escola ainda não possui turmas cadastradas para o ano letivo.")
            else:
                with st.form("form_matricula"):
                    al_map = dict(zip(df_al["nome"], df_al["id"]))
                    tur_map = dict(zip(turmas_esc["nome"] + " (" + turmas_esc["turno"] + ")", turmas_esc["id"]))

                    c1, c2, c3 = st.columns([2, 2, 1])
                    al_sel = c1.selectbox("Estudante *", list(al_map.keys()))
                    tur_sel = c2.selectbox("Turma *", list(tur_map.keys()))
                    transp = c3.checkbox("Utiliza Transporte Escolar?")

                    if st.form_submit_button("Confirmar Matrícula", type="primary"):
                        try:
                            supabase.table("matriculas").insert({
                                "aluno_id": al_map[al_sel],
                                "turma_id": tur_map[tur_sel],
                                "escola_id": esc_map[esc_escolhida],
                                "ano_letivo": ano_letivo_atual,
                                "utiliza_transporte": transp
                            }).execute()
                            st.success("Matrícula realizada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Não foi possível matricular (verifique se o aluno já possui matrícula neste ano): {e}")

# ==============================================================================
# 10. MÓDULO 5: DIÁRIO DE CLASSE DIGITAL
# ==============================================================================
elif menu_selecionado == "📖 Diário de Classe Digital":
    st.title("📖 Diário de Classe Digital")
    df_esc = carregar_tabela("escolas", {"id": escola_vinculada} if escola_vinculada else None)
    df_tur = carregar_tabela("turmas", {"ano_letivo": ano_letivo_atual, "escola_id": escola_vinculada})
    df_mat = carregar_tabela("matriculas", {"ano_letivo": ano_letivo_atual, "situacao": "Ativa"})
    df_al = carregar_tabela("alunos")
    df_disc = carregar_tabela("disciplinas")

    if df_esc.empty or df_tur.empty or df_mat.empty:
        st.info("É necessário ter escolas, turmas e alunos matriculados para utilizar o Diário.")
    else:
        c1, c2 = st.columns(2)
        esc_map = dict(zip(df_esc["nome"], df_esc["id"]))
        esc_sel = c1.selectbox("Unidade Escolar", list(esc_map.keys()))

        turmas_filtradas = df_tur[df_tur["escola_id"] == esc_map[esc_sel]]
        if turmas_filtradas.empty:
            st.warning("Sem turmas nesta escola.")
            st.stop()

        tur_map = dict(zip(turmas_filtradas["nome"] + " - " + turmas_filtradas["turno"], turmas_filtradas["id"]))
        tur_sel = c2.selectbox("Turma", list(tur_map.keys()))
        turma_id_atual = tur_map[tur_sel]

        alunos_turma = df_mat[df_mat["turma_id"] == turma_id_atual].merge(df_al, left_on="aluno_id", right_on="id")

        if alunos_turma.empty:
            st.warning("Nenhum aluno matriculado nesta turma.")
        else:
            tab_freq, tab_notas = st.tabs(["✅ Chamada / Frequência", "📝 Lançamento de Notas"])

            with tab_freq:
                data_chamada = st.date_input("Data da Aula", value=date.today())
                with st.form("form_frequencia"):
                    st.write("Desmarque os alunos ausentes:")
                    presencas = {}
                    for _, row in alunos_turma.iterrows():
                        badge_aee = " 🧩 [AEE]" if row["publico_aee"] else ""
                        presencas[row["id_x"]] = st.checkbox(f"{row['nome']}{badge_aee}", value=True, key=f"freq_{row['id_x']}")

                    if st.form_submit_button("Salvar Frequência do Dia", type="primary"):
                        try:
                            registros = [
                                {
                                    "matricula_id": mat_id,
                                    "turma_id": turma_id_atual,
                                    "data_aula": str(data_chamada),
                                    "presente": status,
                                    "registrado_por": user["id"]
                                }
                                for mat_id, status in presencas.items()
                            ]
                            supabase.table("frequencias").upsert(registros, on_conflict="matricula_id,data_aula").execute()
                            st.success("Frequência registrada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao salvar frequência: {e}")

            with tab_notas:
                if df_disc.empty:
                    st.warning("Nenhuma disciplina cadastrada.")
                else:
                    c_d, c_u = st.columns(2)
                    disc_map = dict(zip(df_disc["nome"], df_disc["id"]))
                    disc_sel = c_d.selectbox("Componente Curricular", list(disc_map.keys()))
                    unidade_sel = c_u.selectbox("Unidade / Bimestre", [1, 2, 3, 4])

                    with st.form("form_notas"):
                        notas_input = {}
                        for _, row in alunos_turma.iterrows():
                            col_n, col_v = st.columns([3, 1])
                            col_n.markdown(f"**{row['nome']}**")
                            notas_input[row["id_x"]] = col_v.number_input(
                                "Nota", min_value=0.0, max_value=10.0, step=0.5, value=0.0,
                                key=f"nota_{row['id_x']}", label_visibility="collapsed"
                            )

                        if st.form_submit_button("Salvar Notas da Unidade", type="primary"):
                            try:
                                payload_notas = [
                                    {
                                        "matricula_id": mat_id,
                                        "disciplina_id": disc_map[disc_sel],
                                        "unidade": unidade_sel,
                                        "nota": valor
                                    }
                                    for mat_id, valor in notas_input.items()
                                ]
                                supabase.table("avaliacoes_notas").upsert(payload_notas, on_conflict="matricula_id,disciplina_id,unidade").execute()
                                st.success("Notas salvas com sucesso!")
                            except Exception as e:
                                st.error(f"Erro ao salvar notas: {e}")

# ==============================================================================
# 11. MÓDULO 6: EDUCAÇÃO ESPECIAL (AEE)
# ==============================================================================
elif menu_selecionado == "🧩 Educação Especial (AEE)":
    st.title("🧩 Acompanhamento da Educação Especial e Inclusiva")
    df_al = carregar_tabela("alunos", {"publico_aee": True})
    if df_al.empty:
        st.info("Nenhum estudante marcado como público-alvo AEE no cadastro.")
    else:
        st.metric("Total de Estudantes em Acompanhamento AEE", len(df_al))
        st.dataframe(
            df_al[["nome", "data_nascimento", "nome_responsavel", "telefone_responsavel", "detalhes_aee"]],
            use_container_width=True,
            hide_index=True
        )

# ==============================================================================
# 12. MÓDULO 7: MERENDA E TRANSPORTE ESCOLAR
# ==============================================================================
elif menu_selecionado == "🍎 Merenda e Transporte":
    st.title("🍎 Alimentação Escolar (PNAE) e Transporte (PNATE)")
    tab_mer, tab_transp = st.tabs(["Controle Diário de Merenda", "Rotas de Transporte Escolar"])

    with tab_mer:
        df_esc = carregar_tabela("escolas", {"id": escola_vinculada} if escola_vinculada else None)
        if not df_esc.empty:
            with st.form("form_merenda"):
                esc_map = dict(zip(df_esc["nome"], df_esc["id"]))
                c1, c2, c3 = st.columns([2, 1, 1])
                e_mer = c1.selectbox("Unidade Escolar", list(esc_map.keys()))
                t_mer = c2.selectbox("Turno", ["Matutino", "Vespertino", "Noturno", "Integral"])
                qtd_ref = c3.number_input("Refeições Servidas", min_value=1, value=120)
                cardapio = st.text_input("Cardápio Servido no Dia", placeholder="Ex: Arroz, feijão, carne moída com legumes e suco")

                if st.form_submit_button("Registrar Produção Diária", type="primary"):
                    try:
                        supabase.table("merenda_registros").insert({
                            "escola_id": esc_map[e_mer], "turno": t_mer,
                            "refeicoes_servidas": qtd_ref, "cardapio_do_dia": cardapio
                        }).execute()
                        st.success("Registro de merenda salvo!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar registro de merenda: {e}")

        st.dataframe(carregar_tabela("merenda_registros", {"escola_id": escola_vinculada}), use_container_width=True, hide_index=True)

    with tab_transp:
        df_esc = carregar_tabela("escolas", {"id": escola_vinculada} if escola_vinculada else None)
        if not df_esc.empty:
            with st.form("form_rota"):
                esc_map = dict(zip(df_esc["nome"], df_esc["id"]))
                c1, c2 = st.columns(2)
                nome_r = c1.text_input("Nome da Rota *", placeholder="Ex: Linha Zona Rural - Fazenda Nova")
                esc_r = c2.selectbox("Escola de Destino", list(esc_map.keys()))
                itin_r = st.text_area("Itinerário / Povoados Atendidos *")
                c3, c4, c5 = st.columns(3)
                mot_r = c3.text_input("Motorista")
                placa_r = c4.text_input("Placa do Veículo")
                cap_r = c5.number_input("Capacidade", min_value=4, value=40)

                if st.form_submit_button("Cadastrar Rota", type="primary"):
                    if nome_r and itin_r:
                        try:
                            supabase.table("rotas_transporte").insert({
                                "escola_destino_id": esc_map[esc_r], "nome_rota": nome_r.strip(),
                                "itinerario": itin_r.strip(), "motorista": mot_r,
                                "placa_veiculo": placa_r, "capacidade_passageiros": cap_r
                            }).execute()
                            st.success("Rota cadastrada!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao cadastrar rota: {e}")
                    else:
                        st.warning("Nome da rota e itinerário são obrigatórios.")

        st.dataframe(carregar_tabela("rotas_transporte"), use_container_width=True, hide_index=True)

# ==============================================================================
# 13. MÓDULO 8: USUÁRIOS E PERMISSÕES (RBAC)
# ==============================================================================
elif menu_selecionado == "🔐 Usuários e Permissões":
    st.title("🔐 Controle de Usuários e Permissões de Acesso")
    df_esc = carregar_tabela("escolas")

    with st.expander("➕ Criar Novo Acesso ao Sistema", expanded=True):
        with st.form("form_usuario"):
            c1, c2, c3, c4 = st.columns(4)
            nome_u = c1.text_input("Nome de Exibição *")
            login_u = c2.text_input("Login *")
            senha_u = c3.text_input("Senha Inicial *", type="password")
            perfil_u = c4.selectbox("Perfil", ["Admin SMED", "Diretor(a)", "Secretário(a) Escolar", "Professor(a)", "Apoio / Merenda"])

            opcoes_esc = {"Acesso Global (SMED)": None}
            if not df_esc.empty:
                opcoes_esc.update(dict(zip(df_esc["nome"], df_esc["id"])))
            esc_vinc = st.selectbox("Restringir à Escola (Opcional)", list(opcoes_esc.keys()))

            st.markdown("**Permissões Granulares:**")
            p1, p2, p3 = st.columns(3)
            perm_rede = p1.checkbox("Administrar Rede / Escolas")
            perm_serv = p1.checkbox("Gerir Servidores / Lotação")
            perm_mat = p2.checkbox("Gerir Alunos / Matrículas")
            perm_diario = p2.checkbox("Acessar Diário de Classe")
            perm_mer = p3.checkbox("Merenda e Transporte")
            perm_aee = p3.checkbox("Educação Especial (AEE)")

            if st.form_submit_button("Criar Usuário", type="primary"):
                if nome_u and login_u and senha_u:
                    try:
                        supabase.table("usuarios_sistema").insert({
                            "nome_exibicao": nome_u.strip(), "login": login_u.strip(), "senha_hash": senha_u.strip(),
                            "perfil": perfil_u, "escola_id": opcoes_esc[esc_vinc],
                            "perm_admin_rede": perm_rede, "perm_gestao_servidores": perm_serv,
                            "perm_matriculas": perm_mat, "perm_diario_classe": perm_diario,
                            "perm_merenda_transporte": perm_mer, "perm_educacao_especial": perm_aee
                        }).execute()
                        st.success("Usuário criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário: {e}")
                else:
                    st.warning("Nome, login e senha são obrigatórios.")

    df_users = carregar_tabela("usuarios_sistema")
    if not df_users.empty:
        st.dataframe(df_users.drop(columns=["senha_hash"]), use_container_width=True, hide_index=True)