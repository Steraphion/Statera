<script lang="ts">
  import { columns } from '../lib/columns.svelte'
  import { dragWidth, keyWidth, limits, pxOf, type ColumnId } from '../lib/columns'

  /**
   * Separatore tra due colonne su PC (design system: Separatore): si trascina col mouse o si sposta
   * con le frecce; doppio clic o Invio riportano la colonna alla larghezza iniziale. Sta nello spazio
   * tra le colonne, quindi non ruba larghezza.
   */
  let {
    id,
    label,
    controls,
    grows,
    token,
  }: {
    id: ColumnId
    /** Nome per gli screen reader, es. "Larghezza della colonna di destra". */
    label: string
    /** id dell'elemento della colonna che cambia larghezza. */
    controls: string
    /** Da che parte si allarga la colonna: 'left' se sta a destra del separatore. */
    grows: 'left' | 'right'
    /** Token della larghezza iniziale; minimo e massimo sono lo stesso nome con -min e -max. */
    token: string
  } = $props()

  let el = $state<HTMLElement>()
  let dragging = $state(false)
  let now = $state(0)

  function token$(name: string, fallback: number): number {
    return pxOf(getComputedStyle(document.documentElement).getPropertyValue(name), fallback)
  }

  /** Limiti di adesso: il massimo tiene conto dello spazio che resta alla colonna principale. */
  function bounds() {
    const min = token$(`${token}-min`, 200)
    const max = token$(`${token}-max`, 600)
    const host = el?.parentElement
    if (!host || !el) return { min, max }
    const other = host.clientWidth - el.offsetWidth - token$('--size-main-min', 400)
    return limits(min, max, other)
  }

  function current(): number {
    const col = document.getElementById(controls)
    return Math.round(col?.getBoundingClientRect().width ?? token$(token, 320))
  }

  // Valore mostrato agli screen reader: si aggiorna quando cambia la scelta o la finestra
  $effect(() => {
    void columns.width(id)
    void columns.pc
    void columns.railNow
    requestAnimationFrame(() => (now = current()))
  })

  let start = { w: 0, x: 0 }

  function onpointerdown(e: PointerEvent) {
    if (e.button !== 0) return
    e.preventDefault()
    el!.setPointerCapture(e.pointerId)
    start = { w: current(), x: e.clientX }
    dragging = true
    document.documentElement.classList.add('resizing')
  }

  function onpointermove(e: PointerEvent) {
    if (!dragging) return
    const b = bounds()
    columns.setWidth(id, dragWidth(start.w, start.x, e.clientX, grows, b.min, b.max), false)
  }

  function stop() {
    if (!dragging) return
    dragging = false
    document.documentElement.classList.remove('resizing')
    columns.save()
  }

  function onkeydown(e: KeyboardEvent) {
    if (e.ctrlKey || e.metaKey || e.altKey) return
    if (e.key === 'Enter') {
      e.preventDefault()
      columns.setWidth(id, null)
      return
    }
    const b = bounds()
    const w = keyWidth(current(), e.key, e.shiftKey, grows, b.min, b.max)
    if (w === null) return
    e.preventDefault()
    // Le frecce qui spostano il separatore, non cambiano mese (Movimenti) né conto (Conti)
    e.stopPropagation()
    columns.setWidth(id, w)
  }
</script>

<!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
<div
  bind:this={el}
  class="splitter"
  class:dragging
  role="separator"
  tabindex="0"
  aria-orientation="vertical"
  aria-label={label}
  aria-controls={controls}
  aria-valuenow={now}
  aria-valuemin={bounds().min}
  aria-valuemax={bounds().max}
  aria-valuetext="{now} pixel"
  title="Trascina per cambiare la larghezza. Doppio clic: larghezza iniziale"
  {onpointerdown}
  {onpointermove}
  onpointerup={stop}
  onpointercancel={stop}
  onlostpointercapture={stop}
  ondblclick={() => columns.setWidth(id, null)}
  {onkeydown}
>
  <span class="grip" aria-hidden="true"></span>
</div>

<style>
  /* Occupa lo spazio tra le colonne: area di presa larga quanto lo spazio, linea sottile al centro */
  .splitter {
    position: relative;
    align-self: stretch;
    display: flex;
    justify-content: center;
    cursor: col-resize;
    touch-action: none;
    user-select: none;
    outline: none;
  }

  /* Linea: compare passando col puntatore, col focus e mentre si trascina */
  .splitter::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 50%;
    width: var(--focus-width);
    translate: -50% 0;
    border-radius: var(--radius-full);
    background: var(--color-accent);
    opacity: 0;
    transition: opacity var(--duration-fast) var(--ease-standard);
  }

  /* Maniglia: resta a metà schermo mentre si scorre, così si trova sempre */
  .grip {
    position: sticky;
    top: calc(50dvh - var(--space-5));
    width: var(--space-1);
    height: var(--space-7);
    margin-top: var(--space-8);
    border-radius: var(--radius-full);
    background: var(--color-border);
    transition: background-color var(--duration-fast) var(--ease-standard);
  }

  .splitter:hover::before,
  .splitter.dragging::before,
  .splitter:focus-visible::before {
    opacity: 1;
  }

  .splitter:hover .grip,
  .splitter.dragging .grip,
  .splitter:focus-visible .grip {
    background: var(--color-accent);
  }

  .splitter:focus-visible .grip {
    outline: var(--focus-width) solid var(--color-focus);
    outline-offset: var(--focus-offset);
  }
</style>
