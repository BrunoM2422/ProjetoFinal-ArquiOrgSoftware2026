/**
 * Cliente da API REST.
 *
 * Único ponto do front que fala HTTP com o backend. Concentra a URL base, o
 * tratamento de erro (extraindo a mensagem do corpo `{ "erro": ... }`) e a
 * desserialização — os componentes só chamam funções tipadas.
 *
 * Em desenvolvimento, o proxy do Vite reescreve `/api` para o backend
 * FastAPI (ver vite.config.ts), evitando configuração de CORS.
 */

import type {
  AnaliseView,
  LanceInput,
  PartidaView,
  ResultadoLanceView,
} from "./tipos";

const BASE = "/api/v1";

async function tratar<T>(resposta: Response): Promise<T> {
  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => ({}));
    const mensagem = corpo.erro ?? corpo.detail ?? `Erro HTTP ${resposta.status}`;
    throw new Error(typeof mensagem === "string" ? mensagem : JSON.stringify(mensagem));
  }
  return resposta.json() as Promise<T>;
}

function postar<T>(caminho: string, corpo?: unknown): Promise<T> {
  return fetch(`${BASE}${caminho}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  }).then((r) => tratar<T>(r));
}

export function criarPartida(
  nivelBot: string,
  corHumano: string
): Promise<PartidaView> {
  return postar<PartidaView>("/games", {
    nivel_bot: nivelBot,
    cor_humano: corHumano,
  });
}

export function obterPartida(id: string): Promise<PartidaView> {
  return fetch(`${BASE}/games/${id}`).then((r) => tratar<PartidaView>(r));
}

export function aplicarLance(
  id: string,
  lance: LanceInput
): Promise<ResultadoLanceView> {
  return postar<ResultadoLanceView>(`/games/${id}/moves`, lance);
}

export function desfazer(id: string): Promise<PartidaView> {
  return postar<PartidaView>(`/games/${id}/undo`);
}

export function refazer(id: string): Promise<PartidaView> {
  return postar<PartidaView>(`/games/${id}/redo`);
}

export function analisar(
  id: string,
  lances: LanceInput[]
): Promise<AnaliseView> {
  return postar<AnaliseView>(`/games/${id}/analysis`, { lances });
}
