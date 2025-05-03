export default function PalettePage() {
    const colors = [
      { name: 'primary', class: 'bg-primary', hex: '#1E3A8A' },
      { name: 'secondary', class: 'bg-secondary', hex: '#F59E0B' },
      { name: 'accent', class: 'bg-accent', hex: '#84CC16' },
      { name: 'bg', class: 'bg-bg', hex: '#F3F4F6' },
      { name: 'surface', class: 'bg-surface', hex: '#FFFFFF' },
      { name: 'border', class: 'bg-border', hex: '#D1D5DB' },
      { name: 'text', class: 'bg-text', hex: '#0F172A' },
    ];
  
    return (
      <main className="min-h-screen p-10 bg-bg text-text">
        <h1 className="text-4xl font-bold mb-8">Overview de la Paleta</h1>
  
        {/* Color Swatches */}
        <section className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {colors.map(color => (
            <div key={color.name} className="rounded-lg shadow overflow-hidden">
              <div className={`${color.class} h-24 w-full`}></div>
              <div className="p-4 bg-surface">
                <p className="font-semibold capitalize">{color.name}</p>
                <p className="text-sm">{color.hex}</p>
                <p className="text-xs italic">class: {color.class}</p>
              </div>
            </div>
          ))}
        </section>
  
        {/* Typography */}
        <section className="space-y-4 mb-16">
          <h2 className="text-2xl font-semibold">Tipografía</h2>
          <p className="text-lg">Texto normal (text-text)</p>
          <p className="text-lg text-primary">Texto primario (text-primary)</p>
          <p className="text-lg text-secondary">Texto secundario (text-secondary)</p>
          <p className="text-lg text-accent">Texto de acento (text-accent)</p>
        </section>
  
        {/* Buttons */}
        <section className="mb-16">
          <h2 className="text-2xl font-semibold mb-4">Botones</h2>
          <div className="space-x-4">
            <button className="bg-primary text-surface px-4 py-2 rounded">Primary</button>
            <button className="bg-secondary text-surface px-4 py-2 rounded">Secondary</button>
            <button className="bg-accent text-surface px-4 py-2 rounded">Accent</button>
            <button className="bg-surface text-text px-4 py-2 rounded border border-border">Outline</button>
          </div>
        </section>
      </main>
    );
  }