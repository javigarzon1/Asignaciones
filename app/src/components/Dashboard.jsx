import { useEffect, useState } from "react";
import api from "../api/api";
import ConsultaCard from "../components/ConsultaCard";
import Filters from "../components/Filters";
import Notifications from "../components/Notifications";

export default function Dashboard() {
  const [consultas, setConsultas] = useState([]);
  const [notis, setNotis] = useState([]);

  const load = async (filters = {}) => {
    const res = await api.get("/consultas/", { params: filters });
    setConsultas(res.data);
  };

  useEffect(() => {
    load();
    // notificaciones dummy
    setNotis(["Consulta urgente vence en 1h", "3 consultas vencen hoy"]);
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Dashboard</h1>
      <Notifications items={notis} />
      <Filters onFilter={load} />
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-2 mt-2">
        {consultas.map((c) => (
          <ConsultaCard key={c.id} consulta={c} />
        ))}
      </div>
    </div>
  );
}
