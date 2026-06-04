import { Link } from 'react-router-dom'
import { FadeIn } from '../motion/FadeIn'

export function Footer() {
  return (
    <footer className="border-t border-black/[0.06] bg-white">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <FadeIn>
          <div className="grid gap-12 md:grid-cols-4">
            <div className="md:col-span-1">
              <Link to="/" className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-black">
                  <span className="text-xs font-bold text-white">P</span>
                </div>
                <span className="text-lg font-semibold text-black">PropIQ</span>
              </Link>
              <p className="mt-4 text-sm leading-relaxed text-app-muted">
                AI-powered real estate investment analysis. From damage detection to deal ranking.
              </p>
            </div>
            {[
              { title: 'Product', items: ['Features', 'Pricing', 'Dashboard', 'Reports'] },
              { title: 'Resources', items: ['Documentation', 'API', 'Support', 'Blog'] },
              { title: 'Company', items: ['About', 'Careers', 'Privacy', 'Terms'] },
            ].map((col) => (
              <div key={col.title}>
                <h4 className="text-sm font-semibold text-black">{col.title}</h4>
                <ul className="mt-4 space-y-3">
                  {col.items.map((item) => (
                    <li key={item}>
                      <Link to="/login" className="text-sm text-app-muted transition-colors hover:text-black">
                        {item}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </FadeIn>
        <div className="mt-16 flex flex-col items-center justify-between gap-4 border-t border-black/[0.06] pt-8 md:flex-row">
          <p className="text-xs text-app-muted">© 2026 PropIQ. FCCU COMP497A Final Year Project.</p>
          <p className="text-xs text-app-muted">AI Real Estate Investment Analyzer</p>
        </div>
      </div>
    </footer>
  )
}
