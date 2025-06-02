/* File: frontend/app/page.tsx */
import Image from "next/image";
import Link from "next/link";

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
            La plataforma definitiva para crear, filtrar y seguir rutinas de
            entrenamiento personalizadas. Filtra por parte del cuerpo, nivel,
            dificultad y mucho más.
          </p>
          <Link
            href="/registro"
            className="inline-block bg-primary hover:opacity-90 text-surface font-semibold px-8 py-3 rounded-lg transition"
          >
            Empieza ahora
          </Link>
        </div>
        <div className="w-full md:w-1/2 mb-10 md:mb-0">
          <Image
            src="/home/home-1.jpg"
            alt="Entrenamiento personalizado"
            className="w-full h-auto"
            width={3000}
            height={2000}
          />
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-surface py-16">
        <div className="max-w-5xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-10 text-center">
          <div>
            <Image
              src="/home/home-2.jpg"
              alt="Filtrado"
              className="mx-auto"
              width={5157}
              height={3438}
            />
            <h3 className="text-xl font-semibold text-primary mb-2">
              Amplia base de datos
            </h3>
            <p className="text-text">
              Encuentra cientos de ejercicios y rutinas por parte del cuerpo, nivel y
              dificultad.
            </p>
          </div>
          <div>
            <Image
              src="/home/home-3.jpg"
              alt="Recomendaciones"
              className="mx-auto"
              width={3000}
              height={2000}
            />
            <h3 className="text-xl font-semibold text-primary mb-2">
              Sistema de Recomendación
            </h3>
            <p className="text-text">
              Descubre nuevos ejercicios y rutinas basados en tus preferencias y necesidades.
            </p>
          </div>
          <div>
            <Image
              src="/home/home-4.jpg"
              alt="Integraciones Saludables"
              width={3000}
              height={2000}
              className="mx-auto"
            />
            <h3 className="text-xl font-semibold text-primary mb-2">
              Integraciones Saludables
            </h3>
            <p className="text-text">
              Regístrate con Google Fit, Apple Health, Fitbit y más en unos simples pasos.
            </p>
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
            Únete a la comunidad de Workout-RS y optimiza tus objetivos de
            fitness con tecnología de vanguardia.
          </p>
          <Link
            href="/registro"
            className="inline-block bg-surface text-primary font-semibold px-8 py-3 rounded-lg transition hover:bg-gray-100"
          >
            ¡Regístrate gratis!
          </Link>
        </div>
      </section>
    </main>
  );
}
