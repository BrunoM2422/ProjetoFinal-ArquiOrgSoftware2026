/**
 * Painel de controles: nova partida (nível do bot + cor), desfazer, refazer e
 * pedir análise ("e se?").
 */

import { useState } from "react";

import type { PartidaView } from "../api/tipos";

const NIVEIS: Array<{ valor: string; rotulo: string }> = [
  { valor: "aleatorio", rotulo: "Aleatório" },
  { valor: "guloso", rotulo: "Guloso" },
  { valor: "minimax", rotulo: "Minimax (prof. 2)" },
];

interface Props {
  partida: PartidaView | null;
  ocupado: boolean;
  onNova: (nivelBot: string, corHumano: string) => void;
  onDesfazer: () => void;
  onRefazer: () => void;
  onAnalisar: () => void;
}

export function Controles({
  partida,
  ocupado,
  onNova,
  onDesfazer,
  onRefazer,
  onAnalisar,
}: Props) {
  const [nivel, setNivel] = useState("minimax");
  const [cor, setCor] = useState("branca");

  return (
    <div className="controles">
      <div className="nova-partida">
        <h2>Nova partida</h2>
        <label>
          Nível do bot
          <select value={nivel} onChange={(e) => setNivel(e.target.value)} disabled={ocupado}>
            {NIVEIS.map((n) => (
              <option key={n.valor} value={n.valor}>
                {n.rotulo}
              </option>
            ))}
          </select>
        </label>
        <label>
          Você joga de
          <select value={cor} onChange={(e) => setCor(e.target.value)} disabled={ocupado}>
            <option value="branca">Brancas</option>
            <option value="preta">Pretas</option>
          </select>
        </label>
        <button type="button" onClick={() => onNova(nivel, cor)} disabled={ocupado}>
          Iniciar
        </button>
      </div>

      <div className="acoes">
        <h2>Ações</h2>
        <button
          type="button"
          onClick={onDesfazer}
          disabled={ocupado || !partida?.pode_desfazer}
        >
          ↶ Desfazer
        </button>
        <button
          type="button"
          onClick={onRefazer}
          disabled={ocupado || !partida?.pode_refazer}
        >
          ↷ Refazer
        </button>
        <button
          type="button"
          onClick={onAnalisar}
          disabled={ocupado || !partida || partida.estado.terminada}
        >
          💡 Analisar
        </button>
      </div>
    </div>
  );
}
