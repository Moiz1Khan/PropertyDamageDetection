import { Navbar } from '../components/layout/Navbar'
import { Footer } from '../components/layout/Footer'
import { Button } from '../components/ui/Button'
import { FadeIn, StaggerContainer, StaggerItem } from '../components/motion/FadeIn'
import { Marquee } from '../components/motion/Marquee'
import { motion } from 'framer-motion'
import {
  ArrowRight,
  Building2,
  BarChart3,
  Layers,
  Scan,
  Calculator,
  MapPin,
  TrendingUp,
  FileBarChart,
  Shield,
  Star,
} from 'lucide-react'

const marqueeItems = [
  'Property Investors', 'Real Estate Agents', 'Lenders', 'Wholesalers', 'REITs',
  'Fix & Flip', 'Buy & Hold', 'PropTech', 'AI Analysis', 'Deal Ranking',
]

const features = [
  { icon: Scan, title: 'AI Damage Detection', desc: 'CV scans images for roof wear, water damage, and foundation issues.' },
  { icon: Calculator, title: 'Deal Metrics', desc: 'Rehab, ARV, rent, ROI, profit, and max offer in seconds.' },
  { icon: MapPin, title: 'Comps & Area Data', desc: 'Comparable sales and neighborhood trends in one view.' },
  { icon: TrendingUp, title: 'Strategy Engine', desc: 'Flip vs. hold recommendations with rank scores.' },
  { icon: FileBarChart, title: 'PDF Reports', desc: 'Lender-ready investment summaries on one click.' },
  { icon: Shield, title: 'Risk Scoring', desc: 'Structured assessment from damage and market data.' },
]

