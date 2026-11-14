// Generato da scripts/icona-app.mjs: non modificare a mano.
// Simbolo di Statera (bilancia a tratto) su una griglia di 512 unità, già centrato nel riquadro.
export type LogoNode = ['path' | 'circle', Record<string, string>]

export const LOGO_SIZE = 512
export const LOGO_RADIUS = 115

/** Disegno grande (da 48 px) e piccolo (fino a 32 px), con la trasformazione che lo centra. */
export const LOGO: Record<'grande' | 'piccolo', { transform: string; nodes: LogoNode[] }> = {
  "grande": {
    "transform": "translate(89.043 87.374) scale(3.339)",
    "nodes": [
      [
        "path",
        {
          "d": "M50 24V82",
          "fill": "none",
          "stroke": "currentColor",
          "stroke-width": "7.5",
          "stroke-linecap": "round"
        }
      ],
      [
        "path",
        {
          "d": "M33 84H67",
          "fill": "none",
          "stroke": "currentColor",
          "stroke-width": "8",
          "stroke-linecap": "round"
        }
      ],
      [
        "path",
        {
          "d": "M14 30H86",
          "fill": "none",
          "stroke": "currentColor",
          "stroke-width": "7.5",
          "stroke-linecap": "round"
        }
      ],
      [
        "path",
        {
          "d": "M8 58L20 30L32 58M68 58L80 30L92 58",
          "fill": "none",
          "stroke": "currentColor",
          "stroke-width": "4.5",
          "stroke-linecap": "round",
          "stroke-linejoin": "round"
        }
      ],
      [
        "circle",
        {
          "cx": "50",
          "cy": "20",
          "r": "7",
          "fill": "currentColor"
        }
      ],
      [
        "path",
        {
          "d": "M4 58H36A16 16 0 0 1 4 58Z",
          "fill": "currentColor"
        }
      ],
      [
        "path",
        {
          "d": "M64 58H96A16 16 0 0 1 64 58Z",
          "fill": "currentColor"
        }
      ]
    ]
  },
  "piccolo": {
    "transform": "translate(81.92 67.994) scale(3.482)",
    "nodes": [
      [
        "path",
        {
          "d": "M50 22V82M30 86H70M10 28H90",
          "fill": "none",
          "stroke": "currentColor",
          "stroke-width": "11",
          "stroke-linecap": "round",
          "stroke-linejoin": "round"
        }
      ],
      [
        "path",
        {
          "d": "M20 30V50M80 30V50",
          "fill": "none",
          "stroke": "currentColor",
          "stroke-width": "8",
          "stroke-linecap": "round"
        }
      ],
      [
        "path",
        {
          "d": "M0 52H40A20 20 0 0 1 0 52Z",
          "fill": "currentColor"
        }
      ],
      [
        "path",
        {
          "d": "M60 52H100A20 20 0 0 1 60 52Z",
          "fill": "currentColor"
        }
      ]
    ]
  }
}
