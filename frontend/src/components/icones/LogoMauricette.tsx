interface Props {
  className?: string;
}

/**
 * Marque de Mauricette : un document (l'Appel d'Offres) surmonté d'une
 * étincelle (l'assistance de l'IA), dans un badge aux couleurs SMACL.
 */
export function LogoMauricette({ className }: Props) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="logo-mauricette-fond" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#1c4694" />
          <stop offset="1" stopColor="#0d2456" />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="9" fill="url(#logo-mauricette-fond)" />
      <rect x="9" y="8" width="12" height="16" rx="2" fill="#ffffff" />
      <rect x="11.5" y="12" width="7" height="1.5" rx="0.75" fill="#133478" opacity="0.3" />
      <rect x="11.5" y="15" width="7" height="1.5" rx="0.75" fill="#133478" opacity="0.3" />
      <rect x="11.5" y="18" width="4.5" height="1.5" rx="0.75" fill="#133478" opacity="0.3" />
      <path d="M23.6 5.8l1.05 2.3 2.3 1.05-2.3 1.05-1.05 2.3-1.05-2.3-2.3-1.05 2.3-1.05z" fill="#65d8f4" />
    </svg>
  );
}
