/**
 * Lista dos lances já jogados, em pares (brancas / pretas) numerados.
 */

interface Props {
  historico: string[];
}

export function ListaLances({ historico }: Props) {
  const pares: Array<[string, string | null]> = [];
  for (let i = 0; i < historico.length; i += 2) {
    pares.push([historico[i], historico[i + 1] ?? null]);
  }

  return (
    <div className="lista-lances">
      <h2>Lances</h2>
      {pares.length === 0 ? (
        <p className="vazio">Nenhum lance ainda.</p>
      ) : (
        <ol>
          {pares.map(([brancas, pretas], indice) => (
            <li key={indice}>
              <span className="numero">{indice + 1}.</span>
              <span className="lance">{brancas}</span>
              <span className="lance">{pretas ?? ""}</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
