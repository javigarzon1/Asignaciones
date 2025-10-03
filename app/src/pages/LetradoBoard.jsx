// src/pages/LetradoBoard.jsx
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/api";
import ConsultaCard from "../components/ConsultaCard";

export default function LetradoBoard() {
  const { id } = useParams();
  const [consultas, setConsultas] = useState([]);
  const [letrado, setLetrado] = useState(null);

  useEffect(() => {
    async function load() {
      const resL = await api.get(`/letrados/${id}/`);
      setLetrado(resL.data);
      const resC = await api.get("/consultas/", { params: { letrado_id: id } });
      setConsultas(resC.data);
    }
    load();
  }, [id]);

  return (
    <div className="p-4">
      {letrado && (
        <h1 className="text-xl font-bold mb-4">
          Consultas de {letrado.nombre}
        </h1>
      )}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-2 mt-2">
        {consultas.map((c) => (
          <ConsultaCard key={c.id} consulta={c} />
        ))}
      </div>
    </div>
  );
}
