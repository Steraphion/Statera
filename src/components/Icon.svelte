<script lang="ts">
  // Icone disegnate in SVG direttamente nel codice: nessuna libreria esterna.
  const PATHS: Record<string, string> = {
    list: 'M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01',
    wallet:
      'M3 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v1M3 7v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2H5a2 2 0 0 1-2-2zM16 14h.01',
    chart: 'M4 20V10M10 20V4M16 20v-7M22 20H2',
    more: 'M5 12h.01M12 12h.01M19 12h.01',
    plus: 'M12 5v14M5 12h14',
    balance: 'M12 4v16M8 20h8M4 7h16M6 7l-3 7h6zM18 7l-3 7h6z',
    transfer: 'M7 7h13M16 3l4 4-4 4M17 17H4M8 13l-4 4 4 4',
    left: 'M15 18l-6-6 6-6',
    search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM21 21l-4.35-4.35',
    right: 'M9 18l6-6-6-6',
  }

  let { name, size = 24 }: { name: string; size?: number } = $props()
</script>

<svg
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="2"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
>
  <path d={PATHS[name] ?? ''} />
</svg>
