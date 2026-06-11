"""O tabuleiro — o agregado central que guarda a posição do jogo.

Um ``Tabuleiro`` reúne tudo que define uma posição de xadrez:

* o **mapa de peças** (``dict`` de casa ocupada para peça);
* de quem é a **vez**;
* os **direitos de roque** ainda disponíveis (notação FEN: ``K Q k q``);
* o **alvo de en passant**, quando o último lance foi um avanço duplo de peão.

Ele oferece duas responsabilidades ao resto do domínio: *consultar* a
posição (que peça está onde, o rei está em xeque?) e *executar* um lance já
validado, atualizando todo esse estado — inclusive os lances especiais
(roque, en passant e promoção). Decidir se um lance é **legal** não é tarefa
do tabuleiro; isso fica no validador de lances.
"""

from __future__ import annotations

import copy

from app.domain.casa import Casa
from app.domain.cor import Cor
from app.domain.history.memento import MementoTabuleiro
from app.domain.pieces.fabrica import criar_peca
from app.domain.pieces.peao import Peao
from app.domain.pieces.rei import Rei
from app.domain.moves.lance import Lance

# FEN da posição inicial padrão do xadrez.
FEN_INICIAL = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Casas de canto que, ao serem deixadas ou capturadas, retiram um direito
# de roque (a torre daquele lado já não pode rocar).
_CANTO_PARA_DIREITO: dict[Casa, str] = {
    Casa(7, 0): "K",  # h1
    Casa(0, 0): "Q",  # a1
    Casa(7, 7): "k",  # h8
    Casa(0, 7): "q",  # a8
}


