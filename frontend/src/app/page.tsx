/* File: frontend/app/page.tsx */
import Image from 'next/image';
import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-bg to-surface text-text">
      {/* Hero Section */}
      <section className="flex flex-col-reverse md:flex-row items-center max-w-6xl mx-auto px-6 py-20">
        <div className="w-full md:w-1/2 text-center md:text-left">
          <h1 className="text-4xl md:text-5xl font-extrabold mb-4">
            ¡Bienvenido a <span className="text-primary">Workout-RS</span>!
          </h1>
          <p className="text-lg md:text-xl mb-6">
            La plataforma definitiva para crear, filtrar y seguir rutinas de entrenamiento
            personalizadas. Filtra por parte del cuerpo, nivel, dificultad y mucho más.
          </p>
          <Link href="/registro" className="inline-block bg-primary hover:opacity-90 text-surface font-semibold px-8 py-3 rounded-lg transition">
            Empieza ahora
          </Link>
        </div>
        <div className="w-full md:w-1/2 mb-10 md:mb-0">
          <img
            src="/workout-hero.svg"
            alt="Entrenamiento personalizado"
            className="w-full h-auto"
          />
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-surface py-16">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-10 text-center">
          <div>
            <img src="/icons/filter.svg" alt="Filtrado" className="mx-auto mb-4 h-16" />
            <h3 className="text-xl font-semibold text-primary mb-2">Filtrado Avanzado</h3>
            <p className="text-text">Encuentra ejercicios y rutinas por parte del cuerpo, nivel y dificultad.</p>
          </div>
          <div>
            <img src="/icons/recommend.svg" alt="Recomendaciones" className="mx-auto mb-4 h-16" />
            <h3 className="text-xl font-semibold text-primary mb-2">Sistema de Recomendación</h3>
            <p className="text-text">Descubre nuevas rutinas basadas en tus preferencias y rendimiento.</p>
          </div>
          <div>
            <Image
              src="/home/health-app-integration.png"
              alt="Integraciones Saludables"
              width={4000}
              height={2662}
              className="mx-auto"
            />
            <h3 className="text-xl font-semibold text-primary mb-2">Integraciones Saludables</h3>
            <p className="text-text">Conecta con Google Fit, Samsung Health y más para un seguimiento completo.</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-primary to-secondary text-surface">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Lleva tu entrenamiento al siguiente nivel
          </h2>
          <p className="mb-6 text-text">
            Únete a la comunidad de Workout-RS y optimiza tus objetivos de fitness con tecnología de vanguardia.
          </p>
          <Link href="/registro" className="inline-block bg-surface text-primary font-semibold px-8 py-3 rounded-lg transition hover:bg-gray-100">
            ¡Regístrate gratis!
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-bg py-6 border-t border-border">
        <div className="max-w-6xl mx-auto px-6 text-center text-sm text-text">
          © {new Date().getFullYear()} Workout-RS. Todos los derechos reservados.
        </div>
      </footer>
    </main>
  );
}
