import { createContext, useContext, useState } from "react";
import { api } from "./api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(() => {
    const salvo = localStorage.getItem("usuario");
    return salvo ? JSON.parse(salvo) : null;
  });

  async function login(email, senha) {
    const resp = await api.login(email, senha);
    localStorage.setItem("token", resp.access_token);
    localStorage.setItem("usuario", JSON.stringify(resp.usuario));
    setUsuario(resp.usuario);
  }

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    setUsuario(null);
  }

  return (
    <AuthContext.Provider value={{ usuario, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
