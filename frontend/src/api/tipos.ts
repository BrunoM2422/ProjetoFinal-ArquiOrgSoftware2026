/**
 * Tipos espelhando os DTOs da API REST (ver backend/app/adapters/api/schemas.py).
 *
 * Manter os tipos do front alinhados aos schemas do back dá segurança de tipo
 * de ponta a ponta: se o contrato mudar, o TypeScript acusa onde o front
 * precisa acompanhar.
 */

export interface LanceView {
  origem: string;
  destino: string;
  promocao: string | null;
  notacao: string;
}

export interface EstadoView {
  nome: string;
  descricao: string;
  terminada: boolean;
  em_xeque: boolean;
  resultado: string | null;
}

export interface PartidaView {
  id: string;
  fen: string;
  vez: string;
  estado: EstadoView;
  historico: string[];
  lances_legais: LanceView[];
  pode_desfazer: boolean;
  pode_refazer: boolean;
  nivel_bot: string;
  cor_bot: string;
  cor_humano: string;
}

export interface ResultadoLanceView {
  partida: PartidaView;
  lance_humano: LanceView;
  lance_bot: LanceView | null;
}

export interface AnaliseView {
  fen: string;
  vez: string;
  estado: EstadoView;
  historico: string[];
  lance_sugerido: LanceView | null;
}

/** Um lance pedido pela interface, em coordenadas algébricas. */
export interface LanceInput {
  origem: string;
  destino: string;
  promocao: string | null;
}
