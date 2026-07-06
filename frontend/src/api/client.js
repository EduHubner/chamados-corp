// Em produção, o ALB fica na mesma origem (ou defina VITE_API_URL no build).
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!resp.ok) {
    const erro = await resp.json().catch(() => ({}));
    throw new Error(erro.detail || `Erro ${resp.status}`);
  }
  if (resp.status === 204) return null;
  return resp.json();
}

export const api = {
  login: (email, senha) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ email, senha }) }),
  registrar: (dados) =>
    request("/auth/registrar", { method: "POST", body: JSON.stringify(dados) }),
  me: () => request("/auth/me"),
  listarChamados: () => request("/chamados"),
  criarChamado: (dados) =>
    request("/chamados", { method: "POST", body: JSON.stringify(dados) }),
  atualizarChamado: (id, dados) =>
    request(`/chamados/${id}`, { method: "PATCH", body: JSON.stringify(dados) }),
  excluirChamado: (id) => request(`/chamados/${id}`, { method: "DELETE" }),
  listarComentarios: (id) => request(`/chamados/${id}/comentarios`),
  comentar: (id, texto) =>
    request(`/chamados/${id}/comentarios`, { method: "POST", body: JSON.stringify({ texto }) }),
  listarAnexos: (id) => request(`/chamados/${id}/anexos`),
  uploadAnexo: async (id, arquivo) => {
    const formData = new FormData();
    formData.append("arquivo", arquivo);
    const token = getToken();
    const resp = await fetch(`${API_URL}/chamados/${id}/anexos`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!resp.ok) {
      const erro = await resp.json().catch(() => ({}));
      throw new Error(erro.detail || `Erro ${resp.status}`);
    }
    return resp.json();
  },
  listarTarefas: () => request("/tarefas"),
  criarTarefa: (dados) => request("/tarefas", { method: "POST", body: JSON.stringify(dados) }),
  dashboard: () => request("/dashboard"),
  listarCategorias: () => request("/categorias"),
  criarCategoria: (nome) =>
    request("/categorias", { method: "POST", body: JSON.stringify({ nome }) }),
  listarUsuarios: () => request("/usuarios"),

  // Administração de usuários (somente perfil admin)
  adminListarUsuarios: () => request("/admin/usuarios"),
  adminCriarUsuario: (dados) =>
    request("/admin/usuarios", { method: "POST", body: JSON.stringify(dados) }),
  adminAtualizarUsuario: (id, dados) =>
    request(`/admin/usuarios/${id}`, { method: "PATCH", body: JSON.stringify(dados) }),
};
