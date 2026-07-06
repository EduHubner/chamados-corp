import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import Layout from "./Layout";
import Login from "./pages/Login";
import Chamados from "./pages/Chamados";
import Dashboard from "./pages/Dashboard";
import AdminUsuarios from "./pages/AdminUsuarios";
import Categorias from "./pages/Categorias";

function RotaProtegida({ children }) {
  const { usuario } = useAuth();
  if (!usuario) return <Navigate to="/login" replace />;
  return children;
}

function RotaAdmin({ children }) {
  const { usuario } = useAuth();
  if (!usuario) return <Navigate to="/login" replace />;
  if (usuario.perfil !== "admin") return <Navigate to="/chamados" replace />;
  return children;
}

function RotaGestorOuAdmin({ children }) {
  const { usuario } = useAuth();
  if (!usuario) return <Navigate to="/login" replace />;
  if (!["gestor", "admin"].includes(usuario.perfil)) return <Navigate to="/chamados" replace />;
  return children;
}

function Rotas() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <RotaProtegida>
            <Layout />
          </RotaProtegida>
        }
      >
        <Route path="/chamados" element={<Chamados />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route
          path="/admin/usuarios"
          element={
            <RotaAdmin>
              <AdminUsuarios />
            </RotaAdmin>
          }
        />
        <Route
          path="/categorias"
          element={
            <RotaGestorOuAdmin>
              <Categorias />
            </RotaGestorOuAdmin>
          }
        />
        <Route path="/" element={<Navigate to="/chamados" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Rotas />
      </AuthProvider>
    </BrowserRouter>
  );
}
