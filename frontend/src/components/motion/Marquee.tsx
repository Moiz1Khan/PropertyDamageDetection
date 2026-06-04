interface MarqueeProps {
  items: string[]
}

export function Marquee({ items }: MarqueeProps) {
  const doubled = [...items, ...items]

  return (
    <div className="relative overflow-hidden border-y border-black/[0.06] bg-white py-5">
      <div className="absolute left-0 top-0 z-10 h-full w-20 bg-gradient-to-r from-white to-transparent" />
      <div className="absolute right-0 top-0 z-10 h-full w-20 bg-gradient-to-l from-white to-transparent" />
      <div className="flex w-max animate-marquee gap-10">
        {doubled.map((item, i) => (
          <span
            key={`${item}-${i}`}
            className="shrink-0 text-sm font-medium tracking-wide text-black/20"
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}
