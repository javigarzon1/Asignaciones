export default function Notifications({ items }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="p-2 bg-yellow-50 border rounded mb-2">
      <h3 className="font-bold text-sm mb-1">Avisos</h3>
      <ul className="text-xs list-disc pl-4">
        {items.map((n, i) => (
          <li key={i}>{n}</li>
        ))}
      </ul>
    </div>
  );
}
