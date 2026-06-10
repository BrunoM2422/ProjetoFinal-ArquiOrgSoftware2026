/**
 * Hook que concentra o estado da partida e as ações sobre ela.
 *
 * Mantém a `PartidaView` atual, indicadores de carregamento/erro e a eventual
 * sugestão de lance vinda da análise. Os componentes consomem este hook e
 * ficam livres de detalhes de chamada à API.
 */

import { useCallback, useState } from "react";

import {
  aplicarLance,
  analisar,
  criarPartida,
  desfazer as apiDesfazer,
  refazer as apiRefazer,
} from "../api/cliente";
import type { LanceInput, LanceView, PartidaView } from "../api/tipos";

export function usePartida() {
  const [partida, setPartida] = useState<PartidaView | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [ocupado, setOcupado] = useState(false);
  const [sugestao, setSugestao] = useState<LanceView | null>(null);
  const [ultimoLanceBot, setUltimoLanceBot] = useState<LanceView | null>(null);

  const executar = useCallback(async (acao: () => Promise<void>) => {
    setOcupado(true);
    setErro(null);
    try {
      await acao();
    } catch (e) {
      setErro((e as Error).message);
    } finally {
      setOcupado(false);
    }
  }, []);

  const novaPartida = useCallback(
    (nivelBot: string, corHumano: string) =>
      executar(async () => {
        setSugestao(null);
        setUltimoLanceBot(null);
        setPartida(await criarPartida(nivelBot, corHumano));
      }),
    [executar]
  );

  const jogar = useCallback(
    (lance: LanceInput) =>
      executar(async () => {
        if (!partida) return;
        setSugestao(null);
        const resultado = await aplicarLance(partida.id, lance);
        setPartida(resultado.partida);
        setUltimoLanceBot(resultado.lance_bot);
      }),
    [executar, partida]
  );

  const desfazer = useCallback(
    () =>
      executar(async () => {
        if (!partida) return;
        setSugestao(null);
        setUltimoLanceBot(null);
        setPartida(await apiDesfazer(partida.id));
      }),
    [executar, partida]
  );

  const refazer = useCallback(
    () =>
      executar(async () => {
        if (!partida) return;
        setSugestao(null);
        setUltimoLanceBot(null);
        setPartida(await apiRefazer(partida.id));
      }),
    [executar, partida]
  );

  const pedirAnalise = useCallback(
    () =>
      executar(async () => {
        if (!partida) return;
        const analise = await analisar(partida.id, []);
        setSugestao(analise.lance_sugerido);
      }),
    [executar, partida]
  );

  return {
    partida,
    erro,
    ocupado,
    sugestao,
    ultimoLanceBot,
    novaPartida,
    jogar,
    desfazer,
    refazer,
    pedirAnalise,
  };
}
