import Link from 'next/link';

export default async function RutinasPage() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}rutinas/`, { cache: 'no-store' });
  const rutinas = await res.json();

  return (
    <main className="min-h-screen bg-bg text-text p-8">
      <h1 className="text-3xl font-bold mb-6">Listado de Rutinas</h1>
      <section className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {rutinas.map((rutina: any) => (
          <div key={rutina.id} className="bg-surface border border-border rounded-lg p-6 shadow">
            <h2 className="text-xl font-semibold text-primary mb-2">{rutina.nombre}</h2>
            <p className="text-text mb-4">{rutina.descripcion}</p>
            <span className="inline-block bg-accent text-surface px-2 py-1 text-sm rounded mb-4">
              {rutina.dificultad}
            </span>
            <Link href={`/rutinas/${rutina.id}`} className="block text-secondary hover:underline">
              Ver detalles
            </Link>
          </div>
        ))}
      </section>
    </main>
  );
}
