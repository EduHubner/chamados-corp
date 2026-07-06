import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../AuthContext";

const CORES_STATUS = {
  aberto: "#3b82f6",
  em_andamento: "#f59e0b",
  aguardando_usuario: "#a855f7",
  resolvido: "#22c55e",
  fechado: "#6b7280",
};

export default function Chamados() {
  const { usuario } = useAuth();
  const [chamados, setChamados] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [prioridade, setPrioridade] = useState("media");
  const [categoriaId, setCategoriaId] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [editandoId, setEditandoId] = useState(null);
  const [descricaoEdicao, setDescricaoEdicao] = useState("");
  const [anexosAbertos, setAnexosAbertos] = useState({});
  const [anexosPorChamado, setAnexosPorChamado] = useState({});
  const [enviandoAnexo, setEnviandoAnexo] = useState(null);
  const [erroAnexo, setErroAnexo] = useState({});

  async function carregar() {
    setCarregando(true);
    const dados = await api.listarChamados();
    setChamados(dados);
    setCarregando(false);
  }

  async function carregarCategorias() {
    const dados = await api.listarCategorias();
    setCategorias(dados);
  }

  useEffect(() => {
    carregar();
    carregarCategorias();
  }, []);

  async function handleCriar(e) {
    e.preventDefault();
    await api.criarChamado({
      titulo,
      descricao,
      prioridade,
      categoria_id: categoriaId || null,
    });
    setTitulo("");
    setDescricao("");
    setPrioridade("media");
    setCategoriaId("");
    carregar();
  }

  async function avancarStatus(chamado) {
    const fluxo = {
      aberto: "em_andamento",
      em_andamento: "resolvido",
      aguardando_usuario: "em_andamento",
      resolvido: "fechado",
    };
    const proximo = fluxo[chamado.status];
    if (!proximo) return;
    await api.atualizarChamado(chamado.id, { status: proximo });
    carregar();
  }

  async function excluir(chamado) {
    const confirmar = window.confirm(
      `Excluir o chamado "${chamado.titulo}"? Esta ação não pode ser desfeita.`
    );
    if (!confirmar) return;
    await api.excluirChamado(chamado.id);
    carregar();
  }

  function iniciarEdicaoDescricao(chamado) {
    setEditandoId(chamado.id);
    setDescricaoEdicao(chamado.descricao);
  }

  function cancelarEdicaoDescricao() {
    setEditandoId(null);
    setDescricaoEdicao("");
  }

  async function salvarDescricao(chamado) {
    await api.atualizarChamado(chamado.id, { descricao: descricaoEdicao });
    setEditandoId(null);
    setDescricaoEdicao("");
    carregar();
  }

  async function alternarAnexos(chamado) {
    const abertoAgora = !anexosAbertos[chamado.id];
    setAnexosAbertos({ ...anexosAbertos, [chamado.id]: abertoAgora });
    if (abertoAgora) {
      await carregarAnexos(chamado.id);
    }
  }

  async function carregarAnexos(chamadoId) {
    try {
      const lista = await api.listarAnexos(chamadoId);
      setAnexosPorChamado((atual) => ({ ...atual, [chamadoId]: lista }));
      setErroAnexo((atual) => ({ ...atual, [chamadoId]: null }));
    } catch (e) {
      setErroAnexo((atual) => ({ ...atual, [chamadoId]: e.message }));
    }
  }

  async function enviarArquivo(chamado, arquivo) {
    if (!arquivo) return;
    setEnviandoAnexo(chamado.id);
    try {
      await api.uploadAnexo(chamado.id, arquivo);
      await carregarAnexos(chamado.id);
    } catch (e) {
      setErroAnexo((atual) => ({ ...atual, [chamado.id]: e.message }));
    }
    setEnviandoAnexo(null);
  }

  const mapaCategorias = Object.fromEntries(categorias.map((c) => [c.id, c.nome]));

  const podeGerenciar = ["tecnico", "gestor", "admin"].includes(usuario?.perfil);
  const podeExcluir = ["tecnico", "admin"].includes(usuario?.perfil);
  const podeEditarDescricao = ["tecnico", "admin"].includes(usuario?.perfil);

  return (
    <div className="pagina">
      <h2>Chamados</h2>

      <form className="cartao formulario-chamado" onSubmit={handleCriar}>
        <h3>Abrir novo chamado</h3>
        <input
          placeholder="Título"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
          required
        />
        <textarea
          placeholder="Descreva o problema ou solicitação"
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          required
        />
        <select value={prioridade} onChange={(e) => setPrioridade(e.target.value)}>
          <option value="baixa">Baixa</option>
          <option value="media">Média</option>
          <option value="alta">Alta</option>
          <option value="critica">Crítica</option>
        </select>
        <select value={categoriaId} onChange={(e) => setCategoriaId(e.target.value)}>
          <option value="">Sem categoria</option>
          {categorias.map((c) => (
            <option key={c.id} value={c.id}>{c.nome}</option>
          ))}
        </select>
        <button type="submit">Abrir chamado</button>
      </form>

      {carregando ? (
        <p>Carregando...</p>
      ) : (
        <div className="lista-chamados">
          {chamados.length === 0 && <p>Nenhum chamado encontrado.</p>}
          {chamados.map((c) => (
            <div className="cartao chamado-item" key={c.id}>
              <div className="chamado-cabecalho">
                <strong>{c.titulo}</strong>
                <span
                  className="badge"
                  style={{ backgroundColor: CORES_STATUS[c.status] }}
                >
                  {c.status.replace("_", " ")}
                </span>
              </div>
              <span className="tag-categoria">
                {c.categoria_id ? (mapaCategorias[c.categoria_id] || "Categoria") : "Sem categoria"}
              </span>

              {editandoId === c.id ? (
                <div className="edicao-descricao">
                  <textarea
                    value={descricaoEdicao}
                    onChange={(e) => setDescricaoEdicao(e.target.value)}
                  />
                  <div className="acoes-chamado">
                    <button onClick={() => salvarDescricao(c)}>Salvar</button>
                    <button className="botao-secundario" onClick={cancelarEdicaoDescricao}>
                      Cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <p>{c.descricao}</p>
              )}

              <div className="chamado-rodape">
                <span>Prioridade: {c.prioridade}</span>
                <div className="acoes-chamado">
                  {podeGerenciar && c.status !== "fechado" && (
                    <button onClick={() => avancarStatus(c)}>
                      Avançar status
                    </button>
                  )}
                  {podeEditarDescricao && editandoId !== c.id && (
                    <button onClick={() => iniciarEdicaoDescricao(c)}>
                      Editar descrição
                    </button>
                  )}
                  <button onClick={() => alternarAnexos(c)}>
                    {anexosAbertos[c.id] ? "Ocultar anexos" : "Anexos"}
                  </button>
                  {podeExcluir && (
                    <button className="botao-perigo" onClick={() => excluir(c)}>
                      Excluir
                    </button>
                  )}
                </div>
              </div>

              {anexosAbertos[c.id] && (
                <div className="secao-anexos">
                  {erroAnexo[c.id] && <p className="erro">{erroAnexo[c.id]}</p>}

                  <ul className="lista-simples">
                    {(anexosPorChamado[c.id] || []).length === 0 && (
                      <li>Nenhum anexo enviado ainda.</li>
                    )}
                    {(anexosPorChamado[c.id] || []).map((a) => (
                      <li key={a.id}>
                        <a href={a.url} target="_blank" rel="noreferrer">
                          {a.nome_arquivo}
                        </a>
                      </li>
                    ))}
                  </ul>

                  <label className="botao-upload">
                    {enviandoAnexo === c.id ? "Enviando..." : "Anexar arquivo"}
                    <input
                      type="file"
                      hidden
                      disabled={enviandoAnexo === c.id}
                      onChange={(e) => enviarArquivo(c, e.target.files[0])}
                    />
                  </label>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
