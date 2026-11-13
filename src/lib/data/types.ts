/**
 * MODELLO DATI DI STATERA
 * - Importi: interi in centesimi (1234 = 12,34 €)
 * - Date contabili: stringhe 'AAAA-MM-GG'
 * - Timestamp tecnici: millisecondi (Date.now())
 * - Colori: chiave di una tinta definita in tokens.css ('s1'…'s8'), mai un colore fisso
 */

/** Campi comuni a ogni record: servono alla sincronizzazione (Fase 2). */
export interface Base {
  id: string
  createdAt: number
  updatedAt: number
  /** Cancellazione logica: il record resta, così la cancellazione si propaga agli altri dispositivi. */
  deletedAt: number | null
}

export type SwatchKey = 's1' | 's2' | 's3' | 's4' | 's5' | 's6' | 's7' | 's8'

export type AccountType = 'contanti' | 'conto_corrente' | 'buoni_pasto' | 'altro'

export interface Account extends Base {
  name: string
  type: AccountType
  /** Saldo alla data iniziale (per i buoni pasto: initialVouchers × voucherValue). */
  initialBalance: number
  /** Da questa data in poi i movimenti modificano il saldo. */
  initialDate: string
  /** Solo buoni pasto: valore nominale di un buono, in centesimi. */
  voucherValue: number | null
  /** Solo buoni pasto: numero di buoni alla data iniziale. */
  initialVouchers: number | null
  color: SwatchKey
  order: number
  archived: boolean
}

export interface Card extends Base {
  name: string
  /** Conto da cui la carta preleva. */
  accountId: string
  order: number
  archived: boolean
}

export type CategoryKind = 'entrata' | 'uscita'

export interface Category extends Base {
  name: string
  kind: CategoryKind
  /** null = categoria principale; altrimenti id della categoria madre. */
  parentId: string | null
  color: SwatchKey
  order: number
  archived: boolean
  /** Solo categorie principali di spesa: budget mensile in centesimi (assente/null = nessun budget). */
  monthlyBudget?: number | null
}

export type TransactionType = 'entrata' | 'uscita' | 'trasferimento'

/** Una parte di un movimento: da quale conto/carta e quanto. */
export interface TransactionPart {
  accountId: string
  cardId: string | null
  /** Importo positivo in centesimi. */
  amount: number
  /** Solo buoni pasto: numero di buoni e valore unitario al momento del movimento. */
  vouchers: number | null
  voucherValue: number | null
}

export interface Transaction extends Base {
  type: TransactionType
  date: string
  categoryId: string | null
  description: string
  notes: string
  /** Una parte = pagamento normale; più parti = pagamento misto. Per i trasferimenti: il conto di origine. */
  parts: TransactionPart[]
  /** Solo trasferimenti: conto di destinazione. */
  toAccountId: string | null
  /** Indice derivato: tutti i conti coinvolti (per le ricerche veloci). */
  accountIds: string[]
}

export interface Meta {
  key: string
  value: unknown
}

export const ACCOUNT_TYPE_LABELS: Record<AccountType, string> = {
  contanti: 'Contanti',
  conto_corrente: 'Conto corrente',
  buoni_pasto: 'Buoni pasto',
  altro: 'Altro',
}

export const SWATCHES: SwatchKey[] = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']
