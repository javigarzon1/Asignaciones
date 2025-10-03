import { useState } from "react";
import api from "../api/api";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");

  const upload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await api.post("/upload-excel/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMsg(`Subidas: ${res.data.created}, Asignadas: ${res.data.assigned}`);
    } catch (e) {
      setMsg("Error al subir el archivo");
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Subir Excel</h1>
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-2"
      />
      <button
        onClick={upload}
        className="px-4 py-2 bg-green-600 text-white rounded"
      >
        Subir y Asignar
      </button>
      {msg && <div className="mt-2 text-sm">{msg}</div>}
    </div>
  );
}
