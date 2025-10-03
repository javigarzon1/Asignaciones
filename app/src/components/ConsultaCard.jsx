export default function ConsultaCard({ consulta }) {
  return (
    <div
      className={`p-4 rounded-2xl shadow mb-2 ${
        consulta.urgente_sn ? "border-2 border-red-500 bg-red-50" : "border"
      }`}
    >
      <div className="text-sm font-bold">{consulta.ritm}</div>
      <div className="text-xs text-gray-600">
        Tipología: {consulta.tipologia?.nombre || "Sin tipología"}
      </div>
      <div className="text-xs">
        Entrada: {new Date(consulta.fecha_alta).toLocaleString()}
      </div>
      <div className="text-xs">
        Vencimiento: {new Date(consulta.fecha_fin_sla).toLocaleString()}
      </div>
      <div
        className={`text-xs font-semibold ${
          consulta.estado === "En proceso" ? "text-blue-600" : "text-gray-600"
        }`}
      >
        Estado: {consulta.estado}
      </div>
    </div>
  );
}
