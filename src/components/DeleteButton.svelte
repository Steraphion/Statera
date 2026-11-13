<script lang="ts">
  // Eliminazione in due tocchi: il primo chiede conferma, il secondo elimina.
  let { onconfirm, label = 'Elimina' }: { onconfirm: () => void; label?: string } = $props()

  let armed = $state(false)

  $effect(() => {
    if (!armed) return
    const t = setTimeout(() => (armed = false), 4000)
    return () => clearTimeout(t)
  })
</script>

<button
  type="button"
  class="btn btn-danger"
  class:confirm={armed}
  onclick={() => {
    if (armed) onconfirm()
    else armed = true
  }}
>
  {armed ? 'Conferma eliminazione' : label}
</button>
