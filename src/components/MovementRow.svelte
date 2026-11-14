<script lang="ts">
  import Icon from './Icon.svelte'
  import * as mv from '../lib/data/transactions'
  import type { Refs } from '../lib/data/refs.svelte'
  import type { Transaction } from '../lib/data/types'
  import { formatEuro, formatShortDay, formatVouchers } from '../lib/format'

  let {
    t,
    refs,
    effect = null,
    balanceAfter = null,
    muted = false,
    showDate = false,
    onclick,
  }: {
    t: Transaction
    refs: Refs
    /** Effetto con segno su un conto specifico (vista conto); altrimenti si mostra il totale. */
    effect?: number | null
    /** Saldo del conto dopo questo movimento (vista conto). */
    balanceAfter?: number | null
    /** Movimento che non incide sul saldo (precedente al saldo iniziale). */
    muted?: boolean
    showDate?: boolean
    onclick: () => void
  } = $props()

  /** Categoria, o le categorie di un movimento ripartito ("Spesa alimentare + Casa"). */
  const catText = $derived(
    mv
      .categoryShares(t)
      .map((sp) => mv.categoryLabel(sp.categoryId, refs.categoryMap))
      .join(' + '),
  )

  const title = $derived.by(() => {
    if (t.description) return t.description
    if (t.type === 'trasferimento') return 'Trasferimento'
    return catText
  })

  const subtitle = $derived.by(() => {
    const from = t.parts.map((p) => mv.partLabel(p, refs.accountMap, refs.cardMap)).join(' + ')
    const pieces: string[] = []
    if (t.id.startsWith('rec-')) pieces.push('↻ ricorrente')
    if (showDate) pieces.push(formatShortDay(t.date))
    if (t.type === 'trasferimento') pieces.push(`${from} → ${refs.accountMap.get(t.toAccountId ?? '')?.name ?? '—'}`)
    else {
      if (t.description) pieces.push(catText)
      pieces.push(from)
    }
    for (const tag of t.tags ?? []) pieces.push(`#${tag}`)
    return pieces.join(' · ')
  })

  const vouchers = $derived(t.parts.reduce((s, p) => s + (p.vouchers ?? 0), 0))

  const color = $derived.by(() => {
    const c = t.categoryId ? refs.categoryMap.get(t.categoryId) : null
    const top = c?.parentId ? refs.categoryMap.get(c.parentId) : c
    return top ? `var(--swatch-${top.color})` : 'var(--color-text-muted)'
  })

  const shown = $derived.by(() => {
    if (effect !== null) return { value: effect, sign: effect > 0 ? '+' : effect < 0 ? '−' : '' }
    const total = mv.total(t)
    return { value: total, sign: t.type === 'entrata' ? '+' : t.type === 'uscita' ? '−' : '' }
  })
</script>

<button class="list-row" class:muted {onclick}>
  {#if t.type === 'trasferimento'}
    <span class="icon"><Icon name="transfer" size={16} /></span>
  {:else}
    <span class="dot" style:background={color}></span>
  {/if}
  <span class="main">
    <span class="name">{title}</span>
    <span class="sub">{subtitle}</span>
  </span>
  <span class="end">
    <span
      class="num amount"
      class:income={effect !== null ? effect > 0 : t.type === 'entrata'}
      class:expense={effect !== null ? effect < 0 : t.type === 'uscita'}
    >
      {shown.sign}{formatEuro(Math.abs(shown.value))}
    </span>
    {#if balanceAfter !== null}
      <span class="sub small num">{muted ? 'non incide' : formatEuro(balanceAfter)}</span>
    {:else if vouchers > 0}
      <span class="sub small">{formatVouchers(vouchers)}</span>
    {/if}
  </span>
</button>

<style>
  .icon {
    flex: none;
    display: grid;
    place-items: center;
    width: 12px;
    color: var(--color-text-muted);
  }

  .end {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
  }

  .amount {
    font-weight: 600;
  }

  .income {
    color: var(--color-income);
  }

  .expense {
    color: var(--color-expense);
  }

  .small {
    font-size: var(--text-xs);
  }

  .muted {
    opacity: 0.55;
  }
</style>
