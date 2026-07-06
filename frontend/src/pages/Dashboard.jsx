import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Dashboard() {
  const [dados, setDados] = useState(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.dashboard().then(setDados).catch((e) => setErro(e.message));
  }, []);

  if (erro) return <p className="erro">{erro}</p>;
  if (!dados) return <p>Carregando indicadores...</p>;

  return (
    <div className="pagina">
      <h2>Dashboard Gerencial</h2>
      <div className="grade-indicadores">
        <div className="cartao indicador">
          <span className="indicador-valor">{dados.chamados_abertos}</span>
          <span>Chamados abertos</span>
        </div>
        <div className="cartao indicador">
          <span className="indicador-valor">{dados.chamados_concluidos}</span>
          <span>Chamados concluídos</span>
        </div>
        <div className="cartao indicador">
          <span className="indicador-valor">{dados.chamados_em_atraso}</span>
          <span>Em atraso</span>
        </div>
        <div className="cartao indicador">
          <span className="indicador-valor">
            {dados.tempo_medio_resolucao_horas ?? "-"}h
          </span>
          <span>Tempo médio de resolução</span>
        </div>
      </div>

      <div className="cartao">
        <h3>Chamados por categoria</h3>
        {Object.entries(dados.por_categoria).length === 0 && <p>Sem dados.</p>}
        {Object.entries(dados.por_categoria).map(([nome, total]) => (
          <div key={nome} className="linha-categoria">
            <span>{nome}</span>
            <span>{total}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