function ChatMockup() {
  const messages = [
    { role: 'user', text: 'Analyze 1842 Oakwood Drive' },
    { role: 'agent', text: 'Running CV damage scan on 8 images…' },
    { role: 'agent', text: '3 issues found. Est. rehab: $42,000' },
    { role: 'user', text: "What's the max offer?" },
    { role: 'agent', text: 'Max offer: $298,000 · ROI 23.8%', solid: true },
  ]

  return (
    <div className="flex flex-col gap-3 p-6 md:p-8">
      {messages.map((m, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: i * 0.1 }}
          className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
            m.role === 'user'
              ? 'ml-auto border border-white/30 bg-white/15 text-white backdrop-blur-sm'
              : m.solid
                ? 'bg-white text-black shadow-sm'
                : 'border border-white/25 bg-white/20 text-white backdrop-blur-sm'
          }`}
        >
          {m.text}
        </motion.div>
      ))}
    </div>
  )
}

function ChartMockup() {
  return (
    <div className="p-6 md:p-8">
      <div className="rounded-2xl bg-white p-5 shadow-sm">
        <p className="text-xs font-medium text-app-muted">Average ROI</p>
        <p className="mt-1 text-3xl font-semibold tracking-tight text-black">19.4%</p>
        <div className="mt-6 flex items-end gap-1.5 h-24">
          {[40, 65, 45, 80, 55, 90, 70, 85].map((h, i) => (
            <motion.div
              key={i}
              initial={{ height: 0 }}
              whileInView={{ height: `${h}%` }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 + i * 0.05, duration: 0.5 }}
              className="flex-1 rounded-t-md bg-gradient-to-t from-neutral-300 to-neutral-400"
            />
          ))}
        </div>
        <div className="mt-4 flex gap-4 text-xs">
          <span className="flex items-center gap-1.5 text-app-muted">
            <span className="h-2 w-2 rounded-full bg-orange-400" /> Flip deals
          </span>
          <span className="flex items-center gap-1.5 text-app-muted">
            <span className="h-2 w-2 rounded-full bg-blue-400" /> Rental
          </span>
        </div>
      </div>
    </div>
  )
}

export function LandingPage() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-app-bg">
      <Navbar />

      {/* Hero — ElevenAgents split layout */}
      <section className="mx-auto max-w-7xl px-6 pb-8 pt-28 md:pt-32">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 lg:items-end">
          <motion.div
            initial={{ opacity: 0, y: 32 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          >
            <p className="mb-4 text-sm font-medium text-app-muted">PropIQ</p>
            <h1 className="text-4xl font-semibold leading-[1.08] tracking-tight text-black sm:text-5xl lg:text-[3.5rem]">
              Analyze properties that talk, type, and deliver insights
            </h1>
            <Button variant="primary" size="lg" to="/login" className="mt-8">
              Learn more
            </Button>
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="max-w-md text-base leading-relaxed text-app-muted lg:pb-2"
          >
            Configure, upload, and monitor AI-powered property analysis in minutes — from computer
            vision damage detection to deal metrics, comps, and ranked investment reports.
          </motion.p>
        </div>

        {/* Hero feature cards */}
        <div id="platform" className="mt-16 grid gap-5 lg:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="feature-card grainy-gradient-mint min-h-[380px]"
          >
            <p className="px-6 pt-6 text-sm font-medium text-white/80 md:px-8 md:pt-8">
              Property analysis flow
            </p>
            <ChatMockup />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="feature-card bg-app-muted-bg min-h-[380px]"
          >
            <p className="px-6 pt-6 text-sm font-medium text-app-muted md:px-8 md:pt-8">
              Deal performance
            </p>
            <ChartMockup />
          </motion.div>
        </div>
      </section>

      <Marquee items={marqueeItems} />

      {/* Glass hero banner — WoodNest-inspired */}
      <section className="mx-auto max-w-7xl px-6 py-20">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-[32px] grainy-gradient-hero"
        >
          <div className="absolute inset-0 bg-black/20" />
          <div className="relative grid gap-8 p-8 md:grid-cols-2 md:items-center md:p-12 lg:p-16">
            <div>
              <div className="mb-4 flex items-center gap-2 text-white/90">
                <Star className="h-4 w-4 fill-amber-300 text-amber-300" />
                <span className="text-sm font-medium">4.9 from 200+ analyses</span>
              </div>
              <h2 className="text-3xl font-semibold leading-tight tracking-tight text-white sm:text-4xl">
                Nature&apos;s not required —
                <br />
                just smarter deals
              </h2>
              <p className="mt-4 max-w-md text-sm leading-relaxed text-white/75">
                Upload property details and photos. Get rehab estimates, ARV predictions, and
                investment metrics in under two minutes.
              </p>
            </div>

            <div className="glass-dark rounded-[24px] p-6 md:p-7">
              <p className="font-medium text-white">1842 Oakwood Drive</p>
              <p className="mt-1 text-sm text-white/60">Austin, TX · Single Family</p>
              <div className="mt-5 grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-white/10 px-3 py-2.5">
                  <p className="text-[11px] text-white/50">List Price</p>
                  <p className="text-sm font-medium">$285,000</p>
                </div>
                <div className="rounded-xl bg-white/10 px-3 py-2.5">
                  <p className="text-[11px] text-white/50">Max Offer</p>
                  <p className="text-sm font-medium">$298,000</p>
                </div>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <div>
                  <p className="text-2xl font-semibold text-emerald-300">23.8% ROI</p>
                  <p className="text-xs text-white/50">Score 92/100</p>
                </div>
                <Button variant="white" size="md" to="/login">
                  Reserve analysis
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features grid */}
      <section id="features" className="mx-auto max-w-7xl px-6 py-24">
        <FadeIn className="max-w-2xl">
          <h2 className="text-3xl font-semibold tracking-tight text-black sm:text-4xl">
            One platform for the full analysis pipeline
          </h2>
          <p className="mt-4 text-app-muted">
            Computer vision, machine learning, and market data — unified from upload to PDF report.
          </p>
        </FadeIn>

        <StaggerContainer className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { icon: Building2, title: 'Property Intake', desc: 'Guided forms, photos, room tags.' },
            { icon: BarChart3, title: 'Deal Intelligence', desc: 'ROI, profit, max offer, strategy.' },
            { icon: Layers, title: 'Compare & Rank', desc: 'Stack up to 4 deals side-by-side.' },
          ].map(({ icon: Icon, title, desc }) => (
            <StaggerItem key={title}>
              <div className="glass-card-hover h-full rounded-[24px] p-6">
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-2xl bg-black/[0.04]">
                  <Icon className="h-5 w-5 text-app-subtle" />
                </div>
                <h3 className="font-semibold text-black">{title}</h3>
                <p className="mt-2 text-sm text-app-muted">{desc}</p>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>

        <StaggerContainer className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3" stagger={0.05}>
          {features.map(({ icon: Icon, title, desc }) => (
            <StaggerItem key={title}>
              <div className="glass-card-hover h-full rounded-[24px] p-6">
                <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-black/[0.04]">
                  <Icon className="h-4 w-4 text-app-subtle" />
                </div>
                <h3 className="text-sm font-semibold text-black">{title}</h3>
                <p className="mt-1.5 text-sm text-app-muted">{desc}</p>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-y border-black/[0.06] bg-white py-24">
        <div className="mx-auto max-w-7xl px-6">
          <FadeIn>
            <h2 className="text-3xl font-semibold tracking-tight text-black">How it works</h2>
          </FadeIn>
          <StaggerContainer className="mt-16 grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { n: '01', t: 'Upload property', d: 'Address, price, beds/baths, and photos.' },
              { n: '02', t: 'AI analyzes', d: 'CV damage scan + ML estimates.' },
              { n: '03', t: 'Review metrics', d: 'ROI, max offer, strategy, comps.' },
              { n: '04', t: 'Compare & decide', d: 'Rank deals and export PDF reports.' },
            ].map(({ n, t, d }) => (
              <StaggerItem key={n}>
                <span className="text-4xl font-semibold text-black/10">{n}</span>
                <h3 className="mt-3 font-semibold text-black">{t}</h3>
                <p className="mt-2 text-sm text-app-muted">{d}</p>
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </section>

      {/* CTA */}
      <section id="pricing" className="mx-auto max-w-7xl px-6 py-24">
        <FadeIn className="rounded-[32px] bg-app-muted-bg px-8 py-16 text-center md:px-16">
          <h2 className="text-3xl font-semibold tracking-tight text-black sm:text-4xl">
            Start analyzing deals today
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-app-muted">
            Free demo — log in with pre-configured accounts to explore every page.
          </p>
          <p className="mt-2 text-xs text-app-muted">demo@propiq.com / demo123</p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button variant="primary" size="lg" to="/login">
              Get started
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="lg" to="/login">
              Log in
            </Button>
          </div>
        </FadeIn>
      </section>

      <Footer />
    </div>
  )
}
