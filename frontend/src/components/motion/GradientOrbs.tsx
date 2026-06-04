export function GradientOrbs() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      <div
        className="orb -left-32 top-0 h-[500px] w-[500px] bg-white/[0.07] animate-pulse-glow"
        style={{ animationDelay: '0s' }}
      />
      <div
        className="orb orb-slow -right-24 top-1/4 h-[400px] w-[400px] bg-white/[0.05]"
        style={{ animationDelay: '-5s' }}
      />
      <div
        className="orb bottom-0 left-1/3 h-[350px] w-[350px] bg-white/[0.04]"
        style={{ animationDelay: '-10s' }}
      />
    </div>
  )
}

export function HeroGrid() {
  return (
    <div
      className="pointer-events-none absolute inset-0 opacity-[0.15]"
      aria-hidden
      style={{
        backgroundImage: `
          linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
        `,
        backgroundSize: '64px 64px',
        maskImage: 'radial-gradient(ellipse 70% 60% at 50% 0%, black, transparent)',
      }}
    />
  )
}
