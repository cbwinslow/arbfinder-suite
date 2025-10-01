'use client'
import { useEffect, useState } from 'react'

export default function Home() {
  const [rows, setRows] = useState<any[]>([])
  const [title, setTitle] = useState('')
  const [price, setPrice] = useState('')

  useEffect(() => {
    fetch((process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080') + '/api/listings')
      .then(r => r.json()).then(setRows).catch(() => {})
  }, [])

  const checkout = async (t: string, p: number) => {
    const base = (process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080')
    const url = new URL(base + '/api/stripe/create-checkout-session')
    url.searchParams.set('title', t)
    url.searchParams.set('price', String(p))
    const r = await fetch(url, { method: 'POST' })
    const j = await r.json(); if (j.url) window.location.href = j.url
  }

  const submit = async () => {
    await fetch((process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080') + '/api/listings', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, price: Number(price), url: '#' })
    })
    setTitle(''); setPrice('');
    const data = await fetch((process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8080') + '/api/listings').then(r => r.json())
    setRows(data)
  }

  return (
    <main className="mx-auto max-w-4xl p-6 space-y-6">
      <h1 className="text-3xl font-bold">ArbFinder — Deals & Checkout</h1>
      <div className="space-y-2">
        <input className="w-full bg-neutral-900 p-2 rounded" placeholder="Title" value={title} onChange={e => setTitle(e.target.value)} />
        <input className="w-full bg-neutral-900 p-2 rounded" placeholder="Price" value={price} onChange={e => setPrice(e.target.value)} />
        <button className="bg-green-700 px-4 py-2 rounded" onClick={submit}>Add Listing</button>
      </div>
      <div className="space-y-3">
        {rows.map((r, i) => (
          <div key={i} className="bg-neutral-900 p-4 rounded">
            <div className="text-lg font-semibold">{r.title}</div>
            <div className="text-sm">${'{'}r.price{'}'} {'{'}r.currency{'}'} — <a className="underline" href={'{'}r.url{'}'} target="_blank">source</a></div>
            <div className="mt-2">
              <button className="bg-blue-700 px-3 py-1 rounded" onClick={() => checkout(r.title, r.price)}>Buy with Stripe</button>
            </div>
          </div>
        ))}
      </div>
    </main>
  )
}
