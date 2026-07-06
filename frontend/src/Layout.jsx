import { Link, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function Layout() {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div>
      <nav className="barra-navegacao">
        <div className="logo">Chamados Corp</div>
        <div className="links">
          <Link to="/chamados">Chamados</Link>
          {["gestor", "admin"].includes(usuario?.perfil) && (
            <Link to="/dashboard">Dashboard</Link>
          )}
          {["gestor", "admin"].includes(usuario?.perfil) && (
            <Link to="/categorias">Categorias</Link>
          )}
          {usuario?.perfil === "admin" && (
            <Link to="/admin/usuarios">Usuários</Link>
          )}
        </div>
        <div className="usuario-info">
          <span>{usuario?.nome} ({usuario?.perfil})</span>
          <button onClick={handleLogout}>Sair</button>
        </div>
      </nav>
      <Outlet />
    </div>
  );
}