class Tabuleiro:
    def __init__(
        self,
        casas: dict[Casa, "Peca"],
        vez: Cor = Cor.BRANCA,
        direitos_roque: set[str] | None = None,
        alvo_en_passant: Casa | None = None,
        meio_lances_sem_progresso: int = 0,
    ) -> None:
        self.casas = casas
        self.vez = vez
        self.direitos_roque = direitos_roque if direitos_roque is not None else set()
        self.alvo_en_passant = alvo_en_passant
        # Contador da regra dos 50 lances: meios-lances desde a última captura
        # ou avanço de peão. 100 meios-lances (50 de cada lado) levam a empate.
        self.meio_lances_sem_progresso = meio_lances_sem_progresso

    # -- Construção ------------------------------------------------------

    @classmethod
    def inicial(cls) -> "Tabuleiro":
        """Cria o tabuleiro na posição inicial padrão."""
        return cls.de_fen(FEN_INICIAL)

    @classmethod
    def de_fen(cls, fen: str) -> "Tabuleiro":
        """Monta um tabuleiro a partir de uma string FEN.

        Cada casa ocupada é criada pela fábrica de peças (Factory Method),
        o que mantém este parser ignorante das classes concretas.
        """
        partes = fen.split()
        if len(partes) < 4:
            raise ValueError(f"FEN incompleta: {fen!r}")
        posicao, lado, roque, en_passant = partes[0], partes[1], partes[2], partes[3]

        casas: dict[Casa, "Peca"] = {}
        fileiras = posicao.split("/")
        if len(fileiras) != 8:
            raise ValueError(f"FEN deve ter 8 fileiras: {fen!r}")

        # A FEN descreve da fileira 8 (topo) para a 1; aqui linha 7 é a 8.
        for indice, fileira in enumerate(fileiras):
            linha = 7 - indice
            coluna = 0
            for caractere in fileira:
                if caractere.isdigit():
                    coluna += int(caractere)  # casas vazias seguidas
                else:
                    casas[Casa(coluna, linha)] = criar_peca(caractere)
                    coluna += 1

        vez = Cor.BRANCA if lado == "w" else Cor.PRETA
        direitos = set() if roque == "-" else {c for c in roque if c in "KQkq"}
        alvo = None if en_passant == "-" else Casa.de_algebrica(en_passant)
        meio_lances = int(partes[4]) if len(partes) >= 5 and partes[4].isdigit() else 0
        return cls(casas, vez, direitos, alvo, meio_lances)

    # -- Consultas -------------------------------------------------------

    def peca_em(self, casa: Casa) -> "Peca | None":
        return self.casas.get(casa)

    def esta_vazia(self, casa: Casa) -> bool:
        return casa not in self.casas

    def pecas_da_cor(self, cor: Cor) -> list[tuple[Casa, "Peca"]]:
        return [(casa, peca) for casa, peca in self.casas.items() if peca.cor is cor]

    def encontrar_rei(self, cor: Cor) -> Casa:
        for casa, peca in self.casas.items():
            if isinstance(peca, Rei) and peca.cor is cor:
                return casa
        raise ValueError(f"Não há rei {cor.value} no tabuleiro")

    def casa_atacada(self, alvo: Casa, por_cor: Cor) -> bool:
        """Indica se alguma peça de ``por_cor`` ameaça a casa ``alvo``."""
        for casa, peca in self.pecas_da_cor(por_cor):
            if alvo in peca.casas_atacadas(self, casa):
                return True
        return False

    def esta_em_xeque(self, cor: Cor) -> bool:
        """Indica se o rei de ``cor`` está sob ataque."""
        return self.casa_atacada(self.encontrar_rei(cor), cor.adversaria)

    # -- Execução --------------------------------------------------------

    def aplicar_lance(self, lance: Lance) -> None:
        """Executa um lance já validado, atualizando todo o estado.

        Pressupõe que o lance é legal; a verificação de legalidade é feita
        antes, pelo validador. Trata os três lances especiais (roque, en
        passant e promoção) e atualiza vez, direitos de roque e alvo de en
        passant.
        """
        peca = self.casas[lance.origem]
        houve_captura = self.peca_em(lance.destino) is not None or lance.eh_en_passant
        eh_avanco_peao = isinstance(peca, Peao)

        if lance.eh_en_passant:
            self._remover_peao_capturado_en_passant(lance)
        if lance.eh_roque:
            self._mover_torre_do_roque(lance)

        novo_alvo = self._calcular_alvo_en_passant(peca, lance)
        self._atualizar_direitos_roque(peca, lance)

        del self.casas[lance.origem]
        if lance.promocao:
            peca = criar_peca(self._simbolo_promocao(peca.cor, lance.promocao))
        self.casas[lance.destino] = peca

        self.alvo_en_passant = novo_alvo
        # Captura ou avanço de peão zeram o contador da regra dos 50 lances.
        if houve_captura or eh_avanco_peao:
            self.meio_lances_sem_progresso = 0
        else:
            self.meio_lances_sem_progresso += 1
        self.vez = self.vez.adversaria

    def chave_posicao(self) -> tuple:
        """Chave que identifica a posição para fins de tripla repetição.

        Duas posições são "a mesma" quando coincidem o arranjo das peças, o
        lado da vez, os direitos de roque e o alvo de en passant. O contador
        de 50 lances deliberadamente *não* entra: ele não muda a posição de
        xadrez, só o relógio.
        """
        arranjo = tuple(sorted(
            (casa.coluna, casa.linha, peca.simbolo_fen)
            for casa, peca in self.casas.items()
        ))
        return (
            arranjo,
            self.vez,
            frozenset(self.direitos_roque),
            self.alvo_en_passant,
        )

    def para_fen(self) -> str:
        """Serializa a posição atual em notação FEN (inverso de ``de_fen``).

        Útil para comunicar a posição à interface, que consome FEN. O número
        do lance cheio não é rastreado pelo domínio (não altera as regras),
        então sai sempre como ``1``; os demais campos refletem o estado real.
        """
        fileiras = []
        for linha in range(7, -1, -1):  # FEN vai da fileira 8 para a 1
            texto = ""
            vazias = 0
            for coluna in range(8):
                peca = self.casas.get(Casa(coluna, linha))
                if peca is None:
                    vazias += 1
                    continue
                if vazias:
                    texto += str(vazias)
                    vazias = 0
                texto += peca.simbolo_fen
            if vazias:
                texto += str(vazias)
            fileiras.append(texto)

        posicao = "/".join(fileiras)
        lado = "w" if self.vez is Cor.BRANCA else "b"
        roque = "".join(c for c in "KQkq" if c in self.direitos_roque) or "-"
        en_passant = self.alvo_en_passant.algebrica if self.alvo_en_passant else "-"
        return f"{posicao} {lado} {roque} {en_passant} {self.meio_lances_sem_progresso} 1"

    # -- Memento (padrão Memento) ----------------------------------------

    def criar_memento(self) -> MementoTabuleiro:
        """Tira uma fotografia profunda do estado atual, para undo futuro."""
        return MementoTabuleiro(
            casas=copy.deepcopy(self.casas),
            vez=self.vez,
            direitos_roque=set(self.direitos_roque),
            alvo_en_passant=self.alvo_en_passant,
            meio_lances_sem_progresso=self.meio_lances_sem_progresso,
        )

    def restaurar(self, memento: MementoTabuleiro) -> None:
        """Restaura o tabuleiro a partir de um memento criado por ele mesmo.

        Como originador, o tabuleiro é o único que conhece a estrutura
        interna do memento. A cópia profunda na saída evita que o estado
        restaurado fique compartilhado com a fotografia guardada.
        """
        self.casas = copy.deepcopy(memento._casas)
        self.vez = memento._vez
        self.direitos_roque = set(memento._direitos_roque)
        self.alvo_en_passant = memento._alvo_en_passant
        self.meio_lances_sem_progresso = memento._meio_lances_sem_progresso

    # -- Bastidores da execução -----------------------------------------

    def _remover_peao_capturado_en_passant(self, lance: Lance) -> None:
        # O peão capturado fica na coluna do destino, mas na fileira da origem.
        casa_capturada = Casa(lance.destino.coluna, lance.origem.linha)
        self.casas.pop(casa_capturada, None)

    def _mover_torre_do_roque(self, lance: Lance) -> None:
        linha = lance.origem.linha
        if lance.destino.coluna == 6:  # roque curto: torre de h vai para f
            torre = self.casas.pop(Casa(7, linha))
            self.casas[Casa(5, linha)] = torre
        else:  # roque longo: torre de a vai para d
            torre = self.casas.pop(Casa(0, linha))
            self.casas[Casa(3, linha)] = torre

    def _calcular_alvo_en_passant(self, peca: "Peca", lance: Lance) -> Casa | None:
        avanco_duplo = (
            isinstance(peca, Peao)
            and abs(lance.destino.linha - lance.origem.linha) == 2
        )
        if not avanco_duplo:
            return None
        # O alvo é a casa "saltada" entre a origem e o destino.
        linha_intermediaria = (lance.origem.linha + lance.destino.linha) // 2
        return Casa(lance.origem.coluna, linha_intermediaria)

    def _atualizar_direitos_roque(self, peca: "Peca", lance: Lance) -> None:
        if isinstance(peca, Rei):
            if peca.cor is Cor.BRANCA:
                self.direitos_roque -= {"K", "Q"}
            else:
                self.direitos_roque -= {"k", "q"}
        # Torre que sai do canto, ou canto onde uma torre foi capturada.
        self.direitos_roque.discard(_CANTO_PARA_DIREITO.get(lance.origem))  # type: ignore[arg-type]
        self.direitos_roque.discard(_CANTO_PARA_DIREITO.get(lance.destino))  # type: ignore[arg-type]

    @staticmethod
    def _simbolo_promocao(cor: Cor, simbolo: str) -> str:
        return simbolo.upper() if cor is Cor.BRANCA else simbolo.lower()


# Evita import circular em tempo de carga, mas mantém o type hint útil.
from app.domain.pieces.peca import Peca  # noqa: E402
