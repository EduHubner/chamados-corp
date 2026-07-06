import { useEffect, useState } from "react";
import { api } from "../api/client";

const PERFIS = ["funcionario", "tecnico", "gestor", "admin"];

export default function AdminUsuarios() {
  const [usuarios, setUsuarios] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const [nome, setNome] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [perfil, setPerfil] = useState("funcionario");

  async function carregar() {
    setCarregando(true);
    try {
      const dados = await api.adminListarUsuarios();
      setUsuarios(dados);
    } catch (e) {
      setErro(e.message);
    }
    setCarregando(false);
  }

  useEffect(() => {
    carregar();
  }, []);

  async function handleCriar(e) {
    e.preventDefault();
    setErro("");
    try {
      await api.adminCriarUsuario({ nome, email, senha, perfil });
      setNome("");
      setEmail("");
      setSenha("");
      setPerfil("funcionario");
      carregar();
    } catch (e) {
      setErro(e.message);
    }
  }

  async function alterarPerfil(usuario, novoPerfil) {
    try {
      await api.adminAtualizarUsuario(usuario.id, { perfil: novoPerfil });
      carregar();
    } catch (e) {
      setErro(e.message);
    }
  }

  async function alternarAtivo(usuario) {
    try {
      await api.adminAtualizarUsuario(usuario.id, { ativo: !usuario.ativo });
      carregar();
    } catch (e) {
      setErro(e.message);
    }
  }

  return (
    <div className="pagina">
      <h2>Administração de Usuários</h2>
      {erro && <p className="erro">{erro}</p>}

      <form className="cartao formulario-chamado" onSubmit={handleCriar}>
        <h3>Cadastrar novo usuário</h3>
        <input
          placeholder="Nome"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="E-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Senha provisória"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          required
        />
        <select value={perfil} onChange={(e) => setPerfil(e.target.value)}>
          {PERFIS.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <button type="submit">Cadastrar usuário</button>
      </form>

      {carregando ? (
        <p>Carregando...</p>
      ) : (
        <div className="cartao">
          <h3>Usuários cadastrados</h3>
          <table className="tabela-usuarios">
            <thead>
              <tr>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Perfil</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map((u) => (
                <tr key={u.id}>
                  <td>{u.nome}</td>
                  <td>{u.email}</td>
                  <td>
                    <select
                      value={u.perfil}
                      onChange={(e) => alterarPerfil(u, e.target.value)}
                    >
                      {PERFIS.map((p) => (
                        <option key={p} value={p}>{p}</option>
                      ))}
                    </select>
                  </td>
                  <td>{u.ativo ? "Ativo" : "Inativo"}</td>
                  <td>
                    <button onClick={() => alternarAtivo(u)}>
                      {u.ativo ? "Desativar" : "Ativar"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
