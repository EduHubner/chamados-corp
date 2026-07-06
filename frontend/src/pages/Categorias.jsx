import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Categorias() {
  const [categorias, setCategorias] = useState([]);
  const [nome, setNome] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  async function carregar() {
    setCarregando(true);
    try {
      const dados = await api.listarCategorias();
      setCategorias(dados);
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
      await api.criarCategoria(nome);
      setNome("");
      carregar();
    } catch (e) {
      setErro(e.message);
    }
  }

  return (
    <div className="pagina">
      <h2>Categorias de Chamados</h2>
      {erro && <p className="erro">{erro}</p>}

      <form className="cartao formulario-chamado" onSubmit={handleCriar}>
        <h3>Nova categoria</h3>
        <input
          placeholder="Nome da categoria (ex.: Hardware, Software, Rede...)"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          required
        />
        <button type="submit">Cadastrar categoria</button>
      </form>

      {carregando ? (
        <p>Carregando...</p>
      ) : (
        <div className="cartao">
          <h3>Categorias cadastradas</h3>
          {categorias.length === 0 && <p>Nenhuma categoria cadastrada ainda.</p>}
          <ul className="lista-simples">
            {categorias.map((c) => (
              <li key={c.id}>{c.nome}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
