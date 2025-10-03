import { useState } from "react";

export default function Filters({ onFilter }) {
  const [estado, setEstado] = useState("");
  const [tipologia, setTipologia] = useState("");

  const apply = () => {
    onFilter({ estado, tipologia });
  };

  return (
    <div className="flex gap-2 p-2">
      <select
        value={estado}
        onChange={(e) => setEstado(e.target.value)}
        className="border p-1 rounded"
      >
        <option value="">Todos los estados</option>
        <option value="En proceso">En proceso</option>
        <option value="Finalizada">Finalizada</option>
      </select>
      <input
        placeholder="Tipología..."
        value={tipologia}
        onChange={(e) => setTipologia(e.target.value)}
        className="border p-1 rounded"
      />
      <button onClick={apply} className="px-2 py-1 bg-blue-500 text-white rounded">
        Filtrar
      </button>
    </div>
  );
}
